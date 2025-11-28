// Eco-Health AI Dashboard - Interactive Application

// API Configuration
const API_URL = 'http://localhost:8000';

// Global state
let currentHospitalId = 1;
let charts = {
    surge: null,
    aqi: null,
    correlation: null,
    multiFactor: null,
    carbon: null
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function () {
    initializeCharts();
    loadDashboardData();

    // Set up hospital selector
    document.getElementById('hospitalSelect').addEventListener('change', function (e) {
        currentHospitalId = parseInt(e.target.value);
        loadDashboardData();
    });

    // Auto-refresh every 30 seconds
    setInterval(loadDashboardData, 30000);
});

// Tab Switching Logic
function switchTab(tabId) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabId}`).classList.add('active');
}

// Initialize Chart.js charts
function initializeCharts() {
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#f1f5f9' } }
        },
        scales: {
            y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
            x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
        }
    };

    // 1. Surge Prediction Chart
    const surgeCtx = document.getElementById('surgePredictionChart').getContext('2d');
    charts.surge = new Chart(surgeCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Predicted Admissions',
                data: [],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: commonOptions
    });

    // 2. Historical AQI Chart
    const aqiCtx = document.getElementById('aqiTrendChart').getContext('2d');
    charts.aqi = new Chart(aqiCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'AQI History',
                data: [],
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                annotation: {
                    annotations: {
                        line1: {
                            type: 'line',
                            yMin: 200,
                            yMax: 200,
                            borderColor: '#ef4444',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            label: { content: 'Poor AQI', enabled: true }
                        }
                    }
                }
            }
        }
    });

    // 3. Correlation Chart (Analytics)
    const corrCtx = document.getElementById('correlationChart').getContext('2d');
    charts.correlation = new Chart(corrCtx, {
        type: 'bar',
        data: {
            labels: ['AQI Impact', 'Rainfall Impact', 'Temperature Impact'],
            datasets: [{
                label: 'Correlation with Admissions',
                data: [0, 0, 0],
                backgroundColor: ['#f59e0b', '#3b82f6', '#ef4444']
            }]
        },
        options: commonOptions
    });

    // 4. Multi-Factor Chart (Analytics)
    const multiCtx = document.getElementById('multiFactorChart').getContext('2d');
    charts.multiFactor = new Chart(multiCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Admissions',
                    data: [],
                    borderColor: '#ef4444',
                    yAxisID: 'y'
                },
                {
                    label: 'AQI',
                    data: [],
                    borderColor: '#f59e0b',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });

    // 5. Carbon Chart (Sustainability)
    const carbonCtx = document.getElementById('carbonChart').getContext('2d');
    charts.carbon = new Chart(carbonCtx, {
        type: 'bar',
        data: {
            labels: ['Baseline Emissions', 'Optimized Emissions'],
            datasets: [{
                label: 'Tons CO2',
                data: [0, 0],
                backgroundColor: ['#94a3b8', '#10b981']
            }]
        },
        options: commonOptions
    });
}

// Load all dashboard data
async function loadDashboardData() {
    try {
        await Promise.all([
            loadKPIs(),
            loadSurgePredictions(),
            loadHistoricalData(),
            loadAnalytics(),
            loadAIRecommendations(),
            loadSustainabilityData()
        ]);

        updateLastUpdateTime();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Load KPI cards
async function loadKPIs() {
    try {
        const response = await fetch(`${API_URL}/api/data/latest?hospital_id=${currentHospitalId}`);
        const data = await response.json();

        document.getElementById('currentAQI').textContent = Math.round(data.aqi);
        document.getElementById('aqiCategory').textContent = getAQICategory(data.aqi);
        document.getElementById('aqiCategory').style.color = getAQIColor(data.aqi);

        // Update Rainfall
        if (document.getElementById('rainfallValue')) {
            document.getElementById('rainfallValue').textContent = (data.rainfall_mm || 0).toFixed(1) + ' mm';
        }

        // Update Event
        if (document.getElementById('eventValue')) {
            document.getElementById('eventValue').textContent = data.active_events || 'None';
        }

    } catch (error) {
        console.error('Error loading KPIs:', error);
    }
}

// Load surge predictions
async function loadSurgePredictions() {
    try {
        const response = await fetch(`${API_URL}/api/predictions/surge?hospital_id=${currentHospitalId}&days_ahead=7`);
        const data = await response.json();

        const labels = data.map(d => formatDate(d.date));
        const values = data.map(d => d.predicted_admissions);

        charts.surge.data.labels = labels;
        charts.surge.data.datasets[0].data = values;
        charts.surge.update();

        // Update KPI
        const maxSurge = Math.max(...data.map(d => d.surge_multiplier));
        const maxData = data.find(d => d.surge_multiplier === maxSurge);

        document.getElementById('surgeMultiplier').textContent = maxSurge.toFixed(1) + 'x';
        document.getElementById('surgeDate').textContent = `Peak on ${formatDate(maxData.date)}`;
        document.getElementById('surgeDate').style.color = maxSurge > 1.5 ? '#ef4444' : '#10b981';

        // Display Gemini Narrative in Alert Banner if surge is high
        const banner = document.getElementById('alertBanner');
        if (maxSurge > 1.2 && maxData.surge_reasons) {
            banner.classList.remove('hidden');
            banner.querySelector('p').innerHTML = `<strong>AI FORECAST:</strong> ${maxData.surge_reasons}`;
        } else {
            banner.classList.add('hidden');
        }

    } catch (error) {
        console.error('Error loading predictions:', error);
    }
}

// Load real historical data
async function loadHistoricalData() {
    try {
        const response = await fetch(`${API_URL}/api/data/historical?hospital_id=${currentHospitalId}&days=30`);
        const data = await response.json();

        // Update AQI Chart
        charts.aqi.data.labels = data.dates.map(d => formatDate(d));
        charts.aqi.data.datasets[0].data = data.aqi;
        charts.aqi.update();

        // Update Multi-Factor Chart
        charts.multiFactor.data.labels = data.dates.map(d => formatDate(d));
        charts.multiFactor.data.datasets[0].data = data.admissions;
        charts.multiFactor.data.datasets[1].data = data.aqi;
        charts.multiFactor.update();

    } catch (error) {
        console.error('Error loading historical data:', error);
    }
}

// Load analytics and correlation
async function loadAnalytics() {
    try {
        const response = await fetch(`${API_URL}/api/analytics/correlation?hospital_id=${currentHospitalId}`);
        const data = await response.json();

        // Update Correlation Chart
        charts.correlation.data.datasets[0].data = [
            data.correlations.aqi_vs_admissions,
            data.correlations.rainfall_vs_admissions,
            data.correlations.temp_vs_admissions
        ];
        charts.correlation.update();

        // Update Surge Events Table
        const tableContainer = document.getElementById('surgeEventsTableContainer');
        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Admissions</th>
                        <th>Severity</th>
                        <th>Primary Causes</th>
                    </tr>
                </thead>
                <tbody>
        `;

        data.surge_events.reverse().forEach(event => {
            html += `
                <tr>
                    <td>${formatDate(event.date)}</td>
                    <td>${event.admissions} (${event.multiplier.toFixed(1)}x)</td>
                    <td><span class="priority-badge ${event.severity.toLowerCase()}">${event.severity}</span></td>
                    <td>${event.causes.join(', ')}</td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        tableContainer.innerHTML = html;

    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Load AI recommendations
async function loadAIRecommendations() {
    try {
        const response = await fetch(`${API_URL}/api/recommendations?hospital_id=${currentHospitalId}&days_ahead=5`);
        const data = await response.json();

        // Update Readiness Score
        document.getElementById('readinessScore').textContent = data.readiness_score + '/100';
        const status = data.readiness_score >= 90 ? '✓ Excellent' : data.readiness_score >= 70 ? '⚠ Fair' : '✗ Critical';
        document.getElementById('readinessStatus').textContent = status;
        document.getElementById('readinessStatus').style.color = data.readiness_score >= 90 ? '#10b981' : data.readiness_score >= 70 ? '#f59e0b' : '#ef4444';

        // Render Recommendations
        const container = document.getElementById('recommendationsList');
        container.innerHTML = '';

        if (data.recommendations && data.recommendations.length > 0) {
            data.recommendations.forEach(rec => {
                container.appendChild(createRecommendationCard(rec));
            });
        } else {
            container.innerHTML = '<div class="loading">No active recommendations. Operations normal.</div>';
        }

        // Render Timeline
        const timelineContainer = document.getElementById('actionTimeline');
        timelineContainer.innerHTML = '';

        data.action_timeline.forEach(item => {
            timelineContainer.appendChild(createTimelineItem(item));
        });

        // Update Resources
        // Note: In a real app, we'd get actual resource data. Here we simulate based on agent plan.
        updateResourceBar('doctors', { current: 18, required: 20 });
        updateResourceBar('nurses', { current: 55, required: 60 });
        updateResourceBar('support', { current: 28, required: 30 });
        updateResourceBar('ppe', { current: 450, required: 600 });
        updateResourceBar('oxygen', { current: 2500, required: 3000 });
        updateResourceBar('meds', { current: 1200, required: 1500 });

    } catch (error) {
        console.error('Error loading recommendations:', error);
    }
}

// Load sustainability data
async function loadSustainabilityData() {
    try {
        const response = await fetch(`${API_URL}/api/sustainability/impact`);
        const data = await response.json();

        document.getElementById('carbonCredits').textContent = Math.round(data.estimated_carbon_reduction_tons);
        document.getElementById('totalCO2').textContent = data.estimated_carbon_reduction_tons.toFixed(1);
        document.getElementById('carbonRevenue').textContent = '$' + data.estimated_value_usd.toFixed(0);
        document.getElementById('efficiencyGain').textContent = '32%'; // Simulated

        // Update Chart
        charts.carbon.data.datasets[0].data = [
            data.estimated_carbon_reduction_tons * 1.4, // Baseline (simulated)
            data.estimated_carbon_reduction_tons // Optimized
        ];
        charts.carbon.update();

    } catch (error) {
        console.error('Error loading sustainability:', error);
    }
}

// Helpers
function createRecommendationCard(rec) {
    const card = document.createElement('div');
    card.className = `recommendation-card ${rec.priority.toLowerCase()}-priority`;

    const detailsList = rec.details.map(detail => `<li>${detail}</li>`).join('');

    card.innerHTML = `
        <div class="recommendation-header">
            <div class="recommendation-title">${rec.category}</div>
            <span class="priority-badge ${rec.priority.toLowerCase()}">${rec.priority}</span>
        </div>
        <p style="color: #f1f5f9; margin-bottom: 1rem; font-weight: 500">${rec.action}</p>
        <ul class="recommendation-details">${detailsList}</ul>
    `;
    return card;
}

function createTimelineItem(item) {
    const div = document.createElement('div');
    div.className = `timeline-item ${item.priority === 'URGENT' ? 'urgent' : ''}`;

    div.innerHTML = `
        <div class="timeline-date">${item.date}</div>
        <div class="timeline-content">
            <div class="timeline-action">${item.action}</div>
            <div class="timeline-details">
                <span style="color: ${item.priority === 'URGENT' ? '#ef4444' : '#f59e0b'}">${item.priority}</span>
                • ${item.category}
            </div>
        </div>
    `;
    return div;
}

function updateResourceBar(id, resource) {
    const percentage = (resource.current / resource.required) * 100;
    const bar = document.getElementById(id + 'Bar');
    const value = document.getElementById(id + 'Value');

    if (bar && value) {
        bar.style.width = Math.min(percentage, 100) + '%';
        bar.style.background = percentage >= 90 ? 'linear-gradient(90deg, #10b981, #059669)' :
            percentage >= 70 ? 'linear-gradient(90deg, #f59e0b, #d97706)' :
                'linear-gradient(90deg, #ef4444, #dc2626)';
        value.textContent = `${resource.current} / ${resource.required}`;
    }
}

function getAQICategory(aqi) {
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Satisfactory';
    if (aqi <= 200) return 'Moderate';
    if (aqi <= 300) return 'Poor';
    if (aqi <= 400) return 'Very Poor';
    return 'Severe';
}

function getAQIColor(aqi) {
    if (aqi <= 100) return '#10b981';
    if (aqi <= 200) return '#f59e0b';
    return '#ef4444';
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function updateLastUpdateTime() {
    const now = new Date();
    document.getElementById('lastUpdate').textContent = now.toLocaleTimeString();
}

function closeAlert() {
    document.getElementById('alertBanner').classList.add('hidden');
}
