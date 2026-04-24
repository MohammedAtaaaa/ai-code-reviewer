import type { ReviewResult } from '@/lib/api'
import { ScoreRing } from '@/components/ui/ScoreRing'
import { ScoreBar } from '@/components/ui/ScoreBar'
import { Badge } from '@/components/ui/Badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import { getScoreLabel, getSeverityColor, formatDate } from '@/lib/utils'
import {
  AlertTriangle,
  Shield,
  Lightbulb,
  Copy,
  Check,
  FileDown,
  Brain,
  Clock,
  Layers,
} from 'lucide-react'
import { useState } from 'react'
import toast from 'react-hot-toast'
import jsPDF from 'jspdf'

interface ReviewResultsProps {
  result: ReviewResult
}

export function ReviewResults({ result }: ReviewResultsProps) {
  const [copiedField, setCopiedField] = useState<string | null>(null)

  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text)
    setCopiedField(field)
    toast.success('Copied to clipboard')
    setTimeout(() => setCopiedField(null), 2000)
  }

  const exportPdf = () => {
    const doc = new jsPDF()
    const margin = 20
    let y = margin

    doc.setFontSize(18)
    doc.text('AI Code Review Report', margin, y)
    y += 12

    doc.setFontSize(10)
    doc.setTextColor(100)
    doc.text(`Review ID: ${result.id}`, margin, y)
    y += 6
    doc.text(`Date: ${formatDate(result.reviewed_at)}`, margin, y)
    y += 6
    doc.text(`Version: ${result.version}`, margin, y)
    y += 12

    doc.setFontSize(14)
    doc.setTextColor(0)
    doc.text(`Overall Score: ${result.score_breakdown.overall.toFixed(1)}/10 - ${getScoreLabel(result.score_breakdown.overall)}`, margin, y)
    y += 10

    doc.setFontSize(11)
    doc.text('Score Breakdown:', margin, y)
    y += 7

    doc.setFontSize(9)
    const dimensions = ['clean_code', 'readability', 'maintainability', 'security', 'ml_quality'] as const
    for (const dim of dimensions) {
      const label = dim.replace(/_/g, ' ')
      const score = result.score_breakdown[dim]
      doc.text(`  ${label}: ${score.toFixed(1)}/10`, margin, y)
      y += 5
    }
    y += 5

    if (result.issues.length > 0) {
      doc.setFontSize(11)
      doc.text(`Issues (${result.issues.length}):`, margin, y)
      y += 7
      doc.setFontSize(9)
      for (const issue of result.issues) {
        if (y > 270) { doc.addPage(); y = margin }
        doc.text(`  [${issue.severity.toUpperCase()}] Line ${issue.line}: ${issue.message}`, margin, y, { maxWidth: 170 })
        y += 5
      }
      y += 5
    }

    if (result.security_flags.length > 0) {
      doc.setFontSize(11)
      doc.text(`Security Flags (${result.security_flags.length}):`, margin, y)
      y += 7
      doc.setFontSize(9)
      for (const flag of result.security_flags) {
        if (y > 270) { doc.addPage(); y = margin }
        doc.text(`  [${flag.severity.toUpperCase()}] ${flag.rule}: ${flag.message}`, margin, y, { maxWidth: 170 })
        y += 5
      }
      y += 5
    }

    if (result.suggestions.length > 0) {
      if (y > 250) { doc.addPage(); y = margin }
      doc.setFontSize(11)
      doc.text('Suggestions:', margin, y)
      y += 7
      doc.setFontSize(9)
      for (const s of result.suggestions) {
        if (y > 270) { doc.addPage(); y = margin }
        doc.text(`  - ${s}`, margin, y, { maxWidth: 170 })
        y += 5
      }
    }

    doc.save(`code-review-${result.id.slice(0, 8)}.pdf`)
    toast.success('PDF exported successfully')
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header with overall score */}
      <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
        <ScoreRing score={result.score_breakdown.overall} size={140} label={getScoreLabel(result.score_breakdown.overall)} />
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-3 flex-wrap">
            <Badge variant={result.score >= 8 ? 'success' : result.score >= 6 ? 'warning' : 'destructive'}>
              {getScoreLabel(result.score)}
            </Badge>
            <Badge variant="outline">
              <Layers size={12} className="mr-1" /> v{result.version}
            </Badge>
            {result.cached && <Badge variant="info">Cached</Badge>}
            {result.ml_prediction && (
              <Badge variant={result.ml_prediction.quality_label === 'good' ? 'success' : result.ml_prediction.quality_label === 'medium' ? 'warning' : 'destructive'}>
                <Brain size={12} className="mr-1" />
                ML: {result.ml_prediction.quality_label} ({(result.ml_prediction.confidence * 100).toFixed(0)}%)
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1">
              <Clock size={14} />
              {formatDate(result.reviewed_at)}
            </span>
            <span>{result.issues.length} issue{result.issues.length !== 1 ? 's' : ''}</span>
            <span>{result.security_flags.length} security flag{result.security_flags.length !== 1 ? 's' : ''}</span>
          </div>
          <div className="flex gap-2 pt-1">
            <Button
              variant="outline"
              size="sm"
              onClick={() => copyToClipboard(result.summary, 'summary')}
            >
              {copiedField === 'summary' ? <Check size={14} /> : <Copy size={14} />}
              Copy Summary
            </Button>
            <Button variant="outline" size="sm" onClick={exportPdf}>
              <FileDown size={14} />
              Export PDF
            </Button>
          </div>
        </div>
      </div>

      {/* Score Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Score Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-3">
              <ScoreBar label="clean_code" score={result.score_breakdown.clean_code} />
              <ScoreBar label="readability" score={result.score_breakdown.readability} />
              <ScoreBar label="maintainability" score={result.score_breakdown.maintainability} />
            </div>
            <div className="space-y-3">
              <ScoreBar label="security" score={result.score_breakdown.security} />
              <ScoreBar label="ml_quality" score={result.score_breakdown.ml_quality} />
            </div>
          </div>
          {/* Explanations */}
          <div className="mt-6 space-y-3">
            {Object.entries(result.score_breakdown.explanations).map(([key, explanations]) =>
              explanations.length > 0 ? (
                <div key={key} className="text-sm">
                  <span className="font-medium capitalize text-foreground">{key.replace(/_/g, ' ')}: </span>
                  <span className="text-muted-foreground">{explanations.join(' ')}</span>
                </div>
              ) : null
            )}
          </div>
        </CardContent>
      </Card>

      {/* Issues */}
      {result.issues.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle size={18} className="text-warning" />
              Issues ({result.issues.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {result.issues.map((issue, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 rounded-lg border border-border p-3 transition-colors hover:bg-accent/50"
                >
                  <Badge
                    variant={issue.severity === 'critical' ? 'destructive' : issue.severity === 'warning' ? 'warning' : 'info'}
                    className="mt-0.5 shrink-0"
                  >
                    {issue.severity}
                  </Badge>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <code className="text-xs font-mono bg-muted px-1.5 py-0.5 rounded">{issue.rule}</code>
                      <span className="text-xs text-muted-foreground">Line {issue.line}</span>
                    </div>
                    <p className="text-sm text-foreground">{issue.message}</p>
                    {issue.suggestion && (
                      <p className="text-xs text-muted-foreground italic">{issue.suggestion}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Security Flags */}
      {result.security_flags.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield size={18} className="text-destructive" />
              Security Flags ({result.security_flags.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {result.security_flags.map((flag, i) => (
                <div
                  key={i}
                  className={`rounded-lg border p-3 ${getSeverityColor(flag.severity)}`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <code className="text-xs font-mono font-bold">{flag.rule}</code>
                    <Badge
                      variant={flag.severity === 'critical' ? 'destructive' : 'warning'}
                      className="text-[10px]"
                    >
                      {flag.severity}
                    </Badge>
                    <span className="text-xs opacity-70">Line {flag.line}</span>
                  </div>
                  <p className="text-sm">{flag.message}</p>
                  <p className="text-xs opacity-80 mt-1">{flag.recommendation}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Suggestions */}
      {result.suggestions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb size={18} className="text-warning" />
              Suggestions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {result.suggestions.map((s, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                  {s}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Complexity Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Complexity Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Cyclomatic', value: result.complexity_metrics.cyclomatic_complexity },
              { label: 'Maintainability', value: result.complexity_metrics.maintainability_index, suffix: '/100' },
              { label: 'Lines of Code', value: result.complexity_metrics.lines_of_code },
              { label: 'Comment Ratio', value: result.complexity_metrics.comment_ratio, suffix: '%' },
              { label: 'Functions', value: result.complexity_metrics.function_count },
              { label: 'Classes', value: result.complexity_metrics.class_count },
              { label: 'SLOC', value: result.complexity_metrics.source_lines_of_code },
            ].map(({ label, value, suffix }) => (
              <div key={label} className="text-center p-3 rounded-lg bg-muted/50">
                <div className="text-lg font-bold text-foreground tabular-nums">
                  {typeof value === 'number' ? value.toFixed(value % 1 === 0 ? 0 : 1) : value}
                  {suffix && <span className="text-xs font-normal text-muted-foreground">{suffix}</span>}
                </div>
                <div className="text-xs text-muted-foreground">{label}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
