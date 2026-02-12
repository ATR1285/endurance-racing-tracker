"""
Race Data Export Module - Exports completed race data to JSON
"""
import json
import os
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session

from backend.database import Race, Car, Driver, Lap, PitStop, SessionLocal
import logging

logger = logging.getLogger(__name__)


class RaceDataExporter:
    """Exports race data to JSON format"""
    
    def __init__(self, export_dir: str = "race_exports"):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
    
    def export_race_to_json(self, race_id: int, db: Session = None) -> str:
        """
        Export complete race data to JSON file
        
        Args:
            race_id: ID of the race to export
            db: Database session (optional)
            
        Returns:
            Path to exported JSON file
        """
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            race = db.query(Race).filter(Race.id == race_id).first()
            if not race:
                raise ValueError(f"Race {race_id} not found")
            
            # Build complete race data structure
            race_data = {
                "race_info": {
                    "id": race.id,
                    "series": race.series,
                    "name": race.name,
                    "track": race.track,
                    "start_time": race.start_time.isoformat() if race.start_time else None,
                    "end_time": race.end_time.isoformat() if race.end_time else None,
                    "is_active": race.is_active,
                    "exported_at": datetime.utcnow().isoformat()
                },
                "cars": [],
                "laps": [],
                "pit_stops": [],
                "statistics": {}
            }
            
            # Get all cars in this race
            cars = db.query(Car).filter(Car.race_id == race_id).all()
            
            for car in cars:
                # Car data
                car_data = {
                    "car_number": car.car_number,
                    "team": car.team,
                    "class": car.car_class,
                    "manufacturer": car.manufacturer,
                    "drivers": []
                }
                
                # Get drivers for this car
                if car.drivers:
                    for driver in car.drivers:
                        car_data["drivers"].append({
                            "name": driver.name,
                            "nationality": driver.nationality
                        })
                
                race_data["cars"].append(car_data)
                
                # Get all laps for this car
                laps = db.query(Lap).filter(
                    Lap.race_id == race_id,
                    Lap.car_number == car.car_number
                ).order_by(Lap.lap_number).all()
                
                for lap in laps:
                    lap_data = {
                        "car_number": lap.car_number,
                        "lap_number": lap.lap_number,
                        "lap_time": lap.lap_time,
                        "sector1_time": lap.sector1_time,
                        "sector2_time": lap.sector2_time,
                        "sector3_time": lap.sector3_time,
                        "position": lap.position,
                        "gap_to_leader": lap.gap_to_leader,
                        "tire_age": lap.tire_age,
                        "fuel_remaining": lap.fuel_remaining,
                        "is_pit_lap": lap.is_pit_lap,
                        "timestamp": lap.timestamp.isoformat() if lap.timestamp else None
                    }
                    race_data["laps"].append(lap_data)
                
                # Get pit stops for this car
                pit_stops = db.query(PitStop).filter(
                    PitStop.race_id == race_id,
                    PitStop.car_number == car.car_number
                ).order_by(PitStop.lap_number).all()
                
                for pit in pit_stops:
                    pit_data = {
                        "car_number": pit.car_number,
                        "lap_number": pit.lap_number,
                        "duration": pit.duration,
                        "stop_type": pit.stop_type,
                        "timestamp": pit.timestamp.isoformat() if pit.timestamp else None
                    }
                    race_data["pit_stops"].append(pit_data)
            
            # Calculate statistics
            race_data["statistics"] = self._calculate_statistics(race_data)
            
            # Generate filename
            race_name_safe = race.name.replace(" ", "_").replace("/", "-")
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{race_name_safe}_{timestamp}.json"
            filepath = os.path.join(self.export_dir, filename)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(race_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Race data exported to {filepath}")
            return filepath
            
        finally:
            if should_close:
                db.close()
    
    def _calculate_statistics(self, race_data: Dict) -> Dict:
        """Calculate race statistics"""
        stats = {
            "total_cars": len(race_data["cars"]),
            "total_laps": len(race_data["laps"]),
            "total_pit_stops": len(race_data["pit_stops"]),
            "fastest_lap": None,
            "most_pit_stops": None
        }
        
        # Find fastest lap
        if race_data["laps"]:
            fastest = min(
                (lap for lap in race_data["laps"] if lap["lap_time"] and not lap["is_pit_lap"]),
                key=lambda x: x["lap_time"],
                default=None
            )
            if fastest:
                stats["fastest_lap"] = {
                    "car_number": fastest["car_number"],
                    "lap_number": fastest["lap_number"],
                    "time": fastest["lap_time"]
                }
        
        # Count pit stops per car
        pit_counts = {}
        for pit in race_data["pit_stops"]:
            car = pit["car_number"]
            pit_counts[car] = pit_counts.get(car, 0) + 1
        
        if pit_counts:
            most_pits_car = max(pit_counts, key=pit_counts.get)
            stats["most_pit_stops"] = {
                "car_number": most_pits_car,
                "count": pit_counts[most_pits_car]
            }
        
        return stats


# Global exporter instance
race_exporter = RaceDataExporter()
