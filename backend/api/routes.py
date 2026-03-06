"""
api/routes.py — ALL endpoint definitions.

Endpoints (from readme §5):
  GET  /                  → API info
  GET  /health            → status + ML model loaded state
  POST /api/parse-url     → scrape article from URL
  POST /api/analyze       → ML classification
  POST /api/cross-reference → fact-check via NewsAPI
  POST /api/full-check    → master pipeline (scrape → analyze + cross-ref concurrently)
"""

import asyncio
from datetime import datetime

from fastapi import APIRouter, HTTPException

from core.schema import (
    StandardResponse,
    ErrorDetail,
    ParseUrlRequest,
    ParseUrlData,
    AnalyzeRequest,
    AnalyzeData,
    CrossReferenceRequest,
    CrossReferenceData,
    FullCheckData,
)
from services.scrapper import extract_article
from services.cross_ref import verify_claims

# ── Lazy import for the ML model (Nayan's domain) ────────
# We import at call-time so the app boots even if the model
# isn't downloaded yet. The /health endpoint reports status.
_detector = None


def _get_detector():
    """Lazy-load the FakeNewsDetector singleton."""
    global _detector
    if _detector is None:
        try:
            from ml.model_loader import FakeNewsDetector
            _detector = FakeNewsDetector()
        except Exception:
            _detector = None
    return _detector


# ── Router ────────────────────────────────────────────────
router = APIRouter()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /  — API info
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.get("/")
async def root():
    return StandardResponse(
        data={
            "name": "Fake News Detector API",
            "version": "1.0.0",
            "docs": "/docs",
        }
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /health  — status + ML model loaded state
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.get("/health")
async def health():
    detector = _get_detector()
    return StandardResponse(
        data={
            "status": "healthy",
            "ml_model_loaded": detector is not None,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# POST /api/parse-url  — scrape article from URL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.post("/api/parse-url")
async def parse_url(request: ParseUrlRequest):
    try:
        article_dict = await extract_article(str(request.url))
        parsed = ParseUrlData(**article_dict)
        return StandardResponse(data=parsed.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# POST /api/analyze  — ML classification
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    detector = _get_detector()
    if detector is None:
        raise HTTPException(
            status_code=503,
            detail="ML model is not loaded. Please try again later.",
        )

    try:
        # ML boundary: we only call predict(), never train
        result = await detector.predict(request.text)
        analysis = AnalyzeData(**result)
        return StandardResponse(data=analysis.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# POST /api/cross-reference  — fact-check via NewsAPI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.post("/api/cross-reference")
async def cross_reference(request: CrossReferenceRequest):
    try:
        result = await verify_claims(request.key_claims)
        cross_ref = CrossReferenceData(**result)
        return StandardResponse(data=cross_ref.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cross-reference failed: {str(e)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# POST /api/full-check  — Master pipeline
#   1. Scrape the URL
#   2. Run analysis + cross-reference CONCURRENTLY (asyncio.gather)
#   3. Return unified FullCheckData
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@router.post("/api/full-check")
async def full_check(request: ParseUrlRequest):
    # Step 1 — Scrape
    try:
        article_dict = await extract_article(str(request.url))
        article = ParseUrlData(**article_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Scraping failed: {str(e)}")

    # Step 2 — Run analysis + cross-reference concurrently
    detector = _get_detector()
    if detector is None:
        raise HTTPException(
            status_code=503,
            detail="ML model is not loaded. Please try again later.",
        )

    try:
        # Extract key claims from the headline for cross-referencing
        key_claims = [article.headline] if article.headline else []

        analysis_task = detector.predict(article.body)
        cross_ref_task = verify_claims(key_claims)

        analysis_result, cross_ref_result = await asyncio.gather(
            analysis_task,
            cross_ref_task,
            return_exceptions=False,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed during concurrent execution: {str(e)}",
        )

    # Step 3 — Assemble the unified response
    try:
        full = FullCheckData(
            article=article,
            analysis=AnalyzeData(**analysis_result),
            cross_reference=CrossReferenceData(**cross_ref_result),
        )
        return StandardResponse(data=full.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assemble response: {str(e)}",
        )