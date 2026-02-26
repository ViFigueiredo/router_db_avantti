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
    def get_connection(config: Dict[str, Any]):
        return pymssql.connect(
            server=config['host'],
            port=config['port'],
            user=config['username'],
            password=config['password'],
            database=config['database'],
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
            
            # Check if there is a result set (for SELECT queries)
            try:
                result = cursor.fetchall()
                return result
            except pymssql.OperationalError:
                # This might happen for non-SELECT queries that don't return data
                return []
        finally:
            cursor.close()
            conn.close()
