import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './ResetPasswordPage.module.css'

function ResetPasswordPage() {
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const navigate = useNavigate()

    const handleSubmit = (e) => {
        e.preventDefault()
        if (password === confirmPassword) {
            console.log('Password reset:', password)
            navigate('/login')
        }
    }

    return (
        <div className={styles['mobile-container']}>
            <header>
                <div className={styles['logo']}>
                    <img src="src/assets/logo.svg" alt="Логотип" className={styles['logo-svg']} />
                </div>
            </header>

            <form onSubmit={handleSubmit} className={styles['reg']}>
                <h2 className={styles['registration-title']}>Смена пароля</h2>
                <div className={styles['form-group']}>
                    <input
                        type="password"
                        className={styles['form-input']}
                        placeholder="Введите новый пароль"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <div className={styles['form-group']}>
                    <input
                        type="password"
                        className={styles['form-input']}
                        placeholder="Повторите пароль"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />
                </div>
                <div className={styles['maks']}>
                    <button type="submit" className={styles['submit-btn']}>Войти</button>
                </div>
            </form>

            <img src="src/assets/car-footer.svg" alt="Машина" className={styles['car-footer']} />
        </div>
    )
}

export default ResetPasswordPage