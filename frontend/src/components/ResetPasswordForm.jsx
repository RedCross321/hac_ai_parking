import { useState } from 'react';
import { authAPI } from '../api/auth';

const ResetPasswordForm = () => {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  // Получаем токен из URL (например, ?token=...)
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }
    if (!token) {
      setError('Отсутствует токен сброса в URL');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await authAPI.resetPassword(token, newPassword);
      setSuccess(true);
      setMessage('Пароль успешно изменён! Теперь вы можете войти.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при сбросе пароля');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div>
        <h2>Ошибка</h2>
        <p style={{ color: 'red' }}>Недействительная ссылка для сброса пароля.</p>
      </div>
    );
  }

  if (success) {
    return (
      <div>
        <h2>Пароль изменён</h2>
        <p style={{ color: 'green' }}>{message}</p>
        <a href="/">Перейти на страницу входа</a>
      </div>
    );
  }

  return (
    <div>
      <h2>Новый пароль</h2>
      <form onSubmit={handleSubmit}>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <div>
          <input
            type="password"
            placeholder="Новый пароль"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
            minLength={6}
          />
        </div>
        <div>
          <input
            type="password"
            placeholder="Подтвердите пароль"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Сохранение...' : 'Сохранить новый пароль'}
        </button>
      </form>
    </div>
  );
};

export default ResetPasswordForm;