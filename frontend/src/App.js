import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AppLayout from './layouts/AppLayout.jsx';
import HomePage from './pages/HomePage.jsx';
import JournalPage from './pages/JournalPage.jsx';
import SessionsPage from './pages/SessionsPage.jsx';
import ExercisesPage from './pages/ExercisesPage.jsx';
import ChatPage from './pages/ChatPage.jsx';
import ProgressPage from './pages/ProgressPage.jsx';
import SettingsPage from './pages/SettingsPage';
import LoginPage from './pages/LoginPage.jsx';
import SignupPage from './pages/SignupPage.jsx';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public auth routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />

          {/* Protected routes - require authentication */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/journal" element={<JournalPage />} />
                    <Route path="/sessions" element={<SessionsPage />} />
                    <Route path="/exercises" element={<ExercisesPage />} />
                    <Route path="/progress" element={<ProgressPage />} />
                    <Route path="/chat" element={<ChatPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                    {/* Catch all - redirect to home */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </AppLayout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;