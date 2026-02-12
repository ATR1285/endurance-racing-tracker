# How the Endurance Racing Tracker Works

## 🏎️ Project Overview

This is a **real-time endurance racing analytics dashboard** with ML-powered predictions for WEC and IMSA races.

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Dashboard (HTML/CSS/JS + Chart.js)                  │  │
│  │  - Live leaderboard                                  │  │
│  │  - Lap time charts                                   │  │
│  │  - ML predictions                                    │  │
│  │  - Video background                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP Requests (every 5 seconds)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              FASTAPI BACKEND SERVER                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  REST API Endpoints                                  │  │
│  │  /api/leaderboard  /api/predictions  /api/strategy   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Race Monitor (Background Task)                      │  │
│  │  - Checks schedule every 5 minutes                   │  │
│  │  - Auto-starts scraping when races begin             │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Ingestion Manager                              │  │
│  │  - Web scraping (BeautifulSoup/Selenium)             │  │
│  │  - Retry logic (3 attempts)                          │  │
│  │  - Data validation                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ML Models                                           │  │
│  │  - Lap Time Predictor (Random Forest)                │  │
│  │  - Anomaly Detector (Isolation Forest)               │  │
│  │  - Strategy Engine (Fuel/Tire calculations)          │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SQLite Database                                     │  │
│  │  - Races, Cars, Drivers, Laps, Pit Stops             │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ Web Scraping
                     ↓
┌─────────────────────────────────────────────────────────────┐
│         LIVE TIMING SOURCES                                 │
│  - WEC: https://timing.71wytham.org.uk/                    │
│  - IMSA: https://www.imsa.com/scoring/                     │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 How It Works (Step by Step)

### 1. **Server Startup**
```bash
python -m uvicorn backend.main:app --reload
```
- Initializes SQLite database
- Loads ML models (if available)
- **Starts Race Monitor** (NEW!)
- Serves frontend at http://localhost:8000/dashboard

### 2. **Race Monitor (Automatic)**
- Runs in background every 5 minutes
- Checks race schedule against current time
- **When race detected:**
  - Creates race entry in database
  - Starts Data Ingestion Manager
  - Begins scraping timing data

### 3. **Data Ingestion (When Race is Live)**
- Fetches data from timing websites every 10 seconds
- **Retry logic:** 3 attempts with 5-second delays
- **Validates data** before storing
- Stores in database:
  - Car positions
  - Lap times (sector times)
  - Pit stops
  - Driver stints

### 4. **ML Pipeline (Automatic)**
- **After 10 laps collected:** Trains initial models
- **Every 5 laps:** Updates models with new data
- Models saved to disk for persistence

### 5. **Frontend Dashboard**
- Refreshes every 5 seconds
- Fetches data from API endpoints:
  - `/api/leaderboard` - Current positions
  - `/api/laps/{car_number}` - Lap times for charts
  - `/api/predictions/{car_number}` - ML predictions
  - `/api/strategy/{car_number}` - Pit strategy
  - `/api/anomalies` - Recent incidents

### 6. **Video Background**
- HTML5 video element plays racing footage
- Served from `frontend/static/racing-background.mp4`
- 40% opacity with cinematic overlay

## 🎯 Current State

### ✅ What's Working
- Dashboard UI with leaderboard
- Lap time charts
- Sample data generation
- Video background support
- Race schedule system
- Race monitor service

### 🔄 What Needs Live Data
- **Predictions** - Requires ML models trained on real data
- **Strategy** - Needs pit stop data
- **Anomalies** - Needs lap time variations

### 🔴 How to Get Predictions Working

**Option 1: Use Sample Data (Current)**
```bash
python generate_sample_data.py
```
- Generates ~500 laps of realistic data
- ML models can train on this
- Predictions will work but with sample data

**Option 2: Wait for Live Race**
- Next race: **6 Hours of Qatar** (Feb 28, 2025)
- System will auto-activate
- Real predictions from live data

**Option 3: Manual Training**
```python
# Train models manually with existing data
from backend.ml_models import LapTimePredictor
predictor = LapTimePredictor()
predictor.train(laps_dataframe)
predictor.save_model()
```

## 📁 Project Structure

```
Race/
├── backend/
│   ├── main.py              # FastAPI app & API endpoints
│   ├── database.py          # SQLAlchemy models
│   ├── ingest.py            # Web scraping
│   ├── race_monitor.py      # Auto race detection (NEW!)
│   ├── ml_models.py         # ML prediction models
│   ├── preprocess.py        # Data preprocessing
│   └── schedule.py          # Race calendar
├── frontend/
│   ├── index.html           # Dashboard UI
│   ├── styles.css           # Styling + animations
│   ├── app.js               # JavaScript logic
│   └── static/
│       └── racing-background.mp4  # Video background
├── generate_sample_data.py  # Sample data generator
├── start.bat                # Quick start script
└── requirements.txt         # Python dependencies
```

## 🚀 Quick Start Commands

```bash
# 1. Generate sample data
python generate_sample_data.py

# 2. Start server
python -m uvicorn backend.main:app --reload

# 3. Open dashboard
# http://localhost:8000/dashboard

# 4. Check API docs
# http://localhost:8000/docs

# 5. Check monitor status
curl http://localhost:8000/api/status/monitor
```

## 🔧 Troubleshooting

**Predictions not showing?**
- ML models need training data
- Run `generate_sample_data.py` first
- Check logs for ML training messages

**Video not playing?**
- Ensure `racing-background.mp4` is in `frontend/static/`
- Hard refresh browser (Ctrl+Shift+R)
- Check browser console for errors

**Server won't start?**
- Install dependencies: `pip install -r requirements.txt`
- Check if port 8000 is available
- Look for error messages in terminal

---

**The system is designed to be fully automatic once a race starts!** 🏁
