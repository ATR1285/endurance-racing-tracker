"""
Track Map Visualization - Display cars moving on track map
"""
from typing import Dict, List, Optional
import math


class TrackMap:
    """Generate track coordinates and car positions"""
    
    # Track definitions (simplified coordinates)
    TRACKS = {
        "Bahrain International Circuit": {
            "length_km": 5.412,
            "turns": 15,
            "coordinates": [
                # Main straight
                {"x": 50, "y": 50, "sector": 1},
                {"x": 70, "y": 50, "sector": 1},
                # Turn 1-4 complex
                {"x": 75, "y": 45, "sector": 1},
                {"x": 80, "y": 35, "sector": 1},
                {"x": 75, "y": 25, "sector": 1},
                # Back straight
                {"x": 60, "y": 20, "sector": 2},
                {"x": 40, "y": 20, "sector": 2},
                # Turns 9-11
                {"x": 30, "y": 25, "sector": 2},
                {"x": 25, "y": 35, "sector": 3},
                # Final sector
                {"x": 30, "y": 45, "sector": 3},
                {"x": 40, "y": 50, "sector": 3},
            ]
        },
        "Circuit de la Sarthe": {  # Le Mans
            "length_km": 13.626,
            "turns": 38,
            "coordinates": [
                # Mulsanne straight
                {"x": 20, "y": 50, "sector": 1},
                {"x": 80, "y": 50, "sector": 1},
                # Mulsanne corner
                {"x": 85, "y": 45, "sector": 2},
                {"x": 85, "y": 30, "sector": 2},
                # Indianapolis/Arnage
                {"x": 80, "y": 20, "sector": 2},
                {"x": 60, "y": 15, "sector": 2},
                # Porsche curves
                {"x": 40, "y": 20, "sector": 3},
                {"x": 25, "y": 30, "sector": 3},
                # Ford chicanes
                {"x": 20, "y": 40, "sector": 3},
            ]
        },
        "Sebring International Raceway": {
            "length_km": 6.019,
            "turns": 17,
            "coordinates": [
                {"x": 50, "y": 50, "sector": 1},
                {"x": 70, "y": 45, "sector": 1},
                {"x": 80, "y": 30, "sector": 1},
                {"x": 75, "y": 20, "sector": 2},
                {"x": 55, "y": 15, "sector": 2},
                {"x": 35, "y": 20, "sector": 2},
                {"x": 25, "y": 35, "sector": 3},
                {"x": 30, "y": 45, "sector": 3},
            ]
        }
    }
    
    @classmethod
    def get_car_position(cls, track_name: str, lap_progress: float, sector: int = 1) -> Dict:
        """
        Calculate car position on track
        
        Args:
            track_name: Name of the track
            lap_progress: Progress through lap (0.0 to 1.0)
            sector: Current sector (1, 2, or 3)
            
        Returns:
            Dictionary with x, y coordinates and rotation
        """
        track = cls.TRACKS.get(track_name)
        if not track:
            # Default circular track
            angle = lap_progress * 2 * math.pi
            return {
                "x": 50 + 30 * math.cos(angle),
                "y": 50 + 30 * math.sin(angle),
                "rotation": math.degrees(angle) + 90
            }
        
        coords = track["coordinates"]
        total_points = len(coords)
        
        # Calculate position along track
        point_index = int(lap_progress * total_points) % total_points
        next_index = (point_index + 1) % total_points
        
        # Interpolate between points
        t = (lap_progress * total_points) % 1.0
        current = coords[point_index]
        next_point = coords[next_index]
        
        x = current["x"] + (next_point["x"] - current["x"]) * t
        y = current["y"] + (next_point["y"] - current["y"]) * t
        
        # Calculate rotation (direction of travel)
        dx = next_point["x"] - current["x"]
        dy = next_point["y"] - current["y"]
        rotation = math.degrees(math.atan2(dy, dx))
        
        return {
            "x": x,
            "y": y,
            "rotation": rotation,
            "sector": current["sector"]
        }
    
    @classmethod
    def get_track_path(cls, track_name: str) -> List[Dict]:
        """Get track path coordinates for drawing"""
        track = cls.TRACKS.get(track_name)
        if not track:
            # Generate circular track
            points = []
            for i in range(100):
                angle = (i / 100) * 2 * math.pi
                points.append({
                    "x": 50 + 30 * math.cos(angle),
                    "y": 50 + 30 * math.sin(angle)
                })
            return points
        
        return track["coordinates"]


# Weather conditions
WEATHER_CONDITIONS = {
    "clear": {"icon": "☀️", "grip": 1.0, "visibility": 1.0},
    "cloudy": {"icon": "☁️", "grip": 0.95, "visibility": 0.95},
    "light_rain": {"icon": "🌧️", "grip": 0.85, "visibility": 0.85},
    "heavy_rain": {"icon": "⛈️", "grip": 0.70, "visibility": 0.70},
    "night": {"icon": "🌙", "grip": 1.0, "visibility": 0.80}
}
