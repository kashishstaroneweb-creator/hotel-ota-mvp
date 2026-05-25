# Run Commands

## Git Bash

From the project root:

```bash
./start.sh
```

If Git Bash says permission denied:

```bash
bash start.sh
```

## PowerShell

From the project root:

```powershell
.\start.ps1
```

If PowerShell blocks scripts:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

## Manual Commands

Backend:

```bash
cd backend
source .venv/Scripts/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

