from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class DrawingType(str, Enum):
    PART = "PART"
    SHOP = "SHOP"
    ERECTION = "ERECTION"
    UNKNOWN = "UNKNOWN"

class DrawingBase(BaseModel):
    drawing_no: str
    revision_no: str
    description: Optional[str] = None
    drawing_type: DrawingType
    quantity: Optional[int] = 1

class DrawingCreate(DrawingBase):
    filename: str
    project_id: int

class Drawing(DrawingBase):
    id: int
    project_id: int
    filename: str
    status: str
    created_at: datetime
    drawing_date: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    title: str
    client_name: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    folder_path: str
    created_at: datetime
    drawings: List[Drawing] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
