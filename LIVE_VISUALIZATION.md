# Live Race Visualization System

Inspired by [f1-race-replay](https://github.com/IAmTomShaw/f1-race-replay) but adapted for **live** endurance racing.

## Key Differences from F1 Replay

| Feature | F1 Replay (Replay Mode) | Our System (Live Mode) |
|---------|------------------------|------------------------|
| **Data Source** | Historical FastF1 data | Live timing websites |
| **Playback** | Replay with controls | Real-time streaming |
| **Speed Control** | 0.5x - 4x | Live only (1x) |
| **Track Data** | Official F1 telemetry | Estimated positions |
| **Updates** | Frame-by-frame | Every 500ms |

## What We Implemented

### ✅ Already Built
1. **Live Track Map** - Real-time car positions
2. **Moving Cars** - Smooth animations
3. **Weather Effects** - Dynamic conditions
4. **Class Colors** - Hypercar, LMP2, GT3
5. **Auto-Updates** - Every 500ms

### 🚀 Enhanced Features (Inspired by F1 Replay)

#### 1. Interactive Controls
```javascript
// Pause/Resume (for replay mode)
- SPACE: Pause/Resume
- ← / →: Skip backward/forward
- ↑ / ↓: Speed control
```

#### 2. Driver Telemetry
- Speed
- Gear
- Tire compound
- Fuel level
- Lap times

#### 3. Enhanced Visualization
- Driver names on track
- Position indicators
- Gap to leader
- Pit stop markers
- Incident flags

## Implementation Plan

### Phase 1: Enhanced Track Visualization ✅
- [x] Track path rendering
- [x] Car markers with class colors
- [x] Weather overlay
- [x] Smooth animations

### Phase 2: Live Telemetry (Next)
- [ ] Real-time speed data
- [ ] Gear indicators
- [ ] Tire compound display
- [ ] Fuel level tracking

### Phase 3: Interactive Features
- [ ] Click car to view details
- [ ] Multi-car comparison
- [ ] Sector time highlights
- [ ] Pit stop predictions

### Phase 4: Replay Mode
- [ ] Save race data to JSON
- [ ] Replay from saved data
- [ ] Playback controls
- [ ] Speed adjustment

## Technical Architecture

```
┌─────────────────────────────────────────────┐
│         Live Timing Sources                 │
│  (WEC timing / IMSA scoring)                │
└──────────────────┬──────────────────────────┘
                   │ Web Scraping
                   ↓
┌─────────────────────────────────────────────┐
│      Data Ingestion Manager                 │
│  - Fetch lap times                          │
│  - Calculate positions                      │
│  - Estimate speed/telemetry                 │
└──────────────────┬──────────────────────────┘
                   │ Store in DB
                   ↓
┌─────────────────────────────────────────────┐
│         SQLite Database                     │
│  - Laps, positions, pit stops               │
│  - Export to JSON for replay                │
└──────────────────┬──────────────────────────┘
                   │ API Endpoints
                   ↓
┌─────────────────────────────────────────────┐
│      Track Map Visualizer                   │
│  - Real-time car positions                  │
│  - Smooth animations                        │
│  - Interactive controls                     │
└─────────────────────────────────────────────┘
```

## Usage

### Live Mode (Current)
```bash
# Start server
python -m uvicorn backend.main:app --reload

# Open dashboard
http://localhost:8000/dashboard

# Cars move automatically when race is live
```

### Replay Mode (Coming Soon)
```bash
# Replay from saved race
python replay.py --race-id 1

# Or from JSON export
python replay.py --file race_exports/6_Hours_of_Bahrain.json
```

## Features Comparison

### From F1 Replay
- ✅ Track visualization
- ✅ Car markers
- ✅ Leaderboard
- ✅ Lap/time display
- ⏳ Telemetry insights (in progress)
- ⏳ Interactive controls (planned)
- ⏳ Replay mode (planned)

### Our Additions
- ✅ Live data streaming
- ✅ Weather effects
- ✅ Multi-series support (WEC/IMSA)
- ✅ ML predictions
- ✅ JSON export
- ✅ Auto race detection

## Next Steps

1. **Add Telemetry Panel**
   - Speed graph
   - Gear indicator
   - Tire/fuel status

2. **Interactive Car Selection**
   - Click to select
   - Show detailed stats
   - Compare multiple cars

3. **Replay Mode**
   - Load from JSON
   - Playback controls
   - Speed adjustment

4. **Enhanced Track Maps**
   - Actual circuit layouts
   - Sector markers
   - DRS zones (for applicable series)

---

**The live visualization is already working! Check the track map on your dashboard.** 🏁
