import React, { useState, useMemo } from 'react';
import { cn } from '../../lib/utils';
import { 
  ChevronDown, 
  ChevronUp, 
  MoreHorizontal,
  Download,
  Filter,
  Search,
  RefreshCw,
  Eye,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react';

const DataTable = ({ 
  data = [], 
  columns = [],
  sortable = true,
  filterable = false,
  searchable = false,
  pagination = false,
  pageSize = 10,
  loading = false,
  emptyMessage = "No data available",
  className,
  onRowClick,
  ...props 
}) => {
  const [sortField, setSortField] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});

  const handleSort = (field) => {
    if (!sortable) return;
    
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const filteredAndSortedData = useMemo(() => {
    let processedData = [...data];

    // Apply search
    if (searchable && searchTerm) {
      processedData = processedData.filter(row =>
        Object.values(row).some(value =>
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Apply filters
    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        processedData = processedData.filter(row =>
          String(row[key]).toLowerCase().includes(String(value).toLowerCase())
        );
      }
    });

    // Apply sorting
    if (sortField) {
      processedData.sort((a, b) => {
        let aValue = a[sortField];
        let bValue = b[sortField];

        // Handle numbers
        if (typeof aValue === 'number' && typeof bValue === 'number') {
          return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
        }

        // Handle strings
        aValue = String(aValue).toLowerCase();
        bValue = String(bValue).toLowerCase();

        if (sortDirection === 'asc') {
          return aValue.localeCompare(bValue);
        } else {
          return bValue.localeCompare(aValue);
        }
      });
    }

    return processedData;
  }, [data, searchTerm, filters, sortField, sortDirection, searchable]);

  const paginatedData = useMemo(() => {
    if (!pagination) return filteredAndSortedData;
    
    const startIndex = (currentPage - 1) * pageSize;
    return filteredAndSortedData.slice(startIndex, startIndex + pageSize);
  }, [filteredAndSortedData, currentPage, pageSize, pagination]);

  const totalPages = Math.ceil(filteredAndSortedData.length / pageSize);

  const renderCell = (row, column) => {
    if (column.render) {
      return column.render(row[column.key], row);
    }

    const value = row[column.key];
    
    if (column.type === 'currency') {
      return `$${Number(value).toFixed(2)}`;
    }
    
    if (column.type === 'percentage') {
      const numValue = Number(value);
      const isPositive = numValue > 0;
      const isNegative = numValue < 0;
      
      return (
        <span className={cn(
          'flex items-center gap-1 font-semibold',
          isPositive && 'text-green-600',
          isNegative && 'text-red-600'
        )}>
          {isPositive && <TrendingUp className="w-4 h-4" />}
          {isNegative && <TrendingDown className="w-4 h-4" />}
          {!isPositive && !isNegative && <Minus className="w-4 h-4" />}
          {numValue > 0 ? '+' : ''}{numValue.toFixed(2)}%
        </span>
      );
    }
    
    if (column.type === 'number') {
      return Number(value).toLocaleString();
    }

    return value;
  };

  if (loading) {
    return (
      <div className={cn('stock-table-enhanced-container', className)}>
        <div className="animate-pulse space-y-4">
          <div className="h-12 bg-gray-200 rounded" />
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-16 bg-gray-100 rounded" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={cn('stock-table-enhanced-container', className)} {...props}>
      {/* Table Controls */}
      {(searchable || filterable) && (
        <div className="flex items-center justify-between mb-6 gap-4">
          {searchable && (
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          )}
          
          <div className="flex items-center gap-2">
            {filterable && (
              <button className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
                <Filter className="w-4 h-4" />
                Filter
              </button>
            )}
            <button className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto rounded-2xl border border-gray-200">
        <table className="stock-table-enhanced">
          <thead>
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={cn(
                    sortable && column.sortable !== false && 'cursor-pointer hover:bg-gray-100 transition-colors group'
                  )}
                  onClick={() => column.sortable !== false && handleSort(column.key)}
                >
                  <div className="flex items-center justify-between">
                    <span>{column.title}</span>
                    {sortable && column.sortable !== false && (
                      <div className="flex flex-col ml-2">
                        <ChevronUp 
                          className={cn(
                            'w-3 h-3 -mb-1',
                            sortField === column.key && sortDirection === 'asc' 
                              ? 'text-blue-600' 
                              : 'text-gray-300 group-hover:text-gray-400'
                          )}
                        />
                        <ChevronDown 
                          className={cn(
                            'w-3 h-3',
                            sortField === column.key && sortDirection === 'desc' 
                              ? 'text-blue-600' 
                              : 'text-gray-300 group-hover:text-gray-400'
                          )}
                        />
                      </div>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="text-center py-12 text-gray-500">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              paginatedData.map((row, index) => (
                <tr
                  key={row.id || index}
                  className={cn(
                    'transition-colors',
                    onRowClick && 'cursor-pointer hover:bg-blue-50'
                  )}
                  onClick={() => onRowClick?.(row)}
                >
                  {columns.map((column) => (
                    <td key={column.key} className={cn(column.className)}>
                      {renderCell(row, column)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && totalPages > 1 && (
        <div className="flex items-center justify-between mt-6">
          <div className="text-sm text-gray-700">
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, filteredAndSortedData.length)} of {filteredAndSortedData.length} results
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter(page => 
                page === 1 || 
                page === totalPages || 
                Math.abs(page - currentPage) <= 2
              )
              .map((page, index, array) => (
                <React.Fragment key={page}>
                  {index > 0 && array[index - 1] < page - 1 && (
                    <span className="px-2 text-gray-400">...</span>
                  )}
                  <button
                    onClick={() => setCurrentPage(page)}
                    className={cn(
                      'px-3 py-2 text-sm font-medium border rounded-lg',
                      currentPage === page
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'text-gray-700 bg-white border-gray-300 hover:bg-gray-50'
                    )}
                  >
                    {page}
                  </button>
                </React.Fragment>
              ))}
            
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const MetricCard = ({ 
  title, 
  value, 
  change, 
  changeType = 'percentage',
  trend,
  icon: Icon,
  color = 'blue',
  loading = false,
  className,
  ...props 
}) => {
  const colors = {
    blue: 'text-blue-600 bg-blue-100',
    green: 'text-green-600 bg-green-100',
    red: 'text-red-600 bg-red-100',
    yellow: 'text-yellow-600 bg-yellow-100',
    purple: 'text-purple-600 bg-purple-100',
    gray: 'text-gray-600 bg-gray-100'
  };

  if (loading) {
    return (
      <div className={cn('card-enhanced p-6', className)} {...props}>
        <div className="animate-pulse space-y-4">
          <div className="flex items-center justify-between">
            <div className="h-4 bg-gray-200 rounded w-1/2" />
            <div className="h-8 w-8 bg-gray-200 rounded-lg" />
          </div>
          <div className="h-8 bg-gray-200 rounded w-3/4" />
          <div className="h-4 bg-gray-200 rounded w-1/3" />
        </div>
      </div>
    );
  }

  const isPositive = change > 0;
  const isNegative = change < 0;

  return (
    <div className={cn('card-enhanced p-6 hover-lift', className)} {...props}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        {Icon && (
          <div className={cn('p-2 rounded-lg', colors[color])}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      
      <div className="mb-2">
        <span className="text-3xl font-bold text-gray-900">{value}</span>
      </div>
      
      {change !== undefined && (
        <div className={cn(
          'flex items-center text-sm font-medium',
          isPositive && 'text-green-600',
          isNegative && 'text-red-600',
          !isPositive && !isNegative && 'text-gray-500'
        )}>
          {isPositive && <TrendingUp className="w-4 h-4 mr-1" />}
          {isNegative && <TrendingDown className="w-4 h-4 mr-1" />}
          {!isPositive && !isNegative && <Minus className="w-4 h-4 mr-1" />}
          <span>
            {change > 0 && '+'}{change}
            {changeType === 'percentage' && '%'}
          </span>
          <span className="text-gray-500 ml-1">vs last period</span>
        </div>
      )}
    </div>
  );
};

const StatsList = ({ 
  stats = [], 
  orientation = 'horizontal',
  variant = 'default',
  loading = false,
  className,
  ...props 
}) => {
  if (loading) {
    return (
      <div className={cn(
        'grid gap-6',
        orientation === 'horizontal' ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4' : 'grid-cols-1',
        className
      )} {...props}>
        {Array.from({ length: 4 }).map((_, i) => (
          <MetricCard key={i} loading={true} />
        ))}
      </div>
    );
  }

  return (
    <div className={cn(
      'grid gap-6',
      orientation === 'horizontal' ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4' : 'grid-cols-1',
      className
    )} {...props}>
      {stats.map((stat, index) => (
        <MetricCard
          key={index}
          title={stat.title}
          value={stat.value}
          change={stat.change}
          changeType={stat.changeType}
          trend={stat.trend}
          icon={stat.icon}
          color={stat.color}
        />
      ))}
    </div>
  );
};

const DataGrid = ({ 
  data = [], 
  columns = 4,
  gap = 6,
  loading = false,
  emptyMessage = "No items to display",
  className,
  renderItem,
  ...props 
}) => {
  if (loading) {
    return (
      <div className={cn(
        'grid gap-6',
        `grid-cols-1 sm:grid-cols-2 lg:grid-cols-${columns}`,
        className
      )} {...props}>
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="card-enhanced p-6 animate-pulse">
            <div className="space-y-4">
              <div className="h-4 bg-gray-200 rounded w-3/4" />
              <div className="h-8 bg-gray-200 rounded" />
              <div className="h-4 bg-gray-200 rounded w-1/2" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <Eye className="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={cn(
      'grid',
      `gap-${gap}`,
      `grid-cols-1 sm:grid-cols-2 lg:grid-cols-${columns}`,
      className
    )} {...props}>
      {data.map((item, index) => (
        <div key={item.id || index}>
          {renderItem ? renderItem(item, index) : (
            <div className="card-enhanced p-6">
              <pre>{JSON.stringify(item, null, 2)}</pre>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export {
  DataTable,
  MetricCard,
  StatsList,
  DataGrid
};