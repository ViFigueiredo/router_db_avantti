from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db, SQLServerConnection
from .. import models, schemas
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/stats", response_model=schemas.DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    total_projects = db.query(models.Project).count()
    total_requests = db.query(models.RequestLog).count()
    
    # Calculate average response time
    avg_duration = db.query(func.avg(models.RequestLog.duration_ms)).scalar()
    avg_response_time = f"{int(avg_duration)}ms" if avg_duration else "0ms"
    
    # Active connections (using projects count as proxy for now)
    active_connections = total_projects 

    return {
        "total_projects": total_projects,
        "total_requests": total_requests,
        "active_connections": active_connections,
        "avg_response_time": avg_response_time
    }

@router.get("/status", response_model=schemas.SystemStatus)
def get_status():
    # Check SQL Server
    sql_config = SQLServerConnection.get_global_config()
    sql_status = "connected" if SQLServerConnection.check_port_open(sql_config['host'], sql_config['port']) else "offline"
    
    return {
        "api_gateway": "online",
        "sql_server": sql_status,
        "discovery": "active"
    }

@router.get("/activity", response_model=List[schemas.RequestLog])
def get_activity(limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.RequestLog).order_by(models.RequestLog.timestamp.desc()).limit(limit).all()
