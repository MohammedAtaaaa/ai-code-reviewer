import { useState, useEffect, useCallback } from 'react'
import { authApi, type UserInfo } from '@/lib/api'

export function useAuth() {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const fetchUser = useCallback(async () => {
    const token = localStorage.getItem('auth_token')
    if (!token) {
      setLoading(false)
      return
    }
    try {
      const { data } = await authApi.me()
      setUser(data)
      setIsAuthenticated(true)
    } catch {
      localStorage.removeItem('auth_token')
      setIsAuthenticated(false)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await authApi.login(email, password)
    localStorage.setItem('auth_token', data.access_token)
    setIsAuthenticated(true)
    await fetchUser()
    return data
  }, [fetchUser])

  const register = useCallback(async (email: string, username: string, password: string) => {
    const { data } = await authApi.register(email, username, password)
    localStorage.setItem('auth_token', data.access_token)
    setIsAuthenticated(true)
    await fetchUser()
    return data
  }, [fetchUser])

  const logout = useCallback(() => {
    localStorage.removeItem('auth_token')
    setUser(null)
    setIsAuthenticated(false)
  }, [])

  return { user, loading, isAuthenticated, login, register, logout, refreshUser: fetchUser }
}
