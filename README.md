# 🌿 AI-Based Crop Treatment Recommendation System

Upload a crop leaf photo. A vision model diagnoses the disease and severity, then a ReAct agent
checks the farmer's live local weather and returns the chemical, the dosage, and whether it is
safe to spray right now — colour-coded Red / Yellow / Green.

## How it works

```
leaf photo ──► vision model (OpenRouter)  ──► {disease, severity %}
                                                    │
                                                    ▼
                          ReAct agent (DeepSeek R1) ──► get_weather (Open-Meteo, no API key)
                                                    └─► web_search  (Tavily, optional)
                                                    │
                                                    ▼
                                    {chemical, dosage, spray_now, best window}
```

## Setup

```bash
./setup.sh                    # creates .venv and installs everything (once)
# then add your OPENROUTER_API_KEY to backend/.env
```

## Run

```bash
./run.sh                      # starts the API and the dashboard together
```

Both run from the shared `.venv` at the repo root. Ports default to 8000 (API) and 8501 (UI),
and automatically shift up if those are busy — the URLs are printed on startup. Ctrl-C stops both.
Override with `BACKEND_PORT=9000 FRONTEND_PORT=9501 ./run.sh`.

Open the printed frontend URL, set the city and state in the sidebar, upload a leaf photo,
and click **Analyze Leaf**.

<details>
<summary>Running the two services manually</summary>

```bash
cd backend  && ../.venv/bin/uvicorn main:app --reload    # terminal 1
cd frontend && ../.venv/bin/streamlit run app.py         # terminal 2
```
</details>

## Quick checks

```bash
curl localhost:8000/health
cd backend && PYTHONPATH=. ../.venv/bin/python -c "from tools import get_weather; print(get_weather('Nashik','Maharashtra'))"
```

The weather check needs no API key — Open-Meteo is free and unauthenticated.

## Layout

| Path | What it does |
|---|---|
| `backend/main.py` | FastAPI, `POST /analyze` (image + city + state) |
| `backend/vision.py` | Stage 1 — leaf photo to disease + severity JSON |
| `backend/agent.py` | Stage 2 — the ReAct loop (~50 lines, no framework) |
| `backend/tools.py` | `get_weather` (Open-Meteo), `web_search` (Tavily) + tool schemas |
| `backend/prompts.py` | Both system prompts and the output JSON contract |
| `backend/llm.py` | OpenRouter call + JSON extraction |
| `frontend/app.py` | Streamlit dashboard with colour-coded cards and the agent trace |

## Notes

- `TAVILY_API_KEY` is optional. Without it, `web_search` returns a "not available" note and the
  agent falls back on its own knowledge — the demo still runs.
- Swap models via `.env` if one is rate-limited, e.g. `AGENT_MODEL=moonshotai/kimi-k2`.
