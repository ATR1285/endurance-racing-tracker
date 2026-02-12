// Professional Track Visualization - Using F1-Style Coordinate System
// Based on TUMFTM racetrack-database methodology

class TrackMapVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.cars = new Map();
        this.trackData = null;
        this.weather = 'clear';
        this.animationFrame = null;
        this.trackScale = 1;
    }

    initialize(trackName) {
        this.trackData = this.loadTrackCoordinates(trackName);
        this.render();
        this.startUpdates();
    }

    loadTrackCoordinates(trackName) {
        // Professional track coordinates using center line method
        // Similar to TUMFTM racetrack database format
        const tracks = {
            'bahrain': {
                name: 'Bahrain International Circuit',
                length: 5.412,
                turns: 15,
                width: 15, // meters
                // Center line coordinates (x, y in meters, normalized to 0-1000 range)
                centerline: [
                    // Start/Finish straight
                    [100, 500], [150, 500], [200, 500], [250, 500], [300, 500],
                    // Turn 1 (90° right)
                    [350, 490], [400, 470], [440, 440], [470, 400], [490, 350],
                    // Turn 2-3 complex
                    [500, 300], [500, 250], [490, 200], [470, 160], [440, 130],
                    // Turn 4 (left hairpin)
                    [400, 110], [350, 100], [300, 100], [250, 110],
                    // Back straight
                    [200, 120], [150, 130], [100, 140],
                    // Turn 5-6
                    [70, 160], [50, 200], [40, 250], [40, 300],
                    // Turn 7-8
                    [50, 350], [70, 390], [100, 420],
                    // Turn 9-10 (chicane)
                    [140, 440], [180, 450], [220, 455],
                    // Turn 11
                    [260, 460], [300, 470], [340, 480],
                    // Turn 12-13
                    [380, 490], [420, 495], [460, 498],
                    // Turn 14
                    [500, 500], [540, 500], [580, 498],
                    // Turn 15 (final corner)
                    [620, 490], [650, 475], [670, 455],
                    [680, 430], [680, 400], [670, 370],
                    [650, 345], [620, 330], [580, 320],
                    [540, 315], [500, 315], [460, 320],
                    [420, 330], [380, 345], [340, 365],
                    [300, 390], [260, 420], [220, 450],
                    [180, 475], [140, 490], [100, 500]
                ],
                // Sector markers (distance along track, 0-1)
                sectors: [
                    { id: 1, start: 0.0, end: 0.33, color: '#ff3366' },
                    { id: 2, start: 0.33, end: 0.66, color: '#ffaa00' },
                    { id: 3, start: 0.66, end: 1.0, color: '#00d4ff' }
                ]
            }
        };

        return tracks['bahrain'];
    }

    render() {
        if (!this.container) return;

        // Calculate bounding box for proper scaling
        const bounds = this.calculateBounds(this.trackData.centerline);
        this.trackScale = 800 / Math.max(bounds.width, bounds.height);

        const weatherIcon = this.getWeatherIcon();
        const weatherName = this.getWeatherName();
        const gripLevel = this.getGripLevel();

        this.container.innerHTML = `
            <div class="track-map-container">
                <svg class="track-path" viewBox="${bounds.minX - 50} ${bounds.minY - 50} ${bounds.width + 100} ${bounds.height + 100}" preserveAspectRatio="xMidYMid meet">
                    <!-- Track background -->
                    <path class="track-outline" d="${this.generateTrackPath()}" 
                          fill="none" 
                          stroke="rgba(80, 100, 130, 0.4)" 
                          stroke-width="${this.trackData.width * 2}" 
                          stroke-linecap="round" 
                          stroke-linejoin="round"/>
                    
                    <!-- Track surface -->
                    <path class="track-surface" d="${this.generateTrackPath()}" 
                          fill="none" 
                          stroke="rgba(60, 70, 90, 0.6)" 
                          stroke-width="${this.trackData.width}" 
                          stroke-linecap="round" 
                          stroke-linejoin="round"/>
                    
                    <!-- Center line -->
                    <path class="track-center-line" d="${this.generateTrackPath()}" 
                          fill="none" 
                          stroke="rgba(255, 255, 255, 0.1)" 
                          stroke-width="1" 
                          stroke-dasharray="5, 5"/>
                    
                    <!-- Start/Finish line -->
                    <line x1="${this.trackData.centerline[0][0]}" 
                          y1="${this.trackData.centerline[0][1] - this.trackData.width / 2}" 
                          x2="${this.trackData.centerline[0][0]}" 
                          y2="${this.trackData.centerline[0][1] + this.trackData.width / 2}" 
                          stroke="white" 
                          stroke-width="3"/>
                </svg>
                
                <div class="weather-overlay">
                    <div class="weather-icon">${weatherIcon}</div>
                    <div class="weather-info">
                        <div class="weather-condition">${weatherName}</div>
                        <div class="weather-details">Grip: ${gripLevel}%</div>
                    </div>
                </div>
                
                <div class="track-info">
                    <div class="track-name">${this.trackData.name}</div>
                    <div class="track-length">${this.trackData.length} km • ${this.trackData.turns} turns</div>
                </div>
                
                <div id="car-markers"></div>
            </div>
        `;
    }

    calculateBounds(points) {
        let minX = Infinity, minY = Infinity;
        let maxX = -Infinity, maxY = -Infinity;

        points.forEach(([x, y]) => {
            minX = Math.min(minX, x);
            minY = Math.min(minY, y);
            maxX = Math.max(maxX, x);
            maxY = Math.max(maxY, y);
        });

        return {
            minX, minY, maxX, maxY,
            width: maxX - minX,
            height: maxY - minY
        };
    }

    generateTrackPath() {
        const points = this.trackData.centerline;

        // Create smooth path using cubic bezier curves
        let path = `M ${points[0][0]} ${points[0][1]}`;

        for (let i = 1; i < points.length; i++) {
            const curr = points[i];
            const prev = points[i - 1];

            // Calculate control points for smooth curves
            const cp1x = prev[0] + (curr[0] - prev[0]) * 0.5;
            const cp1y = prev[1] + (curr[1] - prev[1]) * 0.5;

            path += ` L ${curr[0]} ${curr[1]}`;
        }

        return path;
    }

    updateCarPosition(carNumber, lapProgress, carClass = 'hypercar', position = 1) {
        const pos = this.getPositionOnTrack(lapProgress);
        const carId = `car-${carNumber}`;

        let carMarker = document.getElementById(carId);
        if (!carMarker) {
            const markersContainer = document.getElementById('car-markers');
            if (!markersContainer) return;

            carMarker = document.createElement('div');
            carMarker.id = carId;
            carMarker.className = `car-marker ${carClass.toLowerCase()} ${position === 1 ? 'leading' : ''}`;
            carMarker.innerHTML = `
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
                </svg>
                <div class="car-number">#${carNumber}</div>
            `;
            markersContainer.appendChild(carMarker);
        }

        // Update position
        carMarker.style.left = `${pos.screenX}%`;
        carMarker.style.top = `${pos.screenY}%`;
        carMarker.style.transform = `translate(-50%, -50%) rotate(${pos.rotation}deg)`;
    }

    getPositionOnTrack(progress) {
        const points = this.trackData.centerline;
        const totalPoints = points.length;

        // Get exact position along track
        const exactIndex = progress * (totalPoints - 1);
        const index = Math.floor(exactIndex);
        const nextIndex = Math.min(index + 1, totalPoints - 1);
        const t = exactIndex - index;

        const curr = points[index];
        const next = points[nextIndex];

        // Interpolate position
        const x = curr[0] + (next[0] - curr[0]) * t;
        const y = curr[1] + (next[1] - curr[1]) * t;

        // Calculate rotation
        const dx = next[0] - curr[0];
        const dy = next[1] - curr[1];
        const rotation = Math.atan2(dy, dx) * (180 / Math.PI);

        // FIXED: Convert to screen coordinates accounting for viewBox offset
        const bounds = this.calculateBounds(points);
        // The viewBox is: minX-50, minY-50, width+100, height+100
        // So we need to account for the -50 offset
        const screenX = ((x - (bounds.minX - 50)) / (bounds.width + 100)) * 100;
        const screenY = ((y - (bounds.minY - 50)) / (bounds.height + 100)) * 100;

        return { x, y, screenX, screenY, rotation };
    }

    setWeather(condition) {
        this.weather = condition;
        const weatherOverlay = this.container.querySelector('.weather-overlay');
        if (weatherOverlay) {
            weatherOverlay.innerHTML = `
                <div class="weather-icon">${this.getWeatherIcon()}</div>
                <div class="weather-info">
                    <div class="weather-condition">${this.getWeatherName()}</div>
                    <div class="weather-details">Grip: ${this.getGripLevel()}%</div>
                </div>
            `;
        }
    }

    getWeatherIcon() {
        const icons = { 'clear': '☀️', 'cloudy': '☁️', 'light_rain': '🌧️', 'heavy_rain': '⛈️', 'night': '🌙' };
        return icons[this.weather] || '☀️';
    }

    getWeatherName() {
        const names = { 'clear': 'Clear', 'cloudy': 'Cloudy', 'light_rain': 'Light Rain', 'heavy_rain': 'Heavy Rain', 'night': 'Night' };
        return names[this.weather] || 'Clear';
    }

    getGripLevel() {
        const grip = { 'clear': 100, 'cloudy': 95, 'light_rain': 85, 'heavy_rain': 70, 'night': 100 };
        return grip[this.weather] || 100;
    }

    startUpdates() {
        const animate = () => {
            this.updateDemoCars();
            this.animationFrame = requestAnimationFrame(animate);
        };
        animate();
    }

    updateDemoCars() {
        const demoCars = [
            { number: 7, class: 'hypercar', speed: 1.0, offset: 0 },
            { number: 8, class: 'hypercar', speed: 0.98, offset: 0.04 },
            { number: 23, class: 'lmp2', speed: 0.94, offset: 0.12 },
            { number: 38, class: 'lmp2', speed: 0.92, offset: 0.18 },
            { number: 51, class: 'lmgt3', speed: 0.87, offset: 0.28 },
            { number: 85, class: 'lmgt3', speed: 0.85, offset: 0.35 }
        ];

        const time = Date.now() / 30000; // 30 second lap

        demoCars.forEach((car, index) => {
            const lapProgress = ((time * car.speed) + car.offset) % 1;
            this.updateCarPosition(car.number, lapProgress, car.class, index + 1);
        });
    }

    destroy() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
    }
}

// Initialize
let trackMap;

function initializeTrackMap() {
    trackMap = new TrackMapVisualizer('trackMap');
    trackMap.initialize('bahrain');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTrackMap);
} else {
    initializeTrackMap();
}

// Weather cycling
let weatherIndex = 0;
const weatherConditions = ['clear', 'cloudy', 'light_rain', 'heavy_rain', 'night'];

function cycleWeather() {
    if (trackMap) {
        weatherIndex = (weatherIndex + 1) % weatherConditions.length;
        trackMap.setWeather(weatherConditions[weatherIndex]);
    }
}

setInterval(cycleWeather, 30000);
