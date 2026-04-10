import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import BootstrapAdmin from './components/BootstrapAdmin';
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
    <Router>
      <div className="App">
        <nav style={{ padding: '10px', background: '#f0f0f0', marginBottom: '20px' }}>
          <Link to="/" style={{ marginRight: '10px' }}>Главная</Link>
          <Link to="/setup">Настройка администратора</Link>
        </nav>

        <Routes>
          <Route path="/" element={
            <>
              <h1>Анализатор парковочных мест</h1>
              <p>{status}</p>
            </>
          } />
          <Route path="/setup" element={<BootstrapAdmin />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;