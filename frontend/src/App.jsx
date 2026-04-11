import { useState } from 'react';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import UserDashboard from './components/UserDashboard';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access_token'));
  const [showRegister, setShowRegister] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  const handleRegisterSuccess = () => {
    // После успешной регистрации переключаем на форму входа
    setShowRegister(false);
  };

  if (isLoggedIn) {
    return <UserDashboard onLogout={handleLogout} />;
  }

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto' }}>
      {showRegister ? (
        <>
          <RegisterForm onSuccess={handleRegisterSuccess} />
          <p>
            Уже есть аккаунт?{' '}
            <button onClick={() => setShowRegister(false)}>Войти</button>
          </p>
        </>
      ) : (
        <>
          <LoginForm onLogin={handleLogin} />
          <p>
            Нет аккаунта?{' '}
            <button onClick={() => setShowRegister(true)}>Зарегистрироваться</button>
          </p>
        </>
      )}
    </div>
  );
}

export default App;