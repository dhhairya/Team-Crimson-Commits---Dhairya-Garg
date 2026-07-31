#!/usr/bin/env bash
# One-time setup: create .venv and install backend + frontend dependencies.
set -e

cd "$(dirname "$0")"

python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r backend/requirements.txt -r frontend/requirements.txt

[ -f backend/.env ] || cp backend/.env.example backend/.env

echo
echo "Done. Add your OPENROUTER_API_KEY to backend/.env, then run:  ./run.sh"
