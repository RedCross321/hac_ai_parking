import { Link } from 'react-router-dom'
import styles from './NoLoginPage.module.css'

function NoLoginPage() {
    return (
        <div className={styles['mobile-container']}>
            <header>
                <div className={styles['logo']}>
                    <img src="src/assets/logo.svg" alt="Логотип" className={styles['logo-svg']} />
                </div>
            </header>

            <div className={styles['search-section']}>
                <input type="text" className={styles['search-input']} placeholder="Введите адрес" />
                <div className={styles['glass-round']}>
                    <img src="src/assets/settings.svg" alt="Настройки" className={styles['icon-btn']} />
                </div>
                <div className={styles['glass-round']}>
                    <img src="src/assets/search.svg" alt="Поиск" className={styles['icon-btn']} />
                </div>
            </div>

            <p className={styles['slogin']}>Пожалуйста,<br /> войдите в аккаунт!</p>
            <img src="src/assets/car-stop.svg" alt="Машина" className={styles['car-stop']} />

            <div className={styles['btn-log']}>
                <Link to="/login" className={styles['logIn-btn']}>Вход</Link>
                <Link to="/registration" className={styles['regIn-btn']}>Регистрация</Link>
            </div>
        </div>
    )
}

export default NoLoginPage