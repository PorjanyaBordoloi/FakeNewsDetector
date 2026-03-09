"""
main.py — FastAPI app entry point.

This file:
  1. Creates the FastAPI app
  2. Configures CORS for React frontend + Chrome Extension
  3. Defines the streaming and simple analysis endpoints
  4. Runs uvicorn
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Lifespan — startup / shutdown hooks
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Fake News Detector API starting up...")
    yield
    logger.info("🛑 Fake News Detector API shutting down...")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# App instance
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
app = FastAPI(
    title="Fake News Detector API",
    version="1.0.0",
    lifespan=lifespan,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CORS — allow React frontend + Chrome Extension origins
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Endpoints
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@app.post("/api/analyze-stream")
async def analyze_stream(url: str):
    """
    Streaming endpoint for the website (shows chain of thought).
    Returns SSE stream of agent thoughts.
    """
    from agents.orchestrator import AgentOrchestrator

    orchestrator = AgentOrchestrator()
    return StreamingResponse(
        orchestrator.run_chain(url),
        media_type="text/event-stream",
    )


@app.post("/api/analyze-simple")
async def analyze_simple(url: str):
    """
    Simple endpoint for Chrome extension (no streaming).
    Returns final verdict only.
    """
    from agents.orchestrator import AgentOrchestrator

    orchestrator = AgentOrchestrator()
    result = await orchestrator.run_chain_sync(url)

    return {
        "score": result["authenticity_score"],
        "verdict": result["final_verdict"],
        "confidence": result["confidence"],
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Uvicorn entry point
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
