from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from starlette.status import HTTP_409_CONFLICT

router = APIRouter()

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
        host=project.sql_server.host,
        port=project.sql_server.port,
        database=project.sql_server.database,
        username=project.sql_server.username,
        password=project.sql_server.password
    )
    db.add(new_conn)
    db.commit()
    db.refresh(new_project)
    
    return new_project
