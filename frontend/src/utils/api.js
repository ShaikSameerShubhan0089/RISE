import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

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

// Auth API
export const authAPI = {
    login: (credentials) => api.post('/auth/login', credentials),
    getCurrentUser: () => api.get('/auth/me'),
    createUser: (userData) => api.post('/auth/users', userData),
    updateUser: (userId, userData) => api.put(`/auth/users/${userId}`, userData),
    listUsers: (role) => api.get('/auth/users', { params: { role } }),
};

// Users Management API (system_admin)
export const usersAPI = {
    list: (params) => api.get('/auth/users', { params }),
    create: (userData) => api.post('/auth/users', userData),
    update: (userId, userData) => api.put(`/auth/users/${userId}`, userData),
    toggleStatus: (userId) => api.patch(`/auth/users/${userId}/status`),
    resetPassword: (userId, newPassword) => api.post(`/auth/users/${userId}/reset-password`, { new_password: newPassword }),
    delete: (userId) => api.delete(`/auth/users/${userId}`),
};

// Analytics API (system_admin)
export const analyticsAPI = {
    getSummary: () => api.get('/dashboard/analytics/summary'),
    getUsers: () => api.get('/dashboard/analytics/users'),
    getChildren: (period = 'month') => api.get('/dashboard/analytics/children', { params: { period } }),
    getPredictions: () => api.get('/dashboard/analytics/predictions'),
};

// Children API
export const childrenAPI = {
    create: (childData) => api.post('/children', childData),
    getById: (childId) => api.get(`/children/${childId}`),
    list: (filters) => api.get('/children', { params: filters }),
    update: (childId, childData) => api.put(`/children/${childId}`, childData),
    getAssessments: (childId) => api.get(`/children/${childId}/assessments`),
};

// Assessments API
export const assessmentsAPI = {
    create: (assessmentData) => api.post('/assessments', assessmentData),
    getById: (assessmentId) => api.get(`/assessments/${assessmentId}`),
    list: (limit) => api.get('/assessments', { params: { limit } }),
};

// Predictions API
export const predictionsAPI = {
    generate: (assessmentId) => api.post(`/predictions/${assessmentId}/predict`),
    getById: (predictionId) => api.get(`/predictions/${predictionId}`),
};

// Referrals API
export const referralsAPI = {
    create: (referralData) => api.post('/referrals', referralData),
    update: (referralId, updateData) => api.put(`/referrals/${referralId}`, updateData),
    getById: (referralId) => api.get(`/referrals/${referralId}`),
    getByChild: (childId) => api.get(`/referrals/child/${childId}`),
    list: (statusFilter) => api.get('/referrals', { params: { status_filter: statusFilter } }),
};

// Interventions API
export const interventionsAPI = {
    create: (interventionData) => api.post('/interventions', interventionData),
    update: (interventionId, updateData) => api.put(`/interventions/${interventionId}`, updateData),
    getById: (interventionId) => api.get(`/interventions/${interventionId}`),
    getByChild: (childId, activeOnly) => api.get(`/interventions/child/${childId}`, { params: { active_only: activeOnly } }),
    list: (filters) => api.get('/interventions', { params: filters }),
};

// Dashboard API
export const dashboardAPI = {
    getSummary: (params) => api.get('/dashboard/summary', { params }),
    getChildren: (params) => api.get('/dashboard/children', { params }),
    getInterventions: (params) => api.get('/dashboard/interventions', { params }),
    getUsers: (params) => api.get('/dashboard/users', { params }),
    getCharts: (params) => api.get('/dashboard/charts', { params }),
    getDistricts: () => api.get('/dashboard/districts'),
    getMandals: (districtId) => api.get('/dashboard/mandals', { params: { district_id: districtId } }),
    getChildGrowth: (childId, lang = 'en') => api.get(`/dashboard/child-growth/${childId}?lang=${lang}`),
    getMandalsForDistrict: () => api.get('/dashboard/mandals-for-district'),
    getCentersForMandal: () => api.get('/dashboard/centers-for-mandal'),
    getDistrictsForState: () => api.get('/dashboard/districts-for-state'),
    runRealtimePrediction: (data, lang = 'en') => api.post(`/predictions/run?lang=${lang}`, data),
};

// Health check
export const healthCheck = () => api.get('/health');

export default api;
