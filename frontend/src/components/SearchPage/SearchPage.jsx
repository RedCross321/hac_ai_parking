import { useState } from 'react'
import { Link } from 'react-router-dom'
import styles from './SearchPage.module.css'

const addresses = [
    'г.Сургут, ул. Пролетарский проспект 1',
    'г.Сургут, ул. Пролетарский проспект 3',
    'г.Сургут, ул. Пролетарский проспект 3/1',
    'г.Сургут, ул. Пролетарский проспект 5',
]

function SearchPage() {
    const [searchQuery, setSearchQuery] = useState('')

    const filteredAddresses = addresses.filter(addr =>
        addr.toLowerCase().includes(searchQuery.toLowerCase())
    )

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
                <input
                    type="text"
                    className={styles['search-input']}
                    placeholder="Введите адрес"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
                <div className={styles['glass-round']}>
                    <img src="src/assets/settings.svg" alt="Настройки" className={styles['icon-btn']} />
                </div>
                <div className={styles['glass-round']}>
                    <img src="src/assets/search.svg" alt="Поиск" className={styles['icon-btn']} />
                </div>
            </div>

            <main className={styles['main']}>
                {filteredAddresses.map((addr, index) => (
                    <div key={index} className={styles['address-card']}>
                        <span className={styles['address-text']}>{addr}</span>
                        <div className={styles['address-icon']}>
                            <svg viewBox="0 0 24 24">
                                <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z" />
                            </svg>
                        </div>
                    </div>
                ))}
            </main>
        </div>
    )
}

export default SearchPage