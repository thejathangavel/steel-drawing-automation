from fastapi import FastAPI
from .api import auth, projects
from .db import models
from .db.database import engine
from .db.mongodb import connect_to_mongo, close_mongo_connection

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Steel Drawing Workflow System")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])

from sqlalchemy.orm import Session
from . import crud, schemas
from .db.database import SessionLocal

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    db = SessionLocal()
    try:
        user = crud.get_user_by_username(db, "admin")
        if not user:
            crud.create_user(db, schemas.UserCreate(username="admin", password="password123"))
            print("Created default user: admin / password123")
    finally:
        db.close()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/")
def read_root():
    return {"message": "Welcome to Steel Drawing Workflow System API"}
