"""
Database models for AutoLabMate
SQLAlchemy models for experiments, plans, and reports
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Experiment(Base):
    """Experiment record - stores uploaded datasets"""
    __tablename__ = "experiments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="uploaded")  # uploaded, planned, executing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class AnalysisPlan(Base):
    """Analysis plan - stores generated step-by-step plans"""
    __tablename__ = "analysis_plans"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String, nullable=True)
    steps = Column(JSON, nullable=False)  # List of step objects
    plan_metadata = Column(JSON, nullable=True)  # Additional plan metadata
    estimated_duration = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "steps": self.steps,
            "metadata": self.metadata,
            "estimated_duration": self.estimated_duration,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ExecutionLog(Base):
    """Execution log - stores runtime logs and monitoring data"""
    __tablename__ = "execution_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, nullable=False, index=True)
    experiment_id = Column(String, nullable=True)
    step_number = Column(Integer, nullable=True)
    log_level = Column(String, default="INFO")  # DEBUG, INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "experiment_id": self.experiment_id,
            "step_number": self.step_number,
            "log_level": self.log_level,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class Report(Base):
    """Generated report - stores paths to PDF, notebook, metadata"""
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String, nullable=False, unique=True)
    pdf_path = Column(String, nullable=False)
    notebook_path = Column(String, nullable=False)
    metadata_path = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    calendar_event_id = Column(String, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "pdf_path": self.pdf_path,
            "notebook_path": self.notebook_path,
            "metadata_path": self.metadata_path,
            "github_url": self.github_url,
            "calendar_event_id": self.calendar_event_id,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None
        }


class VectorStoreEntry(Base):
    """Vector store entry - stores experiment context for RAG"""
    __tablename__ = "vector_store_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    embedding_id = Column(String, nullable=True)  # External vector DB ID
    pla_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "content": self.content,
            "embedding_id": self.embedding_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

