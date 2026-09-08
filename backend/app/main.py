from fastapi import FastAPI
from app.api.repository import router as repository_router
from app.api.analyze import router as analyze_router
from app.api.repository_analysis import (
    router as repository_analysis_router,
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RootCause AI API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(analyze_router)
app.include_router(repository_router)
app.include_router(
    repository_analysis_router
)

@app.get("/")
def root():
    return {
        "message": "RootCause AI backend is running"
    }
    

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }   

  
