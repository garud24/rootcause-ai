from fastapi import FastAPI

from app.api.analyze import router as analyze_router

app = FastAPI(
    title="RootCause AI API",
    version="1.0.0",
)

app.include_router(analyze_router)

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

  
