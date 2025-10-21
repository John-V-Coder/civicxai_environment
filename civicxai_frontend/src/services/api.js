import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });
          
          localStorage.setItem('access_token', response.data.access);
          api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
          
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh_token: refreshToken }),
  refreshToken: (refreshToken) => api.post('/auth/refresh/', { refresh: refreshToken }),
  getUserProfile: () => api.get('/user/profile/'),
  updateProfile: (data) => api.patch('/user/profile/', data),
  changePassword: (data) => api.post('/user/change-password/', data),
  checkAuthStatus: () => api.get('/auth/status/'),
};

// Dashboard API
export const dashboardAPI = {
  getOverview: () => api.get('/dashboard/'),
  getMetrics: () => api.get('/dashboard/metrics/'),
};

// Regions API
export const regionsAPI = {
  list: (params) => api.get('/regions/', { params }),
  get: (id) => api.get(`/regions/${id}/`),
  create: (data) => api.post('/regions/', data),
  update: (id, data) => api.patch(`/regions/${id}/`, data),
  delete: (id) => api.delete(`/regions/${id}/`),
  calculatePriority: (id) => api.post(`/regions/${id}/calculate_priority/`),
  batchCalculate: () => api.post('/regions/batch_calculate_priorities/'),
  getAllocations: (id) => api.get(`/regions/${id}/allocations/`),
};

// Allocations API
export const allocationsAPI = {
  list: (params) => api.get('/allocations/', { params }),
  get: (id) => api.get(`/allocations/${id}/`),
  create: (data) => api.post('/allocations/', data),
  approve: (id) => api.post(`/allocations/${id}/approve/`),
  disburse: (id) => api.post(`/allocations/${id}/disburse/`),
};

// Workgroups API
export const workgroupsAPI = {
  list: (params) => api.get('/workgroups/', { params }),
  get: (id) => api.get(`/workgroups/${id}/`),
  create: (data) => api.post('/workgroups/', data),
  update: (id, data) => api.patch(`/workgroups/${id}/`, data),
  join: (id) => api.post(`/workgroups/${id}/join/`),
  leave: (id) => api.post(`/workgroups/${id}/leave/`),
  getProposals: (id) => api.get(`/workgroups/${id}/proposals/`),
};

// Proposals API
export const proposalsAPI = {
  list: (params) => api.get('/proposals/', { params }),
  get: (id) => api.get(`/proposals/${id}/`),
  create: (data) => api.post('/proposals/', data),
  update: (id, data) => api.patch(`/proposals/${id}/`, data),
  delete: (id) => api.delete(`/proposals/${id}/`),
  submitForReview: (id) => api.post(`/proposals/${id}/submit_for_review/`),
  vote: (id, voteData) => api.post(`/proposals/${id}/vote/`, voteData),
};

// Events API
export const eventsAPI = {
  list: (params) => api.get('/events/', { params }),
  get: (id) => api.get(`/events/${id}/`),
  create: (data) => api.post('/events/', data),
  update: (id, data) => api.patch(`/events/${id}/`, data),
  delete: (id) => api.delete(`/events/${id}/`),
};

// Users API
export const usersAPI = {
  list: (params) => api.get('/users/', { params }),
  updateRole: (userId, role) => api.post(`/users/${userId}/role/`, { role }),
};

// MeTTa AI Engine API
export const mettaAPI = {
  // Calculate priority score using MeTTa engine (fast, local)
  calculatePriority: (data) => api.post('/metta/calculate-priority/', data),
  
  // Generate explanation using MeTTa
  generateExplanation: (data) => api.post('/metta/explain/', data),
  
  // Health check for MeTTa engine
  healthCheck: () => api.get('/metta/health/'),
};

// Gateway (uagents) AI API - Advanced with PDFs
export const gatewayAPI = {
  // Submit allocation request with optional PDFs
  requestAllocation: (formData) => {
    return api.post('/gateway/allocation/request/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // Request AI explanation with optional PDFs
  requestExplanation: (formData) => {
    return api.post('/gateway/explanation/request/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // Check status of a request (polling)
  checkStatus: (requestId) => api.get(`/gateway/status/${requestId}/`),
  
  // Check gateway health
  healthCheck: () => api.get('/gateway/health/'),
  
  // Get gateway metrics
  getMetrics: () => api.get('/gateway/metrics/'),
};

// Legacy XAI API (deprecated - use mettaAPI or gatewayAPI)
export const xaiAPI = {
  calculatePriority: (data) => api.post('/metta/calculate-priority/', data),
  generateExplanation: (data) => api.post('/metta/explain/', data),
  healthCheck: () => api.get('/metta/health/'),
};

export default api;
