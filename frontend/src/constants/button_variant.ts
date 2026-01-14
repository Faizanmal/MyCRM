import { cva } from "class-variance-authority";

export const buttonVariants = cva(
    "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-medium ring-offset-background transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 active:scale-[0.98]",
    {
      variants: {
        variant: {
          default: 
            "bg-gradient-to-r from-primary to-primary/90 text-primary-foreground hover:from-primary/90 hover:to-primary shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 hover:-translate-y-0.5",
          destructive:
            "bg-gradient-to-r from-destructive to-red-600 text-destructive-foreground hover:from-destructive/90 hover:to-red-600/90 shadow-lg shadow-destructive/25 hover:shadow-xl hover:shadow-destructive/30 hover:-translate-y-0.5",
          outline:
            "border-2 border-input bg-background/50 backdrop-blur-sm hover:bg-accent hover:text-accent-foreground hover:border-primary/50",
          secondary:
            "bg-secondary/80 text-secondary-foreground hover:bg-secondary backdrop-blur-sm shadow-sm hover:shadow-md hover:-translate-y-0.5",
          ghost: 
            "hover:bg-accent/50 hover:text-accent-foreground backdrop-blur-sm",
          link: 
            "text-primary underline-offset-4 hover:underline decoration-2 decoration-primary/50",
          hero: 
            "btn-hero relative overflow-hidden",
          premium: 
            "btn-premium relative overflow-hidden bg-gradient-to-r from-primary via-purple-500 to-pink-500 text-white shadow-xl shadow-primary/30 hover:shadow-2xl hover:shadow-primary/40 hover:-translate-y-1",
          glass:
            "glass border-white/20 text-foreground hover:bg-white/20 dark:hover:bg-white/10 backdrop-blur-xl",
          glow:
            "bg-primary text-primary-foreground glow-border animate-pulse-glow hover:-translate-y-0.5",
          success:
            "bg-gradient-to-r from-emerald-500 to-green-600 text-white shadow-lg shadow-emerald-500/25 hover:shadow-xl hover:shadow-emerald-500/30 hover:-translate-y-0.5",
          warning:
            "bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg shadow-amber-500/25 hover:shadow-xl hover:shadow-amber-500/30 hover:-translate-y-0.5",
        },
        size: {
          default: "h-10 px-5 py-2",
          sm: "h-9 rounded-lg px-4 text-xs",
          lg: "h-12 rounded-xl px-8 text-base",
          xl: "h-14 rounded-2xl px-10 text-lg",
          icon: "h-10 w-10 rounded-xl",
        },
      },
      defaultVariants: {
        variant: "default",
        size: "default",
      },
    }
  )
  
