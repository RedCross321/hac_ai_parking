import { Link } from 'react-router-dom'
import styles from './MainPage.module.css'

function MainPage() {
    return (
        <div className={styles['mobile-container']}>
            <header>
                <div className={styles['logo']}>
                    <img src="src/assets/logo.svg" alt="Логотип" className={styles['logo-svg']} />
                </div>
                <Link to="/profile">
                    <img src="src/assets/profile.svg" alt="профиль" className={styles['profile-icon']} />
                </Link>
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

            <div className={styles['content-grid']}>
                <div className={styles['info-box']}>
                    <div className={styles['info-item']}>
                        <div className={styles['info-label']}>Адрес</div>
                        <div className={styles['address-card']}>
                            ул. Каролинского,14/1,<br />г.Сургут,
                        </div>
                    </div>
                    <div className={styles['info-item']}>
                        <div className={styles['info-label']}>Всего свободных мест</div>
                        <div className={styles['count-card']}>
                            <div className={styles['count-number']}>18</div>
                        </div>
                    </div>
                </div>

                <div className={styles['categories-list']}>
                    <div className={styles['category-item']}><span>категория A</span><span>18</span></div>
                    <div className={styles['category-item']}><span>категория B</span><span>18</span></div>
                    <div className={styles['category-item']}><span>категория C</span><span>18</span></div>
                    <div className={styles['category-item']}><span>категория D</span><span>18</span></div>
                    <div className={styles['category-item']}><span>PICKUP</span><span>18</span></div>
                </div>
            </div>

            <img src="src/assets/car-footer.svg" alt="Машина" className={styles['car-footer']} />
        </div>
    )
}

export default MainPage