import { useState, useEffect } from 'react'
import { Header } from '@/components/layout/Header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Settings, Globe, Palette, Save, RotateCcw, Moon, Sun } from 'lucide-react'
import toast from 'react-hot-toast'

interface SettingsPageProps {
  theme: 'light' | 'dark'
  onToggleTheme: () => void
}

export function SettingsPage({ theme, onToggleTheme }: SettingsPageProps) {
  const [apiUrl, setApiUrl] = useState('')

  useEffect(() => {
    const stored = localStorage.getItem('api_base_url')
    if (stored) setApiUrl(stored)
  }, [])

  const handleSaveApiUrl = () => {
    if (apiUrl.trim()) {
      localStorage.setItem('api_base_url', apiUrl.trim())
      toast.success('API base URL updated')
    } else {
      localStorage.removeItem('api_base_url')
      toast.success('API base URL reset to default (proxy)')
    }
  }

  const handleResetApiUrl = () => {
    setApiUrl('')
    localStorage.removeItem('api_base_url')
    toast.success('API base URL reset to default')
  }

  return (
    <div>
      <Header
        title="Settings"
        subtitle="Configure your AI Code Reviewer"
        theme={theme}
        onToggleTheme={onToggleTheme}
      />
      <div className="p-6 space-y-6 max-w-2xl">
        {/* API Configuration */}
        <Card className="animate-fade-in">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe size={18} />
              API Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">
                API Base URL
              </label>
              <p className="text-xs text-muted-foreground">
                Leave empty to use the default proxy (recommended for local development).
                Set a custom URL to point to a different backend instance.
              </p>
              <div className="flex gap-2">
                <Input
                  placeholder="e.g., http://localhost:8000"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                />
                <Button variant="primary" onClick={handleSaveApiUrl}>
                  <Save size={16} />
                  Save
                </Button>
                <Button variant="outline" onClick={handleResetApiUrl}>
                  <RotateCcw size={16} />
                </Button>
              </div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>Current:</span>
                <Badge variant="outline">
                  {apiUrl || 'Default (Vite proxy → http://127.0.0.1:8000)'}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Theme */}
        <Card className="animate-fade-in" style={{ animationDelay: '100ms' }}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette size={18} />
              Appearance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-foreground">Theme</p>
                <p className="text-xs text-muted-foreground">
                  Toggle between light and dark mode
                </p>
              </div>
              <Button variant="outline" onClick={onToggleTheme}>
                {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
                {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* About */}
        <Card className="animate-fade-in" style={{ animationDelay: '200ms' }}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings size={18} />
              About
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Frontend Version</span>
                <Badge variant="outline">1.0.0</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Backend API</span>
                <Badge variant="outline">v2.0.0</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Stack</span>
                <span className="text-foreground">React + Vite + TailwindCSS</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">ML Engine</span>
                <span className="text-foreground">scikit-learn (Gradient Boosting)</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
