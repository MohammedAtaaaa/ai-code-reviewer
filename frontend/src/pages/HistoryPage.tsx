import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Header } from '@/components/layout/Header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import Button from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { reviewApi, type ReviewListItem } from '@/lib/api'
import { formatDate, getScoreColor, getScoreLabel } from '@/lib/utils'
import { History, ChevronLeft, ChevronRight, Search, Code2 } from 'lucide-react'
import Input from '@/components/ui/Input'

interface HistoryPageProps {
  theme: 'light' | 'dark'
  onToggleTheme: () => void
}

export function HistoryPage({ theme, onToggleTheme }: HistoryPageProps) {
  const navigate = useNavigate()
  const [reviews, setReviews] = useState<ReviewListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState('')
  const pageSize = 10

  useEffect(() => {
    const fetchReviews = async () => {
      setLoading(true)
      try {
        const { data } = await reviewApi.list(0, 100)
        setReviews(data.reviews)
      } catch {
        // ignore
      } finally {
        setLoading(false)
      }
    }
    fetchReviews()
  }, [])

  const filteredReviews = reviews.filter((r) => {
    if (!search) return true
    const q = search.toLowerCase()
    return (
      r.language.toLowerCase().includes(q) ||
      r.id.toLowerCase().includes(q) ||
      (r.code && r.code.toLowerCase().includes(q)) ||
      (r.ml_quality_label && r.ml_quality_label.toLowerCase().includes(q))
    )
  })

  const totalPages = Math.ceil(filteredReviews.length / pageSize)
  const paginatedReviews = filteredReviews.slice(page * pageSize, (page + 1) * pageSize)

  return (
    <div>
      <Header
        title="Review History"
        subtitle={`${reviews.length} total reviews`}
        theme={theme}
        onToggleTheme={onToggleTheme}
      />
      <div className="p-6 space-y-6">
        {/* Search */}
        <div className="relative animate-fade-in">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by language, ID, or code content..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0) }}
            className="pl-9"
          />
        </div>

        {loading ? (
          <div className="flex justify-center py-16">
            <Spinner size={32} label="Loading review history..." />
          </div>
        ) : filteredReviews.length === 0 ? (
          <Card className="animate-fade-in">
            <CardContent className="flex flex-col items-center gap-3 py-16">
              <History size={48} className="text-muted-foreground/30" />
              <p className="text-muted-foreground">
                {search ? 'No reviews match your search' : 'No reviews yet'}
              </p>
              {!search && (
                <Button variant="primary" size="sm" onClick={() => navigate('/review')}>
                  <Code2 size={16} />
                  Submit Your First Review
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <>
            <Card className="animate-fade-in">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <History size={18} />
                  Reviews
                  <Badge variant="outline">{filteredReviews.length}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {paginatedReviews.map((review, i) => (
                    <button
                      key={review.id}
                      onClick={() => navigate(`/review/${review.id}`)}
                      className="flex w-full items-center gap-4 rounded-lg border border-border p-4 text-left transition-all hover:bg-accent/50 hover:border-primary/20 animate-fade-in cursor-pointer"
                      style={{ animationDelay: `${i * 50}ms` }}
                    >
                      {/* Score */}
                      <div className="flex flex-col items-center w-16 shrink-0">
                        <span className={`text-2xl font-bold tabular-nums ${getScoreColor(review.score)}`}>
                          {review.score.toFixed(1)}
                        </span>
                        <span className="text-[10px] text-muted-foreground">{getScoreLabel(review.score)}</span>
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0 space-y-1">
                        <code className="text-xs text-muted-foreground font-mono truncate block">
                          {review.code ? review.code.split('\n')[0].slice(0, 80) : `Review ${review.id.slice(0, 8)}`}
                        </code>
                        <div className="flex items-center gap-2 flex-wrap">
                          <Badge variant="outline">{review.language}</Badge>
                          {review.issue_count > 0 && (
                            <Badge variant="warning">{review.issue_count} issue{review.issue_count !== 1 ? 's' : ''}</Badge>
                          )}
                          {review.security_flag_count > 0 && (
                            <Badge variant="destructive">{review.security_flag_count} security</Badge>
                          )}
                          {review.ml_quality_label && (
                            <Badge variant={
                              review.ml_quality_label === 'good' ? 'success' :
                              review.ml_quality_label === 'medium' ? 'warning' : 'destructive'
                            }>
                              ML: {review.ml_quality_label}
                            </Badge>
                          )}
                        </div>
                      </div>

                      {/* Date */}
                      <span className="text-xs text-muted-foreground shrink-0 hidden md:block">
                        {formatDate(review.reviewed_at)}
                      </span>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === 0}
                  onClick={() => setPage(page - 1)}
                >
                  <ChevronLeft size={16} />
                </Button>
                <span className="text-sm text-muted-foreground px-3">
                  Page {page + 1} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= totalPages - 1}
                  onClick={() => setPage(page + 1)}
                >
                  <ChevronRight size={16} />
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
