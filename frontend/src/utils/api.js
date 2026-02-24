import axios from 'axios';

// Remove trailing slash from VITE_API_URL if present
const API_BASE_URL = import.meta.env.VITE_API_URL?.replace(/\/+$/, '') || '/api';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add JWT token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// -----------------------------
// Auth API
// -----------------------------
export const authAPI = {
    login: (credentials) => api.post('/api/auth/login', credentials),  // Always include /api
    getCurrentUser: () => api.get('/api/auth/me'),
    createUser: (userData) => api.post('/api/auth/users', userData),
    updateUser: (userId, userData) => api.put(`/api/auth/users/${userId}`, userData),
    listUsers: (role) => api.get('/api/auth/users', { params: { role } }),
};

// Users Management API
export const usersAPI = {
    list: (params) => api.get('/api/auth/users', { params }),
    create: (userData) => api.post('/api/auth/users', userData),
    update: (userId, userData) => api.put(`/api/auth/users/${userId}`, userData),
    toggleStatus: (userId) => api.patch(`/api/auth/users/${userId}/status`),
    resetPassword: (userId, newPassword) =>
        api.post(`/api/auth/users/${userId}/reset-password`, { new_password: newPassword }),
    delete: (userId) => api.delete(`/api/auth/users/${userId}`),
};

// Analytics API
export const analyticsAPI = {
    getSummary: () => api.get('/api/dashboard/analytics/summary'),
    getUsers: () => api.get('/api/dashboard/analytics/users'),
    getChildren: (period = 'month') => api.get('/api/dashboard/analytics/children', { params: { period } }),
    getPredictions: () => api.get('/api/dashboard/analytics/predictions'),
};

// Children API
export const childrenAPI = {
    create: (childData) => api.post('/api/children', childData),
    getById: (childId) => api.get(`/api/children/${childId}`),
    list: (filters) => api.get('/api/children', { params: filters }),
    update: (childId, childData) => api.put(`/api/children/${childId}`, childData),
    getAssessments: (childId) => api.get(`/api/children/${childId}/assessments`),
};

// Assessments API
export const assessmentsAPI = {
    create: (assessmentData) => api.post('/api/assessments', assessmentData),
    getById: (assessmentId) => api.get(`/api/assessments/${assessmentId}`),
    list: (limit) => api.get('/api/assessments', { params: { limit } }),
};

// Predictions API
export const predictionsAPI = {
    generate: (assessmentId) => api.post(`/api/predictions/${assessmentId}/predict`),
    getById: (predictionId) => api.get(`/api/predictions/${predictionId}`),
};

// Referrals API
export const referralsAPI = {
    create: (referralData) => api.post('/api/referrals', referralData),
    update: (referralId, updateData) => api.put(`/api/referrals/${referralId}`, updateData),
    getById: (referralId) => api.get(`/api/referrals/${referralId}`),
    getByChild: (childId) => api.get(`/api/referrals/child/${childId}`),
    list: (statusFilter) => api.get('/api/referrals', { params: { status_filter: statusFilter } }),
};

// Interventions API
export const interventionsAPI = {
    create: (interventionData) => api.post('/api/interventions', interventionData),
    update: (interventionId, updateData) => api.put(`/api/interventions/${interventionId}`, updateData),
    getById: (interventionId) => api.get(`/api/interventions/${interventionId}`),
    getByChild: (childId, activeOnly) =>
        api.get(`/api/interventions/child/${childId}`, { params: { active_only: activeOnly } }),
    list: (filters) => api.get('/api/interventions', { params: filters }),
};

// Dashboard API
export const dashboardAPI = {
    getSummary: (params) => api.get('/api/dashboard/summary', { params }),
    getChildren: (params) => api.get('/api/dashboard/children', { params }),
    getInterventions: (params) => api.get('/api/dashboard/interventions', { params }),
    getUsers: (params) => api.get('/api/dashboard/users', { params }),
    getCharts: (params) => api.get('/api/dashboard/charts', { params }),
    getDistricts: () => api.get('/api/dashboard/districts'),
    getMandals: (districtId) => api.get('/api/dashboard/mandals', { params: { district_id: districtId } }),
    getChildGrowth: (childId, lang = 'en') => api.get(`/api/dashboard/child-growth/${childId}?lang=${lang}`),
    getMandalsForDistrict: () => api.get('/api/dashboard/mandals-for-district'),
    getCentersForMandal: () => api.get('/api/dashboard/centers-for-mandal'),
    getDistrictsForState: () => api.get('/api/dashboard/districts-for-state'),
    runRealtimePrediction: (data, lang = 'en') => api.post(`/api/predictions/run?lang=${lang}`, data),
};

// Health check
export const healthCheck = () => api.get('/api/health');

export default api;