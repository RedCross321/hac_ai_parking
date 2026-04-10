import { useEffect, useState } from 'react'
import { SmartCaptcha } from '@yandex/smart-captcha'
import axios from 'axios'
import './App.css'

function captchaForm() {

  const [siteKey, setSiteKey] = useState('')
  const [captchaToken, setCaptchaToken] = useState('')
  const [formData, setFormData] = useState({name: '', email: ''})
  const [message, setMessage] = useState('')

  const [captchaKey, setCaptchaKey] = useState(0);

  useEffect(() => {
    // получение клиентского ключа c бэка    

    axios.get('http://localhost:8000/auth/captcha-config')
      .then(response => {

        setSiteKey(response.data.site_key)

      })
      .catch(error => {

        console.error('Ошибка получения конфигурации капчи:', error)
        setMessage('Не удалось загрузить капчу. Попробуйте позже.')

      })
  }, [])

  const handleCaptchaSuccess = (token) => {

    console.log("Капча пройдена, токен:", token)
    setCaptchaToken(token)
    setMessage('')

  }

  const handleInputChange = (e) => {

    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))

  }

  const resetFormAndCaptcha = () => {
    
    setFormData({ name: '', email: '' });
    
    setCaptchaToken('');
    
    setCaptchaKey(prevKey => prevKey + 1);
  };

  const handleSubmit = async (e) => {

    e.preventDefault();

    if (!captchaToken) {
      setMessage('Пожалуйста, подтвердите, что вы не робот.')
      return
    }

    try {

      await axios.post('http://localhost:8000/auth/verify-captcha', {
        token: captchaToken
      })

      console.log('Токен валиден, отправка данных формы...', formData)
      
      setMessage("Форма отправлена")

      resetFormAndCaptcha();

    } catch (error) {

      console.error('Ошибка при проверке токена или отправке формы:', error);

      if (error.response) {
        setMessage(`Ошибка: ${error.response.data.detail || 'Не удалось проверить капчу.'}`);
      } else {
        setMessage('Произошла ошибка. Попробуйте еще раз.');
      }

      resetFormAndCaptcha()

    }
  }

return (
    <form onSubmit={handleSubmit}>
      <h2>Форма с капчей</h2>
      
      <div>
        <label>Имя:</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleInputChange}
          required
        />
      </div>
      
      <div>
        <label>Email:</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleInputChange}
          required
        />
      </div>

      {/* Виджет SmartCaptcha */}
      {siteKey && (
        <SmartCaptcha
          key={captchaKey} 
          sitekey={siteKey}
          onSuccess={handleCaptchaSuccess}
          language="ru" // Опционально: язык виджета
        />
      )}

      <button type="submit" disabled={!captchaToken}>
        Отправить
      </button>

      {message && <p>{message}</p>}
    </form>
  );
}

export default captchaForm;