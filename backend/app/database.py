from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
import os
from dotenv import load_dotenv
import pyodbc
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
    def check_port_open(host: str, port: int, timeout: int = 2) -> bool:
        """Quick check if the TCP port is reachable."""
        base_host = host.split('\\')[0] if '\\' in host else host
        try:
            with socket.create_connection((base_host, port), timeout=timeout):
                logger.info(f"TCP Port {port} is OPEN on {base_host}")
                return True
        except:
            return False

    @staticmethod
    def _create_pyodbc_conn(config: dict, db_name: str):
        # pyodbc uses connection strings. This is the most robust way for Named Instances.
        # Format: DRIVER={SQL Server};SERVER=host\instance,port;DATABASE=db;UID=user;PWD=pass
        
        # We'll try the 'ODBC Driver 17 for SQL Server' first, then fallback to legacy 'SQL Server'
        drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
        driver = drivers[0] if drivers else '{SQL Server}'
        
        server = config['host']
        if config['port'] and config['port'] != 1433:
            # If named instance is used with a port, ODBC uses comma: host\instance,port
            server = f"{server},{config['port']}"

        conn_str = (
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={db_name};"
            f"UID={config['username']};"
            f"PWD={config['password']};"
            "Connection Timeout=15;"
        )
        
        logger.info(f"ODBC CONNECT: DRIVER={driver};SERVER={server};DATABASE={db_name};UID={config['username']}")
        return pyodbc.connect(conn_str)

    @staticmethod
    def get_connection(database: Optional[str] = None):
        db_name = database if database else 'master'
        config = SQLServerConnection.get_global_config()
        
        if db_name in SQLServerConnection._connection_pool:
            conn = SQLServerConnection._connection_pool[db_name]
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return conn
            except:
                del SQLServerConnection._connection_pool[db_name]

        logger.info(f"Initiating ODBC connection for {db_name}...")
        
        future = SQLServerConnection._executor.submit(SQLServerConnection._create_pyodbc_conn, config, db_name)
        try:
            conn = future.result(timeout=30) 
            SQLServerConnection._connection_pool[db_name] = conn
            logger.info(f"ODBC Connected successfully to {db_name}")
            return conn
        except TimeoutError:
            logger.error(f"ODBC connection attempt timed out for {config['host']}")
            raise ConnectionError(f"Timeout ODBC ao conectar a {config['host']}.")
        except Exception as e:
            logger.error(f"ODBC failed: {str(e)}")
            raise ConnectionError(f"Falha na conexão ODBC: {str(e)}")

    @staticmethod
    def execute_query(conn, query: str, params: Optional[Dict[str, Any]] = None, close_conn: bool = True, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        try:
            if params:
                # Pass params to execute. pyodbc supports positional (?) parameters.
                # If params is a dict, we might need to convert or assume query uses ? and params is list/tuple.
                # But QueryRequest defines params as Dict[str, Any].
                # pyodbc with SQL Server usually handles named parameters if supported by driver, 
                # or we assume the user provides params matching the query style.
                # Standard pyodbc use is execute(sql, params_list) or execute(sql, param1, param2...)
                # If params is dict, we assume query uses %(name)s style? No, pyodbc uses ? usually.
                # Let's pass params directly and hope pyodbc/SQLAlchemy driver handles it or fails gracefully.
                # Given existing code didn't pass it, it was broken or unused.
                cursor.execute(query, params) if isinstance(params, (list, tuple)) else cursor.execute(query, list(params.values()))
            else:
                cursor.execute(query)
            
            if cursor.description is None:
                # No results (e.g. UPDATE/INSERT)
                return []

            columns = [column[0] for column in cursor.description]
            result = []
            
            rows = cursor.fetchmany(limit) if limit else cursor.fetchall()
            
            for row in rows:
                result.append(dict(zip(columns, row)))
            return result
        except Exception as e:
            logger.error(f"ODBC Query Error: {str(e)}")
            raise
        finally:
            cursor.close()
            if close_conn:
                try:
                    conn.close()
                except:
                    pass
                # Cleanup from pool if we are closing
                # Note: logic here is a bit simplistic for a real pool, but matches existing pattern
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
