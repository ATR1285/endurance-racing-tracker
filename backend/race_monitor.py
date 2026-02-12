"""
Race Monitor Service - Automatically detects live races and starts data ingestion.
Runs as a background task and checks race schedule every 5 minutes.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from backend.database import SessionLocal, Race
from backend.schedule import get_next_race, is_race_live
from backend.ingest import DataIngestionManager

logger = logging.getLogger(__name__)


class RaceMonitor:
    """Monitors race schedule and auto-starts data ingestion when races go live"""
    
    def __init__(self):
        self.ingestion_manager: Optional[DataIngestionManager] = None
        self.current_race_name: Optional[str] = None
        self.is_running = False
        self.check_interval = 300  # 5 minutes
        
    async def start_monitoring(self):
        """Start the race monitoring background task"""
        self.is_running = True
        logger.info("Race monitor started - checking every 5 minutes")
        
        while self.is_running:
            try:
                await self.check_for_live_race()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in race monitor: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def check_for_live_race(self):
        """Check if any race is currently live and start/stop scraping accordingly"""
        next_race = get_next_race()
        
        if not next_race:
            logger.info("No upcoming races in schedule")
            await self.stop_ingestion()
            return
        
        # Check if race is live (within 30 minutes before to 12 hours after start)
        now = datetime.now(timezone.utc)
        race_time = next_race['date']
        time_diff = (now - race_time).total_seconds() / 60  # minutes
        
        # Race is live if: -30 min < time_diff < 720 min (12 hours)
        is_live = -30 <= time_diff <= 720
        
        if is_live:
            if not self.ingestion_manager or self.current_race_name != next_race['name']:
                logger.info(f"🔴 LIVE RACE DETECTED: {next_race['name']}")
                await self.start_ingestion(next_race)
            else:
                logger.debug(f"Race {next_race['name']} still live, scraping active")
        else:
            if self.ingestion_manager:
                logger.info(f"Race {self.current_race_name} ended, stopping scraping")
                await self.stop_ingestion()
            
            # Log time until next race
            if time_diff < -30:
                mins_until = abs(time_diff + 30)
                logger.info(f"Next race: {next_race['name']} in {mins_until:.0f} minutes")
    
    async def start_ingestion(self, race_info: dict):
        """Start data ingestion for a live race"""
        try:
            # Stop any existing ingestion
            await self.stop_ingestion()
            
            # Create or update race in database
            db = SessionLocal()
            try:
                # Deactivate all races
                db.query(Race).update({"is_active": False})
                
                # Create new race entry
                race = Race(
                    series=race_info['series'],
                    name=race_info['name'],
                    track=race_info['track'],
                    start_time=race_info['date'],
                    is_active=True
                )
                db.add(race)
                db.commit()
                logger.info(f"Created race entry in database: {race.name}")
            finally:
                db.close()
            
            # Start data ingestion
            self.ingestion_manager = DataIngestionManager(
                series=race_info['series'],
                timing_url=race_info.get('timing_url')
            )
            
            # Start ingestion in background
            asyncio.create_task(self.ingestion_manager.start_ingestion())
            
            self.current_race_name = race_info['name']
            logger.info(f"✅ Data ingestion started for {race_info['name']}")
            
        except Exception as e:
            logger.error(f"Failed to start ingestion: {e}")
    
    async def stop_ingestion(self):
        """Stop data ingestion and export race data to JSON"""
        if self.ingestion_manager:
            try:
                await self.ingestion_manager.stop_ingestion()
                
                # Export race data to JSON when race ends
                try:
                    from backend.export import race_exporter
                    from backend.database import SessionLocal, Race
                    
                    db = SessionLocal()
                    try:
                        # Get the active race
                        race = db.query(Race).filter(Race.is_active == True).first()
                        if race:
                            # Mark race as ended
                            race.is_active = False
                            race.end_time = datetime.now(timezone.utc)
                            db.commit()
                            
                            # Export to JSON
                            filepath = race_exporter.export_race_to_json(race.id, db)
                            logger.info(f"📦 Race data exported to: {filepath}")
                    finally:
                        db.close()
                        
                except Exception as e:
                    logger.error(f"Failed to export race data: {e}")
                
                self.ingestion_manager = None
                self.current_race_name = None
                logger.info("Data ingestion stopped")
            except Exception as e:
                logger.error(f"Error stopping ingestion: {e}")
    
    async def stop_monitoring(self):
        """Stop the race monitor"""
        self.is_running = False
        await self.stop_ingestion()
        logger.info("Race monitor stopped")
    
    def get_status(self) -> dict:
        """Get current monitoring status"""
        return {
            "is_monitoring": self.is_running,
            "is_scraping": self.ingestion_manager is not None,
            "current_race": self.current_race_name,
            "check_interval_seconds": self.check_interval
        }


# Global instance
race_monitor = RaceMonitor()
