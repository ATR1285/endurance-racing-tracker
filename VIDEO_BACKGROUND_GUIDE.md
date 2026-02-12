# Video Background Setup Guide

## Adding Racing Video Background

Your dashboard now supports video backgrounds! Here's how to add racing footage:

### Option 1: Use a Free Racing Video

**Recommended Sources:**
1. **Pexels** - https://www.pexels.com/search/videos/car%20racing/
2. **Pixabay** - https://pixabay.com/videos/search/racing/
3. **Videvo** - https://www.videvo.net/free-video/racing/

**Steps:**
1. Download a racing video (preferably 1080p or 4K)
2. Convert to MP4 and WebM formats (for browser compatibility)
3. Rename files to:
   - `racing-background.mp4`
   - `racing-background.webm`
4. Place in `frontend/static/` folder

### Option 2: Use YouTube Video (Requires Conversion)

If you found a YouTube video:
1. Use a YouTube downloader tool
2. Download as MP4
3. Optimize the file size (recommended: 720p, 10-30 seconds loop)
4. Place in `frontend/static/`

### Option 3: Create Static Folder

```bash
# Create the static folder
mkdir frontend/static

# Place your video files here:
# frontend/static/racing-background.mp4
# frontend/static/racing-background.webm
```

### Video Recommendations

**Best Video Characteristics:**
- **Duration**: 10-30 seconds (will loop seamlessly)
- **Resolution**: 1080p (good balance of quality and file size)
- **Content**: Endurance racing footage (WEC, IMSA, Le Mans)
- **Angle**: Trackside or onboard camera
- **File Size**: Under 20MB for good performance

**Good Search Terms:**
- "endurance racing onboard"
- "Le Mans 24 hours racing"
- "WEC racing footage"
- "IMSA sports car racing"
- "GT3 racing trackside"

### Current Fallback

If no video is found, the system will automatically use the CSS 3D animation as a fallback. Both look great!

### Testing

After adding your video:
1. Refresh the dashboard (F5)
2. Video should autoplay in the background
3. If it doesn't play, check browser console for errors

### Performance Tips

- Keep video file under 20MB
- Use 720p or 1080p (4K may be too large)
- Shorter loops (10-20s) are better than long videos
- WebM format is smaller than MP4 (use both for compatibility)

---

**The video background is now ready to use! Just add your racing video file.** 🏎️
