import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import Button from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { Header } from '@/components/layout/Header'
import { healthApi, reviewApi, type ReviewListItem } from '@/lib/api'
import { formatDate, getScoreColor } from '@/lib/utils'
import {
  Activity,
  Code2,
  Shield,
  TrendingUp,
  AlertTriangle,
  ArrowRight,
  Wifi,
  WifiOff,
} from 'lucide-react'

interface DashboardPageProps {
  theme: 'light' | 'dark'
  onToggleTheme: () => void
}

export function DashboardPage({ theme, onToggleTheme }: DashboardPageProps) {
  const navigate = useNavigate()
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [apiVersion, setApiVersion] = useState('')
  const [reviews, setReviews] = useState<ReviewListItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const { data } = await healthApi.check()
        setApiStatus(data.status === 'healthy' ? 'online' : 'offline')
        setApiVersion(data.version)
      } catch {
        setApiStatus('offline')
      }
    }

    const fetchReviews = async () => {
      try {
        const { data } = await reviewApi.list(0, 50)
        setReviews(data.reviews)
      } catch {
        // ignore
      } finally {
        setLoading(false)
      }
    }

    checkHealth()
    fetchReviews()
  }, [])

  const stats = {
    totalReviews: reviews.length,
    avgScore: reviews.length > 0 ? reviews.reduce((sum, r) => sum + r.score, 0) / reviews.length : 0,
    totalIssues: reviews.reduce((sum, r) => sum + r.issue_count, 0),
    securityFlags: reviews.reduce((sum, r) => sum + r.security_flag_count, 0),
  }

  return (
    <div>
      <Header
        title="Dashboard"
        subtitle="Overview of your AI Code Reviewer"
        theme={theme}
        onToggleTheme={onToggleTheme}
      />
      <div className="p-6 space-y-6">
        {/* API Status */}
        <Card className="animate-fade-in">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {apiStatus === 'checking' ? (
                  <Spinner size={20} />
                ) : apiStatus === 'online' ? (
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <Wifi size={20} className="text-success" />
                      <span className="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-success animate-pulse-glow" />
                    </div>
                    <span className="text-sm font-medium text-success">API Online</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <WifiOff size={20} className="text-destructive" />
                    <span className="text-sm font-medium text-destructive">API Offline</span>
                  </div>
                )}
                {apiVersion && (
                  <Badge variant="outline">v{apiVersion}</Badge>
                )}
              </div>
              <Button variant="primary" size="sm" onClick={() => navigate('/review')}>
                <Code2 size={16} />
                New Review
                <ArrowRight size={14} />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Stats Grid */}
        {loading ? (
          <div className="flex justify-center py-12">
            <Spinner size={32} label="Loading statistics..." />
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 stagger">
            <Card hover>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Reviews</p>
                    <p className="text-3xl font-bold text-foreground mt-1">{stats.totalReviews}</p>
                  </div>
                  <div className="rounded-xl bg-primary/10 p-3">
                    <Code2 size={24} className="text-primary" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card hover>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Average Score</p>
                    <p className={`text-3xl font-bold mt-1 ${getScoreColor(stats.avgScore)}`}>
                      {stats.avgScore > 0 ? stats.avgScore.toFixed(1) : '—'}
                    </p>
                  </div>
                  <div className="rounded-xl bg-success/10 p-3">
                    <TrendingUp size={24} className="text-success" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card hover>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Issues</p>
                    <p className="text-3xl font-bold text-foreground mt-1">{stats.totalIssues}</p>
                  </div>
                  <div className="rounded-xl bg-warning/10 p-3">
                    <AlertTriangle size={24} className="text-warning" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card hover>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Security Flags</p>
                    <p className="text-3xl font-bold text-foreground mt-1">{stats.securityFlags}</p>
                  </div>
                  <div className="rounded-xl bg-destructive/10 p-3">
                    <Shield size={24} className="text-destructive" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Recent Reviews */}
        <Card className="animate-fade-in" style={{ animationDelay: '200ms' }}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Activity size={18} />
                Recent Reviews
              </CardTitle>
              {reviews.length > 0 && (
                <Button variant="ghost" size="sm" onClick={() => navigate('/history')}>
                  View All <ArrowRight size={14} />
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {reviews.length === 0 ? (
              <div className="flex flex-col items-center gap-3 py-12 text-center">
                <Code2 size={48} className="text-muted-foreground/30" />
                <p className="text-muted-foreground">No reviews yet</p>
                <Button variant="primary" size="sm" onClick={() => navigate('/review')}>
                  Submit Your First Review
                </Button>
              </div>
            ) : (
              <div className="space-y-2">
                {reviews.slice(0, 5).map((review) => (
                  <button
                    key={review.id}
                    onClick={() => navigate(`/review/${review.id}`)}
                    className="flex w-full items-center gap-4 rounded-lg border border-border p-3 text-left transition-all hover:bg-accent/50 hover:border-primary/20 cursor-pointer"
                  >
                    <div className={`text-lg font-bold tabular-nums w-12 text-center ${getScoreColor(review.score)}`}>
                      {review.score.toFixed(1)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <code className="text-xs text-muted-foreground font-mono truncate block">
                        {review.code ? review.code.split('\n')[0].slice(0, 60) : review.id.slice(0, 8)}
                      </code>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <Badge variant="outline">{review.language}</Badge>
                      {review.issue_count > 0 && (
                        <Badge variant="warning">{review.issue_count} issues</Badge>
                      )}
                      {review.security_flag_count > 0 && (
                        <Badge variant="destructive">{review.security_flag_count} security</Badge>
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground shrink-0 hidden sm:block">
                      {formatDate(review.reviewed_at)}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
