#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting OTA Revenue MVP..."
echo

if [ ! -f "$ROOT_DIR/backend/.venv/Scripts/python.exe" ]; then
  echo "Backend virtual environment not found."
  echo "Run these first:"
  echo "  cd backend"
  echo "  python -m venv .venv"
  echo "  ./.venv/Scripts/python.exe -m pip install -r requirements.txt"
  exit 1
fi

if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
  echo "Frontend dependencies not found."
  echo "Run these first:"
  echo "  cd frontend"
  echo "  npm install"
  exit 1
fi

echo "Backend:  http://127.0.0.1:8000"
echo "Frontend: http://127.0.0.1:5173"
echo

cd "$ROOT_DIR/backend"
"$ROOT_DIR/backend/.venv/Scripts/python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

cleanup() {
  echo
  echo "Stopping backend..."
  kill "$BACKEND_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cd "$ROOT_DIR/frontend"
npm run dev

