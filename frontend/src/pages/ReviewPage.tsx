import { useState } from 'react'
import { Header } from '@/components/layout/Header'
import { CodeEditor } from '@/components/review/CodeEditor'
import { ReviewResults } from '@/components/review/ReviewResults'
import { Card, CardContent } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { reviewApi, type ReviewResult } from '@/lib/api'
import { Sparkles, RotateCcw, Code2 } from 'lucide-react'
import toast from 'react-hot-toast'

interface ReviewPageProps {
  theme: 'light' | 'dark'
  onToggleTheme: () => void
}

export function ReviewPage({ theme, onToggleTheme }: ReviewPageProps) {
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('python')
  const [result, setResult] = useState<ReviewResult | null>(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    if (!code.trim()) {
      toast.error('Please enter some code to analyze')
      return
    }

    setLoading(true)
    setResult(null)

    try {
      const { data } = await reviewApi.submit(code, language)
      setResult(data)
      toast.success(`Analysis complete! Score: ${data.score_breakdown.overall.toFixed(1)}/10`)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      const msg = error.response?.data?.detail || 'Failed to analyze code. Please try again.'
      toast.error(typeof msg === 'string' ? msg : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setCode('')
    setResult(null)
  }

  return (
    <div>
      <Header
        title="Code Review"
        subtitle="Submit your code for AI-powered analysis"
        theme={theme}
        onToggleTheme={onToggleTheme}
      />
      <div className="p-6 space-y-6">
        {/* Code Input */}
        <Card className="animate-fade-in">
          <CardContent className="p-6">
            <CodeEditor
              code={code}
              language={language}
              onChange={setCode}
              onLanguageChange={setLanguage}
              theme={theme}
            />
            <div className="flex items-center justify-between mt-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Code2 size={14} />
                <span>{code.split('\n').length} lines</span>
                <span className="text-border">|</span>
                <span>{code.length} characters</span>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={handleReset} disabled={!code && !result}>
                  <RotateCcw size={16} />
                  Reset
                </Button>
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handleAnalyze}
                  disabled={loading || !code.trim()}
                >
                  {loading ? (
                    <Spinner size={18} />
                  ) : (
                    <Sparkles size={18} />
                  )}
                  {loading ? 'Analyzing...' : 'Analyze Code'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center gap-4 py-12 animate-fade-in">
            <div className="relative">
              <Spinner size={48} />
            </div>
            <div className="text-center">
              <p className="font-medium text-foreground">Analyzing your code...</p>
              <p className="text-sm text-muted-foreground mt-1">
                Running static analysis, security checks, and ML prediction
              </p>
            </div>
          </div>
        )}

        {/* Results */}
        {result && !loading && <ReviewResults result={result} />}
      </div>
    </div>
  )
}
