from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any

class DatabaseConnectionBase(BaseModel):
    type: str = "SQLSERVER"
    database: str
    allowed_tables: Optional[str] = None
    allowed_methods: Optional[str] = "GET"

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

class DatabaseDiscovery(BaseModel):
    databases: List[str]

class TableDiscovery(BaseModel):
    tables: List[str]

class DashboardStats(BaseModel):
    total_projects: int
    total_requests: int
    active_connections: int
    avg_response_time: str

class SystemStatus(BaseModel):
    api_gateway: str
    sql_server: str
    discovery: str

class RequestLog(BaseModel):
    id: int
    timestamp: datetime
    method: str
    path: str
    status_code: int
    duration_ms: int
    client_ip: str
    project_id: Optional[str]
    error_message: Optional[str]

    class Config:
        from_attributes = True
