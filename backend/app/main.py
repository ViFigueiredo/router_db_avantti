from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routes import projects, query
import uvicorn

app = FastAPI(title="Router API DB - Python Backend")

# Initialize database
init_db()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(query.router, prefix="/api/query", tags=["query"])

@app.get("/")
def read_root():
    return {"message": "Router API DB is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
