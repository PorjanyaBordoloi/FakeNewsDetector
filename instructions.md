# Fake News Detector - Multi-Agent System

> **AI-Powered Misinformation Detection using Agentic Workflows**
> 
> Built with FastAPI, React, and a 3-agent architecture for transparent, real-time fake news verification.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Agent System](#agent-system)
  - [Agent 1: URL Parser & Content Extractor](#agent-1-url-parser--content-extractor)
  - [Agent 2: Fact Checker & LLM Analyzer](#agent-2-fact-checker--llm-analyzer)
  - [Agent 3: Cross-Reference Validator](#agent-3-cross-reference-validator)
- [Chain of Thought Display](#chain-of-thought-display)
- [Frontend Implementation](#frontend-implementation)
- [Backend Implementation](#backend-implementation)
- [Chrome Extension](#chrome-extension)
- [Setup & Installation](#setup--installation)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)

---

## 🎯 Overview

The Fake News Detector is a multi-agent system that analyzes news articles through three sequential agents, each performing specialized tasks:

1. **Content Extraction Agent** - Parses URLs and extracts article text
2. **Fact-Checking Agent** - Verifies claims using Tavily API + LLM reasoning
3. **Cross-Reference Agent** - Validates against trusted sources and outputs final score

### Key Features

✅ **Transparent Agent Workflow** - Users see real-time agent thinking process  
✅ **Chain of Thought Display** - Step-by-step reasoning shown on website  
✅ **Chrome Extension** - Quick fake/real verdict while browsing  
✅ **Multi-Source Verification** - Cross-references News API, Tavily, fact-check databases  
✅ **Natural Language Explanations** - LLM provides human-readable analysis

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INPUT                          │
│  Website: URL input box    |    Extension: Current page URL │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │  FastAPI      │
         │  Backend      │
         └───────┬───────┘
                 │
    ┌────────────┴────────────┐
    ▼                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATOR                        │
│  Manages agent execution, streaming responses, and state    │
└────────────────┬─────────┬──────────┬────────────────────────┘
                 │         │          │
        ┌────────┘         │          └────────┐
        ▼                  ▼                   ▼
   ┌─────────┐      ┌─────────┐       ┌─────────────┐
   │ AGENT 1 │      │ AGENT 2 │       │  AGENT 3    │
   │ Parser  │ ───> │ Fact    │ ───>  │ Cross-Ref   │
   │         │      │ Checker │       │ Validator   │
   └─────────┘      └─────────┘       └─────────────┘
        │                │                    │
        │                │                    │
        ▼                ▼                    ▼
   BeautifulSoup    Tavily API          News API
   Newspaper3k      + LLM (Claude)      Google Fact Check
                                        
                    │
                    ▼
            ┌───────────────┐
            │ Final Score   │
            │ + Explanation │
            └───────┬───────┘
                    │
        ┌───────────┴────────────┐
        ▼                        ▼
   ┌─────────┐            ┌──────────────┐
   │ Website │            │  Extension   │
   │ (Full   │            │  (Score +    │
   │ Chain)  │            │  Verdict)    │
   └─────────┘            └──────────────┘
```

---

## 🤖 Agent System

### Agent 1: URL Parser & Content Extractor

**Purpose:** Extract clean article content from any news URL

#### Responsibilities:
1. Accept URL input from user
2. Fetch webpage HTML
3. Parse and extract:
   - Headline
   - Body text
   - Author
   - Publish date
   - Source domain
4. Clean and structure content
5. Output JSON with extracted data

#### Technologies:
- **BeautifulSoup4** - HTML parsing
- **Newspaper3k** - Article extraction
- **Requests/httpx** - HTTP client

#### Input:
```json
{
  "url": "https://example.com/news-article",
  "user_agent": "FakeNewsDetector/1.0"
}
```

#### Output (to Agent 2):
```json
{
  "success": true,
  "agent": "parser",
  "thought": "Successfully extracted article from example.com. Found headline, 1,234 words of body text, author John Doe, published on 2026-03-06.",
  "data": {
    "url": "https://example.com/news-article",
    "headline": "Breaking: Major Event Happens",
    "body": "Full article text here...",
    "author": "John Doe",
    "publish_date": "2026-03-06",
    "domain": "example.com",
    "word_count": 1234
  },
  "timestamp": "2026-03-06T10:30:00Z"
}
```

#### Agent 1 Thought Process (displayed to user):
```
🔍 Agent 1: Content Extractor
├─ Fetching URL: example.com/news-article
├─ Status: 200 OK (HTML received)
├─ Parsing HTML structure...
├─ Identified article container
├─ Extracted headline: "Breaking: Major Event..."
├─ Extracted body: 1,234 words
├─ Found author: John Doe
├─ Publication date: March 6, 2026
└─ ✅ Extraction complete. Passing to Fact Checker...
```

---

### Agent 2: Fact Checker & LLM Analyzer

**Purpose:** Verify claims using Tavily API and generate natural language reasoning via LLM

#### Responsibilities:
1. Receive extracted article from Agent 1
2. Extract key claims from headline and body
3. Query **Tavily API** for real-world verification
4. Compile Tavily results into markdown report
5. Feed markdown + original article to **LLM (Claude API)**
6. Get natural language analysis of authenticity
7. Output reasoning and initial verdict

#### Technologies:
- **Tavily API** - Real-time web search with source citations
- **Anthropic Claude API** - LLM for reasoning and analysis
- **spaCy/NLTK** - Claim extraction (optional)

#### Workflow:

##### Step 2.1: Extract Key Claims
```python
# Extract factual claims from article
claims = [
    "Biden announces new infrastructure plan",
    "Study shows 80% increase in renewable energy",
    "Event occurred on March 5, 2026"
]
```

##### Step 2.2: Query Tavily API
```python
import httpx

async def verify_with_tavily(claim: str):
    response = await httpx.post(
        "https://api.tavily.com/search",
        json={
            "api_key": TAVILY_API_KEY,
            "query": claim,
            "search_depth": "advanced",
            "include_domains": [
                "reuters.com", 
                "apnews.com", 
                "bbc.com"
            ],
            "max_results": 5
        }
    )
    return response.json()
```

##### Step 2.3: Compile Markdown Report
```markdown
# Tavily Fact-Check Results

## Claim 1: "Biden announces new infrastructure plan"
**Sources Found:** 3

### Supporting Sources:
- ✅ **Reuters** (2026-03-05): "Biden unveils $2T infrastructure package"
  - URL: https://reuters.com/article/123
  - Relevance: 95%
  
- ✅ **AP News** (2026-03-05): "White House releases infrastructure details"
  - URL: https://apnews.com/article/456
  - Relevance: 92%

### Contradicting Sources:
- None found

**Verdict:** SUPPORTED by mainstream sources

---

## Claim 2: "Study shows 80% increase in renewable energy"
**Sources Found:** 1

### Supporting Sources:
- ⚠️ **EnergyBlog.com** (2026-03-04): "Renewable energy surges"
  - URL: https://energyblog.com/article/789
  - Relevance: 67%
  - Note: Non-authoritative source

### Contradicting Sources:
- ❌ **Nature Journal** (2026-02-28): "Renewable growth at 40%, not 80%"
  - URL: https://nature.com/article/101
  - Relevance: 88%

**Verdict:** CONTRADICTED by authoritative source
```

##### Step 2.4: Feed to LLM for Analysis
```python
prompt = f"""You are a fact-checking analyst. Analyze this article for authenticity.

ORIGINAL ARTICLE:
Headline: {headline}
Content: {body}

TAVILY FACT-CHECK RESULTS:
{markdown_report}

Provide a detailed analysis in JSON format:
{{
  "authenticity_verdict": "REAL" | "FAKE" | "MISLEADING" | "UNVERIFIED",
  "confidence": 0.0-1.0,
  "reasoning": "Natural language explanation of why the article is authentic or fake",
  "red_flags": [
    {{
      "type": "exaggerated_claims" | "unsupported_statistics" | "contradicted_by_sources" | "missing_attribution",
      "description": "Specific issue found",
      "severity": "low" | "medium" | "high" | "critical"
    }}
  ],
  "supporting_evidence": ["List of facts that check out"],
  "contradicting_evidence": ["List of facts that don't check out"]
}}
"""

llm_response = await call_claude_api(prompt)
```

#### Output (to Agent 3):
```json
{
  "success": true,
  "agent": "fact_checker",
  "thought": "Verified 3 claims via Tavily. Found 2 supporting sources, 1 contradiction. LLM analysis indicates MISLEADING verdict due to exaggerated statistics.",
  "data": {
    "tavily_results": {
      "claims_checked": 3,
      "sources_found": 7,
      "supporting": 5,
      "contradicting": 2
    },
    "llm_analysis": {
      "authenticity_verdict": "MISLEADING",
      "confidence": 0.87,
      "reasoning": "While the main event (Biden infrastructure announcement) is factually accurate and supported by Reuters and AP News, the article contains a significant exaggeration. The claim of an '80% increase in renewable energy' is contradicted by Nature Journal, which reports only a 40% increase. This type of statistical inflation is a common tactic in misleading articles to sensationalize legitimate news. The article also lacks proper attribution for the renewable energy statistic, citing only an unnamed 'study' without providing a source.",
      "red_flags": [
        {
          "type": "exaggerated_claims",
          "description": "Renewable energy increase reported as 80% vs actual 40%",
          "severity": "high"
        },
        {
          "type": "missing_attribution",
          "description": "No source provided for renewable energy statistic",
          "severity": "medium"
        }
      ],
      "supporting_evidence": [
        "Biden infrastructure announcement confirmed by Reuters and AP News",
        "Event date (March 5, 2026) is accurate",
        "Main policy details match authoritative sources"
      ],
      "contradicting_evidence": [
        "Renewable energy increase is 40%, not 80% (Nature Journal)"
      ]
    }
  },
  "timestamp": "2026-03-06T10:30:15Z"
}
```

#### Agent 2 Thought Process (displayed to user):
```
🔎 Agent 2: Fact Checker & Analyzer
├─ Extracting claims from article...
│  ├─ Claim 1: Biden infrastructure announcement
│  ├─ Claim 2: 80% renewable energy increase
│  └─ Claim 3: Event date (March 5, 2026)
│
├─ Querying Tavily API for verification...
│  ├─ Searching: "Biden infrastructure announcement"
│  │  ├─ Found: Reuters (95% relevant) ✅
│  │  ├─ Found: AP News (92% relevant) ✅
│  │  └─ Verdict: SUPPORTED
│  │
│  ├─ Searching: "renewable energy 80% increase"
│  │  ├─ Found: EnergyBlog.com (67% relevant) ⚠️
│  │  ├─ Found: Nature Journal contradicts (88% relevant) ❌
│  │  └─ Verdict: CONTRADICTED
│  │
│  └─ Summary: 5 supporting, 2 contradicting sources
│
├─ Compiling markdown fact-check report...
│  └─ ✅ Report generated (1,247 words)
│
├─ Feeding to LLM (Claude) for analysis...
│  ├─ Prompt: Article + Tavily results
│  ├─ Requesting: Authenticity verdict + reasoning
│  └─ ✅ LLM response received
│
├─ Analysis Results:
│  ├─ Verdict: MISLEADING
│  ├─ Confidence: 87%
│  ├─ Red Flags: 2 identified
│  │  ├─ HIGH: Exaggerated statistics (80% vs 40%)
│  │  └─ MEDIUM: Missing source attribution
│  │
│  └─ Reasoning: "While main event is factually accurate,
│     article exaggerates renewable energy statistics..."
│
└─ ✅ Fact-check complete. Passing to Cross-Reference Agent...
```

---

### Agent 3: Cross-Reference Validator

**Purpose:** Final validation against multiple trusted sources and output authenticity score

#### Responsibilities:
1. Receive LLM analysis from Agent 2
2. Cross-reference against:
   - News API (trusted sources)
   - Google Fact Check Tools API
   - Manual source whitelist
3. Calculate final authenticity score (0-100)
4. Generate final verdict
5. Compile complete report for user

#### Technologies:
- **News API** - Cross-reference against 80k+ sources
- **Google Fact Check Tools API** - Existing fact-checks
- **Custom scoring algorithm**

#### Workflow:

##### Step 3.1: Query News API
```python
async def cross_reference_news_api(headline: str, claims: list):
    # Search for articles about the same topic
    response = await httpx.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": headline,
            "sources": "reuters,associated-press,bbc-news,the-guardian-uk",
            "language": "en",
            "sortBy": "relevancy",
            "apiKey": NEWS_API_KEY
        }
    )
    return response.json()
```

##### Step 3.2: Query Google Fact Check API
```python
async def check_google_factcheck(claim: str):
    response = await httpx.get(
        "https://factchecktools.googleapis.com/v1alpha1/claims:search",
        params={
            "query": claim,
            "key": GOOGLE_API_KEY
        }
    )
    return response.json()
```

##### Step 3.3: Calculate Authenticity Score
```python
def calculate_score(agent2_data: dict, cross_ref_data: dict) -> int:
    base_score = 50  # Neutral starting point
    
    # Adjust based on LLM verdict
    if agent2_data["llm_analysis"]["authenticity_verdict"] == "REAL":
        base_score += 30
    elif agent2_data["llm_analysis"]["authenticity_verdict"] == "FAKE":
        base_score -= 40
    elif agent2_data["llm_analysis"]["authenticity_verdict"] == "MISLEADING":
        base_score -= 20
    
    # Adjust based on Tavily results
    supporting = agent2_data["tavily_results"]["supporting"]
    contradicting = agent2_data["tavily_results"]["contradicting"]
    
    base_score += min(supporting * 5, 20)  # Max +20
    base_score -= min(contradicting * 10, 30)  # Max -30
    
    # Adjust based on News API cross-reference
    if cross_ref_data["news_api"]["corroborating_articles"] >= 3:
        base_score += 15
    elif cross_ref_data["news_api"]["corroborating_articles"] == 0:
        base_score -= 15
    
    # Adjust based on red flags
    for flag in agent2_data["llm_analysis"]["red_flags"]:
        if flag["severity"] == "critical":
            base_score -= 15
        elif flag["severity"] == "high":
            base_score -= 10
        elif flag["severity"] == "medium":
            base_score -= 5
    
    # Clamp to 0-100
    return max(0, min(100, base_score))
```

#### Output (Final Response):
```json
{
  "success": true,
  "final_verdict": "MISLEADING",
  "authenticity_score": 42,
  "confidence": "high",
  "agent_chain": [
    {
      "agent": "parser",
      "status": "success",
      "thought": "Successfully extracted article...",
      "timestamp": "2026-03-06T10:30:00Z"
    },
    {
      "agent": "fact_checker",
      "status": "success",
      "thought": "Verified 3 claims via Tavily...",
      "timestamp": "2026-03-06T10:30:15Z"
    },
    {
      "agent": "cross_reference",
      "status": "success",
      "thought": "Cross-referenced against 15 sources...",
      "timestamp": "2026-03-06T10:30:25Z"
    }
  ],
  "analysis": {
    "headline": "Breaking: Major Event Happens",
    "source": "example.com",
    "verdict": "MISLEADING",
    "score": 42,
    "reasoning": "While the main event is factually accurate and supported by Reuters and AP News, the article contains significant exaggeration...",
    "red_flags": [...],
    "sources_checked": {
      "tavily": 7,
      "news_api": 8,
      "google_factcheck": 2
    },
    "corroborating_sources": [
      {
        "source": "Reuters",
        "title": "Biden unveils infrastructure package",
        "url": "https://reuters.com/...",
        "relevance": "95%"
      }
    ],
    "contradicting_sources": [
      {
        "source": "Nature Journal",
        "title": "Renewable growth at 40%",
        "url": "https://nature.com/...",
        "relevance": "88%"
      }
    ]
  },
  "timestamp": "2026-03-06T10:30:25Z"
}
```

#### Agent 3 Thought Process (displayed to user):
```
✅ Agent 3: Cross-Reference Validator
├─ Received analysis from Agent 2
│  └─ Preliminary verdict: MISLEADING (87% confidence)
│
├─ Cross-referencing with News API...
│  ├─ Searching 80,000+ sources for: "Biden infrastructure"
│  ├─ Found 8 articles from trusted sources
│  │  ├─ Reuters: Corroborates main event ✅
│  │  ├─ AP News: Corroborates main event ✅
│  │  ├─ BBC: Corroborates main event ✅
│  │  └─ 5 more supporting articles
│  └─ News API Verdict: Main story SUPPORTED
│
├─ Checking Google Fact Check database...
│  ├─ Query: "renewable energy 80% increase"
│  ├─ Found 2 existing fact-checks
│  │  ├─ Snopes: "Exaggerated claim - actual 40%" ❌
│  │  └─ FactCheck.org: "Misleading statistic" ❌
│  └─ Fact Check Verdict: Renewable stat DEBUNKED
│
├─ Calculating final authenticity score...
│  ├─ Base score: 50
│  ├─ LLM verdict (MISLEADING): -20
│  ├─ Supporting sources (5): +15
│  ├─ Contradicting sources (2): -20
│  ├─ News API corroboration: +15
│  ├─ Red flags (2): -15
│  ├─ Fact-check debunks: -10
│  └─ FINAL SCORE: 42/100
│
├─ Final Assessment:
│  ├─ Verdict: MISLEADING
│  ├─ Score: 42/100 (Low credibility)
│  ├─ Confidence: High (87%)
│  └─ Reasoning: Mixed - accurate event, false statistics
│
└─ ✅ Analysis complete. Returning results to user...
```

---

## 📺 Chain of Thought Display

### Website Implementation (Real-time Streaming)

The website displays the agent thinking process in real-time using **Server-Sent Events (SSE)** or **WebSockets**.

#### Backend: FastAPI SSE Endpoint

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

async def agent_chain_generator(url: str):
    """Generator that yields agent thoughts as they happen"""
    
    # Agent 1: Parser
    yield f"data: {json.dumps({'agent': 'parser', 'status': 'started', 'thought': 'Fetching URL...'})}\n\n"
    await asyncio.sleep(0.5)
    
    article = await parse_url(url)
    yield f"data: {json.dumps({'agent': 'parser', 'status': 'success', 'thought': f'Extracted {article.word_count} words', 'data': article})}\n\n"
    
    # Agent 2: Fact Checker
    yield f"data: {json.dumps({'agent': 'fact_checker', 'status': 'started', 'thought': 'Extracting claims...'})}\n\n"
    await asyncio.sleep(0.5)
    
    claims = extract_claims(article)
    yield f"data: {json.dumps({'agent': 'fact_checker', 'status': 'progress', 'thought': f'Found {len(claims)} claims to verify'})}\n\n"
    
    # Query Tavily for each claim
    for i, claim in enumerate(claims):
        yield f"data: {json.dumps({'agent': 'fact_checker', 'status': 'progress', 'thought': f'Verifying claim {i+1}/{len(claims)}: {claim[:50]}...'})}\n\n"
        tavily_result = await verify_with_tavily(claim)
        await asyncio.sleep(1)
    
    # LLM Analysis
    yield f"data: {json.dumps({'agent': 'fact_checker', 'status': 'progress', 'thought': 'Analyzing with LLM...'})}\n\n"
    llm_analysis = await analyze_with_llm(article, tavily_results)
    yield f"data: {json.dumps({'agent': 'fact_checker', 'status': 'success', 'thought': f'LLM verdict: {llm_analysis.verdict}', 'data': llm_analysis})}\n\n"
    
    # Agent 3: Cross-Reference
    yield f"data: {json.dumps({'agent': 'cross_reference', 'status': 'started', 'thought': 'Cross-referencing sources...'})}\n\n"
    await asyncio.sleep(0.5)
    
    news_results = await query_news_api(article.headline)
    yield f"data: {json.dumps({'agent': 'cross_reference', 'status': 'progress', 'thought': f'Found {len(news_results)} related articles'})}\n\n"
    
    final_score = calculate_score(llm_analysis, news_results)
    yield f"data: {json.dumps({'agent': 'cross_reference', 'status': 'success', 'thought': f'Final score: {final_score}/100', 'data': {'score': final_score}})}\n\n"
    
    # Complete
    yield f"data: {json.dumps({'status': 'complete', 'final_score': final_score})}\n\n"

@app.post("/api/analyze-stream")
async def analyze_stream(url: str):
    return StreamingResponse(
        agent_chain_generator(url),
        media_type="text/event-stream"
    )
```

#### Frontend: React SSE Consumer

```jsx
import React, { useState, useEffect } from 'react';

function AgentThinkingDisplay({ url }) {
  const [thoughts, setThoughts] = useState([]);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(
      `http://localhost:8000/api/analyze-stream?url=${encodeURIComponent(url)}`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.status === 'complete') {
        setIsComplete(true);
        eventSource.close();
      } else {
        setThoughts(prev => [...prev, data]);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => eventSource.close();
  }, [url]);

  return (
    <div className="agent-thinking-container">
      <h2>Agent Analysis Progress</h2>
      
      {thoughts.map((thought, index) => (
        <div key={index} className={`thought-item agent-${thought.agent}`}>
          <div className="agent-badge">
            {thought.agent === 'parser' && '🔍 Agent 1: Parser'}
            {thought.agent === 'fact_checker' && '🔎 Agent 2: Fact Checker'}
            {thought.agent === 'cross_reference' && '✅ Agent 3: Validator'}
          </div>
          
          <div className="thought-content">
            <span className={`status-${thought.status}`}>
              {thought.status === 'started' && '⏳'}
              {thought.status === 'progress' && '⚙️'}
              {thought.status === 'success' && '✅'}
            </span>
            {thought.thought}
          </div>
          
          {thought.data && (
            <div className="thought-data">
              {/* Render relevant data preview */}
            </div>
          )}
        </div>
      ))}
      
      {isComplete && (
        <div className="analysis-complete">
          ✅ Analysis Complete!
        </div>
      )}
    </div>
  );
}
```

#### CSS Styling (Claude-like Chain of Thought)

```css
.agent-thinking-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Inter', sans-serif;
}

.thought-item {
  margin-bottom: 16px;
  padding: 16px;
  background: #f7f7f7;
  border-left: 4px solid #ccc;
  border-radius: 8px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.thought-item.agent-parser {
  border-left-color: #4a9eed;
  background: #e8f4fd;
}

.thought-item.agent-fact_checker {
  border-left-color: #f59e0b;
  background: #fef3e2;
}

.thought-item.agent-cross_reference {
  border-left-color: #22c55e;
  background: #e8f8ed;
}

.agent-badge {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
  color: #374151;
}

.thought-content {
  font-size: 15px;
  color: #1f2937;
  line-height: 1.5;
}

.status-started {
  display: inline-block;
  margin-right: 8px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-progress {
  display: inline-block;
  margin-right: 8px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.analysis-complete {
  padding: 20px;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #22c55e;
  background: #e8f8ed;
  border-radius: 8px;
  margin-top: 20px;
}
```

---

## 🌐 Frontend Implementation

### Website (Full Experience)

**Features:**
- URL input box
- Real-time agent thinking display (SSE)
- Final score and verdict
- Detailed breakdown of red flags
- Source citations with links
- Export report as PDF

**Tech Stack:**
- React 18+ with TypeScript
- Tailwind CSS
- EventSource API for SSE
- Framer Motion for animations

**Key Components:**
```
src/
├── components/
│   ├── URLInput.tsx           # URL submission form
│   ├── AgentChain.tsx          # Chain of thought display
│   ├── ScoreDisplay.tsx        # Final score visualization
│   ├── RedFlagsList.tsx        # Red flags breakdown
│   ├── SourceCitations.tsx     # Trusted sources list
│   └── ExportReport.tsx        # PDF export button
├── hooks/
│   ├── useAgentStream.ts       # SSE hook for agent updates
│   └── useAnalysis.ts          # Analysis state management
├── services/
│   └── api.ts                  # API client
└── App.tsx
```

---

## 🧩 Chrome Extension

### Extension Architecture

**Manifest V3 Structure:**
```json
{
  "manifest_version": 3,
  "name": "Fake News Detector",
  "version": "1.0.0",
  "permissions": ["activeTab", "storage"],
  "action": {
    "default_popup": "popup.html"
  },
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"]
  }]
}
```

### Extension Flow

1. **User clicks extension icon** on any webpage
2. **Content script** extracts current page URL
3. **Background worker** sends URL to `/api/analyze-simple` endpoint
4. **Popup displays** simple verdict:

```html
<!-- popup.html -->
<div class="popup-container">
  <div class="header">
    <h1>Fake News Detector</h1>
  </div>
  
  <div id="loading" class="hidden">
    <div class="spinner"></div>
    <p>Analyzing article...</p>
  </div>
  
  <div id="result" class="hidden">
    <!-- FAKE verdict -->
    <div class="verdict verdict-fake">
      <div class="score-badge">Score: 28/100</div>
      <h2>⚠️ Likely Fake</h2>
      <p>Multiple red flags detected</p>
      <button id="view-details">View Full Analysis</button>
    </div>
    
    <!-- REAL verdict -->
    <div class="verdict verdict-real hidden">
      <div class="score-badge">Score: 87/100</div>
      <h2>✅ Likely Real</h2>
      <p>Verified by trusted sources</p>
      <button id="view-details">View Full Analysis</button>
    </div>
  </div>
</div>
```

**Extension displays ONLY:**
- Score (0-100)
- Verdict (Fake/Real/Misleading)
- Button to "View Full Analysis" (opens website)

**Extension does NOT show:**
- Chain of thought
- Detailed reasoning
- Source citations

This keeps the extension lightweight and fast.

---

## 🔧 Backend Implementation

### FastAPI Project Structure

```
backend/
├── main.py                    # FastAPI app entry point
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── agents/
│   ├── __init__.py
│   ├── parser.py             # Agent 1: URL Parser
│   ├── fact_checker.py       # Agent 2: Fact Checker
│   └── cross_reference.py    # Agent 3: Validator
├── services/
│   ├── tavily_service.py     # Tavily API wrapper
│   ├── llm_service.py        # Claude API wrapper
│   ├── news_api_service.py   # News API wrapper
│   └── factcheck_service.py  # Google Fact Check wrapper
├── models/
│   ├── requests.py           # Pydantic request models
│   └── responses.py          # Pydantic response models
└── utils/
    ├── scoring.py            # Score calculation logic
    └── markdown.py           # Markdown report generator
```

### API Endpoints

```python
# main.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agents.orchestrator import AgentOrchestrator

app = FastAPI(title="Fake News Detector API")

@app.post("/api/analyze-stream")
async def analyze_stream(url: str):
    """
    Streaming endpoint for website (shows chain of thought)
    Returns SSE stream of agent thoughts
    """
    orchestrator = AgentOrchestrator()
    return StreamingResponse(
        orchestrator.run_chain(url),
        media_type="text/event-stream"
    )

@app.post("/api/analyze-simple")
async def analyze_simple(url: str):
    """
    Simple endpoint for Chrome extension (no streaming)
    Returns final verdict only
    """
    orchestrator = AgentOrchestrator()
    result = await orchestrator.run_chain_sync(url)
    
    return {
        "score": result["authenticity_score"],
        "verdict": result["final_verdict"],
        "confidence": result["confidence"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- API Keys:
  - Tavily API
  - Anthropic Claude API
  - News API
  - Google Fact Check API (optional)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/fake-news-detector.git
cd fake-news-detector/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
TAVILY_API_KEY=your_tavily_key
ANTHROPIC_API_KEY=your_claude_key
NEWS_API_KEY=your_newsapi_key
GOOGLE_FACTCHECK_API_KEY=your_google_key
EOF

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:8000
EOF

# Run development server
npm run dev
```

### Chrome Extension Setup

```bash
# Navigate to extension
cd ../extension

# Install dependencies
npm install

# Build extension
npm run build

# Load in Chrome:
# 1. Go to chrome://extensions
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select the `extension/dist` folder
```

---

## 📚 API Documentation

### Tavily API Integration

```python
# services/tavily_service.py
import httpx
import os

class TavilyService:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com"
    
    async def search(self, query: str, max_results: int = 5):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/search",
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "search_depth": "advanced",
                    "include_domains": [
                        "reuters.com",
                        "apnews.com",
                        "bbc.com",
                        "nytimes.com"
                    ],
                    "max_results": max_results
                }
            )
            return response.json()
```

### Claude API Integration

```python
# services/llm_service.py
import anthropic
import os

class LLMService:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    
    async def analyze_article(self, article: dict, tavily_report: str):
        prompt = f"""Analyze this article for authenticity.

ARTICLE:
Headline: {article['headline']}
Content: {article['body']}

FACT-CHECK RESULTS:
{tavily_report}

Provide analysis in JSON format with:
- authenticity_verdict (REAL/FAKE/MISLEADING/UNVERIFIED)
- confidence (0.0-1.0)
- reasoning (natural language explanation)
- red_flags (array of issues)
- supporting_evidence (array)
- contradicting_evidence (array)
"""
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
```

---

## 🎯 Environment Variables

```bash
# .env file
TAVILY_API_KEY=tvly-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
NEWS_API_KEY=xxxxxxxxxxxxx
GOOGLE_FACTCHECK_API_KEY=xxxxxxxxxxxxx

# Optional
ENVIRONMENT=development
PORT=8000
CORS_ORIGINS=http://localhost:5173,chrome-extension://*
```

---

## 📦 Deployment

### Backend (Railway/Render)

```bash
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
```

### Frontend (Vercel)

```bash
# vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "env": {
    "VITE_API_URL": "https://your-api.railway.app"
  }
}
```

### Chrome Extension (Chrome Web Store)

1. Build production version: `npm run build`
2. Zip the `dist` folder
3. Upload to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)

---

## 🎨 UI/UX Design

### Chain of Thought Display (Website)

Visual inspiration: Claude's thinking process

```
┌─────────────────────────────────────────────┐
│  🔍 Agent 1: Content Extractor              │
│  ├─ Fetching URL...                         │
│  ├─ ✅ Extracted 1,234 words                │
│  └─ Passing to Agent 2...                   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  🔎 Agent 2: Fact Checker                   │
│  ├─ Extracting claims...                    │
│  ├─ Querying Tavily API...                  │
│  │  ├─ Claim 1: ✅ Supported                │
│  │  └─ Claim 2: ❌ Contradicted             │
│  ├─ Analyzing with LLM...                   │
│  └─ ✅ Verdict: MISLEADING (87%)            │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  ✅ Agent 3: Cross-Reference Validator      │
│  ├─ Checking News API...                    │
│  ├─ Found 8 corroborating articles          │
│  ├─ Calculating score...                    │
│  └─ ✅ Final Score: 42/100                  │
└─────────────────────────────────────────────┘
```

### Extension Popup (Simple)

```
┌──────────────────────┐
│ Fake News Detector   │
├──────────────────────┤
│                      │
│   Score: 28/100      │
│                      │
│   ⚠️ Likely Fake     │
│                      │
│ Multiple red flags   │
│ detected             │
│                      │
│ [View Full Analysis] │
│                      │
└──────────────────────┘
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

---

## 📧 Support

For issues or questions, please open a GitHub issue or contact support@fakenewsdetector.com

---

**Built with ❤️ for truth and transparency**