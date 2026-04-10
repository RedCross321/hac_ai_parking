import React, { useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import './BootstrapAdmin.css';

const BootstrapAdmin = () => {
  const [step, setStep] = useState(1);
  const [bootstrapToken, setBootstrapToken] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isAdminExists, setIsAdminExists] = useState(false);

  useEffect(() => {
    checkBootstrapStatus();
  }, []);

  const checkBootstrapStatus = async () => {
    try {
      await authAPI.getBootstrapToken();
      setIsAdminExists(false);
    } catch (err) {
      if (err.response?.status === 403) {
        setIsAdminExists(true);
        setError('Система уже настроена. Администратор существует.');
      }
    }
  };

  const handleGetToken = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await authAPI.getBootstrapToken();
      setBootstrapToken(response.bootstrap_token);
      setStep(2);
      localStorage.setItem('bootstrap_token', response.bootstrap_token);
    } catch (err) {
      if (err.response?.status === 403) {
        setError('Система уже настроена. Нельзя создать нового администратора.');
        setIsAdminExists(true);
      } else {
        setError('Ошибка при получении токена: ' + (err.response?.data?.detail || err.message));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleCreateAdmin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    if (formData.password !== formData.confirmPassword) {
      setError('Пароли не совпадают');
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('Пароль должен содержать минимум 8 символов');
      setLoading(false);
      return;
    }

    try {
      const response = await authAPI.createAdmin(
        formData.email,
        formData.password,
        formData.confirmPassword
      );
      
      setSuccess(response.message);
      localStorage.removeItem('bootstrap_token');
      
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при создании администратора');
    } finally {
      setLoading(false);
    }
  };

  if (isAdminExists) {
    return (
      <div className="bootstrap-container">
        <div className="card error-card">
          <div className="icon">⚠️</div>
          <h2>Система уже настроена</h2>
          <p>Администратор уже существует в системе.</p>
          <button onClick={() => window.location.href = '/login'}>
            Перейти к входу
          </button>
        </div>
      </div>
    );
  }

  if (step === 1) {
    return (
      <div className="bootstrap-container">
        <div className="card">
          <div className="icon">🚀</div>
          <h1>Первоначальная настройка</h1>
          <p className="description">
            Это первый запуск системы. Вам нужно создать учетную запись администратора.
          </p>
          
          {error && <div className="error-message">{error}</div>}
          
          <button 
            onClick={handleGetToken} 
            disabled={loading}
            className="primary-button"
          >
            {loading ? 'Загрузка...' : 'Начать настройку'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bootstrap-container">
      <div className="card">
        <div className="icon">👑</div>
        <h1>Создание администратора</h1>
        
        {bootstrapToken && (
          <div className="token-info">
            <p className="token-label">Ваш bootstrap токен:</p>
            <code className="token-value">{bootstrapToken}</code>
            <p className="token-warning">
              ⚠️ Сохраните этот токен! Он понадобится для создания администратора.
            </p>
          </div>
        )}

        {success && (
          <div className="success-message">
            ✅ {success}
            <p className="redirect-message">Перенаправление на страницу входа...</p>
          </div>
        )}

        {!success && (
          <form onSubmit={handleCreateAdmin}>
            <div className="form-group">
              <label>Email администратора</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="admin@example.com"
                required
              />
            </div>

            <div className="form-group">
              <label>Пароль</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Минимум 8 символов"
                required
              />
            </div>

            <div className="form-group">
              <label>Подтвердите пароль</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                placeholder="Повторите пароль"
                required
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button 
              type="submit" 
              disabled={loading}
              className="primary-button"
            >
              {loading ? 'Создание...' : 'Создать администратора'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default BootstrapAdmin;