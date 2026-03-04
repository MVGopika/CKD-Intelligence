"""Entry point for FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from .core.config import get_settings
from .db.database import init_db

from .api.routes import auth, consultation, prediction, doctor, reports, patient, ml

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow(), "version": settings.API_VERSION}

# include routers
app.include_router(auth.router)
app.include_router(consultation.router)
app.include_router(prediction.router)
app.include_router(doctor.router)
app.include_router(reports.router)
app.include_router(patient.router)
app.include_router(ml.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
