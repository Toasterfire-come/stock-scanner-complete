import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '../../lib/utils';

const StockCard = React.forwardRef(({
  className,
  symbol,
  price,
  change,
  changePercent,
  volume,
  logo,
  companyName,
  onClick,
  ...props
}, ref) => {
  const isPositive = change > 0;
  const isNegative = change < 0;
  const trend = isPositive ? 'up' : isNegative ? 'down' : 'neutral';

  return (
    <div
      ref={ref}
      className={cn(
        'stock-card-enhanced',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
      {...props}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          {logo ? (
            <img
              src={logo}
              alt={`${symbol} logo`}
              className="stock-logo"
              loading="lazy"
            />
          ) : (
            <div className="stock-logo">
              {symbol.charAt(0)}
            </div>
          )}
          <div>
            <h3 className="font-semibold text-lg text-gray-900">
              {symbol}
            </h3>
            {companyName && (
              <p className="text-sm text-gray-500 line-clamp-1">
                {companyName}
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="stock-price">
        ${price.toFixed(2)}
      </div>

      <div className={cn('stock-change', trend)}>
        {trend === 'up' && <TrendingUp className="w-4 h-4" />}
        {trend === 'down' && <TrendingDown className="w-4 h-4" />}
        {trend === 'neutral' && <Minus className="w-4 h-4" />}
        <span>
          {change > 0 ? '+' : ''}{change.toFixed(2)} ({changePercent > 0 ? '+' : ''}{changePercent.toFixed(2)}%)
        </span>
      </div>

      {volume && (
        <div className="stock-metrics">
          <div className="stock-metric">
            <div className="stock-metric-label">Volume</div>
            <div className="stock-metric-value">
              {volume.toLocaleString()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

const StockTable = React.forwardRef(({
  className,
  stocks,
  columns = ['symbol', 'price', 'change', 'volume'],
  onRowClick,
  sortable = true,
  ...props
}, ref) => {
  const [sortField, setSortField] = React.useState(null);
  const [sortDirection, setSortDirection] = React.useState('asc');

  const handleSort = (field) => {
    if (!sortable) return;
    
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const sortedStocks = React.useMemo(() => {
    if (!sortField) return stocks;

    return [...stocks].sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      if (sortDirection === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
  }, [stocks, sortField, sortDirection]);

  const renderCell = (stock, column) => {
    switch (column) {
      case 'symbol':
        return (
          <div className="flex items-center gap-3">
            <div className="stock-logo w-8 h-8 text-sm">
              {stock.symbol.charAt(0)}
            </div>
            <div>
              <div className="font-semibold">{stock.symbol}</div>
              {stock.companyName && (
                <div className="text-sm text-gray-500 line-clamp-1">
                  {stock.companyName}
                </div>
              )}
            </div>
          </div>
        );
      case 'price':
        return (
          <div className="font-semibold">
            ${stock.price.toFixed(2)}
          </div>
        );
      case 'change':
        const isPositive = stock.change > 0;
        const isNegative = stock.change < 0;
        return (
          <div className={cn(
            'flex items-center gap-1 font-semibold',
            isPositive && 'price-change-positive',
            isNegative && 'price-change-negative'
          )}>
            {isPositive && <TrendingUp className="w-4 h-4" />}
            {isNegative && <TrendingDown className="w-4 h-4" />}
            {!isPositive && !isNegative && <Minus className="w-4 h-4" />}
            <span>
              {stock.change > 0 ? '+' : ''}{stock.change.toFixed(2)} ({stock.changePercent > 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%)
            </span>
          </div>
        );
      case 'volume':
        return (
          <div>
            {stock.volume?.toLocaleString() || 'N/A'}
          </div>
        );
      default:
        return stock[column] || 'N/A';
    }
  };

  const getColumnLabel = (column) => {
    const labels = {
      symbol: 'Symbol',
      price: 'Price',
      change: 'Change',
      volume: 'Volume',
      marketCap: 'Market Cap',
      pe: 'P/E Ratio'
    };
    return labels[column] || column.charAt(0).toUpperCase() + column.slice(1);
  };

  return (
    <div
      ref={ref}
      className={cn('overflow-x-auto', className)}
      {...props}
    >
      <table className="stock-table-enhanced">
        <thead>
          <tr>
            {columns.map((column) => (
              <th
                key={column}
                className={cn(
                  sortable && 'cursor-pointer hover:bg-gray-50 transition-colors',
                  'group'
                )}
                onClick={() => handleSort(column)}
              >
                <div className="flex items-center justify-between">
                  <span>{getColumnLabel(column)}</span>
                  {sortable && (
                    <div className="flex flex-col ml-2">
                      <TrendingUp 
                        className={cn(
                          'w-3 h-3 -mb-1',
                          sortField === column && sortDirection === 'asc' 
                            ? 'text-blue-600' 
                            : 'text-gray-300 group-hover:text-gray-400'
                        )}
                      />
                      <TrendingDown 
                        className={cn(
                          'w-3 h-3',
                          sortField === column && sortDirection === 'desc' 
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
          {sortedStocks.map((stock, index) => (
            <tr
              key={stock.symbol || index}
              className={cn(
                onRowClick && 'cursor-pointer hover:bg-gray-50',
                'transition-colors'
              )}
              onClick={() => onRowClick?.(stock)}
            >
              {columns.map((column) => (
                <td key={column}>
                  {renderCell(stock, column)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
});

const StockBadge = React.forwardRef(({
  className,
  trend,
  value,
  label,
  size = 'md',
  ...props
}, ref) => {
  const sizes = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2'
  };

  const variants = {
    up: 'badge-success',
    down: 'badge-error',
    neutral: 'badge-gray'
  };

  return (
    <span
      ref={ref}
      className={cn(
        'badge-enhanced',
        variants[trend] || 'badge-gray',
        sizes[size],
        className
      )}
      {...props}
    >
      {trend === 'up' && <TrendingUp className="w-3 h-3" />}
      {trend === 'down' && <TrendingDown className="w-3 h-3" />}
      {trend === 'neutral' && <Minus className="w-3 h-3" />}
      {label && <span className="mr-1">{label}:</span>}
      <span>{value}</span>
    </span>
  );
});

const StockProgress = React.forwardRef(({
  className,
  value,
  max = 100,
  min = 0,
  label,
  showValue = true,
  color = 'primary',
  ...props
}, ref) => {
  const percentage = ((value - min) / (max - min)) * 100;
  
  const colors = {
    primary: 'bg-blue-600',
    success: 'bg-green-600',
    error: 'bg-red-600',
    warning: 'bg-yellow-600'
  };

  return (
    <div
      ref={ref}
      className={cn('space-y-2', className)}
      {...props}
    >
      {(label || showValue) && (
        <div className="flex justify-between items-center text-sm">
          {label && <span className="text-gray-600">{label}</span>}
          {showValue && (
            <span className="font-semibold text-gray-900">
              {value.toFixed(1)}{max === 100 ? '%' : ''}
            </span>
          )}
        </div>
      )}
      <div className="progress-enhanced">
        <div
          className={cn('progress-fill', colors[color])}
          style={{ width: `${Math.min(Math.max(percentage, 0), 100)}%` }}
        />
      </div>
    </div>
  );
});

StockCard.displayName = 'StockCard';
StockTable.displayName = 'StockTable';
StockBadge.displayName = 'StockBadge';
StockProgress.displayName = 'StockProgress';

export {
  StockCard,
  StockTable,
  StockBadge,
  StockProgress
};