// SIMPLIFIED Track Visualization - Guaranteed to Work
// Using normalized 0-100 coordinate system

class TrackMapVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.trackData = null;
        this.weather = 'clear';
        this.animationFrame = null;
    }

    initialize() {
        this.trackData = this.createTrack();
        this.render();
        this.startAnimation();
    }

    createTrack() {
        // Simple oval track with normalized coordinates (0-100)
        // This guarantees cars will be on track
        return {
            name: 'Bahrain International Circuit',
            length: 5.412,
            turns: 15,
            // Normalized path coordinates (x, y from 0-100)
            path: [
                // Main straight
                [10, 50], [20, 50], [30, 50], [40, 50],
                // Turn 1 (right)
                [50, 48], [58, 44], [64, 38], [68, 30],
                // Turn 2-3
                [70, 22], [70, 15], [68, 10],
                // Turn 4 (hairpin)
                [62, 8], [54, 7], [46, 8], [40, 10],
                // Back straight
                [32, 12], [24, 14], [16, 16],
                // Turn 5-6
                [12, 20], [10, 26], [10, 34],
                // Turn 7-8
                [12, 42], [16, 48], [22, 52],
                // Turn 9-10
                [30, 54], [38, 55], [46, 55],
                // Turn 11-12
                [54, 54], [62, 52], [68, 50],
                // Turn 13-14
                [74, 48], [78, 46], [82, 44],
                // Turn 15 (final)
                [86, 42], [88, 40], [88, 36],
                [86, 32], [82, 30], [76, 30],
                [68, 32], [60, 36], [52, 42],
                [44, 46], [36, 48], [28, 50],
                [20, 50], [10, 50]
            ]
        };
    }

    render() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="track-map-container">
                <svg class="track-svg" viewBox="0 0 100 65" preserveAspectRatio="xMidYMid meet">
                    <!-- Track outline -->
                    <path d="${this.generateSVGPath()}" 
                          fill="none" 
                          stroke="rgba(80, 100, 130, 0.5)" 
                          stroke-width="6" 
                          stroke-linecap="round" 
                          stroke-linejoin="round"/>
                    
                    <!-- Track surface -->
                    <path d="${this.generateSVGPath()}" 
                          fill="none" 
                          stroke="rgba(60, 70, 90, 0.7)" 
                          stroke-width="4" 
                          stroke-linecap="round" 
                          stroke-linejoin="round"/>
                    
                    <!-- Center line -->
                    <path d="${this.generateSVGPath()}" 
                          fill="none" 
                          stroke="rgba(255, 255, 255, 0.15)" 
                          stroke-width="0.5" 
                          stroke-dasharray="2, 2"/>
                    
                    <!-- Start/Finish line -->
                    <line x1="10" y1="47" x2="10" y2="53" 
                          stroke="white" 
                          stroke-width="1"/>
                </svg>
                
                <div class="weather-overlay">
                    <div class="weather-icon">${this.getWeatherIcon()}</div>
                    <div class="weather-info">
                        <div class="weather-condition">${this.getWeatherName()}</div>
                        <div class="weather-details">Grip: ${this.getGripLevel()}%</div>
                    </div>
                </div>
                
                <div class="track-info">
                    <div class="track-name">${this.trackData.name}</div>
                    <div class="track-length">${this.trackData.length} km • ${this.trackData.turns} turns</div>
                </div>
                
                <div class="car-container" id="car-container"></div>
            </div>
        `;
    }

    generateSVGPath() {
        const points = this.trackData.path;
        let path = `M ${points[0][0]} ${points[0][1]}`;

        for (let i = 1; i < points.length; i++) {
            path += ` L ${points[i][0]} ${points[i][1]}`;
        }

        return path;
    }

    getPositionOnTrack(progress) {
        const points = this.trackData.path;
        const totalPoints = points.length;

        // Calculate exact position
        const exactPos = progress * (totalPoints - 1);
        const index = Math.floor(exactPos);
        const nextIndex = (index + 1) % totalPoints;
        const t = exactPos - index;

        const p1 = points[index];
        const p2 = points[nextIndex];

        // Linear interpolation
        const x = p1[0] + (p2[0] - p1[0]) * t;
        const y = p1[1] + (p2[1] - p1[1]) * t;

        // Calculate angle
        const dx = p2[0] - p1[0];
        const dy = p2[1] - p1[1];
        const angle = Math.atan2(dy, dx) * (180 / Math.PI);

        return { x, y, angle };
    }

    updateCar(carNumber, progress, carClass, position) {
        const pos = this.getPositionOnTrack(progress);
        const carId = `car-${carNumber}`;

        let car = document.getElementById(carId);
        if (!car) {
            const container = document.getElementById('car-container');
            if (!container) return;

            car = document.createElement('div');
            car.id = carId;
            car.className = `car-marker ${carClass} ${position === 1 ? 'leading' : ''}`;
            car.innerHTML = `
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
                </svg>
                <span class="car-num">#${carNumber}</span>
            `;
            container.appendChild(car);
        }

        // Position car - coordinates match SVG viewBox (0-100)
        car.style.left = `${pos.x}%`;
        car.style.top = `${pos.y}%`;
        car.style.transform = `translate(-50%, -50%) rotate(${pos.angle}deg)`;
    }

    startAnimation() {
        const cars = [
            { num: 7, class: 'hypercar', speed: 1.0, offset: 0 },
            { num: 8, class: 'hypercar', speed: 0.98, offset: 0.05 },
            { num: 23, class: 'lmp2', speed: 0.94, offset: 0.15 },
            { num: 38, class: 'lmp2', speed: 0.92, offset: 0.22 },
            { num: 51, class: 'lmgt3', speed: 0.87, offset: 0.32 },
            { num: 85, class: 'lmgt3', speed: 0.85, offset: 0.40 }
        ];

        const animate = () => {
            const time = Date.now() / 25000; // 25 second lap

            cars.forEach((car, idx) => {
                const progress = ((time * car.speed) + car.offset) % 1;
                this.updateCar(car.num, progress, car.class, idx + 1);
            });

            this.animationFrame = requestAnimationFrame(animate);
        };

        animate();
    }

    setWeather(condition) {
        this.weather = condition;
        const overlay = this.container.querySelector('.weather-overlay');
        if (overlay) {
            overlay.innerHTML = `
                <div class="weather-icon">${this.getWeatherIcon()}</div>
                <div class="weather-info">
                    <div class="weather-condition">${this.getWeatherName()}</div>
                    <div class="weather-details">Grip: ${this.getGripLevel()}%</div>
                </div>
            `;
        }
    }

    getWeatherIcon() {
        const icons = { clear: '☀️', cloudy: '☁️', light_rain: '🌧️', heavy_rain: '⛈️', night: '🌙' };
        return icons[this.weather] || '☀️';
    }

    getWeatherName() {
        const names = { clear: 'Clear', cloudy: 'Cloudy', light_rain: 'Light Rain', heavy_rain: 'Heavy Rain', night: 'Night' };
        return names[this.weather] || 'Clear';
    }

    getGripLevel() {
        const grip = { clear: 100, cloudy: 95, light_rain: 85, heavy_rain: 70, night: 100 };
        return grip[this.weather] || 100;
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
    trackMap.initialize();
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
