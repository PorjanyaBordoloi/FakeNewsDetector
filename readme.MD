# 🚀 SYSTEM DIRECTIVE: Fake News Detector Pipeline (Hackathon Build)

## 🎯 1. Project Overview & Meta-Objective
**Deadline:** March 12th.
**Objective:** Build a highly asynchronous, robust backend pipeline for a Fake News Detector. The system takes a URL, extracts article content, runs it through a fine-tuned RoBERTa classification model, cross-references claims via NewsAPI/Google Fact Check, and returns a unified JSON payload to a React frontend/Browser Extension.
**Philosophy (The Karpathy Principle):** The data contracts (Pydantic schemas) are the source of truth. The application logic simply transforms data from one strict schema to another. No implicit types, no generic dictionaries.

## 🛠️ 2. Tech Stack & Environment
**Agent Directive:** STRICTLY adhere to these versions and libraries. Do not hallucinate alternatives (e.g., do not use `requests` instead of `httpx`).
* **Framework:** FastAPI (0.109.0) + Uvicorn
* **Validation:** Pydantic v2 (Strictly v2 syntax)
* **ML Engine:** Hugging Face Transformers (`transformers==4.36.0`, `torch==2.1.0`)
* **Web Scraping:** `newspaper3k` + `beautifulsoup4`
* **Async HTTP:** `httpx`

## 📁 3. Strict Directory Structure
**Agent Directive:** Do not create files outside of this structure unless explicitly instructed.

```text
fake-news-detector/
├── backend/
│   ├── main.py               # FastAPI app initialization, CORS, and uvicorn entry
│   ├── api/
│   │   └── routes.py         # ALL endpoint definitions live here
│   ├── core/
│   │   ├── config.py         # pydantic_settings BaseSettings for .env
│   │   └── schema.py        # Pydantic v2 models (The absolute source of truth)
│   ├── ml/                   
│   │   └── model_loader.py   # Nayan's domain: AutoModelForSequenceClassification wrapper
│   ├── services/
│   │   ├── scraper.py        # newspaper3k logic (URL -> Text)
│   │   └── cross_check.py    # httpx calls to NewsAPI (Text -> Verification)
│   └── requirements.txt
├── .env
```

## 4. Data Contracts (Schemas)
**Agent Directive:** All functions must type-hint these exact models. All API responses MUST be wrapped in the StandardResponse model.

**StandardResponse**: { "success": bool, "data": Any, "error": dict | null }

**ParseUrlRequest**: { "url": HttpUrl }

**ParseUrlData**: { "headline": str, "body": str, "author": str | null, "publish_date": str | null, "url": str, "domain": str }

**AnalyzeRequest**: { "text": str, "headline": str | null }

**AnalyzeData**: { "credibility_score": int (0-100), "prediction": "real"|"fake"|"uncertain", "confidence": float, "red_flags": list, "explanation": str }

**CrossReferenceRequest**: { "headline": str, "key_claims": list[str] }

**CrossReferenceData**: { "sources_found": int, "supporting": int, "contradicting": int, "neutral": int, "articles": list }

}

## 5. API Endpoints Specification

**GET /**: Returns API info.

**GET /health**: Returns API status and ML model loaded state.

**POST /api/parse-url**: Accepts ParseUrlRequest, returns ParseUrlData.

**POST /api/analyze**: Accepts AnalyzeRequest, returns AnalyzeData.

**POST /api/cross-reference**: Accepts CrossReferenceRequest, returns CrossReferenceData.

**POST /api/full-check**: The master pipeline. Accepts ParseUrlRequest. Orchestrates scraping, then runs analysis and cross-referencing concurrently (using asyncio.gather), returns FullCheckData.

## 🛑 6. Anti-Hallucination & Execution Rules
Agent Directive: When the user highlights a section of code or a file and asks you to implement it, you must obey the following:

ASYNC EVERYTHING: All I/O bound operations (scraping, calling external APIs) MUST use async def and await. Use httpx.AsyncClient(), not requests.

ML BOUNDARY: Do not write ML training code. Assume backend/ml/model_loader.py exports a class FakeNewsDetector with an async method async def predict(self, text: str) -> dict. You only need to call this method in the /api/analyze route.

ERROR HANDLING: Do not let the app crash. Wrap external calls (newspaper3k parsing, httpx network requests) in try/except blocks and raise fastapi.HTTPException appropriately.

PYDANTIC V2: Use model_dump() instead of the deprecated dict().