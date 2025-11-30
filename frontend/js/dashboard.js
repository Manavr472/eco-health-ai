// Dashboard.js - Dynamic Data Integration
let surgeChart, carbonChart;
let lastUpdateTime = new Date();

// Initialize Dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Initializing Eco-Health AI Dashboard...');

    // Initial load
    await loadDashboardData();

    // Auto-refresh every 30 seconds
    setInterval(async () => {
        await loadDashboardData();
    }, 30000);

    // Update "last updated" time every 10 seconds
    setInterval(updateLastUpdatedTime, 10000);
});

// Main function to load all dashboard data
async function loadDashboardData() {
    try {
        console.log('📊 Fetching dashboard data...');
        const data = await ecoHealthAPI.getAllDashboardData();

        if (!data) {
            console.error('❌ Failed to fetch dashboard data');
            showErrorState();
            return;
        }

        console.log('✅ Data received:', data);

        // Update all dashboard sections
        updateEnvironmentalData(data);
        updateHospitalStatus(data);
        updateSurgeChart(data);
        updateDepartmentImpact(data);
        updateCarbonImpact(data);

        lastUpdateTime = data.timestamp;
        updateLastUpdatedTime();

        console.log('✨ Dashboard updated successfully');
    } catch (error) {
        console.error('❌ Error loading dashboard:', error);
        showErrorState();
    }
}

// Update Environmental Data (AQI, Rainfall, Festival)
function updateEnvironmentalData(data) {
    const latest = data.latestData;

    if (latest) {
        // Update AQI
        const aqi = latest.aqi || 0;
        const aqiStatus = getAQIStatus(aqi);

        const aqiValue = document.getElementById('aqi-value');
        const aqiBadge = document.getElementById('aqi-badge');
        const aqiProgress = document.getElementById('aqi-progress');

        if (aqiValue) aqiValue.textContent = Math.round(aqi);
        if (aqiBadge) {
            aqiBadge.textContent = aqiStatus.label;
            aqiBadge.className = `badge ${aqiStatus.class}`;
        }
        if (aqiProgress) {
            const aqiPercent = Math.min((aqi / 500) * 100, 100);
            aqiProgress.style.width = `${aqiPercent}%`;
        }

        // Update Rainfall
        const rainfall = latest.rainfall_mm || 0;
        const rainfallStatus = getRainfallStatus(rainfall);

        const rainfallValue = document.getElementById('rainfall-value');
        const rainfallBadge = document.getElementById('rainfall-badge');
        const rainfallProgress = document.getElementById('rainfall-progress');

        if (rainfallValue) rainfallValue.textContent = rainfall.toFixed(1) + 'mm';
        if (rainfallBadge) {
            rainfallBadge.textContent = rainfallStatus.label;
            if (rainfallStatus.class) {
                rainfallBadge.className = `badge ${rainfallStatus.class}`;
            } else {
                rainfallBadge.className = 'badge';
                rainfallBadge.style.backgroundColor = '#f1f5f9';
                rainfallBadge.style.color = '#475569';
            }
        }
        if (rainfallProgress) {
            const rainfallPercent = Math.min((rainfall / 50) * 100, 100);
            rainfallProgress.style.width = `${rainfallPercent}%`;
        }

        // Update Festival/Event Impact
        const eventName = latest.active_events;
        const eventBadge = document.getElementById('event-badge');
        const eventDesc = document.getElementById('event-description');

        if (eventBadge) {
            if (eventName && eventName !== "None" && eventName !== null) {
                // Active events detected
                eventBadge.textContent = eventName;
                eventBadge.className = 'badge';
                eventBadge.style.backgroundColor = '#fff7ed';
                eventBadge.style.color = '#c2410c';
                if (eventDesc) {
                    eventDesc.textContent = "Elevated health risk - monitor patient surge patterns";
                    eventDesc.className = 'text-red text-sm font-medium';
                }
            } else {
                // No active events - all clear
                eventBadge.textContent = "All Clear";
                eventBadge.className = 'badge badge-green';
                if (eventDesc) {
                    eventDesc.textContent = "No major festivals or seasonal events. Normal operations expected.";
                    eventDesc.className = 'text-gray text-sm font-medium';
                }
            }
        }
    }
}

// Update Hospital Status (Patients, Bed Occupancy, Carbon Credits)
function updateHospitalStatus(data) {
    const monitor = data.carbonMonitor;
    const credits = data.carbonCredits;
    const latest = data.latestData;

    // Update Current Patients
    let currentPatients = 0;
    if (latest && latest.total_admissions_today) {
        currentPatients = latest.total_admissions_today;
    } else if (monitor && monitor.hospital_reports && monitor.hospital_reports.length > 0) {
        const kemHospital = monitor.hospital_reports.find(h => h.hospital_id === 'KEM_H1') || monitor.hospital_reports[0];
        currentPatients = kemHospital.total_admissions || 0;
    }

    const currentPatientsEl = document.getElementById('current-patients');
    if (currentPatientsEl) currentPatientsEl.textContent = currentPatients;

    // Update Bed Occupancy
    const totalBeds = 500; // Standard bed count for KEM
    const bedOccupancy = Math.round((currentPatients / totalBeds) * 100);
    const bedOccupancyEl = document.getElementById('bed-occupancy');
    const bedProgress = document.getElementById('bed-progress');

    if (bedOccupancyEl) bedOccupancyEl.textContent = bedOccupancy + '%';
    if (bedProgress) bedProgress.style.width = `${Math.min(bedOccupancy, 100)}%`;

    // Update Carbon Credits
    if (credits && credits.carbon_credits) {
        const creditValue = credits.carbon_credits.credit_value_inr || 0;
        const carbonCreditsEl = document.getElementById('carbon-credits');
        if (carbonCreditsEl) carbonCreditsEl.textContent = formatCurrency(creditValue);
    }
}

// Update Surge Prediction Chart
function updateSurgeChart(data) {
    const predictions = data.surgePredictions?.predictions || [];

    if (predictions.length === 0) {
        initSurgeChart(); // Fallback to static
        return;
    }

    // Update description
    const surgeDesc = document.getElementById('surge-description');
    if (surgeDesc && predictions.length > 0) {
        const avgMultiplier = predictions.reduce((sum, p) => sum + p.surge_multiplier, 0) / predictions.length;
        const increasePercent = Math.round((avgMultiplier - 1) * 100);
        surgeDesc.textContent = `Predicted ${increasePercent}% ${increasePercent > 0 ? 'increase' : 'decrease'} in admissions over the coming week`;
    }

    // Prepare data for chart
    const labels = [];
    const predictedData = [];
    const currentData = [];

    predictions.forEach((pred, index) => {
        const date = new Date(pred.date);
        labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));
        predictedData.push(pred.predicted_admissions);

        // Show actual data for past days only (show none since these are future predictions)
        currentData.push(null);
    });

    // Destroy existing chart if it exists
    if (surgeChart) {
        surgeChart.destroy();
    }

    // Create new chart
    const ctx = document.getElementById('surgeChart').getContext('2d');
    surgeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Predicted Surge',
                    data: predictedData,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 3,
                    pointRadius: 5,
                    pointBackgroundColor: '#ef4444',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function (context) {
                            return `Predicted: ${context.parsed.y} patients`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: Math.max(...predictedData) * 1.2,
                    grid: {
                        color: '#f1f5f9',
                        borderDash: [5, 5]
                    },
                    ticks: {
                        callback: function (value) {
                            return Math.round(value);
                        }
                    }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

// Update Department Impact
function updateDepartmentImpact(data) {
    const forecast = data.departmentForecast;

    if (forecast && forecast.departments) {
        const departments = forecast.departments;

        // Define the order of departments to display
        const deptOrder = ['emergency', 'respiratory', 'cardiology', 'general'];

        deptOrder.forEach(deptId => {
            const dept = departments[deptId];
            if (!dept) return;

            const textEl = document.getElementById(`dept-${deptId}`);
            const badgeEl = document.getElementById(`dept-${deptId}-badge`);

            if (textEl && dept.current >= 0) {
                textEl.textContent = `Current: ${dept.current} → Predicted: ${dept.predicted}`;
            } else if (textEl) {
                textEl.textContent = `Loading...`;
            }

            if (badgeEl && dept.current > 0) {
                const increase = Math.round(((dept.predicted - dept.current) / dept.current) * 100);
                badgeEl.textContent = `+${increase}%`;

                // Color coding based on increase severity
                if (increase > 30) {
                    badgeEl.className = 'badge badge-red';
                } else if (increase > 15) {
                    badgeEl.className = 'badge';
                    badgeEl.style.backgroundColor = '#fb923c'; // Orange
                    badgeEl.style.color = '#ffffff';
                } else {
                    badgeEl.className = 'badge';
                    badgeEl.style.backgroundColor = '#f1f5f9';
                    badgeEl.style.color = '#475569';
                }
            } else if (badgeEl) {
                badgeEl.textContent = '--';
                badgeEl.className = 'badge badge-gray';
            }
        });
    } else {
        console.warn('⚠️ No department forecast data available');
    }
}

// Update Carbon Impact Chart
function updateCarbonImpact(data) {
    const credits = data.carbonCredits;

    let energyPercent = 45;
    let supplyPercent = 30;
    let wastePercent = 25;

    if (credits && credits.energy_savings) {
        energyPercent = Math.round(credits.energy_savings.savings_percentage || 45);
        supplyPercent = Math.round((100 - energyPercent) * 0.55);
        wastePercent = 100 - energyPercent - supplyPercent;
    }

    // Destroy existing chart
    if (carbonChart) {
        carbonChart.destroy();
    }

    // Create new chart
    const ctx = document.getElementById('carbonChart').getContext('2d');
    carbonChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Energy Reduction', 'Supply Optimization', 'Waste Management'],
            datasets: [{
                data: [energyPercent, supplyPercent, wastePercent],
                backgroundColor: ['#10b981', '#3b82f6', '#8b5cf6'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.label}: ${context.parsed}%`;
                        }
                    }
                }
            }
        }
    });
}

// Update last updated time
function updateLastUpdatedTime() {
    const element = document.getElementById('last-updated');
    if (element) {
        element.textContent = getRelativeTime(lastUpdateTime);
    }
}

// Show error state
function showErrorState() {
    console.warn('⚠️ Using fallback static data');
    // Initialize with static data
    initSurgeChart();
    initCarbonChart();
}

// Fallback: Initialize with static data
function initSurgeChart() {
    const ctx = document.getElementById('surgeChart')?.getContext('2d');
    if (!ctx) return;

    const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const predictedData = [155, 158, 160, 185, 210, 190, 175];

    if (surgeChart) surgeChart.destroy();

    surgeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Predicted Surge',
                    data: predictedData,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 3,
                    pointRadius: 5,
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 250,
                    grid: {
                        color: '#f1f5f9',
                        borderDash: [5, 5]
                    }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

function initCarbonChart() {
    const ctx = document.getElementById('carbonChart')?.getContext('2d');
    if (!ctx) return;

    if (carbonChart) carbonChart.destroy();

    carbonChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Energy Reduction', 'Supply Optimization', 'Waste Management'],
            datasets: [{
                data: [45, 30, 25],
                backgroundColor: ['#10b981', '#3b82f6', '#8b5cf6'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: { display: false }
            }
        }
    });
}
