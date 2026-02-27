from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routes import projects, query, dashboard
from .logger import log_middleware, logger
import os

app = FastAPI(title="Router API DB - Python Backend")

# Initialize database
init_db()
logger.info("Database initialized")

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    os.getenv("FRONTEND_URL", "*")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
@app.middleware("http")
async def add_logging_middleware(request, call_next):
    return await log_middleware(request, call_next)

# Include routes
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(query.router, prefix="/api/query", tags=["query"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
def read_root():
    return {"message": "Router API DB is running"}

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
