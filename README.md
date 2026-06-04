# AI-Powered Restaurant Recommendation System

Zomato-inspired restaurant recommendations: structured filtering on real dataset data, personalized ranking and explanations via **Grok (xAI)**, and a **Next.js** UI backed by a **Python (FastAPI)** API.

## Status

| Phase | Status |
|-------|--------|
| 0 — Project setup | Done |
| 1 — Data ingestion | Done (Zomato data loaded & preprocessed) |
| 2 — User input & preference model | Done (Validation schemas & React autocomplete form) |
| 3 — Integration layer | Done (Structured pre-LLM filtering pipeline) |
| 4 — Grok recommendation engine | Done (OpenAI compatible integration, grounding, & fallbacks) |
| 5 — Output display & UX | Done (Glassmorphic cards, ratings, tags, AI summary block) |
| 6 — Testing & Hardening | Done (100% passing test suite for all modules) |


## Prerequisites

- **Python 3.10+** with `pip`
- **Node.js 18+** with `npm`
- Internet access for Hugging Face dataset download (Phase 1)

## Quick start

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

**Ingest data (Phase 1):**

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m src.ingestion.prepare_data
```

Writes `data/processed/restaurants.parquet` and `data/ingestion_report.txt`.

**Run API (Phase 0):**

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Or: `.\scripts\run_api.ps1`

- `GET http://localhost:8000/health` — liveness + `data_ready` + row count
- `POST http://localhost:8000/recommendations` — validates input preferences and returns Grok AI recommendations (grounded in the dataset, with a local fallback engine)

### 2. Frontend

```powershell
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) — the page calls `/health` on the backend.

### 3. Tests

```powershell
cd backend
$env:PYTHONPATH = (Get-Location).Path
python -m pytest
```

## Project layout

```
backend/
  src/
    api/           # FastAPI routes
    ingestion/     # HF load + preprocess
    data/          # Parquet loader
    filters/       # Phase 3
    llm/           # Phase 4 (Grok)
  tests/
frontend/
  app/             # Next.js App Router
  components/
  lib/api.ts
data/processed/    # restaurants.parquet (generated)
docs/
```

## Environment

**Backend** (`backend/.env`):

| Variable | Description |
|----------|-------------|
| `XAI_API_KEY` | xAI key (Phase 4+) |
| `GROK_MODEL` | e.g. `grok-2-latest` |
| `CORS_ORIGINS` | `http://localhost:3000` |
| `DATA_PATH` | Optional override for parquet path |

**Frontend** (`frontend/.env.local`):

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` |

## Documentation

- [Problem statement](docs/problem%20statement.md)
- [Architecture](docs/Architecture.md)
- [Edge cases](docs/edgecase.md)
- [Implementation plan](docs/implementation.md)

## Tech stack

| Layer | Stack |
|-------|--------|
| LLM | Grok (xAI API) — Phase 4 |
| Backend | Python 3.10+, FastAPI, pandas, Hugging Face `datasets` |
| Frontend | Next.js 15, TypeScript |

Dataset: [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
