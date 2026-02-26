from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db, SQLServerConnection
from .. import models, schemas
from starlette.status import HTTP_409_CONFLICT

router = APIRouter()

@router.get("/", response_model=List[schemas.Project])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()

@router.post("/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    # Check if slug exists
    db_project = db.query(models.Project).filter(models.Project.slug == project.slug).first()
    if db_project:
        raise HTTPException(status_code=HTTP_409_CONFLICT, detail="Project slug already exists")
    
    # Create project
    new_project = models.Project(
        name=project.name,
        slug=project.slug
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # Create database connection
    new_conn = models.DatabaseConnection(
        project_id=new_project.id,
        type="SQLSERVER",
        database=project.sql_server.database,
        allowed_tables=project.sql_server.allowed_tables
    )
    db.add(new_conn)
    db.commit()
    db.refresh(new_project)
    
    return new_project

@router.get("/discover/databases", response_model=schemas.DatabaseDiscovery)
def discover_databases():
    try:
        databases = SQLServerConnection.list_databases()
        return {"databases": databases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing databases: {str(e)}")

@router.get("/discover/tables/{database}", response_model=schemas.TableDiscovery)
def discover_tables(database: str):
    try:
        tables = SQLServerConnection.list_tables(database)
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tables: {str(e)}")
