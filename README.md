# 🌿 AI-Based Crop Treatment Recommendation System

**Team Crimson Commits — Dhairya Garg**

Upload a photo of a crop leaf and get an instant AI-powered diagnosis. A vision model identifies the disease and estimates its severity, then a ReAct agent checks the farmer's live local weather and returns the right chemical, the correct dosage, and whether it's actually safe to spray right now — shown as a clear Red / Yellow / Green signal.

Built for farmers, agricultural officers, and government agencies who need fast, actionable crop-health guidance without needing an agronomist on call.

---

## ✨ Features

- **Leaf-photo diagnosis** — upload an image, get the disease name and severity percentage
- **Weather-aware spray timing** — pulls live local weather (no API key required) to decide if conditions are safe to spray
- **Treatment recommendations** — chemical name, dosage, and best application window
- **Agent reasoning trace** — see each step the ReAct agent takes (tool calls and decisions), not just the final answer
- **Two frontends** — a Streamlit dashboard (`frontend/app.py`) and a lightweight static HTML/JS UI (`frontend/index.html`)
- **Streaming endpoint** — `/analyze/stream` emits progress events live instead of waiting for the full result

---

## 🧠 How It Works

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

1. **Vision stage** (`backend/vision.py`) — the uploaded leaf image is sent to a vision model via OpenRouter, which returns a structured diagnosis (disease + severity).
2. **Reasoning stage** (`backend/agent.py`) — a compact (~50 lines, no agent framework) ReAct loop takes that diagnosis, calls tools as needed (live weather, optional web search), and produces a final structured recommendation.
3. **API layer** (`backend/main.py`) — FastAPI exposes `POST /analyze` and a streaming variant `POST /analyze/stream`.
4. **UI layer** (`frontend/`) — a Streamlit dashboard or a static HTML page calls the API and displays the diagnosis, the color-coded spray recommendation, and the agent's reasoning trace.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| Vision / LLM | [OpenRouter](https://openrouter.ai/) (vision model + DeepSeek R1 for the ReAct agent) |
| Weather data | [Open-Meteo](https://open-meteo.com/) (free, no API key) |
| Web search (optional) | [Tavily](https://tavily.com/) |
| Frontend (dashboard) | [Streamlit](https://streamlit.io/) |
| Frontend (static) | HTML / CSS / vanilla JavaScript |
| Image handling | [Pillow](https://python-pillow.org/) |

---

## 📦 Dependencies

**Backend** (`backend/requirements.txt`)
```
fastapi
uvicorn[standard]
python-multipart
requests
python-dotenv
pillow
```

**Frontend** (`frontend/requirements.txt`)
```
streamlit
requests
```

**Requirements**
- Python 3.9+ (developed/tested on Python 3.13)
- An [OpenRouter](https://openrouter.ai/) API key (required)
- A [Tavily](https://tavily.com/) API key (optional — enables live web search for the agent)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/dhhairya/Team-Crimson-Commits---Dhairya-Garg.git
cd Team-Crimson-Commits---Dhairya-Garg
```

### 2. Run setup

This creates a shared virtual environment at the repo root and installs both the backend and frontend dependencies.

```bash
./setup.sh
```

Then add your key to the generated env file:

```bash
# backend/.env
OPENROUTER_API_KEY=your_key_here
# TAVILY_API_KEY=your_key_here   # optional
```

### 3. Run the app

```bash
./run.sh
```

This starts the FastAPI backend and the Streamlit dashboard together, both from the shared `.venv`.

- API defaults to `http://localhost:8000`
- Dashboard defaults to `http://localhost:8501`
- If either port is busy, the script automatically shifts to the next free port and prints the actual URLs on startup
- Override the defaults with:
  ```bash
  BACKEND_PORT=9000 FRONTEND_PORT=9501 ./run.sh
  ```
- Press `Ctrl-C` to stop both services

Open the printed frontend URL, enter the city and state in the sidebar, upload a leaf photo, and click **Analyze Leaf**.

### Running the two services manually

```bash
cd backend  && ../.venv/bin/uvicorn main:app --reload    # terminal 1
cd frontend && ../.venv/bin/streamlit run app.py          # terminal 2
```

---

## ✅ Quick Checks

Verify the API is up:

```bash
curl localhost:8000/health
```

Verify the weather tool works (no API key needed — Open-Meteo is free and unauthenticated):

```bash
cd backend && PYTHONPATH=. ../.venv/bin/python -c "from tools import get_weather; print(get_weather('Nashik','Maharashtra'))"
```

---

## 📁 Project Layout

| Path | What it does |
|---|---|
| `backend/main.py` | FastAPI app — `POST /analyze` and `POST /analyze/stream` (image + city + state) |
| `backend/vision.py` | Stage 1 — leaf photo → disease + severity JSON |
| `backend/agent.py` | Stage 2 — the ReAct loop (no framework, ~50 lines) |
| `backend/tools.py` | `get_weather` (Open-Meteo) and `web_search` (Tavily) tool implementations + schemas |
| `backend/prompts.py` | System prompts and the output JSON contract |
| `backend/llm.py` | OpenRouter API calls + JSON extraction |
| `backend/net.py` | Shared networking helpers |
| `frontend/app.py` | Streamlit dashboard — color-coded result cards and the agent's reasoning trace |
| `frontend/index.html`, `script.js`, `style.css` | Lightweight static HTML/JS alternative frontend |
| `setup.sh` | One-time setup — creates `.venv`, installs all dependencies |
| `run.sh` | Starts the backend and frontend together |

---

## 📝 Notes

- `TAVILY_API_KEY` is optional. Without it, `web_search` returns a "not available" note and the agent falls back on its own knowledge — the app still works fully.
- If a model is rate-limited, swap it via `.env`, e.g. `AGENT_MODEL=moonshotai/kimi-k2`.
- The backend runs `/analyze` synchronously (not `async def`) on purpose — the underlying work is blocking network I/O, so FastAPI dispatches it to a worker thread rather than stalling the event loop.

---

## 👤 Author

**Dhairya Garg** — Team Crimson Commits
