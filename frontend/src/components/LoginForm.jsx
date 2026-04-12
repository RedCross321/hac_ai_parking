import { useState } from 'react';
import { authAPI } from '../api/auth';

const LoginForm = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await authAPI.login(username, password);
      localStorage.setItem('access_token', res.data.access_token);
      onLogin && onLogin();
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка входа');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Вход</h2>
      {error && <p style={{color:'red'}}>{error}</p>}
      <div>
        <input placeholder="Имя пользователя" value={username} onChange={(e) => setUsername(e.target.value)} required />
      </div>
      <div>
        <input type="password" placeholder="Пароль" value={password} onChange={(e) => setPassword(e.target.value)} required />
      </div>
      <button type="submit" disabled={loading}>
        {loading ? 'Вход...' : 'Войти'}
      </button>
    </form>
  );
};

export default LoginForm;