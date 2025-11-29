
// Initialize Charts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initSurgeChart();
    initCarbonChart();
});

function initSurgeChart() {
    const ctx = document.getElementById('surgeChart').getContext('2d');

    // Data points for the chart
    // Data points for the chart - 7 Days
    const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const currentData = [155, 150, 145, null, null, null, null];
    const predictedData = [155, 158, 160, 185, 210, 190, 175];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Actual Patients',
                    data: currentData,
                    borderColor: '#3b82f6', // Blue
                    backgroundColor: '#3b82f6',
                    borderWidth: 2,
                    pointRadius: 4,
                    tension: 0.1,
                    fill: false
                },
                {
                    label: 'Predicted Surge',
                    data: predictedData,
                    borderColor: '#ef4444', // Red
                    backgroundColor: '#ef4444',
                    borderWidth: 2,
                    borderDash: [5, 5], // Dashed line
                    pointRadius: 0,
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
                    display: false // Hide default legend to match design or keep simple
                },
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
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function initCarbonChart() {
    const ctx = document.getElementById('carbonChart').getContext('2d');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Energy Reduction', 'Supply Optimization', 'Waste Management'],
            datasets: [{
                data: [45, 30, 25],
                backgroundColor: [
                    '#10b981', // Green
                    '#3b82f6', // Blue
                    '#8b5cf6'  // Purple
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%', // Thinner donut
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}
