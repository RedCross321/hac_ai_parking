import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authAPI } from '../../api/auth';
import styles from './ResetPasswordPage.module.css';

function ResetPasswordPage() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }
    if (!token) {
      setError('Отсутствует токен сброса');
      return;
    }
    try {
      await authAPI.resetPassword(token, password);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка сброса пароля');
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
        <h2 className={styles['registration-title']}>Новый пароль</h2>
        {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}
        <div className={styles['form-group']}>
          <input
            type="password"
            className={styles['form-input']}
            placeholder="Новый пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div className={styles['form-group']}>
          <input
            type="password"
            className={styles['form-input']}
            placeholder="Повторите пароль"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>
        <div className={styles['maks']}>
          <button type="submit" className={styles['submit-btn']}>Сохранить</button>
        </div>
      </form>

      <img src="src/assets/car-footer.svg" alt="Машина" className={styles['car-footer']} />
    </div>
  );
}

export default ResetPasswordPage;