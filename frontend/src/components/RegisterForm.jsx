import { useState } from 'react';
import { authAPI } from '../api/auth';
import CaptchaWidget from './CaptchaWidget';

const RegisterForm = ({ onSuccess }) => {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [captchaToken, setCaptchaToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [resetCaptcha, setResetCaptcha] = useState(0);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleCaptchaVerify = (token) => {
    setCaptchaToken(token);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!captchaToken) {
      setError('Пожалуйста, подтвердите капчу');
      return;
    }
    setLoading(true);
    setError('');
    try {
      // Сначала проверяем капчу
      await authAPI.verifyCaptcha(captchaToken);
      // Регистрируем пользователя
      await authAPI.register(form);
      onSuccess && onSuccess();
      // Очищаем форму
      setForm({ username: '', email: '', password: '' });
      setResetCaptcha(prev => prev + 1);
      setCaptchaToken('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка регистрации');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Регистрация</h2>
      {error && <p style={{color:'red'}}>{error}</p>}
      <div>
        <input name="username" placeholder="Имя пользователя" value={form.username} onChange={handleChange} required />
      </div>
      <div>
        <input name="email" type="email" placeholder="Email" value={form.email} onChange={handleChange} required />
      </div>
      <div>
        <input name="password" type="password" placeholder="Пароль" value={form.password} onChange={handleChange} required />
      </div>
      <CaptchaWidget onVerify={handleCaptchaVerify} resetTrigger={resetCaptcha} />
      <button type="submit" disabled={loading || !captchaToken}>
        {loading ? 'Загрузка...' : 'Зарегистрироваться'}
      </button>
    </form>
  );
};

export default RegisterForm;