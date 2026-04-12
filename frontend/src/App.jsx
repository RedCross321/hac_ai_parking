import { BrowserRouter as Router, Routes, Route } from 'react-router';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import MainPage from './components/MainPage/MainPage'
import ProfilePage from './components/ProfilePage/ProfilePage'
import AdminPage from './components/AdminPage/AdminPage'
import LoginPage from './components/LoginPage/LoginPage'
import NoLoginPage from './components/NoLoginPage/NoLoginPage'
import RegistrationPage from './components/RegistrationPage/RegistrationPage'
import ResetMailPage from './components/ResetMailPage/ResetMailPage'
import ResetPasswordPage from './components/ResetPasswordPage/ResetPasswordPage'
import SearchPage from './components/SearchPage/SearchPage'
import './index.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/no-login" element={<NoLoginPage />} />
        <Route path="/registration" element={<RegistrationPage />} />
        <Route path="/reset-mail" element={<ResetMailPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/search" element={<SearchPage />} />
      </Routes>
    </Router>
  )
}

export default App
