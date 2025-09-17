import * as React from "react"
import { cn } from "../../lib/utils"

const Carousel = React.forwardRef(({ className, children, ...props }, ref) => (
  <div ref={ref} className={cn("relative w-full overflow-hidden", className)} {...props}>
    <div className="flex gap-4 overflow-x-auto pb-2">
      {children}
    </div>
  </div>
))
Carousel.displayName = "Carousel"

export { Carousel }
