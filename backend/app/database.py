from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
import os
from dotenv import load_dotenv
import pymssql
from typing import List, Dict, Any, Optional

load_dotenv()

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

# SQL Server Connection Management
class SQLServerConnection:
    @staticmethod
    def get_global_config():
        return {
            'host': os.getenv('SQL_SERVER_HOST', 'localhost'),
            'port': int(os.getenv('SQL_SERVER_PORT', '1433')),
            'username': os.getenv('SQL_SERVER_USER', 'sa'),
            'password': os.getenv('SQL_SERVER_PASSWORD', '')
        }

    @staticmethod
    def get_connection(database: Optional[str] = None):
        config = SQLServerConnection.get_global_config()
        return pymssql.connect(
            server=config['host'],
            port=config['port'],
            user=config['username'],
            password=config['password'],
            database=database if database else 'master',
            as_dict=True
        )

    @staticmethod
    def execute_query(conn, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
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
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def list_databases() -> List[str]:
        conn = SQLServerConnection.get_connection()
        query = "SELECT name FROM sys.databases WHERE database_id > 4" # Skip system databases
        result = SQLServerConnection.execute_query(conn, query)
        return [row['name'] for row in result]

    @staticmethod
    def list_tables(database: str) -> List[str]:
        conn = SQLServerConnection.get_connection(database=database)
        query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
        result = SQLServerConnection.execute_query(conn, query)
        return [row['TABLE_NAME'] for row in result]
