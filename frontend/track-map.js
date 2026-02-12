// Track Map Visualization with Moving Cars

class TrackMapVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.cars = new Map();
        this.trackData = null;
        this.weather = 'clear';
        this.updateInterval = null;
    }

    initialize(trackName) {
        this.trackData = this.getTrackData(trackName);
        this.render();
        this.startUpdates();
    }

    getTrackData(trackName) {
        // Track coordinates (simplified)
        const tracks = {
            'Bahrain International Circuit': {
                length: 5.412,
                turns: 15,
                path: [
                    [50, 50], [70, 50], [75, 45], [80, 35], [75, 25],
                    [60, 20], [40, 20], [30, 25], [25, 35], [30, 45], [40, 50]
                ]
            },
            'Circuit de la Sarthe': {
                length: 13.626,
                turns: 38,
                path: [
                    [20, 50], [80, 50], [85, 45], [85, 30], [80, 20],
                    [60, 15], [40, 20], [25, 30], [20, 40]
                ]
            }
        };

        return tracks[trackName] || tracks['Bahrain International Circuit'];
    }

    render() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="track-map-container">
                <svg class="track-path" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
                    <path class="track-outline" d="${this.generateTrackPath()}" />
                    <path class="track-center-line" d="${this.generateTrackPath()}" />
                </svg>
                
                <div class="weather-overlay">
                    <div class="weather-icon">${this.getWeatherIcon()}</div>
                    <div class="weather-info">
                        <div class="weather-condition">${this.getWeatherName()}</div>
                        <div class="weather-details">Grip: ${this.getGripLevel()}%</div>
                    </div>
                </div>
                
                <div class="track-info">
                    <div class="track-name">${this.trackData ? Object.keys(this.getTrackData(''))[0] : 'Track'}</div>
                    <div class="track-length">${this.trackData.length} km • ${this.trackData.turns} turns</div>
                </div>
                
                <div id="car-markers"></div>
            </div>
        `;
    }

    generateTrackPath() {
        if (!this.trackData) return '';

        const points = this.trackData.path;
        let path = `M ${points[0][0]} ${points[0][1]}`;

        for (let i = 1; i < points.length; i++) {
            // Use quadratic curves for smooth track
            const curr = points[i];
            const prev = points[i - 1];
            const cpx = (prev[0] + curr[0]) / 2;
            const cpy = (prev[1] + curr[1]) / 2;
            path += ` Q ${cpx} ${cpy} ${curr[0]} ${curr[1]}`;
        }

        // Close the path
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
                    <path d="M12 2L4 8v6l8 6 8-6V8l-8-6zm0 2.5L17.5 8 12 11.5 6.5 8 12 4.5z"/>
                </svg>
                <div class="car-number">#${carNumber}</div>
            `;
            markersContainer.appendChild(carMarker);
        }

        // Update position
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

        // Calculate rotation
        const dx = next[0] - current[0];
        const dy = next[1] - current[1];
        const rotation = Math.atan2(dy, dx) * (180 / Math.PI);

        return { x, y, rotation };
    }

    setWeather(condition) {
        this.weather = condition;
        this.render();
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
        // Update car positions every second
        this.updateInterval = setInterval(() => {
            this.fetchCarPositions();
        }, 1000);
    }

    async fetchCarPositions() {
        try {
            const response = await fetch('/api/leaderboard');
            const data = await response.json();

            data.forEach((car, index) => {
                // Calculate lap progress (0.0 to 1.0)
                const lapProgress = (car.current_lap % 1);
                this.updateCarPosition(
                    car.car_number,
                    lapProgress,
                    car.car_class,
                    index + 1
                );
            });
        } catch (error) {
            console.error('Failed to fetch car positions:', error);
        }
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Initialize track map when page loads
let trackMap;

function initializeTrackMap() {
    trackMap = new TrackMapVisualizer('trackMap');
    trackMap.initialize('Bahrain International Circuit');

    // Simulate weather changes (for demo)
    const weatherConditions = ['clear', 'cloudy', 'light_rain', 'night'];
    let weatherIndex = 0;

    setInterval(() => {
        weatherIndex = (weatherIndex + 1) % weatherConditions.length;
        trackMap.setWeather(weatherConditions[weatherIndex]);
    }, 60000); // Change weather every minute
}

// Add to existing initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTrackMap);
} else {
    initializeTrackMap();
}
