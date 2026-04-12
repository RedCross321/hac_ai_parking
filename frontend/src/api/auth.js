import axios from 'axios';

const API_URL = 'http://localhost:8001';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Добавляем токен ко всем запросам, если он есть
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  // Получить site_key для капчи
  getCaptchaConfig: () => api.get('/auth/captcha-config'),
  
  // Проверить капчу
  verifyCaptcha: (token) => api.post('/auth/verify-captcha', { token }),
  
  // Регистрация
  register: (userData) => api.post('/auth/register', userData),
  
  // Логин (form-urlencoded, как ожидает OAuth2PasswordRequestForm)
  login: (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  
  // Получить данные текущего пользователя
  getCurrentUser: () => api.get('/auth/me'),
  
  // Выход (передаём токен в теле, хотя бэкенд берёт из заголовка)
  logout: () => api.post('/auth/logout'),

  forgotPassword: (email) => api.post('/auth/forgot-password', { email }),

  resetPassword: (token, new_password) => 
    api.post('/auth/reset-password', { token, new_password }),

};



export default api;