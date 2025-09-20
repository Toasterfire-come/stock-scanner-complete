import * as React from "react"
import * as ProgressPrimitive from "@radix-ui/react-progress"

import { cn } from "../../lib/utils"

const Progress = React.forwardRef(({ className, value, ...props }, ref) => (
  <ProgressPrimitive.Root
    ref={ref}
    className={cn(
<<<<<<< HEAD
      "relative h-4 w-full overflow-hidden rounded-full bg-secondary",
      className
    )}
    {...props}
  >
    <ProgressPrimitive.Indicator
      className="h-full w-full flex-1 bg-primary transition-all"
      style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
    />
=======
      "relative h-2 w-full overflow-hidden rounded-full bg-primary/20",
      className
    )}
    {...props}>
    <ProgressPrimitive.Indicator
      className="h-full w-full flex-1 bg-primary transition-all"
      style={{ transform: `translateX(-${100 - (value || 0)}%)` }} />
>>>>>>> b9dee287 (auto-commit for f45bf728-febb-4567-ac8e-02aafd409816)
  </ProgressPrimitive.Root>
))
Progress.displayName = ProgressPrimitive.Root.displayName

<<<<<<< HEAD
export { Progress }
=======
export { Progress }
>>>>>>> b9dee287 (auto-commit for f45bf728-febb-4567-ac8e-02aafd409816)
