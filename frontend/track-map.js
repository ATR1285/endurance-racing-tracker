// Track Map Visualization - IMPROVED WITH REALISTIC TRACK LAYOUT

class TrackMapVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.cars = new Map();
        this.trackData = null;
        this.weather = 'clear';
        this.updateInterval = null;
        this.animationFrame = null;
    }

    initialize(trackName) {
        this.trackData = this.getTrackData(trackName);
        this.render();
        this.startUpdates();
    }

    getTrackData(trackName) {
        // Realistic Bahrain International Circuit layout
        return {
            length: 5.412,
            turns: 15,
            path: [
                // Start/Finish straight
                [20, 50], [35, 50], [45, 50],
                // Turn 1 (right)
                [52, 48], [58, 44], [62, 38],
                // Turn 2-3 complex
                [64, 32], [64, 26], [62, 20],
                // Turn 4 (left)
                [58, 16], [52, 14], [45, 14],
                // Back straight
                [35, 14], [25, 14], [18, 14],
                // Turn 5-6
                [14, 16], [12, 20], [12, 26],
                // Turn 7-8
                [14, 32], [16, 36], [20, 40],
                // Turn 9-10
                [24, 42], [28, 44], [32, 46],
                // Turn 11-12
                [36, 48], [40, 50], [44, 52],
                // Turn 13-14
                [48, 54], [52, 56], [56, 58],
                // Turn 15 (final corner)
                [60, 58], [64, 56], [68, 52],
                // Back to start
                [70, 48], [68, 44], [64, 42],
                [58, 42], [52, 44], [46, 46],
                [40, 48], [32, 50], [24, 50]
            ]
        };
    }

    render() {
        if (!this.container) return;

        const weatherIcon = this.getWeatherIcon();
        const weatherName = this.getWeatherName();
        const gripLevel = this.getGripLevel();

        this.container.innerHTML = `
            <div class="track-map-container">
                <svg class="track-path" viewBox="0 0 80 70" preserveAspectRatio="xMidYMid meet">
                    <!-- Track outline (wider) -->
                    <path class="track-outline" d="${this.generateTrackPath()}" 
                          fill="none" 
                          stroke="rgba(100, 120, 150, 0.3)" 
                          stroke-width="8" 
                          stroke-linecap="round" 
                          stroke-linejoin="round"/>
                    
                    <!-- Track center line -->
                    <path class="track-center-line" d="${this.generateTrackPath()}" 
                          fill="none" 
                          stroke="rgba(255, 255, 255, 0.15)" 
                          stroke-width="1" 
                          stroke-dasharray="2, 2"/>
                    
                    <!-- Start/Finish line -->
                    <line x1="20" y1="48" x2="20" y2="52" 
                          stroke="rgba(255, 255, 255, 0.8)" 
                          stroke-width="2"/>
                </svg>
                
                <div class="weather-overlay">
                    <div class="weather-icon">${weatherIcon}</div>
                    <div class="weather-info">
                        <div class="weather-condition">${weatherName}</div>
                        <div class="weather-details">Grip: ${gripLevel}%</div>
                    </div>
                </div>
                
                <div class="track-info">
                    <div class="track-name">Bahrain International Circuit</div>
                    <div class="track-length">5.412 km • 15 turns</div>
                </div>
                
                <div id="car-markers"></div>
            </div>
        `;
    }

    generateTrackPath() {
        const points = this.trackData.path;

        // Use smooth curves for realistic track
        let path = `M ${points[0][0]} ${points[0][1]}`;

        for (let i = 1; i < points.length - 2; i++) {
            const curr = points[i];
            const next = points[i + 1];

            // Quadratic bezier for smooth corners
            const cpx = (curr[0] + next[0]) / 2;
            const cpy = (curr[1] + next[1]) / 2;

            path += ` Q ${curr[0]} ${curr[1]} ${cpx} ${cpy}`;
        }

        // Close the path smoothly
        const last = points[points.length - 1];
        const first = points[0];
        path += ` Q ${last[0]} ${last[1]} ${first[0]} ${first[1]}`;

        return path;
    }

    updateCarPosition(carNumber, lapProgress, carClass = 'hypercar', position = 1) {
        if (!this.trackData) return;

        const pos = this.calculatePosition(lapProgress);
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

        // Convert track coordinates to screen percentage
        const screenX = (pos.x / 80) * 100;
        const screenY = (pos.y / 70) * 100;

        // Update position smoothly
        carMarker.style.left = `${screenX}%`;
        carMarker.style.top = `${screenY}%`;
        carMarker.style.transform = `translate(-50%, -50%) rotate(${pos.rotation}deg)`;
    }

    calculatePosition(lapProgress) {
        const points = this.trackData.path;
        const totalPoints = points.length;

        // Smooth interpolation
        const exactIndex = lapProgress * totalPoints;
        const index = Math.floor(exactIndex) % totalPoints;
        const nextIndex = (index + 1) % totalPoints;

        const t = exactIndex % 1;
        const current = points[index];
        const next = points[nextIndex];

        // Linear interpolation
        const x = current[0] + (next[0] - current[0]) * t;
        const y = current[1] + (next[1] - current[1]) * t;

        // Calculate rotation based on direction
        const dx = next[0] - current[0];
        const dy = next[1] - current[1];
        const rotation = Math.atan2(dy, dx) * (180 / Math.PI);

        return { x, y, rotation };
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
        const icons = {
            'clear': '☀️',
            'cloudy': '☁️',
            'light_rain': '🌧️',
            'heavy_rain': '⛈️',
            'night': '🌙'
        };
        return icons[this.weather] || '☀️';
    }

    getWeatherName() {
        const names = {
            'clear': 'Clear',
            'cloudy': 'Cloudy',
            'light_rain': 'Light Rain',
            'heavy_rain': 'Heavy Rain',
            'night': 'Night'
        };
        return names[this.weather] || 'Clear';
    }

    getGripLevel() {
        const grip = {
            'clear': 100,
            'cloudy': 95,
            'light_rain': 85,
            'heavy_rain': 70,
            'night': 100
        };
        return grip[this.weather] || 100;
    }

    startUpdates() {
        // Smooth animation loop
        const animate = () => {
            this.updateDemoCars();
            this.animationFrame = requestAnimationFrame(animate);
        };
        animate();
    }

    updateDemoCars() {
        // Demo cars with realistic spacing
        const demoCars = [
            { number: 7, class: 'hypercar', speed: 1.0, offset: 0 },
            { number: 8, class: 'hypercar', speed: 0.98, offset: 0.05 },
            { number: 23, class: 'lmp2', speed: 0.95, offset: 0.15 },
            { number: 38, class: 'lmp2', speed: 0.93, offset: 0.22 },
            { number: 51, class: 'lmgt3', speed: 0.88, offset: 0.35 },
            { number: 85, class: 'lmgt3', speed: 0.86, offset: 0.42 }
        ];

        const time = Date.now() / 25000; // 25 second lap

        demoCars.forEach((car, index) => {
            const lapProgress = ((time * car.speed) + car.offset) % 1;
            this.updateCarPosition(
                car.number,
                lapProgress,
                car.class,
                index + 1
            );
        });
    }

    destroy() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
    }
}

// Initialize track map
let trackMap;

function initializeTrackMap() {
    trackMap = new TrackMapVisualizer('trackMap');
    trackMap.initialize('Bahrain International Circuit');
}

// Initialize on page load
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

// Auto-cycle weather every 30 seconds
setInterval(cycleWeather, 30000);
