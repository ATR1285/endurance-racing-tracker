/**
 * Frontend JavaScript for Endurance Racing Tracker
 * Handles real-time data fetching and UI updates
 */

// Configuration
const API_BASE = window.location.origin;
const UPDATE_INTERVAL = 5000; // 5 seconds
let currentClass = 'all';
let selectedCar = null;
let lapTimeChart = null;
let updateTimer = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    startAutoUpdate();
});

/**
 * Initialize the application
 */
function initializeApp() {
    fetchRaceInfo();
    fetchNextRace();
    fetchLeaderboard();
    fetchAnomalies();
    initializeChart();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Class filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentClass = e.target.dataset.class;
            fetchLeaderboard();
        });
    });

    // Car selection for charts
    document.getElementById('carSelect').addEventListener('change', (e) => {
        selectedCar = e.target.value;
        if (selectedCar) {
            fetchLapTimes(selectedCar);
            fetchPrediction(selectedCar);
            fetchStrategy(selectedCar);
        }
    });
}

/**
 * Start automatic updates
 */
function startAutoUpdate() {
    updateTimer = setInterval(() => {
        fetchLeaderboard();
        fetchAnomalies();

        if (selectedCar) {
            fetchLapTimes(selectedCar);
            fetchPrediction(selectedCar);
            fetchStrategy(selectedCar);
        }

        updateLastUpdateTime();
    }, UPDATE_INTERVAL);
}

/**
 * Fetch race information
 */
async function fetchRaceInfo() {
    try {
        const response = await fetch(`${API_BASE}/api/race/info`);
        const data = await response.json();

        if (data) {
            document.getElementById('raceName').textContent = `${data.series} - ${data.name}`;
            updateRaceTime(data.elapsed_time);
        }
    } catch (error) {
        console.error('Error fetching race info:', error);
    }
}

/**
 * Update race elapsed time
 */
function updateRaceTime(elapsedMinutes) {
    const hours = Math.floor(elapsedMinutes / 60);
    const minutes = Math.floor(elapsedMinutes % 60);
    document.getElementById('raceTime').textContent = `${hours}h ${minutes}m`;
}

/**
 * Fetch next race schedule
 */
async function fetchNextRace() {
    try {
        const response = await fetch(`${API_BASE}/api/schedule/next`);
        const data = await response.json();

        if (data && data.name) {
            const raceNameEl = document.getElementById('raceName');
            if (!raceNameEl.textContent || raceNameEl.textContent === 'Loading...') {
                raceNameEl.textContent = `Next: ${data.name}`;
                document.getElementById('raceTime').textContent = `Starts in ${data.countdown}`;

                if (data.is_live) {
                    raceNameEl.textContent = `🔴 LIVE: ${data.name}`;
                }
            }
        }
    } catch (error) {
        console.error('Error fetching next race:', error);
    }
}

/**
 * Fetch and display leaderboard
 */
async function fetchLeaderboard() {
    try {
        const url = currentClass === 'all'
            ? `${API_BASE}/api/leaderboard`
            : `${API_BASE}/api/leaderboard?car_class=${currentClass}`;

        const response = await fetch(url);
        const data = await response.json();

        displayLeaderboard(data);
        updateCarSelect(data);
    } catch (error) {
        console.error('Error fetching leaderboard:', error);
        document.getElementById('leaderboard').innerHTML = '<div class="loading">Error loading leaderboard</div>';
    }
}

/**
 * Display leaderboard data
 */
function displayLeaderboard(cars) {
    const container = document.getElementById('leaderboard');

    if (!cars || cars.length === 0) {
        container.innerHTML = '<div class="loading">No cars found</div>';
        return;
    }

    container.innerHTML = cars.map(car => `
        <div class="leaderboard-row ${car.in_pit ? 'in-pit' : ''}" data-car="${car.car_number}">
            <div class="position">${car.position}</div>
            <div class="car-number">#${car.car_number}</div>
            <div class="team-info">
                <div class="team-name">${car.team_name}</div>
                <div class="car-class">${car.car_class} ${car.current_driver ? '• ' + car.current_driver : ''}</div>
            </div>
            <div class="lap-time">${formatLapTime(car.last_lap_time)}</div>
            <div class="lap-time">${formatLapTime(car.best_lap_time)}</div>
            <div class="gap">${car.gap_to_leader}</div>
        </div>
    `).join('');

    // Add click handlers
    document.querySelectorAll('.leaderboard-row').forEach(row => {
        row.addEventListener('click', () => {
            const carNumber = row.dataset.car;
            document.getElementById('carSelect').value = carNumber;
            selectedCar = carNumber;
            fetchLapTimes(carNumber);
            fetchPrediction(carNumber);
            fetchStrategy(carNumber);
        });
    });
}

/**
 * Update car selection dropdown
 */
function updateCarSelect(cars) {
    const select = document.getElementById('carSelect');
    const currentValue = select.value;

    select.innerHTML = '<option value="">Select a car...</option>' +
        cars.map(car => `
            <option value="${car.car_number}">#${car.car_number} - ${car.team_name}</option>
        `).join('');

    if (currentValue) {
        select.value = currentValue;
    }
}

/**
 * Fetch lap times for a car
 */
async function fetchLapTimes(carNumber) {
    try {
        const response = await fetch(`${API_BASE}/api/lap_times/${carNumber}?limit=30`);
        const data = await response.json();

        updateLapTimeChart(data);

        if (data.length > 0) {
            const latest = data[data.length - 1];
            document.getElementById('lastLap').textContent = formatLapTime(latest.lap_time);

            const best = Math.min(...data.map(lap => lap.lap_time));
            document.getElementById('bestLap').textContent = formatLapTime(best);
        }
    } catch (error) {
        console.error('Error fetching lap times:', error);
    }
}

/**
 * Fetch prediction for a car
 */
async function fetchPrediction(carNumber) {
    try {
        const response = await fetch(`${API_BASE}/api/predictions/${carNumber}`);
        const data = await response.json();

        if (data) {
            document.getElementById('predicted').textContent = formatLapTime(data.predicted_lap_time);

            if (data.delta !== null) {
                const deltaEl = document.getElementById('delta');
                const deltaValue = data.delta;
                deltaEl.textContent = (deltaValue >= 0 ? '+' : '') + deltaValue.toFixed(3) + 's';
                deltaEl.style.color = deltaValue >= 0 ? '#ff3366' : '#00ff88';
            }
        }
    } catch (error) {
        console.error('Error fetching prediction:', error);
    }
}

/**
 * Fetch strategy for a car
 */
async function fetchStrategy(carNumber) {
    try {
        const response = await fetch(`${API_BASE}/api/strategy/${carNumber}`);
        const data = await response.json();

        displayStrategy(data);
    } catch (error) {
        console.error('Error fetching strategy:', error);
    }
}

/**
 * Display strategy recommendation
 */
function displayStrategy(strategy) {
    const container = document.getElementById('strategy');

    if (!strategy) {
        container.innerHTML = '<div class="strategy-empty">No strategy available</div>';
        return;
    }

    container.innerHTML = `
        <div class="strategy-item">
            <div class="strategy-label">Recommended Pit Lap</div>
            <div class="strategy-value">Lap ${strategy.recommended_pit_lap}</div>
        </div>
        <div class="strategy-item">
            <div class="strategy-label">Laps Until Pit</div>
            <div class="strategy-value">${strategy.laps_until_pit} laps</div>
        </div>
        <div class="strategy-item">
            <div class="strategy-label">Fuel Remaining</div>
            <div class="strategy-value">${strategy.fuel_remaining.toFixed(1)} laps</div>
        </div>
        <div class="strategy-item">
            <div class="strategy-label">Tire Change</div>
            <div class="strategy-value">${strategy.optimal_tire_change ? 'Yes' : 'No'}</div>
        </div>
        <div class="strategy-reasoning">${strategy.reasoning}</div>
    `;
}

/**
 * Fetch and display anomalies
 */
async function fetchAnomalies() {
    try {
        const response = await fetch(`${API_BASE}/api/anomalies?limit=10`);
        const data = await response.json();

        displayAnomalies(data);
    } catch (error) {
        console.error('Error fetching anomalies:', error);
    }
}

/**
 * Display anomalies
 */
function displayAnomalies(anomalies) {
    const container = document.getElementById('anomalies');

    if (!anomalies || anomalies.length === 0) {
        container.innerHTML = '<div class="loading">No recent incidents</div>';
        return;
    }

    container.innerHTML = anomalies.map(anomaly => `
        <div class="anomaly-item">
            <div class="anomaly-header">
                <span class="anomaly-car">#${anomaly.car_number}</span>
                <span class="anomaly-type">${anomaly.anomaly_type}</span>
            </div>
            <div class="anomaly-description">
                Lap ${anomaly.lap_number}: ${anomaly.description}
            </div>
        </div>
    `).join('');
}

/**
 * Initialize lap time chart
 */
function initializeChart() {
    const ctx = document.getElementById('lapTimeChart').getContext('2d');

    lapTimeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Lap Time',
                    data: [],
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Predicted',
                    data: [],
                    borderColor: '#00ff88',
                    backgroundColor: 'rgba(0, 255, 136, 0.1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.4,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#a0aec0',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(19, 24, 39, 0.9)',
                    titleColor: '#ffffff',
                    bodyColor: '#a0aec0',
                    borderColor: '#00d4ff',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#718096'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#718096',
                        callback: function (value) {
                            return formatLapTime(value);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Update lap time chart
 */
function updateLapTimeChart(laps) {
    if (!lapTimeChart || !laps || laps.length === 0) return;

    // Filter out pit laps to avoid spikes
    const cleanLaps = laps.filter(lap => !lap.is_pit_lap);
    if (cleanLaps.length === 0) return;

    const labels = cleanLaps.map(lap => `Lap ${lap.lap_number}`);
    const times = cleanLaps.map(lap => lap.lap_time);

    lapTimeChart.data.labels = labels;
    lapTimeChart.data.datasets[0].data = times;
    lapTimeChart.update();
}

/**
 * Format lap time (seconds to MM:SS.mmm)
 */
function formatLapTime(seconds) {
    if (!seconds || seconds === 0) return '--:--';

    const minutes = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(3);

    return `${minutes}:${secs.padStart(6, '0')}`;
}

/**
 * Update last update time
 */
function updateLastUpdateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    document.getElementById('lastUpdate').textContent = `Updated: ${timeStr}`;
}

// Initial update time
updateLastUpdateTime();
