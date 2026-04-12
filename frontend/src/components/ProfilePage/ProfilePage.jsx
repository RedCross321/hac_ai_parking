import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../../api/auth';
import styles from './ProfilePage.module.css';

function ProfilePage() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    authAPI.getCurrentUser()
      .then(res => setUser(res.data))
      .catch(() => navigate('/no-login'));
  }, [navigate]);

  const handleLogout = async () => {
    await authAPI.logout();
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  if (!user) return <div>Загрузка...</div>;

  return (
    <div className={styles['mobile-container']}>
      <header className={styles['header']}>
        <div className={styles['container']}>
          <div className={styles['header-inner']}>
            <img src="src/assets/logo.svg" alt="Логотип" className={styles['logo-site']} />
            <div className={styles['profile-info']}>
              <h2 className={styles['user-name']}>{user.username}</h2>
              <img src="src/assets/profile.svg" alt="Профиль" className={styles['profile-vector']} />
            </div>
          </div>
        </div>
      </header>

      <main className={styles['main']}>
        <div className={`${styles['container']} ${styles['top']}`}>
          <div className={styles['adress-title']}>
            <p className={styles['adress-title-txt']}>Имя пользователя</p>
          </div>
          <div className={styles['adress-div-min']}>
            <p className={styles['adress-txt-min']}>{user.username}</p>
          </div>
          <div className={styles['adress-title']}>
            <p className={styles['adress-title-txt']}>Email</p>
          </div>
          <div className={styles['adress-div-min']}>
            <p className={styles['adress-txt-min']}>{user.email}</p>
          </div>
          {/* Остальные статичные поля адресов можно оставить как есть */}
        </div>
      </main>

      <footer>
        <div className={styles['container']}>
          <div className={styles['buttons']}>
            <Link to="/" className={styles['page-btn-main']}>Главная</Link>
            <button onClick={handleLogout} className={styles['page-logOut']}>Выйти</button>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default ProfilePage;