# Emidens

A clinical decision support system for on-call clinicians. Emidens routes
clinical queries to expert AI agents (pharmaceutical, cardiology, and research)
and synthesizes their answers into a single, cited response with confidence
scores, streamed in real time.

Built at Chalmers University (TRA460, Group 4).

---

## Contributors

[@andrej-kocijan](https://github.com/andrej-kocijan) &nbsp;
[@Viggo-Troback](https://github.com/Viggo-Troback) &nbsp;
[@victorzexihe-dev](https://github.com/victorzexihe-dev) &nbsp;
[@idathorburn](https://github.com/idathorburn)

---

## Live Demo

A hosted instance is available at <https://konsult.kocijan.net>.
Access can be requested via [kocijan@chalmers.se](mailto:kocijan@chalmers.se).

---

## Architecture

```text
frontend/   React + TypeScript UI (Vite, Tailwind)
backend/    FastAPI + LangGraph multi-agent pipeline (Python 3.12)
```

The backend exposes SSE endpoints for streaming agent responses. The frontend
consumes them and renders agent reasoning, tool calls, and the final answer as
they arrive.

---

## Prerequisites

- Python 3.12 (the backend uses `uv` for dependency management)
- Node.js 20+
- An Anthropic API key
- A Konsulten API key — required for FASS (drug database)
  and cardiology guideline search

Optional:

- NCBI API key — raises PubMed rate limit from 3 to 10 req/s
  ([free](https://account.ncbi.nlm.nih.gov/settings/))

---

## Setup

### Backend

```bash
cd backend

# Install dependencies (uv recommended)
uv sync
# or: python -m venv .venv && source .venv/bin/activate && pip install -e .

# Configure environment
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY and KONSULTEN_API_KEY (both required)
```

Key `.env` variables:

| Variable | Default | Description |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | — | **Required.** Anthropic API key |
| `MODEL` | `claude-haiku-4-5` | Claude model to use |
| `NCBI_API_KEY` | (empty) | Optional — higher PubMed rate limit |
| `KONSULTEN_API_KEY` | — | **Required.** FASS and cardiology guidelines |
| `ALLOWED_ORIGIN` | `http://localhost:5173` | Frontend URL for CORS |
| `API_HOST` | `127.0.0.1` | Bind address |
| `API_PORT` | `8080` | Bind port |

### Frontend

```bash
cd frontend

npm install

# Configure environment
cp .env.example .env
# Default points to http://127.0.0.1:8080 — no changes needed for local dev
```

---

## Running

Start both servers (in separate terminals):

```bash
# Terminal 1 — backend
cd backend
uv run python -m api
# → http://127.0.0.1:8080

# Terminal 2 — frontend
cd frontend
npm run dev
# → http://localhost:5173
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## API

### `POST /query/stream`

Main endpoint. Returns a Server-Sent Events stream.

**Request**

```json
{
  "query": "Vilken dos av apixaban hos 78-årig patient med eGFR 35?",
  "clinical_context": {
    "age_years": 78,
    "weight_kg": 65,
    "active_conditions": ["heart_failure"],
    "current_medications": ["furosemid"],
    "renal_impairment": true,
    "hepatic_impairment": false
  },
  "skipped_fields": []
}
```

**Response**

Each event has the form `event: <type>\ndata: <json>\n\n`.

| Event | Key fields |
| --- | --- |
| `routing` | `assignments[]` (capability, task), `reasoning` |
| `tool_call` | `tool`, `input`, `tool_call_id` |
| `tool_result` | `tool`, `output`, `tool_call_id`, `artifact` |
| `expert_response` | `capability`, `answer`, `confidence`, `citations[]`, `escalate` |
| `final` | same shape as `expert_response` |
| `done` | (empty) |

### `GET /ping`

Health check, returns `{"status": "ok"}`.

### Dev endpoints (bypass orchestrator)

Useful for testing a single agent directly:

```text
POST /dev/pharmaceutical/stream
POST /dev/cardiology/stream
POST /dev/research/stream
```
