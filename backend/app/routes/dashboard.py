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

import re

@router.get("/activity", response_model=List[schemas.RequestLog])
def get_activity(limit: int = 1000, db: Session = Depends(get_db)):
    # Using joinedload to fetch project name efficiently would be better, but we need dynamic table parsing anyway.
    logs = db.query(models.RequestLog).order_by(models.RequestLog.timestamp.desc()).limit(limit).all()
    
    enriched_logs = []
    for log in logs:
        # Get project name
        project_name = "System"
        if log.project_id:
             project = db.query(models.Project).filter(models.Project.id == log.project_id).first()
             if project:
                 project_name = project.name
        
        # Parse tables from SQL (Basic Regex implementation)
        tables = []
        if log.query_body:
            # Match FROM or JOIN followed by table name (simple case)
            matches = re.findall(r'(?:FROM|JOIN)\s+([a-zA-Z0-9_]+)', log.query_body, re.IGNORECASE)
            # Filter out common SQL keywords if matched by mistake
            cleaned_matches = [t for t in matches if t.upper() not in ['SELECT', 'WHERE', 'GROUP', 'ORDER', 'LIMIT']]
            tables = list(set(cleaned_matches)) # unique tables
        
        # Create a dict from the ORM object
        log_dict = {
            "id": log.id,
            "timestamp": log.timestamp,
            "method": log.method,
            "path": log.path,
            "status_code": log.status_code,
            "duration_ms": log.duration_ms,
            "client_ip": log.client_ip,
            "project_id": log.project_id,
            "error_message": log.error_message,
            "query_body": log.query_body,
            "project_name": project_name,
            "tables_involved": ", ".join(tables) if tables else "-"
        }
        
        enriched_logs.append(log_dict)
        
    return enriched_logs
