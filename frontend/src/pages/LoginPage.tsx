import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Header } from '@/components/layout/Header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import { Spinner } from '@/components/ui/Spinner'
import { LogIn, UserPlus, Mail, Lock, User } from 'lucide-react'
import toast from 'react-hot-toast'

interface LoginPageProps {
  theme: 'light' | 'dark'
  onToggleTheme: () => void
  onLogin: (email: string, password: string) => Promise<unknown>
  onRegister: (email: string, username: string, password: string) => Promise<unknown>
}

export function LoginPage({ theme, onToggleTheme, onLogin, onRegister }: LoginPageProps) {
  const navigate = useNavigate()
  const [isRegister, setIsRegister] = useState(false)
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      if (isRegister) {
        await onRegister(email, username, password)
        toast.success('Account created successfully!')
      } else {
        await onLogin(email, password)
        toast.success('Signed in successfully!')
      }
      navigate('/')
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      const msg = error.response?.data?.detail || 'Authentication failed'
      toast.error(typeof msg === 'string' ? msg : 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <Header
        title={isRegister ? 'Create Account' : 'Sign In'}
        subtitle="Manage your code reviews"
        theme={theme}
        onToggleTheme={onToggleTheme}
      />
      <div className="flex items-center justify-center p-6 min-h-[calc(100vh-80px)]">
        <Card className="w-full max-w-md animate-fade-in">
          <CardHeader className="text-center">
            <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
              {isRegister ? <UserPlus size={24} className="text-primary" /> : <LogIn size={24} className="text-primary" />}
            </div>
            <CardTitle>{isRegister ? 'Create Account' : 'Welcome Back'}</CardTitle>
            <p className="text-sm text-muted-foreground">
              {isRegister
                ? 'Sign up to save your review history'
                : 'Sign in to access your reviews'}
            </p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Email</label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="pl-9"
                  />
                </div>
              </div>

              {isRegister && (
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Username</label>
                  <div className="relative">
                    <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      type="text"
                      placeholder="johndoe"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                      className="pl-9"
                    />
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Password</label>
                <div className="relative">
                  <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type="password"
                    placeholder="Min. 6 characters"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={6}
                    className="pl-9"
                  />
                </div>
              </div>

              <Button type="submit" variant="primary" className="w-full" disabled={loading}>
                {loading ? (
                  <Spinner size={18} />
                ) : isRegister ? (
                  <UserPlus size={18} />
                ) : (
                  <LogIn size={18} />
                )}
                {loading ? 'Processing...' : isRegister ? 'Create Account' : 'Sign In'}
              </Button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => setIsRegister(!isRegister)}
                  className="text-sm text-primary hover:underline cursor-pointer"
                >
                  {isRegister
                    ? 'Already have an account? Sign in'
                    : "Don't have an account? Sign up"}
                </button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
