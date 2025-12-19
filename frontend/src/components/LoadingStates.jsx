// Enhanced Loading States Component - Phase 10 UI/UX
import React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "../lib/utils";

/**
 * Skeleton - Animated placeholder for loading content
 */
export function Skeleton({ className, ...props }) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-gray-200/80",
        className
      )}
      {...props}
    />
  );
}

/**
 * Full page loading spinner
 */
export function PageLoader({ text = "Loading..." }) {
  return (
    <div className="fixed inset-0 bg-white/80 backdrop-blur-sm flex flex-col items-center justify-center z-50">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-blue-200 rounded-full animate-spin border-t-blue-600" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-8 bg-blue-600 rounded-full animate-ping opacity-20" />
        </div>
      </div>
      <p className="mt-4 text-gray-600 font-medium animate-pulse">{text}</p>
    </div>
  );
}

/**
 * Inline spinner for buttons and small areas
 */
export function Spinner({ size = "default", className = "" }) {
  const sizeClasses = {
    sm: "h-4 w-4",
    default: "h-5 w-5",
    lg: "h-6 w-6",
    xl: "h-8 w-8",
  };
  
  return (
    <Loader2 
      className={cn(
        "animate-spin text-current",
        sizeClasses[size],
        className
      )} 
    />
  );
}

/**
 * Card Skeleton - For loading cards with content
 */
export function CardSkeleton({ lines = 3, showImage = false, showFooter = false }) {
  return (
    <div className="bg-white rounded-lg border shadow-sm p-6 space-y-4">
      {showImage && (
        <Skeleton className="h-48 w-full rounded-lg" />
      )}
      <div className="space-y-3">
        <Skeleton className="h-6 w-3/4" />
        {Array.from({ length: lines }).map((_, i) => (
          <Skeleton 
            key={i} 
            className="h-4" 
            style={{ width: `${85 - i * 15}%` }}
          />
        ))}
      </div>
      {showFooter && (
        <div className="flex justify-between pt-4 border-t">
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-8 w-20" />
        </div>
      )}
    </div>
  );
}

/**
 * Table Skeleton - For loading tables
 */
export function TableSkeleton({ rows = 5, columns = 4 }) {
  return (
    <div className="bg-white rounded-lg border overflow-hidden">
      {/* Header */}
      <div className="bg-gray-50 border-b p-4 flex gap-4">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="h-5 flex-1" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIdx) => (
        <div key={rowIdx} className="border-b last:border-0 p-4 flex gap-4">
          {Array.from({ length: columns }).map((_, colIdx) => (
            <Skeleton 
              key={colIdx} 
              className="h-4 flex-1" 
              style={{ 
                animationDelay: `${(rowIdx * columns + colIdx) * 50}ms` 
              }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

/**
 * Chart Skeleton - For loading charts
 */
export function ChartSkeleton({ height = 300 }) {
  return (
    <div 
      className="bg-white rounded-lg border p-6"
      style={{ height }}
    >
      <div className="flex items-end justify-between h-full gap-2">
        {Array.from({ length: 12 }).map((_, i) => (
          <Skeleton 
            key={i} 
            className="flex-1 rounded-t"
            style={{ 
              height: `${Math.random() * 60 + 30}%`,
              animationDelay: `${i * 100}ms`
            }}
          />
        ))}
      </div>
    </div>
  );
}

/**
 * Stats Card Skeleton - For dashboard statistics
 */
export function StatsSkeleton({ count = 4 }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="bg-white rounded-lg border p-4 space-y-2">
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-3 w-2/3" />
        </div>
      ))}
    </div>
  );
}

/**
 * List Item Skeleton - For loading list items
 */
export function ListSkeleton({ items = 5, showAvatar = true }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: items }).map((_, i) => (
        <div 
          key={i} 
          className="flex items-center gap-4 p-4 bg-white rounded-lg border"
          style={{ animationDelay: `${i * 100}ms` }}
        >
          {showAvatar && <Skeleton className="h-10 w-10 rounded-full shrink-0" />}
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
          <Skeleton className="h-8 w-20" />
        </div>
      ))}
    </div>
  );
}

/**
 * Stock Card Skeleton - For loading stock information
 */
export function StockCardSkeleton() {
  return (
    <div className="bg-white rounded-lg border p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Skeleton className="h-12 w-12 rounded-lg" />
          <div className="space-y-2">
            <Skeleton className="h-5 w-20" />
            <Skeleton className="h-3 w-32" />
          </div>
        </div>
        <div className="text-right space-y-2">
          <Skeleton className="h-6 w-24" />
          <Skeleton className="h-4 w-16 ml-auto" />
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4 pt-4 border-t">
        <div className="space-y-1">
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </div>
        <div className="space-y-1">
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </div>
        <div className="space-y-1">
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </div>
      </div>
    </div>
  );
}

/**
 * Pulse Ring - Attention-grabbing loading indicator
 */
export function PulseRing({ size = 48, color = "blue" }) {
  const colorClasses = {
    blue: "border-blue-600",
    green: "border-green-600",
    red: "border-red-600",
    purple: "border-purple-600",
  };
  
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <div 
        className={cn(
          "absolute inset-0 rounded-full border-4 animate-ping opacity-30",
          colorClasses[color]
        )}
      />
      <div 
        className={cn(
          "absolute inset-2 rounded-full border-4 animate-pulse opacity-50",
          colorClasses[color]
        )}
      />
      <div 
        className={cn(
          "absolute inset-4 rounded-full border-4 animate-spin border-t-transparent",
          colorClasses[color]
        )}
      />
    </div>
  );
}

/**
 * Progress Bar - For determinate loading states
 */
export function ProgressBar({ progress = 0, showLabel = true, className = "" }) {
  return (
    <div className={cn("w-full", className)}>
      {showLabel && (
        <div className="flex justify-between mb-1">
          <span className="text-sm text-gray-600">Loading...</span>
          <span className="text-sm font-medium text-gray-900">{Math.round(progress)}%</span>
        </div>
      )}
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className="h-full bg-blue-600 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}

/**
 * Loading Overlay - Overlay with loading indicator for containers
 */
export function LoadingOverlay({ isLoading, children, text }) {
  return (
    <div className="relative">
      {children}
      {isLoading && (
        <div className="absolute inset-0 bg-white/80 backdrop-blur-[2px] flex flex-col items-center justify-center rounded-lg z-10">
          <Spinner size="lg" className="text-blue-600" />
          {text && <p className="mt-2 text-sm text-gray-600">{text}</p>}
        </div>
      )}
    </div>
  );
}

export default {
  Skeleton,
  PageLoader,
  Spinner,
  CardSkeleton,
  TableSkeleton,
  ChartSkeleton,
  StatsSkeleton,
  ListSkeleton,
  StockCardSkeleton,
  PulseRing,
  ProgressBar,
  LoadingOverlay,
};
