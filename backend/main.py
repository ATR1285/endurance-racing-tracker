"""
FastAPI main application for endurance racing tracker.
Provides REST API endpoints for live data, predictions, and strategy.
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio
import logging
from datetime import datetime

from backend.database import get_db, init_db, Race, Car, Lap, PitStop, Prediction, Anomaly, Driver, Stint
from backend.models import (
    CarPosition, LapTimeData, PredictionData, StrategyRecommendation,
    AnomalyData, TelemetryData, LeaderboardEntry, DriverStintInfo,
    PitStopHistory, RaceInfo
)
from backend.ingest import DataIngestionManager
from backend.preprocess import RaceDataPreprocessor
from backend.ml_models import LapTimePredictor, AnomalyDetector, StrategyEngine
from backend.schedule import get_next_race, get_upcoming_races, is_race_live, get_time_until_race
from backend.race_monitor import race_monitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Endurance Racing Tracker API",
    description="Real-time endurance racing data with ML predictions and strategy",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
preprocessor = RaceDataPreprocessor()
lap_predictor = LapTimePredictor()
anomaly_detector = AnomalyDetector()
strategy_engine = StrategyEngine()
ingestion_manager = None

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    global ingestion_manager
    init_db()
    logger.info("Database initialized")
    
    # Try to load ML models
    try:
        lap_predictor.load_model()
        anomaly_detector.load_model()
        logger.info("ML models loaded")
    except Exception as e:
        logger.warning(f"Could not load ML models: {e}")
    
    # Start race monitor - automatically detects and starts scraping
    asyncio.create_task(race_monitor.start_monitoring())
    logger.info("Race monitor started - will auto-detect live races")


@app.on_event("shutdown")
async def shutdown_event():
    await race_monitor.stop_monitoring()
    logger.info("Race monitor stopped")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Endurance Racing Tracker API", "version": "1.0.0"}


@app.get("/api/schedule/next")
async def get_next_race_info():
    """Get next upcoming race with countdown"""
    race = get_next_race()
    if not race:
        return {"message": "No upcoming races scheduled"}
    
    return {
        "name": race['name'],
        "series": race['series'],
        "track": race['track'],
        "date": race['date'].isoformat(),
        "countdown": get_time_until_race(race),
        "is_live": is_race_live(race)
    }


@app.get("/api/schedule/upcoming")
async def get_upcoming_races_list(limit: int = 5):
    """Get list of upcoming races"""
    races = get_upcoming_races(limit)
    return [
        {
            "name": race['name'],
            "series": race['series'],
            "track": race['track'],
            "date": race['date'].isoformat(),
            "countdown": get_time_until_race(race),
            "is_live": is_race_live(race)
        }
        for race in races
    ]


@app.get("/api/status/monitor")
async def get_monitor_status():
    """Get race monitor and scraping status"""
    status = race_monitor.get_status()
    next_race = get_next_race()
    
    return {
        "monitor_active": status['is_monitoring'],
        "scraping_active": status['is_scraping'],
        "current_race": status['current_race'],
        "next_race": next_race['name'] if next_race else None,
        "next_race_countdown": get_time_until_race(next_race) if next_race else None
    }


@app.get("/api/race/info", response_model=Optional[RaceInfo])
async def get_race_info(db: Session = Depends(get_db)):
    """Get current active race information"""
    race = db.query(Race).filter(Race.is_active == True).first()
    
    if not race:
        return None
    
    cars = db.query(Car).filter(Car.race_id == race.id).all()
    classes = list(set([car.car_class for car in cars if car.car_class]))
    
    elapsed = (datetime.utcnow() - race.start_time).total_seconds() / 60 if race.start_time else 0
    
    return RaceInfo(
        series=race.series,
        name=race.name,
        track=race.track,
        start_time=race.start_time,
        elapsed_time=elapsed,
        is_active=race.is_active,
        total_cars=len(cars),
        classes=classes
    )


@app.get("/api/positions", response_model=List[CarPosition])
async def get_positions(car_class: Optional[str] = None, db: Session = Depends(get_db)):
    """Get current car positions"""
    race = db.query(Race).filter(Race.is_active == True).first()
    
    if not race:
        return []
    
    query = db.query(Car).filter(Car.race_id == race.id)
    
    if car_class:
        query = query.filter(Car.car_class == car_class)
    
    cars = query.order_by(Car.current_position).all()
    
    result = []
    for car in cars:
        # Get current driver
        current_stint = db.query(Stint).filter(
            Stint.car_id == car.id,
            Stint.is_current == True
        ).first()
        
        current_driver = None
        if current_stint:
            driver = db.query(Driver).filter(Driver.id == current_stint.driver_id).first()
            if driver:
                current_driver = driver.name
        
        result.append(CarPosition(
            car_number=car.car_number,
            team_name=car.team_name,
            car_class=car.car_class,
            position=car.current_position or 0,
            position_in_class=car.current_position_in_class or 0,
            laps_completed=car.laps_completed or 0,
            gap_to_leader=car.gap_to_leader,
            gap_to_class_leader=car.gap_to_class_leader,
            last_lap_time=car.last_lap_time,
            best_lap_time=car.best_lap_time,
            in_pit=car.in_pit,
            current_driver=current_driver
        ))
    
    return result


@app.get("/api/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(car_class: Optional[str] = None, db: Session = Depends(get_db)):
    """Get race leaderboard"""
    race = db.query(Race).filter(Race.is_active == True).first()
    
    if not race:
        return []
    
    query = db.query(Car).filter(Car.race_id == race.id)
    
    if car_class:
        query = query.filter(Car.car_class == car_class)
    
    cars = query.order_by(Car.current_position).all()
    
    result = []
    for car in cars:
        # Get current driver
        current_stint = db.query(Stint).filter(
            Stint.car_id == car.id,
            Stint.is_current == True
        ).first()
        
        current_driver = None
        if current_stint:
            driver = db.query(Driver).filter(Driver.id == current_stint.driver_id).first()
            if driver:
                current_driver = driver.name
        
        # Format gaps
        gap_leader = f"+{car.gap_to_leader:.1f}s" if car.gap_to_leader else "Leader"
        gap_class = f"+{car.gap_to_class_leader:.1f}s" if car.gap_to_class_leader else "Leader"
        
        result.append(LeaderboardEntry(
            position=car.current_position or 0,
            position_in_class=car.current_position_in_class or 0,
            car_number=car.car_number,
            team_name=car.team_name,
            car_class=car.car_class,
            manufacturer=car.manufacturer or "",
            laps_completed=car.laps_completed or 0,
            gap_to_leader=gap_leader,
            gap_to_class_leader=gap_class,
            last_lap_time=car.last_lap_time,
            best_lap_time=car.best_lap_time,
            current_driver=current_driver,
            in_pit=car.in_pit
        ))
    
    return result


@app.get("/api/lap_times/{car_number}", response_model=List[LapTimeData])
async def get_lap_times(car_number: str, limit: int = 50, db: Session = Depends(get_db)):
    """Get lap times for a specific car"""
    race = db.query(Race).filter(Race.is_active == True).first()
    
    if not race:
        return []
    
    car = db.query(Car).filter(
        Car.race_id == race.id,
        Car.car_number == car_number
    ).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    laps = db.query(Lap).filter(
        Lap.car_id == car.id
    ).order_by(Lap.lap_number.desc()).limit(limit).all()
    
    return [
        LapTimeData(
            car_number=car_number,
            lap_number=lap.lap_number,
            lap_time=lap.lap_time,
            sector1_time=lap.sector1_time,
            sector2_time=lap.sector2_time,
            sector3_time=lap.sector3_time,
            is_pit_lap=lap.is_pit_lap,
            tire_age=lap.tire_age,
            timestamp=lap.timestamp
        )
        for lap in reversed(laps)
    ]


@app.get("/api/predictions/{car_number}", response_model=Optional[PredictionData])
async def get_prediction(car_number: str, db: Session = Depends(get_db)):
    """Get lap time prediction for a car"""
    race = db.query(Race).filter(Race.is_active == True).first()
    
    if not race:
        return None
    
    car = db.query(Car).filter(
        Car.race_id == race.id,
        Car.car_number == car_number
    ).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Get recent laps for feature preparation
    laps = db.query(Lap).filter(Lap.car_id == car.id).all()
    
    if len(laps) < 5:
        return None
    
    import pandas as pd
    laps_df = pd.DataFrame([{
        'car_id': lap.car_id,
        'lap_number': lap.lap_number,
        'lap_time': lap.lap_time,
        'sector1_time': lap.sector1_time,
        'sector2_time': lap.sector2_time,
        'sector3_time': lap.sector3_time,
        'tire_age': lap.tire_age,
        'timestamp': lap.timestamp
    } for lap in laps])
    
    # Prepare features
    current_lap = car.laps_completed
    features = preprocessor.prepare_ml_features(laps_df, current_lap, car.id)
    
    if not features:
        return None
    
    # Predict
    predicted_time, confidence = lap_predictor.predict(features)
    
    delta = None
    if car.last_lap_time:
        delta = predicted_time - car.last_lap_time
    
    return PredictionData(
        car_number=car_number,
        predicted_lap_time=predicted_time,
        confidence=confidence,
        current_lap_time=car.last_lap_time,
        delta=delta
    )


@app.get("/api/strategy/{car_number}", response_model=Optional[StrategyRecommendation])
async def get_strategy(car_number: str, db: Session = Depends(get_db)):
    """Get pit strategy recommendation for a car"""
    race = db.query(Race).filter(Race.is_active == True).first()
    
    if not race:
        return None
    
    car = db.query(Car).filter(
        Car.race_id == race.id,
        Car.car_number == car_number
    ).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Get last pit stop to estimate fuel remaining
    last_pit = db.query(PitStop).filter(
        PitStop.car_id == car.id
    ).order_by(PitStop.lap_number.desc()).first()
    
    laps_since_pit = car.laps_completed - (last_pit.lap_number if last_pit else 0)
    
    # Estimate fuel remaining (assume 80L tank, 2.5L/lap consumption)
    fuel_rate = 2.5
    fuel_remaining = 80 - (laps_since_pit * fuel_rate)
    
    # Get tire age
    tire_age = laps_since_pit
    
    # Calculate gaps (simplified)
    gap_ahead = 5.0
    gap_behind = 5.0
    
    # Estimate race laps remaining (assume 6 hour race, 90s laps = 240 laps total)
    race_laps_remaining = max(0, 240 - car.laps_completed)
    
    # Get strategy recommendation
    strategy = strategy_engine.recommend_pit_stop(
        car_id=car.id,
        current_lap=car.laps_completed,
        fuel_remaining=fuel_remaining,
        tire_age=tire_age,
        gap_to_ahead=gap_ahead,
        gap_to_behind=gap_behind,
        race_laps_remaining=race_laps_remaining
    )
    
    if strategy['recommended_pit_lap'] is None:
        return None
    
    return StrategyRecommendation(
        car_number=car_number,
        recommended_pit_lap=strategy['recommended_pit_lap'],
        laps_until_pit=strategy['laps_until_pit'],
        fuel_remaining=strategy['fuel_remaining_laps'],
        tire_degradation=strategy['tire_degradation'],
        optimal_tire_change=strategy['optimal_tire_change'],
        optimal_fuel_load=strategy['optimal_fuel_load'],
        estimated_pit_duration=strategy['estimated_pit_duration'],
        reasoning=strategy['reasoning']
    )


@app.get("/api/anomalies", response_model=List[AnomalyData])
async def get_anomalies(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent anomalies"""
    race = db.query(Race).filter(Race.is_active == True).first()
    
    if not race:
        return []
    
    anomalies = db.query(Anomaly).join(Car).filter(
        Car.race_id == race.id
    ).order_by(Anomaly.timestamp.desc()).limit(limit).all()
    
    result = []
    for anomaly in anomalies:
        car = db.query(Car).filter(Car.id == anomaly.car_id).first()
        if car:
            result.append(AnomalyData(
                car_number=car.car_number,
                lap_number=anomaly.lap_number,
                anomaly_type=anomaly.anomaly_type,
                severity=anomaly.severity,
                description=anomaly.description,
                timestamp=anomaly.timestamp
            ))
    
    return result


@app.get("/api/drivers/{car_number}", response_model=Optional[DriverStintInfo])
async def get_driver_info(car_number: str, db: Session = Depends(get_db)):
    """Get current driver stint information"""
    race = db.query(Race).filter(Race.is_active == True).first()
    
    if not race:
        return None
    
    car = db.query(Car).filter(
        Car.race_id == race.id,
        Car.car_number == car_number
    ).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    current_stint = db.query(Stint).filter(
        Stint.car_id == car.id,
        Stint.is_current == True
    ).first()
    
    if not current_stint:
        return None
    
    driver = db.query(Driver).filter(Driver.id == current_stint.driver_id).first()
    
    if not driver:
        return None
    
    laps_in_stint = car.laps_completed - current_stint.start_lap
    stint_duration = (datetime.utcnow() - current_stint.start_time).total_seconds() / 60
    
    # Calculate average lap time in stint
    stint_laps = db.query(Lap).filter(
        Lap.car_id == car.id,
        Lap.lap_number >= current_stint.start_lap
    ).all()
    
    avg_lap = sum([lap.lap_time for lap in stint_laps]) / len(stint_laps) if stint_laps else 0
    
    return DriverStintInfo(
        car_number=car_number,
        current_driver=driver.name,
        stint_start_lap=current_stint.start_lap,
        laps_in_stint=laps_in_stint,
        stint_duration=stint_duration,
        average_lap_time=avg_lap
    )


@app.get("/api/pit_history/{car_number}", response_model=List[PitStopHistory])
async def get_pit_history(car_number: str, db: Session = Depends(get_db)):
    """Get pit stop history for a car"""
    race = db.query(Race).filter(Race.is_active == True).first()
    
    if not race:
        return []
    
    car = db.query(Car).filter(
        Car.race_id == race.id,
        Car.car_number == car_number
    ).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    pit_stops = db.query(PitStop).filter(
        PitStop.car_id == car.id
    ).order_by(PitStop.lap_number).all()
    
    return [
        PitStopHistory(
            car_number=car_number,
            lap_number=pit.lap_number,
            duration=pit.duration or 0,
            stop_type=pit.stop_type,
            timestamp=pit.timestamp
        )
        for pit in pit_stops
    ]


@app.get("/api/export/race/{race_id}")
async def export_race(race_id: int, db: Session = Depends(get_db)):
    """Export specific race data to JSON"""
    try:
        from backend.export import race_exporter
        filepath = race_exporter.export_race_to_json(race_id, db)
        return {"success": True, "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/active")
async def export_active_race(db: Session = Depends(get_db)):
    """Export currently active race data to JSON"""
    try:
        from backend.export import race_exporter
        race = db.query(Race).filter(Race.is_active == True).first()
        if not race:
            raise HTTPException(status_code=404, detail="No active race found")
        filepath = race_exporter.export_race_to_json(race.id, db)
        return {"success": True, "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve frontend static files (including video)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/dashboard")
async def serve_dashboard():
    """Serve the frontend dashboard"""
    return FileResponse("frontend/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
