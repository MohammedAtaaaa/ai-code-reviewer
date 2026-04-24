import { Moon, Sun } from 'lucide-react'
import Button from '@/components/ui/Button'

interface HeaderProps {
  title: string
  subtitle?: string
  theme: 'light' | 'dark'
  onToggleTheme: () => void
}

export function Header({ title, subtitle, theme, onToggleTheme }: HeaderProps) {
  return (
    <header className="flex items-center justify-between border-b border-border bg-card/50 backdrop-blur-sm px-6 py-4">
      <div>
        <h1 className="text-xl font-bold text-foreground">{title}</h1>
        {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      <Button variant="ghost" size="sm" onClick={onToggleTheme} className="h-9 w-9 p-0">
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </Button>
    </header>
  )
}
