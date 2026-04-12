import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../../api/auth';
import CaptchaWidget from '../CaptchaWidget/CaptchaWidget'; // путь уточни
import styles from './RegistrationPage.module.css';

function RegistrationPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [captchaToken, setCaptchaToken] = useState('');
  const [resetCaptcha, setResetCaptcha] = useState(0);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!captchaToken) {
      setError('Пожалуйста, подтвердите, что вы не робот');
      return;
    }

    try {
      // Сначала проверяем капчу
      await authAPI.verifyCaptcha(captchaToken);
      // Затем регистрируем
      await authAPI.register({ username, email, password });
      // Перенаправляем на вход
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка регистрации');
      setResetCaptcha(prev => prev + 1); // сбросить капчу при ошибке
      setCaptchaToken('');
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
        <h2 className={styles['registration-title']}>Регистрация</h2>
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
            type="email"
            className={styles['form-input']}
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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

        <CaptchaWidget 
          onVerify={setCaptchaToken} 
          resetTrigger={resetCaptcha} 
        />

        <button type="submit" className={styles['submit-btn']}>Зарегистрироваться</button>
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <Link to="/login">Уже есть аккаунт? Войти</Link>
        </div>
      </form>
    </div>
  );
}

export default RegistrationPage;