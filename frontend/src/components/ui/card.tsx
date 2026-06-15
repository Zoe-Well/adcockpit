import * as React from "react"
import { cn } from "../../lib/utils"

const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("rounded-lg border border-slate-200 bg-white", className)} {...props} />
  )
)
Card.displayName = "Card"

const CardHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("px-4 py-3 border-b border-slate-200", className)} {...props} />
)

const CardContent = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("p-4", className)} {...props} />
)

export { Card, CardHeader, CardContent }
