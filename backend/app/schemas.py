from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any

class DatabaseConnectionBase(BaseModel):
    type: str = "SQLSERVER"
    host: str
    port: int = 1433
    database: str
    username: str
    password: str

class DatabaseConnectionCreate(DatabaseConnectionBase):
    pass

class DatabaseConnection(DatabaseConnectionBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    slug: str

class ProjectCreate(ProjectBase):
    sql_server: DatabaseConnectionCreate

class Project(ProjectBase):
    id: str
    api_key: str
    created_at: datetime
    updated_at: datetime
    database_connections: List[DatabaseConnection] = []

    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    sql: str
    params: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
