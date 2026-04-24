import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

interface SpinnerProps {
  size?: number
  className?: string
  label?: string
}

export function Spinner({ size = 24, className, label }: SpinnerProps) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Loader2 size={size} className="animate-spin text-primary" />
      {label && <span className="text-sm text-muted-foreground">{label}</span>}
    </div>
  )
}
