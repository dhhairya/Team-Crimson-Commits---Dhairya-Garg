# 🌿 AI-Based Crop Treatment Recommendation System

An AI-powered crop disease diagnosis and treatment recommendation platform that combines **computer vision**, **LLM reasoning**, and **real-time weather analysis** to help farmers make informed spraying decisions.

Users simply upload a crop leaf image, and the system:
1. Detects the crop disease using a vision model.
2. Estimates the severity of the infection.
3. Fetches live weather conditions for the farmer's location.
4. Uses a ReAct AI agent to recommend the most suitable treatment, dosage, and spraying schedule.
5. Displays a **Green / Yellow / Red** safety indicator based on current weather conditions.

---

## 🚀 Features

- 📷 AI-powered crop disease detection from leaf images
- 🌱 Disease severity estimation
- 🌦️ Real-time weather integration using Open-Meteo (No API key required)
- 🤖 ReAct AI Agent for intelligent treatment planning
- 💊 Chemical recommendation with dosage instructions
- ⏰ Best spraying time recommendation
- 🟢🟡🔴 Color-coded spray safety status
- 📊 Interactive Streamlit dashboard
- ⚡ FastAPI backend

---

# 🏗️ System Architecture

```text
                    Upload Leaf Image
                            │
                            ▼
          ┌────────────────────────────┐
          │ Vision Model (OpenRouter)  │
          │ Disease Detection          │
          │ Severity Estimation        │
          └────────────────────────────┘
                            │
                            ▼
              { Disease, Severity (%) }
                            │
                            ▼
         ┌─────────────────────────────────┐
         │ ReAct Agent (DeepSeek R1)       │
         │                                 │
         │ • Fetch Live Weather            │
         │ • Search Agricultural Data      │
         │ • Reason Over Results           │
         └─────────────────────────────────┘
                  │                 │
                  ▼                 ▼
        Open-Meteo API        Tavily Search (Optional)
                  │
                  ▼
      Treatment Recommendation Engine
                  │
                  ▼
 ┌────────────────────────────────────────────┐
 │ Recommended Chemical                       │
 │ Recommended Dosage                         │
 │ Safe to Spray? (Yes / No)                  │
 │ Best Spraying Window                       │
 │ Red / Yellow / Green Indicator             │
 └────────────────────────────────────────────┘
```

---

# 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI |
| Frontend | Streamlit |
| Vision Model | OpenRouter Vision Models |
| AI Agent | DeepSeek R1 |
| Weather API | Open-Meteo |
| Web Search | Tavily (Optional) |
| Language | Python 3.13 |

---

# 📂 Project Structure

```text
.
├── backend
│   ├── agent.py          # ReAct agent logic
│   ├── llm.py            # OpenRouter API wrapper
│   ├── main.py           # FastAPI server
│   ├── net.py            # Networking utilities
│   ├── prompts.py        # Prompt templates
│   ├── tools.py          # Weather & Search tools
│   ├── vision.py         # Disease detection
│   └── requirements.txt
│
├── frontend
│   └── app.py            # Streamlit Dashboard
│
├── run.sh
├── setup.sh
└── README.md
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone <repository-url>
cd crop-treatment-ai
```

Create the virtual environment and install dependencies

```bash
./setup.sh
```

Add your API key

```text
backend/.env

OPENROUTER_API_KEY=your_api_key
```

---

# ▶️ Running the Application

Start both the backend and frontend together:

```bash
./run.sh
```

By default:

| Service | Port |
|----------|------|
| FastAPI Backend | 8000 |
| Streamlit Frontend | 8501 |

If either port is already in use, the application automatically selects the next available port.

You can also specify custom ports:

```bash
BACKEND_PORT=9000 FRONTEND_PORT=9501 ./run.sh
```

---

## Running Services Separately

Backend

```bash
cd backend
../.venv/bin/uvicorn main:app --reload
```

Frontend

```bash
cd frontend
../.venv/bin/streamlit run app.py
```

---

# 🌾 How to Use

1. Launch the application.
2. Open the Streamlit dashboard.
3. Select your **City** and **State**.
4. Upload a crop leaf image.
5. Click **Analyze Leaf**.
6. Review the AI-generated diagnosis and treatment recommendations.

The system provides:

- Disease Name
- Disease Severity
- Recommended Chemical
- Recommended Dosage
- Spray Safety Status
- Best Time to Spray
- AI Agent Reasoning Trace

---

# 🧪 API Endpoints

### Health Check

```bash
curl localhost:8000/health
```

### Analyze Crop Leaf

```
POST /analyze
```

**Input**

- Leaf Image
- City
- State

**Response**

```json
{
  "disease": "Early Blight",
  "severity": 42,
  "chemical": "Mancozeb",
  "dosage": "2 g/L",
  "spray_now": true,
  "best_window": "Tomorrow 7 AM - 9 AM",
  "status": "GREEN"
}
```

---

# ✅ Quick Test

Test weather integration

```bash
cd backend

PYTHONPATH=. ../.venv/bin/python -c \
"from tools import get_weather; print(get_weather('Nashik','Maharashtra'))"
```

No API key is required for Open-Meteo.

---

# 🔧 Configuration

Environment variables

```text
OPENROUTER_API_KEY=xxxxxxxxxxxx
TAVILY_API_KEY=xxxxxxxxxxxx      # Optional
AGENT_MODEL=deepseek/deepseek-r1
VISION_MODEL=<vision-model>
```

If Tavily is not configured, the AI agent falls back to its internal knowledge while still providing recommendations.

You can also switch models using:

```text
AGENT_MODEL=moonshotai/kimi-k2
```

---

# 🌟 Future Improvements

- 🌍 Multi-language support
- 📍 GPS-based automatic location detection
- 🌿 Multiple crop support
- 📈 Disease history tracking
- 📊 Farmer analytics dashboard
- 🛰️ Satellite and weather forecast integration
- 📱 Mobile application
- 🎙️ Voice assistant for farmers

---

# 📜 License

This project is developed for educational, research, and demonstration purposes.
