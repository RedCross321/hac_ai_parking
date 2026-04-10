import { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [status, setStatus] = useState('Загрузка...');

  useEffect(() => {
    axios.get('http://localhost:8000/ping')
      .then(response => {
        setStatus(`Статус: ${response.data.status}`);
      })
      .catch(error => {
        console.error('Ошибка при запросе к API:', error);
        setStatus('Ошибка соединения с сервером');
      });
  }, []);

  return (
    <div className="App">
      <h1>Анализатор парковочных мест</h1>
      <p>{status}</p>
    </div>
  );
}

export default App;