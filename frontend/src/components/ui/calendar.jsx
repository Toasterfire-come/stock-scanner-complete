import * as React from "react"
import { cn } from "../../lib/utils"

const Calendar = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("border rounded-md p-3", className)} {...props} />
))
Calendar.displayName = "Calendar"

export { Calendar }
