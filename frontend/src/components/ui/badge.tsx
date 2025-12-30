import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: { 
      variant: {
        default:
          "border-transparent bg-gradient-to-r from-primary to-primary/80 text-primary-foreground shadow-sm shadow-primary/20 hover:shadow-md hover:shadow-primary/30",
        secondary:
          "border-transparent bg-secondary/80 text-secondary-foreground backdrop-blur-sm hover:bg-secondary",
        destructive:
          "border-transparent bg-gradient-to-r from-destructive to-red-500 text-destructive-foreground shadow-sm shadow-destructive/20",
        outline: 
          "border-border/50 text-foreground bg-background/50 backdrop-blur-sm hover:bg-muted/50 hover:border-primary/30",
        success:
          "border-transparent bg-gradient-to-r from-emerald-500 to-green-500 text-white shadow-sm shadow-emerald-500/20",
        warning:
          "border-transparent bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-sm shadow-amber-500/20",
        info:
          "border-transparent bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-sm shadow-blue-500/20",
        glass:
          "border-white/20 bg-white/10 text-foreground backdrop-blur-lg",
        glow:
          "border-transparent bg-primary text-primary-foreground glow-border animate-pulse-glow",
        dot:
          "border-border/30 bg-muted/50 text-muted-foreground pl-2.5",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  dot?: boolean;
  dotColor?: 'green' | 'red' | 'yellow' | 'blue';
}

function Badge({ className, variant, dot, dotColor = 'green', children, ...props }: BadgeProps) {
  const dotColors = {
    green: 'bg-emerald-500',
    red: 'bg-red-500',
    yellow: 'bg-amber-500',
    blue: 'bg-blue-500',
  };

  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props}>
      {dot && (
        <span className={cn("h-1.5 w-1.5 rounded-full animate-pulse", dotColors[dotColor])} />
      )}
      {children}
    </div>
  )
}

export { Badge, badgeVariants }