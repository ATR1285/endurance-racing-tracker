// Track Map Visualization with Moving Cars - FIXED VERSION

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
        // Simplified track paths
        return {
            length: 5.412,
            turns: 15,
            path: [
                [50, 50], [70, 50], [75, 45], [80, 35], [75, 25],
                [60, 20], [40, 20], [30, 25], [25, 35], [30, 45], [40, 50]
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
                <svg class="track-path" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
                    <path class="track-outline" d="${this.generateTrackPath()}" />
                    <path class="track-center-line" d="${this.generateTrackPath()}" />
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
        let path = `M ${points[0][0]} ${points[0][1]}`;

        for (let i = 1; i < points.length; i++) {
            path += ` L ${points[i][0]} ${points[i][1]}`;
        }

        path += ' Z';
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

        // Update position smoothly
        carMarker.style.left = `${pos.x}%`;
        carMarker.style.top = `${pos.y}%`;
        carMarker.style.transform = `translate(-50%, -50%) rotate(${pos.rotation}deg)`;
    }

    calculatePosition(lapProgress) {
        const points = this.trackData.path;
        const totalPoints = points.length;
        const index = Math.floor(lapProgress * totalPoints) % totalPoints;
        const nextIndex = (index + 1) % totalPoints;

        const t = (lapProgress * totalPoints) % 1;
        const current = points[index];
        const next = points[nextIndex];

        const x = current[0] + (next[0] - current[0]) * t;
        const y = current[1] + (next[1] - current[1]) * t;

        const dx = next[0] - current[0];
        const dy = next[1] - current[1];
        const rotation = Math.atan2(dy, dx) * (180 / Math.PI);

        return { x, y, rotation };
    }

    setWeather(condition) {
        this.weather = condition;
        // Update only weather overlay, not entire map
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
        // Animate cars continuously
        const animate = () => {
            this.updateDemoCars();
            this.animationFrame = requestAnimationFrame(animate);
        };
        animate();
    }

    updateDemoCars() {
        // Demo cars with smooth movement
        const demoCars = [
            { number: 7, class: 'hypercar', speed: 1.0 },
            { number: 8, class: 'hypercar', speed: 0.95 },
            { number: 23, class: 'lmp2', speed: 0.9 },
            { number: 38, class: 'lmp2', speed: 0.85 },
            { number: 51, class: 'lmgt3', speed: 0.8 },
            { number: 85, class: 'lmgt3', speed: 0.75 }
        ];

        const time = Date.now() / 20000; // 20 second lap

        demoCars.forEach((car, index) => {
            const lapProgress = (time * car.speed) % 1;
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

// Add to existing initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTrackMap);
} else {
    initializeTrackMap();
}

// Weather cycle for demo
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
