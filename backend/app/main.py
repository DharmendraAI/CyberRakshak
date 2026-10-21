from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .database import engine
from .routers.history import router as history_router
from .routers.statistics import router as statistics_router
from .routers.frauds import router as fraud_router
from .routers.analyzer import router as analyzer_router
from .routers.analytics import router as analytics_router


# Create FastAPI application
app = FastAPI(
    title="CyberRakshak AI",
    description=(
        "AI-Powered Cyber Fraud Prevention "
        "& Digital Safety Platform for India"
    ),
    version="0.1.0",
)
# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
], allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], )


# Register API Routers
app.include_router(history_router)
app.include_router(fraud_router)
app.include_router(analyzer_router)
app.include_router(statistics_router)
app.include_router(analytics_router)


# Root Endpoint
@app.get("/")
def home():
    return {
        "message": "CyberRakshak AI is running",
        "status": "success",
        "version": "0.1.0",
    }


# Health Check Endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CyberRakshak AI",
        "version": "0.1.0",
    }


# Database Connection Test
@app.get("/db-test")
def database_test():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()

        return {
            "status": "success",
            "database": "connected",
            "service": "CyberRakshak AI",
        }

    except Exception as e:
        return {
            "status": "error",
            "database": "not connected",
            "message": str(e),
        }