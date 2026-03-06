"""
main.py — FastAPI app initialization, CORS, and uvicorn entry point.

No business logic lives here. This file:
  1. Creates the FastAPI app
  2. Configures CORS for React frontend + Browser Extension
  3. Loads the ML model once at startup via lifespan
  4. Includes the router from api/routes.py
  5. Starts uvicorn
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Lifespan — ML model loads once on startup, released on shutdown
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────
    try:
        from ml.model_loader import FakeNewsDetector

        app.state.model = FakeNewsDetector()
        logger.info("✅ ML model loaded successfully.")
    except Exception as e:
        app.state.model = None
        logger.warning(f"⚠️ ML model failed to load: {e}. /api/analyze will be unavailable.")

    yield

    # ── Shutdown ──────────────────────────────────────────
    app.state.model = None
    logger.info("🛑 ML model released from memory.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# App instance
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
app = FastAPI(
    title="Fake News Detector API",
    version="2.0",
    lifespan=lifespan,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CORS — allow all origins for React frontend + Browser Extension
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Router — all endpoints defined in api/routes.py
# Routes already carry their full paths (/, /health, /api/*)
# so no prefix is needed here.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from api.routes import router  # noqa: E402

app.include_router(router)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Uvicorn entry point
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
