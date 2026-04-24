import { cn } from '@/lib/utils'

interface ScoreBarProps {
  label: string
  score: number
  maxScore?: number
  className?: string
}

export function ScoreBar({ label, score, maxScore = 10, className }: ScoreBarProps) {
  const percentage = (score / maxScore) * 100

  const getColor = () => {
    if (score >= 8) return 'bg-success'
    if (score >= 6) return 'bg-warning'
    return 'bg-destructive'
  }

  return (
    <div className={cn('space-y-1.5', className)}>
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium capitalize text-foreground">
          {label.replace(/_/g, ' ')}
        </span>
        <span className="font-semibold tabular-nums text-foreground">
          {score.toFixed(1)}/{maxScore}
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
        <div
          className={cn('h-full rounded-full transition-all duration-1000 ease-out', getColor())}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
