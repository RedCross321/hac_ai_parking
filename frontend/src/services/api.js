import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерсептор для добавления токена в заголовки
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('bootstrap_token');
  if (token && config.url.includes('/bootstrap-admin')) {
    config.headers['X-Bootstrap-Token'] = token;
  }
  return config;
});

export const authAPI = {
  // Получить bootstrap токен
  getBootstrapToken: async () => {
    const response = await api.get('/auth/bootstrap-token');
    return response.data;
  },
  
  // Создать первого админа
  createAdmin: async (email, password, confirmPassword) => {
    const response = await api.post('/auth/bootstrap-admin', {
      email,
      password,
      confirm_password: confirmPassword
    });
    return response.data;
  },
  
  // Обычный вход
  login: async (email, password) => {
    const response = await api.post('/auth/login', null, {
      params: { email, password }
    });
    return response.data;
  }
};

export default api;