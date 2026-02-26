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
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            logger.error(f"Port Pre-check Failed: {host}:{port} is unreachable. Error: {str(e)}")
            return False

    @staticmethod
    def _create_pymssql_conn(config: dict, db_name: str):
        return pymssql.connect(
            server=config['host'],
            port=config['port'],
            user=config['username'],
            password=config['password'],
            database=db_name,
            as_dict=True,
            login_timeout=10,
            timeout=30
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

        # 2. Pre-check port to avoid long hangs in pymssql
        if not SQLServerConnection.check_port_open(config['host'], config['port']):
            raise ConnectionError(f"SQL Server at {config['host']}:{config['port']} is unreachable. Check firewall and IP.")

        # 3. Attempt connection with a hard thread timeout
        logger.info(f"Connecting to SQL Server at {config['host']}:{config['port']} (DB: {db_name})...")
        
        future = SQLServerConnection._executor.submit(SQLServerConnection._create_pymssql_conn, config, db_name)
        try:
            conn = future.result(timeout=15) # Hard 15s timeout for the connection attempt
            SQLServerConnection._connection_pool[db_name] = conn
            logger.info(f"Connected successfully to {db_name}")
            return conn
        except TimeoutError:
            logger.error(f"Connection attempt timed out after 15s for {db_name}")
            raise ConnectionError("SQL Server connection timed out.")
        except Exception as e:
            logger.error(f"Failed to connect to SQL Server: {str(e)}")
            raise

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
            return []

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
            return []
