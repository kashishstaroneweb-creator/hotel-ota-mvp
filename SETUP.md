# Teammate Setup Guide

Follow these steps after cloning the repo.

## 1. Open Project

```bash
cd hotel-ai-mvp
```

## 2. Install Backend

Use Git Bash or PowerShell:

```bash
cd backend
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
cd ..
```

PowerShell alternative:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd ..
```

If backend dependencies were already installed before this repo update, refresh them:

```bash
cd backend
./.venv/Scripts/python.exe -m pip install --upgrade -r requirements.txt
cd ..
```

## 3. Install Frontend

```bash
cd frontend
npm install
cd ..
```

## 4. Start App

Git Bash:

```bash
bash start.sh
```

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

## 5. Open App

Frontend:

```text
http://127.0.0.1:5173
```

Backend API:

```text
http://127.0.0.1:8000
```

Backend health check:

```text
http://127.0.0.1:8000/api/health
```

Expected health response:

```json
{"status":"ok"}
```

## Manual Start

If the start script does not work, open two terminals.

Terminal 1:

```bash
cd backend
source .venv/Scripts/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
cd frontend
npm run dev
```

## Common Issues

### Port 8000 Already Busy

Backend is already running or another app is using port `8000`.

Use another backend port:

```bash
cd backend
source .venv/Scripts/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Then start frontend with:

```bash
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8001 npm run dev
```

### Port 5173 Already Busy

Start frontend on another port:

```bash
cd frontend
npm run dev -- --port 5174
```

Open:

```text
http://127.0.0.1:5174
```

### Git Bash Activation Error

Use this:

```bash
source .venv/Scripts/activate
```

Do not use this in Git Bash:

```text
.venv\Scripts\activate
```
