from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models
from .routers import survey_router, submission_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Video Survey Platform with Face Detection")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(survey_router.router, prefix="/api")
app.include_router(submission_router.router, prefix="/api")