import { useState } from 'react';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import UserDashboard from './components/UserDashboard';
import ForgotPasswordForm from './components/ForgotPasswordForm';
import ResetPasswordForm from './components/ResetPasswordForm';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access_token'));
  // mode: 'login', 'register', 'forgot'
  const [mode, setMode] = useState('login');

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  const handleRegisterSuccess = () => {
    setMode('login');
  };

  // Проверяем, есть ли в URL параметр token (для сброса пароля)
  const urlParams = new URLSearchParams(window.location.search);
  const resetToken = urlParams.get('token');

  if (resetToken) {
    // Если есть токен, показываем форму сброса пароля
    return <ResetPasswordForm />;
  }

  if (isLoggedIn) {
    return <UserDashboard onLogout={handleLogout} />;
  }

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto' }}>
      {mode === 'register' && (
        <>
          <RegisterForm onSuccess={handleRegisterSuccess} />
          <p>
            Уже есть аккаунт?{' '}
            <button onClick={() => setMode('login')}>Войти</button>
          </p>
        </>
      )}
      {mode === 'login' && (
        <>
          <LoginForm onLogin={handleLogin} />
          <p>
            Нет аккаунта?{' '}
            <button onClick={() => setMode('register')}>Зарегистрироваться</button>
          </p>
          <p>
            <button onClick={() => setMode('forgot')}>Забыли пароль?</button>
          </p>
        </>
      )}
      {mode === 'forgot' && (
        <ForgotPasswordForm onBackToLogin={() => setMode('login')} />
      )}
    </div>
  );
}

export default App;
