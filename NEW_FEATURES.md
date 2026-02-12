# New Features Added

## 1. Animated Racing Car Background 🏎️

Added a smooth animated racing car that drives across the screen in the background:
- Subtle opacity (15%) so it doesn't distract
- Glowing cyan shadow effect
- 15-second loop animation
- Positioned behind all content

**Files Modified:**
- `frontend/styles.css` - Added car animation and keyframes

---

## 2. Race Schedule System 📅

Created a complete race schedule module that tracks upcoming WEC and IMSA races:

### Features:
- **WEC Schedule**: Qatar, Sebring, Imola, Spa, Le Mans
- **IMSA Schedule**: Sebring 12h, Long Beach, Laguna Seca
- **Countdown Timers**: Shows time until each race starts
- **Live Detection**: Automatically detects when a race is live (within 12 hours of start)

### New API Endpoints:
- `GET /api/schedule/next` - Get next upcoming race with countdown
- `GET /api/schedule/upcoming` - Get list of upcoming races

**Files Created:**
- `backend/schedule.py` - Race calendar and timing logic

---

## 3. Auto-Start Scraping When Race Begins 🔴

The system now automatically activates live data scraping when a race starts:

### How It Works:
1. On server startup, checks if any race is currently live
2. If live race detected → starts web scraping automatically
3. If no live race → shows "Next race" information with countdown
4. When race begins → ML models activate for predictions

### Frontend Display:
- **No Live Race**: Shows "Next: 6 Hours of Qatar - Starts in 15d 12h"
- **Live Race**: Shows "🔴 LIVE: 6 Hours of Qatar - 2h 30m"

**Files Modified:**
- `backend/main.py` - Added auto-start logic in startup event
- `frontend/app.js` - Added fetchNextRace() function

---

## Summary

✅ **Animated Background**: Racing car drives across screen  
✅ **Race Calendar**: Full WEC/IMSA 2025 schedule  
✅ **Countdown Timers**: Shows time until next race  
✅ **Auto-Activation**: Scraping starts when race goes live  
✅ **Smart Display**: Shows next race when no live event  

The system is now fully automated - it will detect when races start and begin collecting live data automatically!
