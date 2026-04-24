import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'react'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'secondary' | 'destructive' | 'success' | 'warning' | 'info' | 'outline'
}

export function Badge({ className, variant = 'default', children, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors',
        {
          'bg-primary/10 text-primary border border-primary/20': variant === 'default',
          'bg-secondary text-secondary-foreground': variant === 'secondary',
          'bg-destructive/10 text-destructive border border-destructive/20': variant === 'destructive',
          'bg-success/10 text-success border border-success/20': variant === 'success',
          'bg-warning/10 text-warning border border-warning/20': variant === 'warning',
          'bg-info/10 text-info border border-info/20': variant === 'info',
          'border border-border text-muted-foreground': variant === 'outline',
        },
        className,
      )}
      {...props}
    >
      {children}
    </span>
  )
}
