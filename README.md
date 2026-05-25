# OTA & Revenue Management MVP

An MVP for managing hotel OTA listings and revenue optimization. It includes:

- Python FastAPI backend with demo hotel, OTA, pricing, and reporting data
- Vite React frontend dashboard
- Demand-based rate recommendations
- ADR, occupancy, inventory, and revenue uplift views

## Project Structure

```text
backend/
  app/
    main.py
  requirements.txt
frontend/
  src/
    App.jsx
    main.jsx
    styles.css
  index.html
  package.json
  vite.config.js
```

## Run Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend API: `http://localhost:8000`

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend app: `http://localhost:5173`

## MVP Flow

1. View OTA health, ADR, revenue uplift, and current inventory.
2. Review AI-style rate recommendations by room type and channel.
3. Add demand signals such as events, pickup, search volume, or competitor changes.
4. Refresh recommendations and view the projected revenue impact.

# hotel-ota-mvp
