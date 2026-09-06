from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from .routers import bugs, scenarios, approvals

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title='ERP Bug-Reproduction Assistant API',
    version='1.0.0',
    description='Automated assistant to generate reproducible scenarios for ERP systems.'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bugs.router)
app.include_router(scenarios.router)
app.include_router(approvals.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing FAISS index and mock DB...")
    # Mock initialization logic
    logger.info("System operational.")

@app.get("/")
async def root():
    return {
        "name": "ERP Bug-Reproduction Assistant API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
