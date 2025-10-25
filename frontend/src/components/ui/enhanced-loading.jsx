import React from 'react';
import { cn } from '../../lib/utils';

const LoadingSkeleton = ({ 
  className, 
  variant = 'rectangular',
  width,
  height,
  ...props 
}) => {
  const variants = {
    rectangular: 'rounded-lg',
    circular: 'rounded-full',
    text: 'rounded h-4',
    card: 'rounded-2xl h-48'
  };

  const style = {
    width: width,
    height: height
  };

  return (
    <div
      className={cn(
        'loading-skeleton animate-pulse',
        variants[variant],
        className
      )}
      style={style}
      {...props}
    />
  );
};

const LoadingSpinner = ({ 
  className, 
  size = 'md',
  color = 'primary',
  ...props 
}) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  const colors = {
    primary: 'border-primary',
    white: 'border-white',
    gray: 'border-gray-300'
  };

  return (
    <div
      className={cn(
        'animate-spin rounded-full border-2 border-t-transparent',
        sizes[size],
        colors[color],
        className
      )}
      {...props}
    />
  );
};

const LoadingDots = ({ 
  className, 
  size = 'md',
  color = 'primary',
  ...props 
}) => {
  const sizes = {
    sm: 'w-1 h-1',
    md: 'w-2 h-2',
    lg: 'w-3 h-3'
  };

  const colors = {
    primary: 'bg-primary',
    white: 'bg-white',
    gray: 'bg-gray-400'
  };

  return (
    <div className={cn('flex items-center space-x-1', className)} {...props}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={cn(
            'rounded-full animate-pulse',
            sizes[size],
            colors[color]
          )}
          style={{
            animationDelay: `${i * 0.15}s`,
            animationDuration: '0.8s'
          }}
        />
      ))}
    </div>
  );
};

const LoadingCard = ({ className, ...props }) => {
  return (
    <div className={cn('card-enhanced p-6 space-y-4', className)} {...props}>
      <div className="flex items-center space-x-4">
        <LoadingSkeleton variant="circular" className="w-12 h-12" />
        <div className="space-y-2 flex-1">
          <LoadingSkeleton variant="text" className="w-1/3" />
          <LoadingSkeleton variant="text" className="w-1/2" />
        </div>
      </div>
      <LoadingSkeleton variant="rectangular" className="h-32 w-full" />
      <div className="space-y-2">
        <LoadingSkeleton variant="text" className="w-full" />
        <LoadingSkeleton variant="text" className="w-4/5" />
        <LoadingSkeleton variant="text" className="w-3/5" />
      </div>
    </div>
  );
};

const LoadingTable = ({ 
  className, 
  rows = 5, 
  columns = 4,
  ...props 
}) => {
  return (
    <div className={cn('space-y-4', className)} {...props}>
      {/* Table Header */}
      <div className="flex space-x-4">
        {Array.from({ length: columns }).map((_, i) => (
          <LoadingSkeleton
            key={i}
            variant="text"
            className="flex-1 h-6"
          />
        ))}
      </div>
      
      {/* Table Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex space-x-4">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <LoadingSkeleton
              key={colIndex}
              variant="text"
              className="flex-1 h-4"
            />
          ))}
        </div>
      ))}
    </div>
  );
};

const LoadingChart = ({ className, ...props }) => {
  return (
    <div className={cn('card-enhanced p-6', className)} {...props}>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <LoadingSkeleton variant="text" className="w-1/4 h-6" />
          <LoadingSkeleton variant="text" className="w-1/6 h-4" />
        </div>
        <LoadingSkeleton variant="rectangular" className="h-64 w-full" />
        <div className="flex justify-between">
          {Array.from({ length: 5 }).map((_, i) => (
            <LoadingSkeleton
              key={i}
              variant="text"
              className="w-12 h-4"
            />
          ))}
        </div>
      </div>
    </div>
  );
};

const LoadingOverlay = ({ 
  className, 
  show = true,
  message = 'Loading...',
  spinner = true,
  backdrop = true,
  ...props 
}) => {
  if (!show) return null;

  return (
    <div
      className={cn(
        'fixed inset-0 z-50 flex items-center justify-center',
        backdrop && 'bg-black/20 backdrop-blur-sm',
        className
      )}
      {...props}
    >
      <div className="glass rounded-2xl p-8 flex flex-col items-center space-y-4 min-w-[200px]">
        {spinner && <LoadingSpinner size="lg" />}
        <p className="text-center font-medium">{message}</p>
      </div>
    </div>
  );
};

const LoadingButton = ({ 
  loading = false, 
  children, 
  className,
  disabled,
  ...props 
}) => {
  return (
    <button
      className={cn(
        'btn-enhanced btn-primary-enhanced',
        'focus-enhanced',
        (loading || disabled) && 'opacity-60 cursor-not-allowed',
        className
      )}
      disabled={loading || disabled}
      {...props}
    >
      {loading && <LoadingSpinner size="sm" color="white" />}
      <span className={loading ? 'opacity-70' : ''}>{children}</span>
    </button>
  );
};

export {
  LoadingSkeleton,
  LoadingSpinner,
  LoadingDots,
  LoadingCard,
  LoadingTable,
  LoadingChart,
  LoadingOverlay,
  LoadingButton
};