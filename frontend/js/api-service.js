// API Service for Eco-Health AI Dashboard
// Base URL - update this to match your backend
const API_BASE_URL = 'http://localhost:8000';

// API Service Class
class EcoHealthAPI {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
        this.hospitalId = 'KEM_H1'; // Default hospital
        this.hospitalIdInt = 1; // For endpoints that use integer IDs
        this.numBeds = 500;
    }

    // Fetch with error handling
    async fetchAPI(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            return null;
        }
    }

    // Get live carbon monitoring data
    async getCarbonMonitor() {
        return await this.fetchAPI('/api/carbon/monitor');
    }

    // Get carbon credits report
    async getCarbonCredits(hospitalId = this.hospitalId, numBeds = this.numBeds, applyAll = false) {
        // Backend endpoint: /api/sustainability/carbon-credits
        return await this.fetchAPI(`/api/sustainability/carbon-credits`);
    }

    // Get surge predictions
    async getSurgePredictions(hospitalId = this.hospitalIdInt, daysAhead = 7) {
        return await this.fetchAPI(`/api/predictions/surge?hospital_id=${hospitalId}&days_ahead=${daysAhead}`);
    }

    // Get recommendations
    async getRecommendations(hospitalId = this.hospitalIdInt, daysAhead = 5) {
        return await this.fetchAPI(`/api/recommendations?hospital_id=${hospitalId}&days_ahead=${daysAhead}`);
    }

    // Get latest environmental data
    async getLatestData(hospitalId = this.hospitalIdInt) {
        return await this.fetchAPI(`/api/data/latest?hospital_id=${hospitalId}`);
    }

    // Get department forecast
    async getDepartmentForecast(hospitalId = this.hospitalIdInt) {
        return await this.fetchAPI(`/api/departments/forecast?hospital_id=${hospitalId}`);
    }

    // Get all dashboard data
    async getAllDashboardData() {
        const [carbonMonitor, carbonCredits, surgePredictions, recommendations, latestData, departmentForecast] = await Promise.all([
            this.getCarbonMonitor(),
            this.getCarbonCredits(),
            this.getSurgePredictions(),
            this.getRecommendations(),
            this.getLatestData(),
            this.getDepartmentForecast()
        ]);

        return {
            carbonMonitor,
            carbonCredits,
            surgePredictions,
            recommendations,
            latestData,
            departmentForecast,
            timestamp: new Date()
        };
    }
}

// Create global API instance
const ecoHealthAPI = new EcoHealthAPI();

// Helper Functions
function getAQIStatus(aqi) {
    if (aqi <= 50) return { label: 'Good', class: 'badge-green' };
    if (aqi <= 100) return { label: 'Moderate', class: 'badge-yellow' };
    if (aqi <= 150) return { label: 'Unhealthy for Sensitive', class: 'badge-orange' };
    if (aqi <= 200) return { label: 'Unhealthy', class: 'badge-red' };
    if (aqi <= 300) return { label: 'Very Unhealthy', class: 'badge-red' };
    return { label: 'Hazardous', class: 'badge-red' };
}

function getRainfallStatus(rainfall) {
    if (rainfall < 5) return { label: 'Light', class: 'badge-green' };
    if (rainfall < 15) return { label: 'Moderate', class: '' };
    if (rainfall < 30) return { label: 'Heavy', class: 'badge-orange' };
    return { label: 'Very Heavy', class: 'badge-red' };
}

function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toFixed(0);
}

function formatCurrency(amount) {
    return '₹' + formatNumber(amount);
}

function getRelativeTime(timestamp) {
    const now = new Date();
    const diff = Math.floor((now - timestamp) / 1000); // seconds

    if (diff < 60) return `${diff} seconds ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    return `${Math.floor(diff / 86400)} days ago`;
}
