import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainPage from './components/MainPage/MainPage';
import ProfilePage from './components/ProfilePage/ProfilePage';
import AdminPage from './components/AdminPage/AdminPage';
import LoginPage from './components/LoginPage/LoginPage';
import NoLoginPage from './components/NoLoginPage/NoLoginPage';
import RegistrationPage from './components/RegistrationPage/RegistrationPage';
import ResetMailPage from './components/ResetMailPage/ResetMailPage';
import ResetPasswordPage from './components/ResetPasswordPage/ResetPasswordPage';
import SearchPage from './components/SearchPage/SearchPage';
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute';
import './App.css';
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/no-login" element={<NoLoginPage />} />
        <Route path="/registration" element={<RegistrationPage />} />
        <Route path="/reset-mail" element={<ResetMailPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/search" element={<SearchPage />} />
        
        <Route path="/profile" element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        } />
        <Route path="/admin" element={
          <ProtectedRoute>
            <AdminPage />
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  );
}

export default App;