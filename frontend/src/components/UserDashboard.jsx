import { useEffect, useState } from 'react';
import { authAPI } from '../api/auth';

const UserDashboard = ({ onLogout }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authAPI.getCurrentUser()
      .then(res => setUser(res.data))
      .catch(err => {
        console.error('Failed to fetch user', err);
        // Если ошибка 401 - токен невалиден, разлогиниваем
        if (err.response?.status === 401) {
          handleLogout();
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const handleLogout = async () => {
    try {
      await authAPI.logout();
    } catch (e) {
      // игнорируем ошибку
    }
    localStorage.removeItem('access_token');
    onLogout && onLogout();
  };

  if (loading) return <div>Загрузка данных пользователя...</div>;
  if (!user) return <div>Не удалось загрузить профиль</div>;

  return (
    <div>
      <h2>Личный кабинет</h2>
      <p><strong>ID:</strong> {user.id}</p>
      <p><strong>Имя:</strong> {user.username}</p>
      <p><strong>Email:</strong> {user.email}</p>
      <button onClick={handleLogout}>Выйти</button>
    </div>
  );
};

export default UserDashboard;