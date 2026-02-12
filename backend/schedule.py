"""
Race schedule and timing information.
Shows upcoming WEC and IMSA races with countdown timers.
"""
from datetime import datetime, timezone
from typing import List, Dict, Optional

# 2024-2025 WEC Season Schedule
WEC_SCHEDULE = [
    {
        "name": "6 Hours of Qatar",
        "track": "Losail International Circuit",
        "date": datetime(2025, 2, 28, 14, 0, tzinfo=timezone.utc),
        "series": "WEC",
        "timing_url": "https://timing.71wytham.org.uk/"
    },
    {
        "name": "1000 Miles of Sebring",
        "track": "Sebring International Raceway",
        "date": datetime(2025, 3, 14, 17, 0, tzinfo=timezone.utc),
        "series": "WEC",
        "timing_url": "https://timing.71wytham.org.uk/"
    },
    {
        "name": "6 Hours of Imola",
        "track": "Autodromo Enzo e Dino Ferrari",
        "date": datetime(2025, 4, 20, 12, 0, tzinfo=timezone.utc),
        "series": "WEC",
        "timing_url": "https://timing.71wytham.org.uk/"
    },
    {
        "name": "6 Hours of Spa-Francorchamps",
        "track": "Circuit de Spa-Francorchamps",
        "date": datetime(2025, 5, 10, 13, 0, tzinfo=timezone.utc),
        "series": "WEC",
        "timing_url": "https://timing.71wytham.org.uk/"
    },
    {
        "name": "24 Hours of Le Mans",
        "track": "Circuit de la Sarthe",
        "date": datetime(2025, 6, 14, 15, 0, tzinfo=timezone.utc),
        "series": "WEC",
        "timing_url": "https://timing.71wytham.org.uk/"
    }
]

# IMSA Schedule
IMSA_SCHEDULE = [
    {
        "name": "12 Hours of Sebring",
        "track": "Sebring International Raceway",
        "date": datetime(2025, 3, 15, 15, 40, tzinfo=timezone.utc),
        "series": "IMSA",
        "timing_url": "https://www.imsa.com/scoring/"
    },
    {
        "name": "Grand Prix of Long Beach",
        "track": "Long Beach Street Circuit",
        "date": datetime(2025, 4, 13, 20, 10, tzinfo=timezone.utc),
        "series": "IMSA",
        "timing_url": "https://www.imsa.com/scoring/"
    },
    {
        "name": "Laguna Seca",
        "track": "WeatherTech Raceway Laguna Seca",
        "date": datetime(2025, 5, 4, 20, 10, tzinfo=timezone.utc),
        "series": "IMSA",
        "timing_url": "https://www.imsa.com/scoring/"
    }
]

def get_next_race() -> Optional[Dict]:
    """Get the next upcoming race from all series"""
    all_races = WEC_SCHEDULE + IMSA_SCHEDULE
    now = datetime.now(timezone.utc)
    
    upcoming = [race for race in all_races if race['date'] > now]
    
    if not upcoming:
        return None
    
    return min(upcoming, key=lambda x: x['date'])

def get_upcoming_races(limit: int = 5) -> List[Dict]:
    """Get list of upcoming races"""
    all_races = WEC_SCHEDULE + IMSA_SCHEDULE
    now = datetime.now(timezone.utc)
    
    upcoming = [race for race in all_races if race['date'] > now]
    upcoming.sort(key=lambda x: x['date'])
    
    return upcoming[:limit]

def is_race_live(race: Dict, tolerance_hours: int = 12) -> bool:
    """Check if a race is currently live (within tolerance window)"""
    now = datetime.now(timezone.utc)
    race_time = race['date']
    
    # Race is live if we're within tolerance hours after start
    time_diff = (now - race_time).total_seconds() / 3600
    
    return 0 <= time_diff <= tolerance_hours

def get_time_until_race(race: Dict) -> str:
    """Get human-readable time until race starts"""
    now = datetime.now(timezone.utc)
    delta = race['date'] - now
    
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"
