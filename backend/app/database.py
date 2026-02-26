from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
import os
from dotenv import load_dotenv
import pymssql
from typing import List, Dict, Any, Optional
import time
import logging
import socket
from concurrent.futures import ThreadPoolExecutor, TimeoutError

load_dotenv()

# Setup logger for discovery
logger = logging.getLogger("router_db_backend.discovery")

# SQLite Configuration for main storage
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_router.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# In-memory cache for discovery
_discovery_cache = {
    'databases': {'data': [], 'expires': 0},
    'tables': {} # database_name: {'data': [], 'expires': 0}
}
CACHE_TTL = 300 # 5 minutes

# SQL Server Connection Management
class SQLServerConnection:
    _connection_pool = {} 
    _executor = ThreadPoolExecutor(max_workers=5)

    @staticmethod
    def get_global_config():
        return {
            'host': os.getenv('SQL_SERVER_HOST', 'localhost'),
            'port': int(os.getenv('SQL_SERVER_PORT', '1433')),
            'username': os.getenv('SQL_SERVER_USER', 'sa'),
            'password': os.getenv('SQL_SERVER_PASSWORD', '')
        }

    @staticmethod
    def check_port_open(host: str, port: int, timeout: int = 3) -> bool:
        """Quick check if the TCP port is reachable before calling pymssql."""
        # Handle Named Instances: extract only the IP/Host part for the socket check
        base_host = host.split('\\')[0] if '\\' in host else host
        
        try:
            logger.info(f"Pre-checking TCP connectivity to {base_host}:{port}...")
            with socket.create_connection((base_host, port), timeout=timeout):
                logger.info(f"TCP Port {port} is OPEN on {base_host}")
                return True
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            logger.error(f"Port Pre-check Failed: {base_host}:{port} is unreachable. Error: {str(e)}")
            return False

    @staticmethod
    def _create_pymssql_conn(config: dict, db_name: str):
        # IMPORTANT: For Named Instances in pymssql, the recommended format is host:port
        # The backslash format (host\instance) can sometimes be flaky with some drivers.
        # We'll try to use the host as is, but if it has a backslash, pymssql should handle it.
        server_str = config['host']
        return pymssql.connect(
            server=server_str,
            port=config['port'],
            user=config['username'],
            password=config['password'],
            database=db_name,
            as_dict=True,
            login_timeout=20,
            timeout=60,
            charset='utf8' # Ensure charset for better compatibility
        )

    @staticmethod
    def get_connection(database: Optional[str] = None):
        db_name = database if database else 'master'
        config = SQLServerConnection.get_global_config()
        
        # 1. Check if cached connection is healthy
        if db_name in SQLServerConnection._connection_pool:
            conn = SQLServerConnection._connection_pool[db_name]
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return conn
            except:
                del SQLServerConnection._connection_pool[db_name]

        # 2. Pre-check port (using only base host for socket)
        # We log the result but DON'T raise an error here to let pymssql try its own logic
        # as Named Instances often use dynamic ports via SQL Browser.
        SQLServerConnection.check_port_open(config['host'], config['port'])

        # 3. Attempt connection with a hard thread timeout
        logger.info(f"Attempting pymssql connection to server: {config['host']} (Port: {config['port']}, User: {config['username']}, DB: {db_name})...")
        
        future = SQLServerConnection._executor.submit(SQLServerConnection._create_pymssql_conn, config, db_name)
        try:
            # Increased hard timeout for named instances discovery
            conn = future.result(timeout=30) 
            SQLServerConnection._connection_pool[db_name] = conn
            logger.info(f"Connected successfully to SQL Server ({db_name})")
            return conn
        except TimeoutError:
            logger.error(f"pymssql connection attempt timed out after 30s for {config['host']}")
            raise ConnectionError(f"Tempo esgotado ao conectar a {config['host']}. Verifique se o SQL Browser está ativo.")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"pymssql failed to connect: {error_msg}")
            # Specific hint for common named instance issues
            if "Adaptive Server is unavailable" in error_msg:
                error_msg += " (Dica: Verifique se o SQL Browser Service está rodando no servidor e se conexões remotas estão habilitadas)"
            raise ConnectionError(f"Erro de conexão SQL Server: {error_msg}")

    @staticmethod
    def execute_query(conn, query: str, params: Optional[Dict[str, Any]] = None, close_conn: bool = True) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            try:
                result = cursor.fetchall()
                return result
            except pymssql.OperationalError:
                return []
        except Exception as e:
            logger.error(f"SQL Query Execution Error: {str(e)}")
            raise
        finally:
            cursor.close()
            if close_conn:
                conn.close()
                for db, c in list(SQLServerConnection._connection_pool.items()):
                    if c == conn:
                        del SQLServerConnection._connection_pool[db]

    @staticmethod
    def list_databases() -> List[str]:
        now = time.time()
        if _discovery_cache['databases']['expires'] > now:
            return _discovery_cache['databases']['data']

        try:
            conn = SQLServerConnection.get_connection()
            query = "SELECT name FROM sys.databases WHERE database_id > 4 AND state = 0" 
            result = SQLServerConnection.execute_query(conn, query, close_conn=False)
            db_list = [row['name'] for row in result]
            
            _discovery_cache['databases'] = {
                'data': db_list,
                'expires': now + CACHE_TTL
            }
            return db_list
        except Exception as e:
            logger.error(f"Discovery Error (Databases): {str(e)}")
            raise

    @staticmethod
    def list_tables(database: str) -> List[str]:
        now = time.time()
        if database in _discovery_cache['tables'] and _discovery_cache['tables'][database]['expires'] > now:
            return _discovery_cache['tables'][database]['data']

        try:
            conn = SQLServerConnection.get_connection(database=database)
            query = "SELECT s.name + '.' + t.name as TABLE_NAME FROM sys.tables t INNER JOIN sys.schemas s ON t.schema_id = s.schema_id WHERE t.is_ms_shipped = 0"
            result = SQLServerConnection.execute_query(conn, query, close_conn=False)
            table_list = [row['TABLE_NAME'] for row in result]
            
            _discovery_cache['tables'][database] = {
                'data': table_list,
                'expires': now + CACHE_TTL
            }
            return table_list
        except Exception as e:
            logger.error(f"Discovery Error (Tables for {database}): {str(e)}")
            raise
