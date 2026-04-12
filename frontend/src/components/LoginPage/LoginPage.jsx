import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import styles from './LoginPage.module.css'

function LoginPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const navigate = useNavigate()

    const handleSubmit = (e) => {
        e.preventDefault()
        console.log('Login:', { email, password })
        navigate('/')
    }

    return (
        <div className={styles['mobile-container']}>
            <header>
                <div className={styles['logo']}>
                    <img src="src/assets/logo.svg" alt="Логотип" className={styles['logo-svg']} />
                </div>
            </header>

            <form onSubmit={handleSubmit} className={styles['reg']}>
                <h2 className={styles['registration-title']}>Войти</h2>
                <div className={styles['form-group']}>
                    <input
                        type="text"
                        className={styles['form-input']}
                        placeholder="Введите адрес"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
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
                <Link to="/reset-mail" className={styles['forgot-link']}>Забыл пароль</Link>
                <div className={styles['maks']}>
                    <button type="submit" className={styles['submit-btn']}>Войти</button>
                    <Link to="/registration" className={styles['regist-link']}>Зарегистрироваться</Link>
                </div>
            </form>
        </div>
    )
}

export default LoginPage