from app import schemas
from app.database import get_db
from app.routers import auth, post, user, vote
from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

# FastAPI app initialization
app = FastAPI(title="Chirp API", version="1.0.0")

# Track application start time for uptime calculation
START_TIME = datetime.now(timezone.utc)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(post.router)
app.include_router(vote.router)

# Health check endpoint
@app.get(
    "/health",
    tags=["Health Check"],
    status_code=status.HTTP_200_OK,
    response_model=schemas.HealthStatus,
)
def health_check(db: Session = Depends(get_db)):
    """
    Health endpoint for readiness and liveness probes.
    Returns:
        status: API status
        uptime_seconds: time since app start
        version: API version
        database: connection status
    Raises:
        HTTPException: 503 if database is unreachable
    """
    # Check database connectivity
    try:
        db.execute(text('SELECT 1;'))
        db_status = schemas.DatabaseStatus.connected
    except Exception:
        db_status = schemas.DatabaseStatus.unreachable
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Database unreachable")
    # Calculate uptime
    uptime_seconds = int((datetime.now(timezone.utc) - START_TIME).total_seconds())
    return {
        "status": "ok",
        "uptime_seconds": uptime_seconds,
        "version": app.version,
        "database": db_status,
    }