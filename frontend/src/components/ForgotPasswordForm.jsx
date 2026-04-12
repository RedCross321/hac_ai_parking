import { useState } from 'react';
import { authAPI } from '../api/auth';

const ForgotPasswordForm = ({ onBackToLogin }) => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');
    try {
      const res = await authAPI.forgotPassword(email);
      // Бэкенд возвращает debug ссылку в ответе (для удобства тестирования)
      if (res.data.debug_reset_link) {
        setMessage(
          `Инструкции отправлены (в тестовом режиме). ` +
          `Ссылка для сброса: ${res.data.debug_reset_link}`
        );
      } else {
        setMessage('Если email существует, на него отправлена ссылка для сброса пароля.');
      }
      setSubmitted(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при отправке запроса');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Восстановление пароля</h2>
      {!submitted ? (
        <form onSubmit={handleSubmit}>
          {error && <p style={{ color: 'red' }}>{error}</p>}
          <div>
            <input
              type="email"
              placeholder="Введите ваш email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <button type="submit" disabled={loading}>
            {loading ? 'Отправка...' : 'Отправить инструкции'}
          </button>
        </form>
      ) : (
        <div>
          <p style={{ color: 'green' }}>{message}</p>
          <button onClick={onBackToLogin}>Вернуться ко входу</button>
        </div>
      )}
      {!submitted && (
        <p>
          <button onClick={onBackToLogin}>← Назад ко входу</button>
        </p>
      )}
    </div>
  );
};

export default ForgotPasswordForm;