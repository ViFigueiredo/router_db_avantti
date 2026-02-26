from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from .database import get_db
from .models import Project, DatabaseConnection
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST

API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_project_by_api_key(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
):
    if not api_key:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="API Key missing"
        )
    
    project = db.query(Project).filter(Project.api_key == api_key).first()
    if not project:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    
    # Get SQL Server connection for this project
    sql_config = db.query(DatabaseConnection).filter(
        DatabaseConnection.project_id == project.id,
        DatabaseConnection.type == "SQLSERVER"
    ).first()

    if not sql_config:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="No SQL Server configuration found for this project"
        )
    
    return {
        "project": project,
        "sql_config": {
            "host": sql_config.host,
            "port": sql_config.port,
            "database": sql_config.database,
            "username": sql_config.username,
            "password": sql_config.password
        }
    }
