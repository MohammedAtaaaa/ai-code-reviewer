import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getScoreColor(score: number): string {
  if (score >= 8) return 'text-success'
  if (score >= 6) return 'text-warning'
  return 'text-destructive'
}

export function getScoreBg(score: number): string {
  if (score >= 8) return 'bg-success/10 border-success/20'
  if (score >= 6) return 'bg-warning/10 border-warning/20'
  return 'bg-destructive/10 border-destructive/20'
}

export function getScoreLabel(score: number): string {
  if (score >= 9) return 'Excellent'
  if (score >= 8) return 'Great'
  if (score >= 7) return 'Good'
  if (score >= 6) return 'Fair'
  if (score >= 4) return 'Needs Improvement'
  return 'Poor'
}

export function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'critical': return 'text-red-500 bg-red-500/10 border-red-500/20'
    case 'error': return 'text-orange-500 bg-orange-500/10 border-orange-500/20'
    case 'warning': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20'
    case 'info': return 'text-blue-500 bg-blue-500/10 border-blue-500/20'
    default: return 'text-muted-foreground bg-muted border-border'
  }
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function truncateCode(code: string, maxLen = 80): string {
  const firstLine = code.split('\n')[0]
  if (firstLine.length > maxLen) return firstLine.slice(0, maxLen) + '...'
  return firstLine
}
