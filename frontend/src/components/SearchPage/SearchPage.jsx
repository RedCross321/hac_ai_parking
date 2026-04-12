import { useState } from 'react'
import { Link } from 'react-router-dom'
import styles from './SearchPage.module.css'

const addresses = [
    'г.Сургут, ул. Пролетарский проспект 1',
    'г.Сургут, ул. Пролетарский проспект 3',
    'г.Сургут, ул. Пролетарский проспект 3/1',
    'г.Сургут, ул. Пролетарский проспект 5',
]

const categories = [
    { name: 'A', count: 18 },
    { name: 'B', count: 18 },
    { name: 'C', count: 18 },
    { name: 'D', count: 18 },
    { name: 'PICKUP', count: 18 },
]

function SearchPage() {
    const [searchQuery, setSearchQuery] = useState('')
    const [expandedIndex, setExpandedIndex] = useState(null)

    const filteredAddresses = addresses.filter(addr =>
        addr.toLowerCase().includes(searchQuery.toLowerCase())
    )

    const handleCardClick = (index) => {
        setExpandedIndex(expandedIndex === index ? null : index)
    }

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
                    <div
                        key={index}
                        className={`${styles['address-card']} ${expandedIndex === index ? styles['expanded'] : ''}`}
                        onClick={() => handleCardClick(index)}
                    >
                        <div className={styles['address-header']}>
                            <span className={styles['address-text']}>{addr}</span>
                            <div className={`${styles['address-icon']} ${expandedIndex === index ? styles['rotated'] : ''}`}>
                                <svg viewBox="0 0 24 24">
                                    <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z" />
                                </svg>
                            </div>
                        </div>

                        {expandedIndex === index && (
                            <div className={styles['expanded-content']}>
                                <p className={styles['categories-title']}>Категории:</p>
                                <div className={styles['categories-row']}>
                                    {categories.map((cat) => (
                                        <div key={cat.name} className={styles['category-item']}>
                                            <span className={`${styles['category-letter']} ${cat.name === 'PICKUP' ? styles['pickup'] : ''}`}>
                                                {cat.name}
                                            </span>
                                            <span className={styles['category-count']}>{cat.count}</span>
                                        </div>
                                    ))}
                                    <div className={styles['car-icon-wrapper']}>
                                        <div className={styles['car-icon']}>
                                            <img src="src/assets/car-right.svg" alt="Машина" className="car-right" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </main>
        </div>
    )
}

export default SearchPage