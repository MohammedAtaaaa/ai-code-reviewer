import { cn } from '@/lib/utils'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Code2,
  History,
  Settings,
  LogIn,
  LogOut,
  User,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from 'lucide-react'
import { useState } from 'react'

interface SidebarProps {
  isAuthenticated: boolean
  username?: string
  onLogout: () => void
}

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/review', icon: Code2, label: 'Code Review' },
  { to: '/history', icon: History, label: 'History' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export function Sidebar({ isAuthenticated, username, onLogout }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 flex h-screen flex-col border-r border-border bg-card transition-all duration-300',
        collapsed ? 'w-16' : 'w-64',
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b border-border px-4">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Sparkles size={18} />
        </div>
        {!collapsed && (
          <div className="flex flex-col overflow-hidden">
            <span className="truncate text-sm font-bold text-foreground">AI Code Reviewer</span>
            <span className="text-[10px] text-muted-foreground">v2.0</span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-accent hover:text-foreground',
                collapsed && 'justify-center px-2',
              )
            }
          >
            <Icon size={20} className="shrink-0" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Auth section */}
      <div className="border-t border-border p-3 space-y-1">
        {isAuthenticated ? (
          <>
            <div className={cn(
              'flex items-center gap-3 rounded-lg px-3 py-2 text-sm',
              collapsed && 'justify-center px-2',
            )}>
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                <User size={14} />
              </div>
              {!collapsed && (
                <span className="truncate font-medium text-foreground">{username}</span>
              )}
            </div>
            <button
              onClick={onLogout}
              className={cn(
                'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive cursor-pointer',
                collapsed && 'justify-center px-2',
              )}
            >
              <LogOut size={18} className="shrink-0" />
              {!collapsed && <span>Sign Out</span>}
            </button>
          </>
        ) : (
          <NavLink
            to="/login"
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-accent hover:text-foreground',
                collapsed && 'justify-center px-2',
              )
            }
          >
            <LogIn size={20} className="shrink-0" />
            {!collapsed && <span>Sign In</span>}
          </NavLink>
        )}
      </div>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex h-10 items-center justify-center border-t border-border text-muted-foreground transition-colors hover:text-foreground cursor-pointer"
      >
        {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
      </button>
    </aside>
  )
}
