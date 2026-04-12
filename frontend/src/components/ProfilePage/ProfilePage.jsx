import { Link } from 'react-router-dom'
import styles from './ProfilePage.module.css'

function ProfilePage() {
    return (
        <>
            <header className={styles['header']}>
                <div className={styles['container']}>
                    <div className={styles['header-inner']}>
                        <img src="src/assets/logo.svg" alt="Логотип" className={styles['logo-site']} />
                        <div className={styles['profile-info']}>
                            <h2 className={styles['user-name']}>Данил Колбасенко</h2>
                            <img src="src/assets/profile.svg" alt="Профиль" className={styles['profile-vector']} />
                        </div>
                    </div>
                </div>
            </header>

            <main className={styles['main']}>
                <div className={`${styles['container']} ${styles['top']}`}>
                    <div className={styles['adress-title']}>
                        <p className={styles['adress-title-txt']}>Адрес по умолчанию</p>
                    </div>

                    <div className={styles['adress-div']}>
                        <div className={styles['home-adress']}>
                            <p className={styles['adress-name']}>Дом</p>
                            <p className={styles['adress-txt']}>г.Сургут, ул. Каролинского,14/1</p>
                            <img src="src/assets/redact.svg" alt="Изменить" className={styles['adress-redact']} />
                        </div>
                        <div className={styles['work-adress']}>
                            <p className={styles['adress-name']}>Работа</p>
                            <p className={styles['adress-txt']}>г.Сургут, ул. Каролинского,14/1</p>
                            <img src="src/assets/redact.svg" alt="Изменить" className={styles['adress-redact']} />
                        </div>
                    </div>

                    <div className={styles['adress-title']}>
                        <p className={styles['adress-title-txt']}>Имя</p>
                    </div>
                    <div className={styles['adress-div-min']}>
                        <p className={styles['adress-txt-min']}>Данил Колбасенко</p>
                        <img src="src/assets/redact.svg" alt="Изменить" className={styles['adress-redact']} />
                    </div>

                    <div className={styles['adress-title']}>
                        <p className={styles['adress-title-txt']}>Почта</p>
                    </div>
                    <div className={styles['adress-div-min']}>
                        <p className={styles['adress-txt-min']}>danilkolbasenrj02@gmail.com</p>
                        <img src="src/assets/redact.svg" alt="Изменить" className={styles['adress-redact']} />
                    </div>

                    <div className={styles['adress-title']}>
                        <p className={styles['adress-title-txt']}>Пароль</p>
                    </div>
                    <div className={styles['adress-div-min']}>
                        <p className={styles['adress-txt-min']}>*************</p>
                        <div className={styles['svg-adress']}>
                            <img src="src/assets/eays.svg" alt="Глаз" className={styles['adress-redact']} />
                            <img src="src/assets/redact.svg" alt="Изменить" className={styles['adress-redact']} />
                        </div>
                    </div>
                </div>
            </main>

            <footer>
                <div className={styles['container']}>
                    <div className={styles['buttons']}>
                        <Link to="/" className={styles['page-btn-main']}>Главная</Link>
                        <Link to="/login" className={styles['page-logOut']}>выйти</Link>
                    </div>
                </div>
            </footer>
        </>
    )
}

export default ProfilePage