from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, unique=True, index=True, default=generate_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    database_connections = relationship("DatabaseConnection", back_populates="project", cascade="all, delete-orphan")

class DatabaseConnection(Base):
    __tablename__ = "database_connections"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    type = Column(String, default="SQLSERVER")
    database = Column(String, nullable=False)
    allowed_tables = Column(Text, nullable=True) # Comma separated or JSON string
    allowed_methods = Column(String, nullable=True, default="GET") # Comma separated: GET,POST,PUT,DELETE
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="database_connections")

    __table_args__ = (UniqueConstraint('project_id', 'type', name='_project_type_uc'),)

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    method = Column(String, index=True)
    path = Column(String, index=True)
    status_code = Column(Integer, index=True)
    duration_ms = Column(Integer)
    client_ip = Column(String)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True) # Optional link to project
    error_message = Column(String, nullable=True)
