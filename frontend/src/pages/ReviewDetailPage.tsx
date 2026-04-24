import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Header } from '@/components/layout/Header'
import { ReviewResults } from '@/components/review/ReviewResults'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import Button from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { reviewApi, type ReviewResult, type VersionHistory } from '@/lib/api'
import { formatDate, getScoreColor } from '@/lib/utils'
import { ArrowLeft, GitBranch, History } from 'lucide-react'

interface ReviewDetailPageProps {
  theme: 'light' | 'dark'
  onToggleTheme: () => void
}

export function ReviewDetailPage({ theme, onToggleTheme }: ReviewDetailPageProps) {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [result, setResult] = useState<ReviewResult | null>(null)
  const [history, setHistory] = useState<VersionHistory | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return

    const fetchData = async () => {
      setLoading(true)
      try {
        const { data } = await reviewApi.getById(id)
        setResult(data)

        try {
          const { data: historyData } = await reviewApi.getHistory(id)
          setHistory(historyData)
        } catch {
          // history might not exist
        }
      } catch {
        setError('Review not found')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [id])

  return (
    <div>
      <Header
        title="Review Details"
        subtitle={id ? `Review ${id.slice(0, 8)}...` : ''}
        theme={theme}
        onToggleTheme={onToggleTheme}
      />
      <div className="p-6 space-y-6">
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
          <ArrowLeft size={16} />
          Back
        </Button>

        {loading ? (
          <div className="flex justify-center py-16">
            <Spinner size={32} label="Loading review..." />
          </div>
        ) : error ? (
          <Card>
            <CardContent className="flex flex-col items-center gap-3 py-16">
              <p className="text-destructive font-medium">{error}</p>
              <Button variant="outline" onClick={() => navigate('/history')}>
                Go to History
              </Button>
            </CardContent>
          </Card>
        ) : result ? (
          <>
            <ReviewResults result={result} />

            {/* Version History */}
            {history && history.total_versions > 1 && (
              <Card className="animate-fade-in">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <GitBranch size={18} />
                    Version History
                    <Badge variant="outline">{history.total_versions} versions</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {history.versions.map((version) => (
                      <button
                        key={version.id}
                        onClick={() => navigate(`/review/${version.id}`)}
                        className={`flex w-full items-center gap-4 rounded-lg border p-3 text-left transition-all hover:bg-accent/50 cursor-pointer ${
                          version.id === id ? 'border-primary bg-primary/5' : 'border-border'
                        }`}
                      >
                        <div className="flex items-center gap-2 shrink-0">
                          <History size={14} className="text-muted-foreground" />
                          <Badge variant={version.id === id ? 'default' : 'outline'}>
                            v{version.version}
                          </Badge>
                        </div>
                        <div className={`font-bold tabular-nums ${getScoreColor(version.score)}`}>
                          {version.score.toFixed(1)}
                        </div>
                        <div className="flex-1 flex gap-2 flex-wrap">
                          <span className="text-xs text-muted-foreground">
                            Issues: {version.issue_count}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            Security: {version.security_flag_count}
                          </span>
                        </div>
                        <span className="text-xs text-muted-foreground shrink-0">
                          {formatDate(version.reviewed_at)}
                        </span>
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        ) : null}
      </div>
    </div>
  )
}
