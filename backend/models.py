"""
Pydantic models for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CarPosition(BaseModel):
    """Current car position data"""
    car_number: str
    team_name: str
    car_class: str
    position: int
    position_in_class: int
    laps_completed: int
    gap_to_leader: Optional[float] = None
    gap_to_class_leader: Optional[float] = None
    last_lap_time: Optional[float] = None
    best_lap_time: Optional[float] = None
    in_pit: bool = False
    current_driver: Optional[str] = None


class LapTimeData(BaseModel):
    """Lap time information"""
    car_number: str
    lap_number: int
    lap_time: float
    sector1_time: Optional[float] = None
    sector2_time: Optional[float] = None
    sector3_time: Optional[float] = None
    is_pit_lap: bool = False
    tire_age: Optional[int] = None
    timestamp: datetime


class PredictionData(BaseModel):
    """Lap time prediction"""
    car_number: str
    predicted_lap_time: float
    confidence: float
    current_lap_time: Optional[float] = None
    delta: Optional[float] = None


class StrategyRecommendation(BaseModel):
    """Pit strategy recommendation"""
    car_number: str
    recommended_pit_lap: int
    laps_until_pit: int
    fuel_remaining: float  # laps worth
    tire_degradation: float  # seconds lost per lap
    optimal_tire_change: bool
    optimal_fuel_load: float  # liters
    estimated_pit_duration: float  # seconds
    reasoning: str


class AnomalyData(BaseModel):
    """Detected anomaly"""
    car_number: str
    lap_number: int
    anomaly_type: str
    severity: float
    description: str
    timestamp: datetime


class TelemetryData(BaseModel):
    """Real-time telemetry"""
    car_number: str
    speed: Optional[float] = None
    sector1_time: Optional[float] = None
    sector2_time: Optional[float] = None
    sector3_time: Optional[float] = None
    current_sector: Optional[int] = None
    timestamp: datetime


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    position: int
    position_in_class: int
    car_number: str
    team_name: str
    car_class: str
    manufacturer: str
    laps_completed: int
    gap_to_leader: Optional[str] = None  # formatted string
    gap_to_class_leader: Optional[str] = None
    last_lap_time: Optional[float] = None
    best_lap_time: Optional[float] = None
    current_driver: Optional[str] = None
    in_pit: bool = False


class DriverStintInfo(BaseModel):
    """Driver stint information"""
    car_number: str
    current_driver: str
    stint_start_lap: int
    laps_in_stint: int
    stint_duration: float  # minutes
    average_lap_time: float


class PitStopHistory(BaseModel):
    """Pit stop history"""
    car_number: str
    lap_number: int
    duration: float
    stop_type: str
    timestamp: datetime


class RaceInfo(BaseModel):
    """Race session information"""
    series: str
    name: str
    track: str
    start_time: datetime
    elapsed_time: float  # minutes
    is_active: bool
    total_cars: int
    classes: List[str]
