from typing import Annotated, List
from fastapi import FastAPI, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, SessionLocal, get_db
from .routers import post, user, auth


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(post.router) 
app.include_router(user.router)
app.include_router(auth.router)

