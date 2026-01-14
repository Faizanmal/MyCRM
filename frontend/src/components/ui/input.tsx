import * as React from "react"

import { cn } from "@/lib/utils"

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input"> & {
  variant?: 'default' | 'glass' | 'filled';
}>(
  ({ className, type, variant = 'default', ...props }, ref) => {
    const variants = {
      default: "border border-input bg-background hover:border-primary/50 focus:border-primary",
      glass: "border border-white/20 bg-white/5 backdrop-blur-lg hover:bg-white/10 focus:bg-white/15",
      filled: "border-0 bg-muted/50 hover:bg-muted focus:bg-muted",
    };

    return (
      <input
        type={type} 
        className={cn(
          "flex h-11 w-full rounded-xl px-4 py-2.5 text-base ring-offset-background transition-all duration-300",
          "file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground",
          "placeholder:text-muted-foreground/70",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-0",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "md:text-sm",
          variants[variant],
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
