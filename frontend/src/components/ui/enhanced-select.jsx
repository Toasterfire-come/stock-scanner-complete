import * as React from "react"
import * as SelectPrimitive from "@radix-ui/react-select"
import { Check, ChevronDown, ChevronUp, Search, X } from "lucide-react"
import { FixedSizeList as List } from 'react-window'
import { cn } from "../../lib/utils"
import { ScrollArea } from "./scroll-area"
import { Input } from "./input"
import { Badge } from "./badge"

const EnhancedSelect = SelectPrimitive.Root

const EnhancedSelectGroup = SelectPrimitive.Group

const EnhancedSelectValue = SelectPrimitive.Value

const EnhancedSelectTrigger = React.forwardRef(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Trigger
    ref={ref}
    className={cn(
      "flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1 transition-all hover:border-primary/50",
      className
    )}
    {...props}
  >
    {children}
    <SelectPrimitive.Icon asChild>
      <ChevronDown className="h-4 w-4 opacity-50" />
    </SelectPrimitive.Icon>
  </SelectPrimitive.Trigger>
))
EnhancedSelectTrigger.displayName = SelectPrimitive.Trigger.displayName

const EnhancedSelectScrollUpButton = React.forwardRef(({ className, ...props }, ref) => (
  <SelectPrimitive.ScrollUpButton
    ref={ref}
    className={cn(
      "flex cursor-default items-center justify-center py-1 bg-gradient-to-b from-background to-transparent",
      className
    )}
    {...props}
  >
    <ChevronUp className="h-4 w-4 animate-bounce" />
  </SelectPrimitive.ScrollUpButton>
))
EnhancedSelectScrollUpButton.displayName = SelectPrimitive.ScrollUpButton.displayName

const EnhancedSelectScrollDownButton = React.forwardRef(({ className, ...props }, ref) => (
  <SelectPrimitive.ScrollDownButton
    ref={ref}
    className={cn(
      "flex cursor-default items-center justify-center py-1 bg-gradient-to-t from-background to-transparent",
      className
    )}
    {...props}
  >
    <ChevronDown className="h-4 w-4 animate-bounce" />
  </SelectPrimitive.ScrollDownButton>
))
EnhancedSelectScrollDownButton.displayName = SelectPrimitive.ScrollDownButton.displayName

const EnhancedSelectContent = React.forwardRef(({
  className,
  children,
  position = "popper",
  searchable = false,
  searchPlaceholder = "Search...",
  emptyMessage = "No results found",
  showCount = false,
  grouped = false,
  virtualScroll = false,
  itemHeight = 36,
  maxHeight = 384,
  ...props
}, ref) => {
  const [searchQuery, setSearchQuery] = React.useState("")
  const [filteredChildren, setFilteredChildren] = React.useState([])
  const searchInputRef = React.useRef(null)

  // Extract items from children
  React.useEffect(() => {
    if (!searchable && !showCount) {
      setFilteredChildren(React.Children.toArray(children))
      return
    }

    const items = React.Children.toArray(children)

    if (!searchQuery) {
      setFilteredChildren(items)
      return
    }

    const filtered = items.filter(child => {
      if (React.isValidElement(child)) {
        // Handle grouped items
        if (child.type === EnhancedSelectGroup) {
          const groupChildren = React.Children.toArray(child.props.children)
          const hasMatch = groupChildren.some(groupChild => {
            if (React.isValidElement(groupChild)) {
              const itemText = groupChild.props.children?.toString().toLowerCase() || ''
              const itemValue = groupChild.props.value?.toLowerCase() || ''
              return itemText.includes(searchQuery.toLowerCase()) ||
                     itemValue.includes(searchQuery.toLowerCase())
            }
            return false
          })
          return hasMatch
        }

        // Handle regular items
        const itemText = child.props.children?.toString().toLowerCase() || ''
        const itemValue = child.props.value?.toLowerCase() || ''
        return itemText.includes(searchQuery.toLowerCase()) ||
               itemValue.includes(searchQuery.toLowerCase())
      }
      return false
    })

    setFilteredChildren(filtered)
  }, [children, searchQuery, searchable, showCount])

  // Focus search input when dropdown opens
  React.useEffect(() => {
    if (searchable && searchInputRef.current) {
      setTimeout(() => searchInputRef.current?.focus(), 100)
    }
  }, [searchable])

  const itemCount = React.useMemo(() => {
    return filteredChildren.length
  }, [filteredChildren])

  return (
    <SelectPrimitive.Portal>
      <SelectPrimitive.Content
        ref={ref}
        className={cn(
          "relative z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
          position === "popper" &&
            "data-[side=bottom]:translate-y-1 data-[side=left]:-translate-x-1 data-[side=right]:translate-x-1 data-[side=top]:-translate-y-1",
          className
        )}
        position={position}
        {...props}
      >
        {/* Search Input */}
        {searchable && (
          <div className="sticky top-0 z-10 bg-popover border-b p-2">
            <div className="relative">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                ref={searchInputRef}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={searchPlaceholder}
                className="pl-8 pr-8 h-8"
                onKeyDown={(e) => {
                  // Prevent SelectPrimitive from closing on certain keys
                  if (e.key === "Escape") {
                    setSearchQuery("")
                  }
                }}
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
            {showCount && (
              <div className="text-xs text-muted-foreground mt-1 px-1">
                {itemCount} {itemCount === 1 ? 'item' : 'items'}
              </div>
            )}
          </div>
        )}

        <EnhancedSelectScrollUpButton />

        <ScrollArea className={cn("overflow-auto")} style={{ maxHeight: `${maxHeight}px` }}>
          <SelectPrimitive.Viewport
            className={cn(
              "p-1",
              position === "popper" &&
                "h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)]"
            )}
          >
            {filteredChildren.length > 0 ? (
              filteredChildren
            ) : (
              <div className="py-6 text-center text-sm text-muted-foreground">
                {emptyMessage}
              </div>
            )}
          </SelectPrimitive.Viewport>
        </ScrollArea>

        <EnhancedSelectScrollDownButton />
      </SelectPrimitive.Content>
    </SelectPrimitive.Portal>
  )
})
EnhancedSelectContent.displayName = SelectPrimitive.Content.displayName

const EnhancedSelectLabel = React.forwardRef(({ className, ...props }, ref) => (
  <SelectPrimitive.Label
    ref={ref}
    className={cn("py-1.5 pl-8 pr-2 text-sm font-semibold text-muted-foreground", className)}
    {...props}
  />
))
EnhancedSelectLabel.displayName = SelectPrimitive.Label.displayName

const EnhancedSelectItem = React.forwardRef(({ className, children, icon, badge, ...props }, ref) => (
  <SelectPrimitive.Item
    ref={ref}
    className={cn(
      "relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50 transition-colors hover:bg-accent/50",
      className
    )}
    {...props}
  >
    <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
      <SelectPrimitive.ItemIndicator>
        <Check className="h-4 w-4" />
      </SelectPrimitive.ItemIndicator>
    </span>

    {icon && <span className="mr-2">{icon}</span>}

    <SelectPrimitive.ItemText className="flex-1">{children}</SelectPrimitive.ItemText>

    {badge && (
      <Badge variant="secondary" className="ml-2 text-xs">
        {badge}
      </Badge>
    )}
  </SelectPrimitive.Item>
))
EnhancedSelectItem.displayName = SelectPrimitive.Item.displayName

const EnhancedSelectSeparator = React.forwardRef(({ className, ...props }, ref) => (
  <SelectPrimitive.Separator
    ref={ref}
    className={cn("-mx-1 my-1 h-px bg-muted", className)}
    {...props}
  />
))
EnhancedSelectSeparator.displayName = SelectPrimitive.Separator.displayName

export {
  EnhancedSelect,
  EnhancedSelectGroup,
  EnhancedSelectValue,
  EnhancedSelectTrigger,
  EnhancedSelectContent,
  EnhancedSelectLabel,
  EnhancedSelectItem,
  EnhancedSelectSeparator,
  EnhancedSelectScrollUpButton,
  EnhancedSelectScrollDownButton,
}
