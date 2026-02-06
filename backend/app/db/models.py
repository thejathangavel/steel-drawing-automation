from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class DrawingType(str, enum.Enum):
    PART = "PART"
    SHOP = "SHOP"
    ERECTION = "ERECTION"
    UNKNOWN = "UNKNOWN"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    client_name = Column(String, index=True)
    folder_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    drawings = relationship("Drawing", back_populates="project")

class Drawing(Base):
    __tablename__ = "drawings"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    filename = Column(String)
    drawing_no = Column(String, index=True)
    revision_no = Column(String)
    description = Column(String, nullable=True)
    drawing_type = Column(SQLEnum(DrawingType), default=DrawingType.UNKNOWN)
    status = Column(String, default="Active")
    drawing_date = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="drawings")
    revisions = relationship("DrawingRevision", back_populates="drawing", cascade="all, delete-orphan")

class DrawingRevision(Base):
    __tablename__ = "drawing_revisions"
    id = Column(Integer, primary_key=True, index=True)
    drawing_id = Column(Integer, ForeignKey("drawings.id"))
    revision_no = Column(String)
    drawing_date = Column(String)
    status = Column(String)
    filename = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    drawing = relationship("Drawing", back_populates="revisions")
