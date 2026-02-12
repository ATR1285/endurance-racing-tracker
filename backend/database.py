"""
Database models and configuration for the endurance racing tracker.
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/racing.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Race(Base):
    """Race session information"""
    __tablename__ = "races"
    
    id = Column(Integer, primary_key=True, index=True)
    series = Column(String, index=True)  # WEC, IMSA, FMSCI
    name = Column(String)
    track = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cars = relationship("Car", back_populates="race")
    laps = relationship("Lap", back_populates="race")


class Car(Base):
    """Car/Entry information"""
    __tablename__ = "cars"
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.id"))
    car_number = Column(String, index=True)
    team_name = Column(String)
    car_class = Column(String, index=True)  # Hypercar, LMP2, LMGT3, etc.
    manufacturer = Column(String)
    current_position = Column(Integer)
    current_position_in_class = Column(Integer)
    laps_completed = Column(Integer, default=0)
    gap_to_leader = Column(Float, nullable=True)  # seconds
    gap_to_class_leader = Column(Float, nullable=True)
    last_lap_time = Column(Float, nullable=True)
    best_lap_time = Column(Float, nullable=True)
    in_pit = Column(Boolean, default=False)
    
    # Relationships
    race = relationship("Race", back_populates="cars")
    laps = relationship("Lap", back_populates="car")
    stints = relationship("Stint", back_populates="car")


class Driver(Base):
    """Driver information"""
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    nationality = Column(String)
    
    # Relationships
    stints = relationship("Stint", back_populates="driver")


class Stint(Base):
    """Driver stint tracking"""
    __tablename__ = "stints"
    
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    start_lap = Column(Integer)
    end_lap = Column(Integer, nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    is_current = Column(Boolean, default=True)
    
    # Relationships
    car = relationship("Car", back_populates="stints")
    driver = relationship("Driver", back_populates="stints")


class Lap(Base):
    """Individual lap data"""
    __tablename__ = "laps"
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.id"))
    car_id = Column(Integer, ForeignKey("cars.id"))
    lap_number = Column(Integer)
    lap_time = Column(Float)  # seconds
    sector1_time = Column(Float, nullable=True)
    sector2_time = Column(Float, nullable=True)
    sector3_time = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_pit_lap = Column(Boolean, default=False)
    is_outlap = Column(Boolean, default=False)
    tire_age = Column(Integer, nullable=True)  # laps on current tires
    
    # Relationships
    race = relationship("Race", back_populates="laps")
    car = relationship("Car", back_populates="laps")


class PitStop(Base):
    """Pit stop events"""
    __tablename__ = "pit_stops"
    
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    lap_number = Column(Integer)
    pit_in_time = Column(DateTime)
    pit_out_time = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)  # seconds
    stop_type = Column(String)  # fuel, tires, driver_change, repair
    timestamp = Column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    """ML predictions for lap times"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    predicted_lap_time = Column(Float)
    confidence = Column(Float)
    features_used = Column(String)  # JSON string of features
    timestamp = Column(DateTime, default=datetime.utcnow)


class Anomaly(Base):
    """Detected anomalies/mistakes"""
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    lap_number = Column(Integer)
    anomaly_type = Column(String)  # slow_lap, off_track, incident, mechanical
    severity = Column(Float)  # 0-1 score
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
