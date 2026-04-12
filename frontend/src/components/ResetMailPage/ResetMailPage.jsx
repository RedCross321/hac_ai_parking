import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../../api/auth';
import styles from './ResetMailPage.module.css';

function ResetMailPage() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await authAPI.forgotPassword(email);
      // В ответе есть debug_reset_link – для разработки можно вывести
      setMessage('Инструкции отправлены на почту (проверьте консоль)');
      console.log('Reset link:', response.data.debug_reset_link);
      // В реальном приложении показываем сообщение и не переходим автоматически
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Ошибка');
    }
  };

  return (
    <div className={styles['mobile-container']}>
      <header>
        <div className={styles['logo']}>
          <img src="src/assets/logo.svg" alt="Логотип" className={styles['logo-svg']} />
        </div>
      </header>

      <p className={styles['mail-reset-txt']}>
        Введите email для восстановления пароля
      </p>
      <img src="src/assets/mail.svg" alt="Письмо" className={styles['reset-img']} />

      <form onSubmit={handleSubmit} className={styles['reg']}>
        <h2 className={styles['registration-title']}>Сброс пароля</h2>
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
        {message && <p style={{ textAlign: 'center' }}>{message}</p>}
        <div className={styles['maks']}>
          <button type="submit" className={styles['submit-btn']}>Отправить</button>
        </div>
      </form>

      <img src="src/assets/car-footer.svg" alt="Машина" className={styles['car-footer']} />
    </div>
  );
}

export default ResetMailPage;