#!/usr/bin/env bash
# Start the backend API and the Streamlit dashboard together. Ctrl-C stops both.
set -e

cd "$(dirname "$0")"
ROOT="$PWD"
PY="$ROOT/.venv/bin"

if [ ! -x "$PY/uvicorn" ]; then
  echo "No .venv found. Run:  ./setup.sh"
  exit 1
fi

if [ ! -f backend/.env ]; then
  echo "Warning: backend/.env is missing. Run:  cp backend/.env.example backend/.env"
fi

cleanup() { kill 0 2>/dev/null; }
trap cleanup EXIT INT TERM

# Skip past any port already in use on this machine.
free_port() {
  port=$1
  while lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; do
    port=$((port + 1))
  done
  echo "$port"
}

API_PORT=$(free_port "${BACKEND_PORT:-8000}")
UI_PORT=$(free_port "${FRONTEND_PORT:-8501}")
export BACKEND_URL="http://localhost:$API_PORT"

# No --reload: its child worker survives Ctrl-C and keeps the port, and an editor save
# restarts the server mid-request. Restart by hand instead.
echo "Backend  -> $BACKEND_URL"
(cd backend && "$PY/uvicorn" main:app --port "$API_PORT") &

sleep 2
echo "Frontend -> http://localhost:$UI_PORT"
(cd frontend && "$PY/streamlit" run app.py --server.port "$UI_PORT") &

wait
