import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Toaster } from 'react-hot-toast'

interface LayoutProps {
  isAuthenticated: boolean
  username?: string
  onLogout: () => void
}

export function Layout({ isAuthenticated, username, onLogout }: LayoutProps) {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar
        isAuthenticated={isAuthenticated}
        username={username}
        onLogout={onLogout}
      />
      <main className="ml-64 flex-1 transition-all duration-300 peer-data-[collapsed]:ml-16">
        <div className="mx-auto max-w-7xl">
          <Outlet />
        </div>
      </main>
      <Toaster
        position="bottom-right"
        toastOptions={{
          className: 'bg-card text-card-foreground border border-border shadow-lg',
          duration: 4000,
          style: {
            background: 'var(--color-card)',
            color: 'var(--color-card-foreground)',
            border: '1px solid var(--color-border)',
          },
        }}
      />
    </div>
  )
}
