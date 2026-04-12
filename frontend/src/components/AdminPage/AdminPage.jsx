import { useState } from 'react'
import styles from './AdminPage.module.css'

const camerasData = [
    { id: 1, name: 'UNI_02-46328', status: 'inactive', date: '12.04.2026 14:00' },
    { id: 2, name: 'UNI_02-46328', status: 'active', date: '12.04.2026 14:00' },
    { id: 3, name: 'UNI_02-46328', status: 'unavailable', date: '12.04.2026 14:00' },
    { id: 4, name: 'UNI_02-46328', status: 'active', date: '12.04.2026 14:00' },
    { id: 5, name: 'UNI_02-46328', status: 'active', date: '12.04.2026 14:00' },
    { id: 6, name: 'UNI_02-46328', status: 'active', date: '12.04.2026 14:00' },
    { id: 7, name: 'UNI_02-46328', status: 'active', date: '12.04.2026 14:00' },
    { id: 8, name: 'UNI_02-46328', status: 'active', date: '12.04.2026 14:00' },
    { id: 9, name: 'UNI_02-46328', status: 'active', date: '12.04.2026 14:00' },
    { id: 10, name: 'UNI_02-46328', status: 'active', date: '12.04.2026 14:00' },
]

function AdminPage() {
    const [activeTab, setActiveTab] = useState(0)
    const [searchQuery, setSearchQuery] = useState('')

    const tabs = ['Регистрация камер', 'Статистика запросов', 'Камеры']

    const filteredCameras = camerasData.filter(cam =>
        cam.name.toLowerCase().includes(searchQuery.toLowerCase())
    )

    const getStatusClass = (status) => {
        switch (status) {
            case 'active': return 'status-active'
            case 'inactive': return 'status-inactive'
            case 'unavailable': return 'status-unavailable'
            default: return ''
        }
    }

    const getStatusText = (status) => {
        switch (status) {
            case 'active': return 'Активна'
            case 'inactive': return 'Неактивна'
            case 'unavailable': return 'Недоступны'
            default: return ''
        }
    }

    return (
        <div className={styles['mobile-container']}>
            <nav className={styles['tabs-nav']}>
                {tabs.map((tab, index) => (
                    <button
                        key={index}
                        className={`${styles['tab-btn']} ${activeTab === index ? styles['active'] : ''}`}
                        onClick={() => setActiveTab(index)}
                    >
                        {tab}
                    </button>
                ))}
            </nav>

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

            <div className={styles['cameras-grid']}>
                {filteredCameras.map(cam => (
                    <div key={cam.id} className={styles['camera-card']}>
                        <span className={styles['cam-name']}>{cam.name}</span>
                        <span className={`${styles['cam-status']} ${styles[getStatusClass(cam.status)]}`}>
                            {getStatusText(cam.status)}
                        </span>
                        <span className={styles['cam-date']}>{cam.date}</span>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default AdminPage