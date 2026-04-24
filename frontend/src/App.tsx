import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { DashboardPage } from '@/pages/DashboardPage'
import { ReviewPage } from '@/pages/ReviewPage'
import { ReviewDetailPage } from '@/pages/ReviewDetailPage'
import { HistoryPage } from '@/pages/HistoryPage'
import { SettingsPage } from '@/pages/SettingsPage'
import { LoginPage } from '@/pages/LoginPage'
import { useTheme } from '@/hooks/useTheme'
import { useAuth } from '@/hooks/useAuth'

export default function App() {
  const { theme, toggleTheme } = useTheme()
  const { user, isAuthenticated, login, register, logout } = useAuth()

  return (
    <BrowserRouter>
      <Routes>
        <Route
          element={
            <Layout
              isAuthenticated={isAuthenticated}
              username={user?.username}
              onLogout={logout}
            />
          }
        >
          <Route path="/" element={<DashboardPage theme={theme} onToggleTheme={toggleTheme} />} />
          <Route path="/review" element={<ReviewPage theme={theme} onToggleTheme={toggleTheme} />} />
          <Route path="/review/:id" element={<ReviewDetailPage theme={theme} onToggleTheme={toggleTheme} />} />
          <Route path="/history" element={<HistoryPage theme={theme} onToggleTheme={toggleTheme} />} />
          <Route path="/settings" element={<SettingsPage theme={theme} onToggleTheme={toggleTheme} />} />
          <Route
            path="/login"
            element={
              <LoginPage
                theme={theme}
                onToggleTheme={toggleTheme}
                onLogin={login}
                onRegister={register}
              />
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
