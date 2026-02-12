# Race Data JSON Export

## Automatic Export When Race Ends

The system now automatically exports complete race data to JSON when a race finishes.

### What Gets Exported

**Complete race data including:**
- Race information (series, name, track, times)
- All cars and drivers
- Every lap with sector times
- All pit stops
- Race statistics (fastest lap, pit stop counts, etc.)

### Export Location

```
race_exports/
├── 6_Hours_of_Bahrain_20250213_001234.json
├── 12_Hours_of_Sebring_20250315_143022.json
└── ...
```

### JSON Structure

```json
{
  "race_info": {
    "id": 1,
    "series": "WEC",
    "name": "6 Hours of Bahrain",
    "track": "Bahrain International Circuit",
    "start_time": "2025-02-28T14:00:00",
    "end_time": "2025-02-28T20:00:00",
    "exported_at": "2025-02-28T20:05:00"
  },
  "cars": [
    {
      "car_number": "7",
      "team": "Toyota Gazoo Racing",
      "class": "Hypercar",
      "manufacturer": "Toyota",
      "drivers": [
        {"name": "Mike Conway", "nationality": "GBR"},
        {"name": "Kamui Kobayashi", "nationality": "JPN"}
      ]
    }
  ],
  "laps": [
    {
      "car_number": "7",
      "lap_number": 1,
      "lap_time": 105.234,
      "sector1_time": 32.1,
      "sector2_time": 38.5,
      "sector3_time": 34.6,
      "position": 1,
      "gap_to_leader": 0.0,
      "tire_age": 0,
      "is_pit_lap": false
    }
  ],
  "pit_stops": [
    {
      "car_number": "7",
      "lap_number": 25,
      "duration": 45.2,
      "stop_type": "Regular",
      "timestamp": "2025-02-28T15:30:00"
    }
  ],
  "statistics": {
    "total_cars": 10,
    "total_laps": 500,
    "total_pit_stops": 35,
    "fastest_lap": {
      "car_number": "7",
      "lap_number": 42,
      "time": 103.456
    },
    "most_pit_stops": {
      "car_number": "51",
      "count": 5
    }
  }
}
```

### How It Works

1. **Race Ends** - Monitor detects race is over (12 hours after start)
2. **Stop Scraping** - Data ingestion stops
3. **Mark Complete** - Race marked as inactive in database
4. **Export JSON** - Complete data exported automatically
5. **Log Created** - Filename logged in console

### Manual Export

You can also export manually via API:

```bash
# Export specific race
curl http://localhost:8000/api/export/race/1

# Export active race
curl http://localhost:8000/api/export/active
```

### Use Cases

- **Data Analysis** - Import into Python/R for analysis
- **Backup** - Keep historical race data
- **Sharing** - Share race results with others
- **Archiving** - Long-term storage of race data
- **Visualization** - Import into other tools

---

**Race data is automatically saved when races complete!** 📦
