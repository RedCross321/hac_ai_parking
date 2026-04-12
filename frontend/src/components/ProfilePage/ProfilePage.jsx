import { useState } from 'react'
import styles from './ProfilePage.module.css'

function ProfilePage() {
    const [editingHome, setEditingHome] = useState(false)
    const [editingWork, setEditingWork] = useState(false)
    const [editingPassword, setEditingPassword] = useState(false)
    const [homeAddress, setHomeAddress] = useState('г.Сургут, ул. Каролинского,14/1')
    const [workAddress, setWorkAddress] = useState('г.Сургут, ул. Каролинского,14/1')
    const [newAddress, setNewAddress] = useState('')
    const [newPassword, setNewPassword] = useState('')
    const [activeField, setActiveField] = useState('')
    const [showPassword, setShowPassword] = useState(false)

    const handleEditClick = (field) => {
        setActiveField(field)
        if (field === 'home') {
            setNewAddress('')
            setEditingHome(true)
        }
        if (field === 'work') {
            setNewAddress('')
            setEditingWork(true)
        }
        if (field === 'password') {
            setNewPassword('')
            setEditingPassword(true)
        }
    }

    const handleSave = (field) => {
        if (field === 'home' && newAddress.trim()) {
            setHomeAddress(newAddress.trim())
        }
        if (field === 'work' && newAddress.trim()) {
            setWorkAddress(newAddress.trim())
        }
        if (field === 'password' && newPassword.trim()) {
            // Здесь можно добавить логику сохранения пароля
            console.log('New password saved:', newPassword)
        }
        setEditingHome(false)
        setEditingWork(false)
        setEditingPassword(false)
        setActiveField('')
        setNewAddress('')
        setNewPassword('')
    }

    const handleCancel = () => {
        setEditingHome(false)
        setEditingWork(false)
        setEditingPassword(false)
        setActiveField('')
        setNewAddress('')
        setNewPassword('')
    }

    return (
        <div className={styles['mobile-container']}>
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
                        {/* Дом */}
                        {!editingHome ? (
                            <div className={styles['home-adress']}>
                                <p className={styles['adress-name']}>Дом</p>
                                <p className={styles['adress-txt']}>{homeAddress}</p>
                                <img
                                    src="src/assets/redact.svg"
                                    alt="Изменить"
                                    className={styles['adress-redact']}
                                    onClick={() => handleEditClick('home')}
                                    style={{ cursor: 'pointer' }}
                                />
                            </div>
                        ) : (
                            <div className={styles['edit-mode']}>
                                <div className={styles['edit-header']}>
                                    <span className={styles['edit-label']}>Дом</span>
                                    <img
                                        src="src/assets/redact.svg"
                                        alt="Отмена"
                                        className={styles['adress-redact']}
                                        onClick={handleCancel}
                                        style={{ cursor: 'pointer' }}
                                    />
                                </div>
                                <div className={styles['edit-input-row']}>
                                    <input
                                        type="text"
                                        className={styles['edit-input']}
                                        placeholder="Новый адрес"
                                        value={newAddress}
                                        onChange={(e) => setNewAddress(e.target.value)}
                                    />
                                    <button
                                        className={styles['save-btn']}
                                        onClick={() => handleSave('home')}
                                    >
                                        Сохранить
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* Работа */}
                        {!editingWork ? (
                            <div className={styles['work-adress']}>
                                <p className={styles['adress-name']}>Работа</p>
                                <p className={styles['adress-txt']}>{workAddress}</p>
                                <img
                                    src="src/assets/redact.svg"
                                    alt="Изменить"
                                    className={styles['adress-redact']}
                                    onClick={() => handleEditClick('work')}
                                    style={{ cursor: 'pointer' }}
                                />
                            </div>
                        ) : (
                            <div className={styles['edit-mode']}>
                                <div className={styles['edit-header']}>
                                    <span className={styles['edit-label']}>Работа</span>
                                    <img
                                        src="src/assets/redact.svg"
                                        alt="Отмена"
                                        className={styles['adress-redact']}
                                        onClick={handleCancel}
                                        style={{ cursor: 'pointer' }}
                                    />
                                </div>
                                <div className={styles['edit-input-row']}>
                                    <input
                                        type="text"
                                        className={styles['edit-input']}
                                        placeholder="Новый адрес"
                                        value={newAddress}
                                        onChange={(e) => setNewAddress(e.target.value)}
                                    />
                                    <button
                                        className={styles['save-btn']}
                                        onClick={() => handleSave('work')}
                                    >
                                        Сохранить
                                    </button>
                                </div>
                            </div>
                        )}
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
                            <img
                                src="src/assets/eays.svg"
                                alt="Глаз"
                                className={styles['adress-redact']}
                                onClick={() => setShowPassword(!showPassword)}
                                style={{ cursor: 'pointer' }}
                            />
                            <img
                                src="src/assets/redact.svg"
                                alt="Изменить"
                                className={styles['adress-redact']}
                                style={{ cursor: 'pointer' }}
                            />
                        </div>
                    </div>
                </div>
            </main>

            <footer>
                <div className={styles['container']}>
                    <div className={styles['buttons']}>
                        <a href="/" className={styles['page-btn-main']}>Главная</a>
                        <a href="#" className={styles['page-logOut']}>выйти</a>
                    </div>
                </div>
            </footer>
        </div>
    )
}

export default ProfilePage
