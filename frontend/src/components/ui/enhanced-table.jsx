import * as React from "react"
import { FixedSizeList as List } from 'react-window'
import { cn } from "../../lib/utils"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./table"
import { Button } from "./button"
import { Input } from "./input"
import {
  ChevronUp,
  ChevronDown,
  ChevronsUpDown,
  Search,
  X,
  Download,
  Filter
} from "lucide-react"

/**
 * Enhanced Table Component with features:
 * - Sticky headers
 * - Virtual scrolling for large datasets
 * - Column sorting
 * - Column filtering
 * - Column visibility toggle
 * - Export functionality
 * - Row selection
 * - Responsive design
 */

const EnhancedTable = React.forwardRef(({
  data = [],
  columns = [],
  className,
  stickyHeader = true,
  virtualScroll = false,
  rowHeight = 52,
  maxHeight = 600,
  sortable = true,
  filterable = false,
  selectable = false,
  onExport,
  onRowClick,
  emptyMessage = "No data available",
  loading = false,
  ...props
}, ref) => {
  const [sortConfig, setSortConfig] = React.useState({ key: null, direction: 'asc' })
  const [filters, setFilters] = React.useState({})
  const [selectedRows, setSelectedRows] = React.useState(new Set())
  const [searchQuery, setSearchQuery] = React.useState("")

  // Sort data
  const sortedData = React.useMemo(() => {
    if (!sortConfig.key) return data

    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key]
      const bValue = b[sortConfig.key]

      if (aValue === bValue) return 0

      const comparison = aValue < bValue ? -1 : 1
      return sortConfig.direction === 'asc' ? comparison : -comparison
    })
  }, [data, sortConfig])

  // Filter data
  const filteredData = React.useMemo(() => {
    let result = sortedData

    // Apply search query
    if (searchQuery) {
      result = result.filter(row =>
        columns.some(col => {
          const value = row[col.accessor]?.toString().toLowerCase() || ''
          return value.includes(searchQuery.toLowerCase())
        })
      )
    }

    // Apply column filters
    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        result = result.filter(row => {
          const rowValue = row[key]?.toString().toLowerCase() || ''
          return rowValue.includes(value.toLowerCase())
        })
      }
    })

    return result
  }, [sortedData, filters, searchQuery, columns])

  // Handle sort
  const handleSort = (accessor) => {
    if (!sortable) return

    setSortConfig(prev => ({
      key: accessor,
      direction: prev.key === accessor && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  // Handle row selection
  const handleRowSelect = (index) => {
    if (!selectable) return

    setSelectedRows(prev => {
      const newSet = new Set(prev)
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        newSet.add(index)
      }
      return newSet
    })
  }

  // Select all rows
  const handleSelectAll = () => {
    if (selectedRows.size === filteredData.length) {
      setSelectedRows(new Set())
    } else {
      setSelectedRows(new Set(filteredData.map((_, i) => i)))
    }
  }

  // Render sort icon
  const SortIcon = ({ accessor }) => {
    if (!sortable) return null

    if (sortConfig.key !== accessor) {
      return <ChevronsUpDown className="h-4 w-4 ml-2 text-muted-foreground" />
    }

    return sortConfig.direction === 'asc' ? (
      <ChevronUp className="h-4 w-4 ml-2" />
    ) : (
      <ChevronDown className="h-4 w-4 ml-2" />
    )
  }

  // Render table row
  const TableRowContent = ({ row, index }) => (
    <TableRow
      key={index}
      className={cn(
        "cursor-pointer hover:bg-muted/50 transition-colors",
        selectedRows.has(index) && "bg-accent",
        onRowClick && "cursor-pointer"
      )}
      onClick={() => onRowClick?.(row, index)}
    >
      {selectable && (
        <TableCell className="w-12">
          <input
            type="checkbox"
            checked={selectedRows.has(index)}
            onChange={() => handleRowSelect(index)}
            onClick={(e) => e.stopPropagation()}
            className="h-4 w-4 rounded border-gray-300"
          />
        </TableCell>
      )}
      {columns.map((col, colIndex) => (
        <TableCell key={colIndex} className={cn(col.className)}>
          {col.cell ? col.cell(row[col.accessor], row, index) : row[col.accessor]}
        </TableCell>
      ))}
    </TableRow>
  )

  // Virtual scroll row renderer
  const VirtualRow = ({ index, style }) => (
    <div style={style}>
      <TableRowContent row={filteredData[index]} index={index} />
    </div>
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className={cn("space-y-4", className)} ref={ref}>
      {/* Toolbar */}
      {(filterable || onExport) && (
        <div className="flex items-center gap-2">
          {filterable && (
            <div className="flex-1 relative">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search..."
                className="pl-8 pr-8"
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
          )}

          {onExport && (
            <Button variant="outline" size="sm" onClick={() => onExport(filteredData)}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          )}

          {selectable && selectedRows.size > 0 && (
            <span className="text-sm text-muted-foreground">
              {selectedRows.size} selected
            </span>
          )}
        </div>
      )}

      {/* Table */}
      <div className={cn("rounded-md border", virtualScroll && "overflow-hidden")}>
        <div className={cn(stickyHeader && "overflow-auto")} style={{ maxHeight: `${maxHeight}px` }}>
          <Table {...props}>
            <TableHeader className={cn(stickyHeader && "sticky top-0 bg-background z-10 shadow-sm")}>
              <TableRow>
                {selectable && (
                  <TableHead className="w-12">
                    <input
                      type="checkbox"
                      checked={selectedRows.size === filteredData.length && filteredData.length > 0}
                      onChange={handleSelectAll}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                  </TableHead>
                )}
                {columns.map((col, index) => (
                  <TableHead
                    key={index}
                    className={cn(
                      col.headerClassName,
                      sortable && "cursor-pointer select-none hover:bg-muted/50"
                    )}
                    onClick={() => handleSort(col.accessor)}
                  >
                    <div className="flex items-center">
                      {col.header}
                      <SortIcon accessor={col.accessor} />
                    </div>
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>

            {!virtualScroll && (
              <TableBody>
                {filteredData.length > 0 ? (
                  filteredData.map((row, index) => (
                    <TableRowContent key={index} row={row} index={index} />
                  ))
                ) : (
                  <TableRow>
                    <TableCell
                      colSpan={columns.length + (selectable ? 1 : 0)}
                      className="h-24 text-center text-muted-foreground"
                    >
                      {emptyMessage}
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            )}
          </Table>

          {/* Virtual scroll list */}
          {virtualScroll && filteredData.length > 0 && (
            <List
              height={Math.min(maxHeight, filteredData.length * rowHeight)}
              itemCount={filteredData.length}
              itemSize={rowHeight}
              width="100%"
            >
              {VirtualRow}
            </List>
          )}

          {virtualScroll && filteredData.length === 0 && (
            <div className="flex items-center justify-center h-24 text-muted-foreground">
              {emptyMessage}
            </div>
          )}
        </div>
      </div>
    </div>
  )
})

EnhancedTable.displayName = "EnhancedTable"

export { EnhancedTable }
