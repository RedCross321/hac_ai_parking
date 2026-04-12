import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './RegistrationPage.module.css'

function RegistrationPage() {
    const [name, setName] = useState('')
    const [address, setAddress] = useState('')
    const [password, setPassword] = useState('')
    const navigate = useNavigate()

    const handleSubmit = (e) => {
        e.preventDefault()
        console.log('Register:', { name, address, password })
        navigate('/login')
    }

    return (
        <div className={styles['mobile-container']}>
            <header>
                <div className={styles['logo']}>
                    <img src="src/assets/logo.svg" alt="Логотип" className={styles['logo-svg']} />
                </div>
            </header>

            <form onSubmit={handleSubmit} className={styles['reg']}>
                <h2 className={styles['registration-title']}>Регистрация</h2>
                <div className={styles['form-group']}>
                    <input
                        type="text"
                        className={styles['form-input']}
                        placeholder="Введите имя"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                </div>
                <div className={styles['form-group']}>
                    <input
                        type="text"
                        className={styles['form-input']}
                        placeholder="Введите адрес"
                        value={address}
                        onChange={(e) => setAddress(e.target.value)}
                        required
                    />
                </div>
                <div className={styles['form-group']}>
                    <input
                        type="password"
                        className={styles['form-input']}
                        placeholder="Введите пароль"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" className={styles['submit-btn']}>Войти</button>
            </form>
        </div>
    )
}

export default RegistrationPage