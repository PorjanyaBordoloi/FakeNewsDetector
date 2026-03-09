# Fake News Detector

An AI-powered multi-agent fact-checking system designed for the Antigravity Agentic IDE. This system utilizes LangGraph to orchestrate multiple LLM agents that autonomously extract claims, retrieve web evidence, and verify information from any news article.

## 🏗️ Architecture Stack

### Backend (FastAPI + LangGraph)
The backend is powered by a robust **LangGraph StateGraph** that orchestrates three discrete AI actions:
1. **Agent 1: Claim Extraction (Groq `llama-3.3-70b-versatile`)**
   - Scrapes article URLs via **Jina Reader**.
   - Cleans the raw markdown and extracts metadata.
   - Extracts a list of structured, checkable claims and ranks them by importance.
2. **Agent 2: Evidence Retrieval (Tavily Search API)**
   - Takes the top-ranked claims and queries the web using Tavily.
   - Retrieves cross-referenced snippets of supporting or refuting evidence.
3. **Agent 3: Fact Checker (Groq `llama-3.3-70b-versatile`)**
   - Correlates the extracted evidence specifically against the initial claims.
   - Returns a strictly structured JSON payload with a truth score (0-100), categorical verdict (`REAL`, `FAKE`, `MISLEADING`, `UNVERIFIED`), a 2-sentence explanation, and properly deduplicated citation URLs.

### Frontend (React + Vite)
- Features a beautiful, highly interactive **Claude-inspired Dark Mode UI** (`#212121`).
- Implements Server-Sent Events (SSE) via `EventSource` to live-stream the exact "Chain of Thought" output from the LangGraph backend.
- Displays the agents' orchestrated breakdown cleanly via an dynamic accordion log terminal.

### Chrome Extension (Manifest V3)
- Provides a frictionless way to analyze fake news securely on-the-fly.
- When clicked, immediately gathers the active tab URL.
- Uses a streamlined single API call to present a fast visual verdict score directly inside a popup.
- One-click capability to hand-off deep analysis to the main React web app via URL routing (`?url=`).

## 🚀 Setting Up the Project

### Prerequisites
Make sure you have API keys for:
- **Groq** (LLM inference)
- **Tavily** (Web Search)
- **Jina Reader** (Clean URL Markdown generation)

### 1. Start the Backend
```bash
cd backend
# Make sure your .env has GROQ_API_KEY, TAVILY_API_KEY, and JINA_READER_API_KEY
uv sync
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend Web App
```bash
cd frontend
npm install
npm run dev
```

### 3. Load the Chrome Extension
1. Open Google Chrome.
2. Navigate to `chrome://extensions/`.
3. Enable **Developer mode** (top right corner).
4. Click **Load unpacked** and select the `extension` directory from this repository.
5. Pin the extension to your toolbar, browse to any news site, and click the icon!

## 🧪 Real-time Graph Streaming
The backend exposes `/api/analyze-stream?user_input=...` and utilizes `langgraph.graph.stream()` to push node-by-node updates to the client in real time, guaranteeing zero-latency feedback on the progress of complex claim extraction.
