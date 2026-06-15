import * as React from "react"
import { cn } from "../../lib/utils"

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success" | "warning"
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "bg-blue-100 text-blue-700", secondary: "bg-slate-100 text-slate-600",
    destructive: "bg-red-100 text-red-700", outline: "border border-slate-200 text-slate-600",
    success: "bg-green-100 text-green-700", warning: "bg-amber-100 text-amber-700",
  }
  return <div className={cn("inline-flex items-center rounded px-2 py-0.5 text-xs font-medium", variants[variant], className)} {...props} />
}
export { Badge }
