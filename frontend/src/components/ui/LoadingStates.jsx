/**
 * Loading States Components
 * ==========================
 * QA Fix: Issue #10 - Missing Loading States
 *
 * Provides consistent loading indicators across the application
 */

import React from 'react';
import { Loader2 } from 'lucide-react';

/**
 * Spinner - Simple loading spinner
 */
export const Spinner = ({ size = 'md', className = '' }) => {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  };

  return (
    <Loader2
      className={`animate-spin ${sizes[size]} ${className}`}
      aria-label="Loading"
      role="status"
    />
  );
};

/**
 * LoadingButton - Button with loading state
 */
export const LoadingButton = ({
  children,
  isLoading,
  disabled,
  loadingText = 'Loading...',
  className = '',
  ...props
}) => {
  return (
    <button
      disabled={isLoading || disabled}
      className={`relative ${className} ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
      aria-busy={isLoading}
      {...props}
    >
      {isLoading && (
        <span className="absolute inset-0 flex items-center justify-center">
          <Spinner size="sm" className="text-current" />
        </span>
      )}
      <span className={isLoading ? 'invisible' : ''}>
        {isLoading ? loadingText : children}
      </span>
    </button>
  );
};

/**
 * SkeletonLoader - Skeleton loading placeholder
 */
export const SkeletonLoader = ({
  variant = 'text',
  count = 1,
  className = ''
}) => {
  const variants = {
    text: 'h-4 w-full rounded',
    title: 'h-8 w-3/4 rounded',
    card: 'h-48 w-full rounded-lg',
    circle: 'h-12 w-12 rounded-full',
    button: 'h-10 w-32 rounded'
  };

  return (
    <>
      {[...Array(count)].map((_, i) => (
        <div
          key={i}
          className={`animate-pulse bg-gray-200 ${variants[variant]} ${className}`}
          aria-label="Loading content"
          role="status"
        />
      ))}
    </>
  );
};

/**
 * LoadingOverlay - Full screen loading overlay
 */
export const LoadingOverlay = ({ message = 'Loading...', show = true }) => {
  if (!show) return null;

  return (
    <div
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      role="dialog"
      aria-modal="true"
      aria-label="Loading"
    >
      <div className="bg-white rounded-lg p-8 flex flex-col items-center space-y-4">
        <Spinner size="lg" className="text-blue-600" />
        <p className="text-gray-700 font-medium">{message}</p>
      </div>
    </div>
  );
};

/**
 * CardSkeleton - Skeleton for pricing/feature cards
 */
export const CardSkeleton = ({ count = 3 }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {[...Array(count)].map((_, i) => (
        <div key={i} className="border rounded-lg p-6 space-y-4">
          <SkeletonLoader variant="title" />
          <SkeletonLoader variant="text" count={3} />
          <SkeletonLoader variant="button" />
        </div>
      ))}
    </div>
  );
};

/**
 * TableSkeleton - Skeleton for data tables
 */
export const TableSkeleton = ({ rows = 5, cols = 4 }) => {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex gap-4">
        {[...Array(cols)].map((_, i) => (
          <SkeletonLoader key={i} variant="text" className="h-6 flex-1" />
        ))}
      </div>
      {/* Rows */}
      {[...Array(rows)].map((_, rowIndex) => (
        <div key={rowIndex} className="flex gap-4">
          {[...Array(cols)].map((_, colIndex) => (
            <SkeletonLoader key={colIndex} variant="text" className="flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
};

/**
 * LoadingCard - Card with loading message
 */
export const LoadingCard = ({
  title = 'Loading',
  message = 'Please wait...',
  className = ''
}) => {
  return (
    <div className={`bg-white rounded-lg shadow p-8 flex flex-col items-center space-y-4 ${className}`}>
      <Spinner size="lg" className="text-blue-600" />
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-gray-600 mt-1">{message}</p>
      </div>
    </div>
  );
};

/**
 * InlineLoader - Small inline loading indicator
 */
export const InlineLoader = ({ text = 'Loading' }) => {
  return (
    <div className="inline-flex items-center space-x-2 text-sm text-gray-600">
      <Spinner size="sm" />
      <span>{text}</span>
    </div>
  );
};

/**
 * ProgressBar - Progress indicator
 */
export const ProgressBar = ({
  progress = 0,
  label,
  showPercentage = true,
  className = ''
}) => {
  return (
    <div className={`w-full ${className}`}>
      {label && (
        <div className="flex justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          {showPercentage && (
            <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
          )}
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
          role="progressbar"
          aria-valuenow={progress}
          aria-valuemin="0"
          aria-valuemax="100"
        />
      </div>
    </div>
  );
};

/**
 * useLoadingState - Hook for managing loading states
 */
export const useLoadingState = (initialState = false) => {
  const [isLoading, setIsLoading] = React.useState(initialState);

  const startLoading = React.useCallback(() => setIsLoading(true), []);
  const stopLoading = React.useCallback(() => setIsLoading(false), []);
  const toggleLoading = React.useCallback(() => setIsLoading(prev => !prev), []);

  return {
    isLoading,
    startLoading,
    stopLoading,
    toggleLoading,
    setIsLoading
  };
};

// Export all components
export default {
  Spinner,
  LoadingButton,
  SkeletonLoader,
  LoadingOverlay,
  CardSkeleton,
  TableSkeleton,
  LoadingCard,
  InlineLoader,
  ProgressBar,
  useLoadingState
};
