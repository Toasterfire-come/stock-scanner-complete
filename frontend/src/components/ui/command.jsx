import * as React from "react"
import { Search } from "lucide-react"

import { cn } from "../../lib/utils"
import { Dialog, DialogContent } from "./dialog"
import { buttonVariants } from "./button"

const Command = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("flex h-10 items-center rounded-md border px-3 py-2 text-sm", className)} {...props} />
))
Command.displayName = "Command"

const CommandInput = React.forwardRef(({ className, ...props }, ref) => (
  <div className={cn("flex items-center border-b px-3", className)}>
    <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
    <input ref={ref} className="flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50" {...props} />
  </div>
))
CommandInput.displayName = "CommandInput"

const CommandList = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("max-h-[300px] overflow-y-auto overflow-x-hidden", className)} {...props} />
))
CommandList.displayName = "CommandList"

const CommandEmpty = React.forwardRef((props, ref) => (
  <div ref={ref} className="py-6 text-center text-sm" {...props} />
))
CommandEmpty.displayName = "CommandEmpty"

const CommandGroup = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("overflow-hidden py-3 px-2 text-foreground", className)} {...props} />
))
CommandGroup.displayName = "CommandGroup"

const CommandSeparator = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("-mx-1 h-px bg-border", className)} {...props} />
))
CommandSeparator.displayName = "CommandSeparator"

const CommandItem = React.forwardRef(({ className, ...props }, ref) => (
  <button ref={ref} className={cn("flex w-full cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground", className)} {...props} />
))
CommandItem.displayName = "CommandItem"

export { Command, CommandInput, CommandList, CommandEmpty, CommandGroup, CommandSeparator, CommandItem }
