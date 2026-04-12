import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../../api/auth';
import styles from './LoginPage.module.css';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await authAPI.login(username, password);
      localStorage.setItem('access_token', response.data.access_token);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка входа');
    }
  };

  return (
    <div className={styles['mobile-container']}>
      <header>
        <div className={styles['logo']}>
          <img src="src/assets/logo.svg" alt="Логотип" className={styles['logo-svg']} />
        </div>
      </header>

      <form onSubmit={handleSubmit} className={styles['reg']}>
        <h2 className={styles['registration-title']}>Войти</h2>
        {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}
        <div className={styles['form-group']}>
          <input
            type="text"
            className={styles['form-input']}
            placeholder="Имя пользователя"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className={styles['form-group']}>
          <input
            type="password"
            className={styles['form-input']}
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <Link to="/reset-mail" className={styles['forgot-link']}>Забыли пароль?</Link>
        <div className={styles['maks']}>
          <button type="submit" className={styles['submit-btn']}>Войти</button>
          <Link to="/registration" className={styles['regist-link']}>Зарегистрироваться</Link>
        </div>
      </form>
    </div>
  );
}

export default LoginPage;