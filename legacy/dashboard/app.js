// Eco-Health AI Dashboard - Modern Single Page

// API Configuration
const API_URL = 'http://localhost:8000';

// Global state
let currentHospitalId = 1;
let charts = {
    surge: null,
    disease: null,
    correlation: null,
    multiFactor: null,
    carbon: null
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function () {
    initializeTheme();
    initializeCharts();
    loadDashboardData();

    // Set up hospital selector
    document.getElementById('hospitalSelect').addEventListener('change', function (e) {
        currentHospitalId = parseInt(e.target.value);
        loadDashboardData();
    });

    // Set up theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);

    // Auto-refresh every 30 seconds
    setInterval(loadDashboardData, 30000);
});

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);

    // Update chart colors
    updateChartThemes();
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('.theme-icon');
    icon.textContent = theme === 'light' ? '🌙' : '☀️';
}

function updateChartThemes() {
    // Re-initialize charts with new theme colors
    Object.values(charts).forEach(chart => {
        if (chart) {
            chart.options.plugins.legend.labels.color = getComputedStyle(document.documentElement)
                .getPropertyValue('--text-primary');
            chart.update();
        }
    });
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
        options: {
            ...commonOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#94a3b8' },
                    grid: { color: '#334155' }
                },
                x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
            }
        }
    });

    // 2. Disease Breakdown Chart (Pie)
    const diseaseCtx = document.getElementById('diseaseBreakdownChart').getContext('2d');
    charts.disease = new Chart(diseaseCtx, {
        type: 'pie',
        data: {
            labels: ['Respiratory', 'Waterborne', 'Heat-Related', 'Trauma', 'Other'],
            datasets: [{
                label: 'Cases',
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',   // Red - Respiratory
                    'rgba(59, 130, 246, 0.8)',   // Blue - Waterborne
                    'rgba(245, 158, 11, 0.8)',   // Orange - Heat
                    'rgba(168, 85, 247, 0.8)',   // Purple - Trauma
                    'rgba(34, 197, 94, 0.8)'     // Green - Other
                ],
                borderWidth: 2,
                borderColor: '#1e293b'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#f1f5f9' },
                    position: 'right'
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

        // Update Temperature
        if (document.getElementById('temperatureValue')) {
            document.getElementById('temperatureValue').textContent = (data.max_temp || 25).toFixed(1) + '°C';
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

        // Update Disease Breakdown Chart (for today - first day)
        if (data.length > 0) {
            // Try to get from latest API or use prediction data
            try {
                const latestResponse = await fetch(`${API_URL}/api/data/latest?hospital_id=${currentHospitalId}`);
                const latestData = await latestResponse.json();

                // Use breakdown from latest data or calculate from first prediction
                const todayPrediction = data[0];
                const totalAdmissions = todayPrediction.predicted_admissions;

                // Calculate disease breakdown (simplified - in real app this would come from API)
                const breakdown = {
                    respiratory: Math.round(totalAdmissions * 0.25),
                    waterborne: Math.round(totalAdmissions * 0.15),
                    heat: Math.round(totalAdmissions * 0.10),
                    trauma: Math.round(totalAdmissions * 0.20),
                    other: Math.round(totalAdmissions * 0.30)
                };

                charts.disease.data.datasets[0].data = [
                    breakdown.respiratory,
                    breakdown.waterborne,
                    breakdown.heat,
                    breakdown.trauma,
                    breakdown.other
                ];
                charts.disease.update();
            } catch (err) {
                console.log('Could not load disease breakdown details');
            }
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

        // Update Multi-Factor Chart (in Analytics tab)
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

    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Load AI recommendations (Resource Recommendations from NESCO logic)
async function loadAIRecommendations() {
    try {
        const response = await fetch(`${API_URL}/api/resources/recommendations?hospital_id=${currentHospitalId}`);
        const data = await response.json();

        const container = document.getElementById('recommendationsList');

        if (!data.success || !data.recommendations || data.recommendations.length === 0) {
            container.innerHTML = '<div class="loading">No resource data available</div>';
            return;
        }

        const recommendation = data.recommendations[0];
        const supplies = recommendation.supplies_status || [];
        const advisory = recommendation.public_advisory;
        const staff = recommendation.staff_requirements;

        let html = '';

        // 1. Public Advisory Section
        if (advisory) {
            const advisoryColor = advisory.level === 'CRITICAL' ? '#ef4444' :
                advisory.level === 'HIGH' ? '#f97316' :
                    advisory.level === 'MODERATE' ? '#eab308' : '#10b981';

            html += `
                <div class="advisory-card" style="border-left: 4px solid ${advisoryColor}; background: rgba(30, 41, 59, 0.7); padding: 1.5rem; border-radius: 0.75rem; margin-bottom: 2rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h3 style="color: ${advisoryColor}; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.5rem;">📢</span> Public Health Advisory
                        </h3>
                        <span style="background: ${advisoryColor}20; color: ${advisoryColor}; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600;">
                            ${advisory.level}
                        </span>
                    </div>
                    <p style="color: #e2e8f0; font-size: 1.1rem; margin-bottom: 1rem;">${advisory.message}</p>
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                        ${advisory.actions.map(action =>
                `<span style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 0.9rem;">• ${action}</span>`
            ).join('')}
                    </div>
                </div>
            `;
        }

        // 2. Staff Requirements Section (Gemini-based, no current staff)
        if (staff) {
            html += `
                <h3 style="margin-bottom: 1rem; color: #f8fafc;">Staffing Requirements (AI Recommended)</h3>
                <div class="staff-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
            `;

            // Doctors
            if (staff.doctors) {
                const statusColor = staff.doctors.status === 'CRITICAL' ? '#ef4444' :
                    staff.doctors.status === 'FALLBACK' ? '#f97316' : '#10b981';
                html += `
                    <div class="staff-card" style="background: rgba(30, 41, 59, 0.5); padding: 1rem; border-radius: 0.75rem; border: 1px solid rgba(255,255,255,0.1);">
                        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                            <span style="font-size: 1.5rem;">👨‍⚕️</span>
                            <h4 style="margin: 0; color: #e2e8f0;">Doctors</h4>
                        </div>
                        <div style="text-align: center; margin: 1rem 0;">
                            <div style="font-size: 2rem; font-weight: 700; color: #f8fafc;">${staff.doctors.required}</div>
                            <div style="color: #94a3b8; font-size: 0.875rem;">Required</div>
                        </div>
                        <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.1); text-align: center;">
                            <span style="color: ${statusColor}; font-weight: 600; font-size: 0.875rem;">
                                ${staff.doctors.status}
                            </span>
                        </div>
                    </div>
                `;
            }

            // Nurses
            if (staff.nurses) {
                const statusColor = staff.nurses.status === 'CRITICAL' ? '#ef4444' :
                    staff.nurses.status === 'FALLBACK' ? '#f97316' : '#10b981';
                html += `
                    <div class="staff-card" style="background: rgba(30, 41, 59, 0.5); padding: 1rem; border-radius: 0.75rem; border: 1px solid rgba(255,255,255,0.1);">
                        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                            <span style="font-size: 1.5rem;">👩‍⚕️</span>
                            <h4 style="margin: 0; color: #e2e8f0;">Nurses</h4>
                        </div>
                        <div style="text-align: center; margin: 1rem 0;">
                            <div style="font-size: 2rem; font-weight: 700; color: #f8fafc;">${staff.nurses.required}</div>
                            <div style="color: #94a3b8; font-size: 0.875rem;">Required</div>
                        </div>
                        <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.1); text-align: center;">
                            <span style="color: ${statusColor}; font-weight: 600; font-size: 0.875rem;">
                                ${staff.nurses.status}
                            </span>
                        </div>
                    </div>
                `;
            }

            // Support Staff
            if (staff.support) {
                const statusColor = staff.support.status === 'CRITICAL' ? '#ef4444' :
                    staff.support.status === 'FALLBACK' ? '#f97316' : '#10b981';
                html += `
                    <div class="staff-card" style="background: rgba(30, 41, 59, 0.5); padding: 1rem; border-radius: 0.75rem; border: 1px solid rgba(255,255,255,0.1);">
                        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                            <span style="font-size: 1.5rem;">🏥</span>
                            <h4 style="margin: 0; color: #e2e8f0;">Support Staff</h4>
                        </div>
                        <div style="text-align: center; margin: 1rem 0;">
                            <div style="font-size: 2rem; font-weight: 700; color: #f8fafc;">${staff.support.required}</div>
                            <div style="color: #94a3b8; font-size: 0.875rem;">Required</div>
                        </div>
                        <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.1); text-align: center;">
                            <span style="color: ${statusColor}; font-weight: 600; font-size: 0.875rem;">
                                ${staff.support.status}
                            </span>
                        </div>
                    </div>
                `;
            }

            html += `</div><h3 style="margin-bottom: 1rem; color: #f8fafc;">Supply Recommendations</h3>`;
        }

        // 3. Supply Recommendations (Existing Logic)
        const urgentSupplies = supplies.filter(s => s.status === 'CRITICAL' || s.status === 'LOW');
        const displaySupplies = urgentSupplies.length > 0 ? urgentSupplies : supplies;

        displaySupplies.forEach(supply => {
            const priorityClass = supply.status === 'CRITICAL' ? 'priority-high' :
                supply.status === 'LOW' ? 'priority-medium' : 'priority-low';

            html += `
                <div class="recommendation-card">
                    <div class="recommendation-header">
                        <span class="recommendation-icon">${getSupplyIcon(supply.item_name)}</span>
                        <h4 class="recommendation-title">${supply.item_name}</h4>
                    </div>
                    <div class="recommendation-description">
                        <p><strong>Current Stock:</strong> ${supply.current_stock}</p>
                        <p><strong>Needed:</strong> ${supply.projected_need}</p>
                        ${supply.quantity_to_order > 0 ?
                    `<p><strong>Order:</strong> ${supply.quantity_to_order} units</p>` : ''}
                    </div>
                    <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                        <span class="recommendation-priority ${priorityClass}">
                            ${supply.status}
                        </span>
                        ${supply.action_required !== 'None' ?
                    `<span class="recommendation-priority priority-high">
                                ${supply.action_required}
                            </span>` : ''}
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;

    } catch (error) {
        console.error('Error loading resource recommendations:', error);
        document.getElementById('recommendationsList').innerHTML =
            '<div class="loading">Error loading recommendations</div>';
    }
}

function getSupplyIcon(itemName) {
    const icons = {
        'Oxygen Cylinders': '💨',
        'Ventilators': '🫁',
        'Oxygen Masks': '😷',
        'Humidifiers': '💧',
        'Trauma Stretchers': '🛏️',
        'IV Stand Kits': '💉',
        'Defibrillators': '⚡',
        'Gloves/PPE': '🧤',
        'Cooling Pads': '🧊',
        'Thermometers': '🌡️'
    };
    return icons[itemName] || '📦';
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
