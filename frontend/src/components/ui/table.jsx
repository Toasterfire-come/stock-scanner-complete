import * as React from "react"

import { cn } from "../../lib/utils"

const Table = React.forwardRef(({ className, ...props }, ref) => (
  <div className="relative w-full overflow-auto">
    <table
      ref={ref}
      className={cn("w-full caption-bottom text-sm", className)}
<<<<<<< HEAD
      {...props}
    />
=======
      {...props} />
>>>>>>> b9dee287 (auto-commit for f45bf728-febb-4567-ac8e-02aafd409816)
  </div>
))
Table.displayName = "Table"

const TableHeader = React.forwardRef(({ className, ...props }, ref) => (
  <thead ref={ref} className={cn("[&_tr]:border-b", className)} {...props} />
))
TableHeader.displayName = "TableHeader"

const TableBody = React.forwardRef(({ className, ...props }, ref) => (
  <tbody
    ref={ref}
    className={cn("[&_tr:last-child]:border-0", className)}
<<<<<<< HEAD
    {...props}
  />
=======
    {...props} />
>>>>>>> b9dee287 (auto-commit for f45bf728-febb-4567-ac8e-02aafd409816)
))
TableBody.displayName = "TableBody"

const TableFooter = React.forwardRef(({ className, ...props }, ref) => (
  <tfoot
    ref={ref}
<<<<<<< HEAD
    className={cn(
      "border-t bg-muted/50 font-medium [&>tr]:last:border-b-0",
      className
    )}
    {...props}
  />
=======
    className={cn("border-t bg-muted/50 font-medium [&>tr]:last:border-b-0", className)}
    {...props} />
>>>>>>> b9dee287 (auto-commit for f45bf728-febb-4567-ac8e-02aafd409816)
))
TableFooter.displayName = "TableFooter"

const TableRow = React.forwardRef(({ className, ...props }, ref) => (
  <tr
    ref={ref}
    className={cn(
      "border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted",
      className
    )}
<<<<<<< HEAD
    {...props}
  />
=======
    {...props} />
>>>>>>> b9dee287 (auto-commit for f45bf728-febb-4567-ac8e-02aafd409816)
))
TableRow.displayName = "TableRow"

const TableHead = React.forwardRef(({ className, ...props }, ref) => (
  <th
    ref={ref}
    className={cn(
<<<<<<< HEAD
      "h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0",
      className
    )}
    {...props}
  />
=======
      "h-10 px-2 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]",
      className
    )}
    {...props} />
>>>>>>> b9dee287 (auto-commit for f45bf728-febb-4567-ac8e-02aafd409816)
))
TableHead.displayName = "TableHead"

const TableCell = React.forwardRef(({ className, ...props }, ref) => (
  <td
    ref={ref}
<<<<<<< HEAD
    className={cn("p-4 align-middle [&:has([role=checkbox])]:pr-0", className)}
    {...props}
  />
=======
    className={cn(
      "p-2 align-middle [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]",
      className
    )}
    {...props} />
>>>>>>> b9dee287 (auto-commit for f45bf728-febb-4567-ac8e-02aafd409816)
))
TableCell.displayName = "TableCell"

const TableCaption = React.forwardRef(({ className, ...props }, ref) => (
  <caption
    ref={ref}
    className={cn("mt-4 text-sm text-muted-foreground", className)}
<<<<<<< HEAD
    {...props}
  />
=======
    {...props} />
>>>>>>> b9dee287 (auto-commit for f45bf728-febb-4567-ac8e-02aafd409816)
))
TableCaption.displayName = "TableCaption"

export {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
<<<<<<< HEAD
}
=======
}
>>>>>>> b9dee287 (auto-commit for f45bf728-febb-4567-ac8e-02aafd409816)
