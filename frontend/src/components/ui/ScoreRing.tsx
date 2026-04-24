import { cn } from '@/lib/utils'

interface ScoreRingProps {
  score: number
  size?: number
  strokeWidth?: number
  className?: string
  label?: string
}

export function ScoreRing({ score, size = 120, strokeWidth = 8, className, label }: ScoreRingProps) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const progress = (score / 10) * circumference
  const offset = circumference - progress

  const getColor = () => {
    if (score >= 8) return 'stroke-success'
    if (score >= 6) return 'stroke-warning'
    return 'stroke-destructive'
  }

  const getTextColor = () => {
    if (score >= 8) return 'text-success'
    if (score >= 6) return 'text-warning'
    return 'text-destructive'
  }

  return (
    <div className={cn('relative inline-flex flex-col items-center gap-1', className)}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={strokeWidth}
          className="stroke-muted"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className={cn(getColor(), 'transition-all duration-1000 ease-out')}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className={cn('text-2xl font-bold', getTextColor())}>
          {score.toFixed(1)}
        </span>
      </div>
      {label && (
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
      )}
    </div>
  )
}
