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
        allowed_tables=project.sql_server.allowed_tables,
        allowed_methods=project.sql_server.allowed_methods
    )
    db.add(new_conn)
    db.commit()
    db.refresh(new_project)
    
    return new_project

@router.put("/{project_id}", response_model=schemas.Project)
def update_project(project_id: str, project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update project fields
    db_project.name = project.name
    
    # Check slug uniqueness if changed
    if db_project.slug != project.slug:
        existing_slug = db.query(models.Project).filter(models.Project.slug == project.slug).first()
        if existing_slug:
             raise HTTPException(status_code=HTTP_409_CONFLICT, detail="Project slug already exists")
        db_project.slug = project.slug
        
    # Update database connection
    # Assuming 1-to-1 for now based on ProjectCreate structure
    db_conn = db.query(models.DatabaseConnection).filter(models.DatabaseConnection.project_id == project_id).first()
    if db_conn:
        db_conn.database = project.sql_server.database
        db_conn.allowed_tables = project.sql_server.allowed_tables
        db_conn.allowed_methods = project.sql_server.allowed_methods
    else:
        # Create if not exists (fallback)
        new_conn = models.DatabaseConnection(
            project_id=project_id,
            type="SQLSERVER",
            database=project.sql_server.database,
            allowed_tables=project.sql_server.allowed_tables,
            allowed_methods=project.sql_server.allowed_methods
        )
        db.add(new_conn)
        
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

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
