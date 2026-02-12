# Endurance Racing Tracker 🏁

A comprehensive real-time endurance racing tracker with machine learning predictions, pit strategy recommendations, and an interactive web dashboard. Supports WEC, IMSA, and other endurance racing series.

![Dashboard Preview](https://img.shields.io/badge/Status-Live-success)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)

## Features

### 🔴 Real-Time Data
- Live timing data scraping from WEC (Al Kamel) and IMSA timing pages
- Multi-class racing support (Hypercar, LMP2, LMGT3, DPi, GTD)
- Driver stint tracking and pit stop detection
- 5-second update intervals

### 🤖 Machine Learning
- **Lap Time Prediction**: Random Forest model predicts next lap times
- **Anomaly Detection**: Isolation Forest detects incidents and performance drops
- **Strategy Engine**: Advanced pit strategy with fuel/tire modeling

### 📊 Interactive Dashboard
- Live leaderboard with class filtering
- Lap time analysis charts
- Real-time telemetry widgets
- Pit strategy recommendations
- Incident detection and alerts

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone or navigate to the project
cd Race

# Build and run with Docker Compose
docker-compose up -d

# Access the dashboard
# Open http://localhost:8000/dashboard in your browser
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from backend.database import init_db; init_db()"

# Run the server
uvicorn backend.main:app --reload

# Access the dashboard
# Open http://localhost:8000/dashboard in your browser
```

## Project Structure

```
Race/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # SQLAlchemy models
│   ├── models.py            # Pydantic schemas
│   ├── ingest.py            # Web scraping (WEC/IMSA)
│   ├── preprocess.py        # Data preprocessing
│   └── ml_models.py         # ML models
├── frontend/
│   ├── index.html           # Dashboard UI
│   ├── styles.css           # Modern styling
│   └── app.js               # Real-time updates
├── data/                    # SQLite database
├── models/                  # Trained ML models
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Race Information
- `GET /api/race/info` - Current race session info
- `GET /api/positions` - Live car positions
- `GET /api/leaderboard` - Race leaderboard (filterable by class)

### Lap Data
- `GET /api/lap_times/{car_number}` - Lap times for a car
- `GET /api/predictions/{car_number}` - Lap time prediction
- `GET /api/telemetry/{car_number}` - Real-time telemetry

### Strategy & Analysis
- `GET /api/strategy/{car_number}` - Pit strategy recommendation
- `GET /api/anomalies` - Recent incidents and anomalies
- `GET /api/drivers/{car_number}` - Current driver info
- `GET /api/pit_history/{car_number}` - Pit stop history

## Configuration

Edit `.env` file to configure:

```env
# Database
DATABASE_URL=sqlite:///./data/racing.db

# Scraping
SCRAPE_INTERVAL=10
WEC_TIMING_URL=https://timing.71wytham.org.uk/
IMSA_TIMING_URL=https://www.imsa.com/scoring/

# ML Models
MODEL_RETRAIN_INTERVAL=3600
PREDICTION_CONFIDENCE_THRESHOLD=0.7
```

## Data Sources

### WEC (World Endurance Championship)
- Uses Al Kamel Systems live timing
- BeautifulSoup for HTML parsing
- Supports Hypercar, LMP2, LMGT3 classes

### IMSA (International Motor Sports Association)
- Uses IMSA official timing page
- Selenium for dynamic content
- Supports DPi, LMP2, LMP3, GTD classes

## Machine Learning Models

### Lap Time Predictor
- **Algorithm**: Random Forest Regressor
- **Features**: Last lap time, sector times, tire age, fuel load, stint length, time of day
- **Accuracy**: MAE < 0.5 seconds (after training)

### Anomaly Detector
- **Algorithm**: Isolation Forest
- **Features**: Lap time, sector times
- **Detection**: Incidents, slow zones, mechanical issues

### Strategy Engine
- **Fuel modeling**: Consumption rate per lap
- **Tire degradation**: Performance curves over stint
- **Pit window optimization**: Traffic-aware recommendations

## Development

### Training ML Models

```python
from backend.ml_models import LapTimePredictor, AnomalyDetector
import pandas as pd

# Load historical race data
data = pd.read_csv('data/historical_laps.csv')

# Train lap time predictor
predictor = LapTimePredictor()
predictor.train(data)

# Train anomaly detector
detector = AnomalyDetector()
detector.train(data)
```

### Adding New Series

1. Create a new scraper class in `backend/ingest.py`
2. Implement `fetch_live_data()` method
3. Parse HTML/JSON to extract positions, lap times, etc.
4. Update `DataIngestionManager` to support the new series

## Troubleshooting

### Web Scraping Issues
- **Problem**: Scraper returns empty data
- **Solution**: Check if timing website structure changed. Update CSS selectors in `ingest.py`

### Database Errors
- **Problem**: Database locked
- **Solution**: Ensure only one instance is running. Delete `data/racing.db` to reset.

### Chrome/Selenium Errors
- **Problem**: Chrome driver not found
- **Solution**: `webdriver-manager` auto-downloads. Check internet connection.

## Contributing

Contributions welcome! Areas for improvement:
- Additional series support (Le Mans Cup, Asian Le Mans, etc.)
- LSTM models for time-series prediction
- Track map visualization with GPS data
- Weather integration for strategy
- Historical race replay mode

## License

MIT License - feel free to use and modify for your projects.

## Acknowledgments

- Al Kamel Systems for WEC timing data
- IMSA for official timing feeds
- FastAPI and Chart.js communities

---

**Note**: This tracker is for educational and personal use. Respect timing website terms of service and implement rate limiting when scraping.
