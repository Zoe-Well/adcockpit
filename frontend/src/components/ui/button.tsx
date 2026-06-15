import * as React from "react"
import { cn } from "../../lib/utils"

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "secondary" | "outline" | "ghost"
  size?: "sm" | "default" | "lg"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    const base = "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 cursor-pointer"
    const variants = {
      default: "bg-blue-600 text-white hover:bg-blue-700",
      secondary: "bg-slate-100 text-slate-700 hover:bg-slate-200",
      outline: "border border-slate-200 bg-white hover:bg-slate-50 text-slate-600",
      ghost: "hover:bg-slate-100 text-slate-600",
    }
    const sizes = {
      sm: "h-8 px-3 text-xs", default: "h-9 px-4 text-sm", lg: "h-10 px-6 text-sm"
    }
    return <button className={cn(base, variants[variant], sizes[size], className)} ref={ref} {...props} />
  }
)
Button.displayName = "Button"
export { Button }
