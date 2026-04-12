import axios from 'axios';

const API_URL = 'http://localhost:8001';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  getCaptchaConfig: () => api.get('/auth/captcha-config'),
  verifyCaptcha: (token) => api.post('/auth/verify-captcha', { token }),
  register: (userData) => api.post('/auth/register', userData),
  login: (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  getCurrentUser: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
  forgotPassword: (email) => api.post('/auth/forgot-password', { email }),
  resetPassword: (token, new_password) =>
    api.post('/auth/reset-password', { token, new_password }),
};

// Дополнительные API для камер и поиска
export const camerasAPI = {
  getAvailable: () => api.get('/cameras/available'),
  searchParking: (params) => api.get('/parking/search', { params }),
  resolveGeo: (address) => api.post('/geo/resolve', { address }),
};

export default api;