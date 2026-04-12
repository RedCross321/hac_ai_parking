import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import styles from './ResetMailPage.module.css'

function ResetMailPage() {
    const [email, setEmail] = useState('')
    const navigate = useNavigate()

    const handleSubmit = (e) => {
        e.preventDefault()
        console.log('Reset request:', email)
        navigate('/reset-password')
    }

    return (
        <div className={styles['mobile-container']}>
            <header>
                <div className={styles['logo']}>
                    <img src="src/assets/logo.svg" alt="Логотип" className={styles['logo-svg']} />
                </div>
            </header>

            <p className={styles['mail-reset-txt']}>
                Письмо для смены пароля <br /> отправлено на почту
            </p>
            <img src="src/assets/mail.svg" alt="Письмо" className={styles['reset-img']} />

            <form onSubmit={handleSubmit} className={styles['reg']}>
                <h2 className={styles['registration-title']}>Смена пароля</h2>
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
                <div className={styles['maks']}>
                    <button type="submit" className={styles['submit-btn']}>Далее</button>
                </div>
            </form>

            <img src="src/assets/car-footer.svg" alt="Машина" className={styles['car-footer']} />
        </div>
    )
}

export default ResetMailPage