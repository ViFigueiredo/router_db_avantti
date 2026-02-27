import logging
import os
from datetime import datetime
from fastapi import Request
import time
import json
from .database import SessionLocal
from .models import RequestLog

# Ensure logs directory exists at root
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

def setup_logging():
    log_filename = f"backend_{datetime.now().strftime('%Y-%m-%d')}.log"
    log_path = os.path.join(LOGS_DIR, log_filename)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(module)s | %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("router_db_backend")

logger = setup_logging()

async def log_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Process the request
    # To capture body for query logging, we might need to read it.
    # However, reading body in middleware consumes the stream.
    # We'll rely on request.state.query_body being set by the route handler if available.
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}ms".format(process_time)
    
    log_dict = {
        "timestamp": datetime.now().isoformat(),
        "type": "REQUEST",
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration": formatted_process_time,
        "client": request.client.host if request.client else "unknown"
    }

    if response.status_code >= 400:
        logger.error(f"Event: {json.dumps(log_dict)}")
    elif response.status_code >= 300:
        logger.warning(f"Event: {json.dumps(log_dict)}")
    else:
        logger.info(f"Event: {json.dumps(log_dict)}")
    
    # Extract project_id from context if available (it might be set by auth middleware)
    project_id = getattr(request.state, "project_id", None)
    query_body = getattr(request.state, "query_body", None)

    # Log to Database
    try:
        db = SessionLocal()
        db_log = RequestLog(
            timestamp=datetime.utcnow(),
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=int(process_time),
            client_ip=request.client.host if request.client else "unknown",
            project_id=project_id,
            query_body=query_body
        )
        db.add(db_log)
        db.commit()
        db.close()
    except Exception as e:
        logger.error(f"Failed to log to DB: {e}")

    return response
