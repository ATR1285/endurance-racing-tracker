"""
Sample data generator for testing the endurance racing tracker.
Creates mock race data to test the application without live scraping.
"""
from backend.database import init_db, SessionLocal, Race, Car, Lap, Driver, Stint, PitStop
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Generate sample race data for testing"""
    init_db()
    db = SessionLocal()
    
    try:
        # Create a sample race
        race = Race(
            series="WEC",
            name="6 Hours of Bahrain",
            track="Bahrain International Circuit",
            start_time=datetime.utcnow() - timedelta(hours=2),
            is_active=True
        )
        db.add(race)
        db.commit()
        
        # Sample teams and classes
        teams = [
            {"number": "7", "team": "Toyota Gazoo Racing", "class": "Hypercar", "manufacturer": "Toyota"},
            {"number": "8", "team": "Toyota Gazoo Racing", "class": "Hypercar", "manufacturer": "Toyota"},
            {"number": "50", "team": "Ferrari AF Corse", "class": "Hypercar", "manufacturer": "Ferrari"},
            {"number": "51", "team": "Ferrari AF Corse", "class": "Hypercar", "manufacturer": "Ferrari"},
            {"number": "38", "team": "Hertz JOTA", "class": "LMP2", "manufacturer": "Porsche"},
            {"number": "23", "team": "United Autosports", "class": "LMP2", "manufacturer": "Oreca"},
            {"number": "31", "team": "Team WRT", "class": "LMP2", "manufacturer": "Oreca"},
            {"number": "51", "team": "AF Corse", "class": "LMGT3", "manufacturer": "Ferrari"},
            {"number": "85", "team": "Iron Dames", "class": "LMGT3", "manufacturer": "Lamborghini"},
            {"number": "92", "team": "Manthey EMA", "class": "LMGT3", "manufacturer": "Porsche"},
        ]
        
        # Create cars
        cars = []
        for i, team_data in enumerate(teams):
            car = Car(
                race_id=race.id,
                car_number=team_data["number"],
                team_name=team_data["team"],
                car_class=team_data["class"],
                manufacturer=team_data["manufacturer"],
                current_position=i + 1,
                current_position_in_class=1,  # Simplified
                laps_completed=0,
                gap_to_leader=0.0 if i == 0 else random.uniform(5, 60),
                gap_to_class_leader=0.0,
                last_lap_time=None,
                best_lap_time=None,
                in_pit=False
            )
            db.add(car)
            cars.append(car)
        
        db.commit()
        
        # Create sample drivers
        driver_names = [
            "Mike Conway", "Kamui Kobayashi", "Antonio Giovinazzi",
            "Alessandro Pier Guidi", "James Calado", "Robert Kubica",
            "Phil Hanson", "Oliver Rasmussen", "Alex Lynn"
        ]
        
        drivers = []
        for name in driver_names:
            driver = Driver(name=name, nationality="Various")
            db.add(driver)
            drivers.append(driver)
        
        db.commit()
        
        # Create current stints
        for i, car in enumerate(cars):
            stint = Stint(
                car_id=car.id,
                driver_id=drivers[i % len(drivers)].id,
                start_lap=1,
                start_time=race.start_time,
                is_current=True
            )
            db.add(stint)
        
        db.commit()
        
        # Generate lap times
        base_lap_times = {
            "Hypercar": 95.0,  # ~1:35
            "LMP2": 100.0,     # ~1:40
            "LMGT3": 110.0     # ~1:50
        }
        
        for car in cars:
            base_time = base_lap_times[car.car_class]
            car_offset = random.uniform(-2, 2)  # Car-specific pace
            
            # Generate 50 laps
            for lap_num in range(1, 51):
                # Add variation
                variation = random.uniform(-0.5, 0.5)
                tire_deg = (lap_num % 30) * 0.02  # Tire degradation
                
                lap_time = base_time + car_offset + variation + tire_deg
                
                # Pit lap every 30 laps
                is_pit = (lap_num % 30 == 0)
                if is_pit:
                    lap_time += 60  # Add pit time
                
                lap = Lap(
                    race_id=race.id,
                    car_id=car.id,
                    lap_number=lap_num,
                    lap_time=lap_time,
                    sector1_time=lap_time * 0.33,
                    sector2_time=lap_time * 0.33,
                    sector3_time=lap_time * 0.34,
                    timestamp=race.start_time + timedelta(seconds=lap_time * lap_num),
                    is_pit_lap=is_pit,
                    tire_age=lap_num % 30
                )
                db.add(lap)
                
                # Add pit stop
                if is_pit:
                    pit_stop = PitStop(
                        car_id=car.id,
                        lap_number=lap_num,
                        pit_in_time=lap.timestamp,
                        pit_out_time=lap.timestamp + timedelta(seconds=60),
                        duration=60.0,
                        stop_type="tires" if lap_num % 60 == 0 else "fuel_only",
                        timestamp=lap.timestamp
                    )
                    db.add(pit_stop)
            
            # Update car stats
            car_laps = db.query(Lap).filter(
                Lap.car_id == car.id,
                Lap.is_pit_lap == False
            ).all()
            
            if car_laps:
                car.laps_completed = 50
                car.last_lap_time = car_laps[-1].lap_time
                car.best_lap_time = min([lap.lap_time for lap in car_laps])
        
        db.commit()
        
        print("Sample data generated successfully!")
        print(f"   - Created 1 race")
        print(f"   - Created {len(cars)} cars")
        print(f"   - Created {len(drivers)} drivers")
        print(f"   - Generated ~{len(cars) * 50} laps")
        print("\nYou can now run the server and view the dashboard!")
        
    except Exception as e:
        print(f"Error generating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_sample_data()
