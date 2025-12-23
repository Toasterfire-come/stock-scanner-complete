/**
 * Performance Optimization Utilities
 * ===================================
 * QA Fix: Issue #24 - Performance Optimization Gaps
 *
 * Provides utilities for improving application performance
 */

import { useEffect, useRef, useCallback, useMemo } from 'react';

/**
 * Debounce function - delay execution until after wait period
 */
export const debounce = (func, wait = 300) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Throttle function - limit execution to once per time period
 */
export const throttle = (func, limit = 300) => {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * useDebounce hook - debounce a value
 */
export const useDebounce = (value, delay = 300) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

/**
 * useThrottle hook - throttle a value
 */
export const useThrottle = (value, limit = 300) => {
  const [throttledValue, setThrottledValue] = useState(value);
  const lastRan = useRef(Date.now());

  useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRan.current >= limit) {
        setThrottledValue(value);
        lastRan.current = Date.now();
      }
    }, limit - (Date.now() - lastRan.current));

    return () => {
      clearTimeout(handler);
    };
  }, [value, limit]);

  return throttledValue;
};

/**
 * Lazy load images - intersection observer
 */
export const useLazyLoad = (ref, options = {}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (!ref.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      {
        rootMargin: '50px',
        ...options
      }
    );

    observer.observe(ref.current);

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current);
      }
    };
  }, [ref, options]);

  return isVisible;
};

/**
 * Memoize expensive computations
 */
export const memoize = (fn) => {
  const cache = new Map();

  return (...args) => {
    const key = JSON.stringify(args);

    if (cache.has(key)) {
      return cache.get(key);
    }

    const result = fn(...args);
    cache.set(key, result);
    return result;
  };
};

/**
 * Optimize array operations
 */
export const optimizeArray = {
  // Virtual scrolling helper - get visible items
  getVisibleItems: (items, scrollTop, itemHeight, containerHeight) => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.ceil((scrollTop + containerHeight) / itemHeight);
    return items.slice(startIndex, endIndex + 1);
  },

  // Chunk large arrays for processing
  chunkArray: (array, size = 100) => {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  },

  // Process array in batches with delay
  processBatches: async (array, batchSize = 100, delay = 10, processor) => {
    const chunks = optimizeArray.chunkArray(array, batchSize);
    const results = [];

    for (const chunk of chunks) {
      results.push(...(await processor(chunk)));
      await new Promise(resolve => setTimeout(resolve, delay));
    }

    return results;
  }
};

/**
 * Image optimization utilities
 */
export const imageOptimization = {
  // Generate srcset for responsive images
  generateSrcSet: (baseUrl, sizes = [320, 640, 960, 1280, 1920]) => {
    return sizes
      .map(size => `${baseUrl}?w=${size} ${size}w`)
      .join(', ');
  },

  // Get optimal image format
  getOptimalFormat: () => {
    // Check browser support
    const canvas = document.createElement('canvas');
    if (canvas.getContext && canvas.getContext('2d')) {
      // Check WebP support
      if (canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0) {
        return 'webp';
      }
    }
    return 'jpg';
  },

  // Lazy load image component
  LazyImage: ({ src, alt, className = '', ...props }) => {
    const imgRef = useRef(null);
    const isVisible = useLazyLoad(imgRef);

    return (
      <img
        ref={imgRef}
        src={isVisible ? src : 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'}
        alt={alt}
        className={className}
        loading="lazy"
        {...props}
      />
    );
  }
};

/**
 * Code splitting utilities
 */
export const codeSplitting = {
  // Lazy load component with fallback
  lazyWithRetry: (componentImport, retries = 3) => {
    return new Promise((resolve, reject) => {
      componentImport()
        .then(resolve)
        .catch((error) => {
          if (retries === 0) {
            reject(error);
            return;
          }

          setTimeout(() => {
            codeSplitting.lazyWithRetry(componentImport, retries - 1)
              .then(resolve)
              .catch(reject);
          }, 1000);
        });
    });
  }
};

/**
 * Bundle size optimization
 */
export const bundleOptimization = {
  // Tree-shakeable imports helper
  treeShake: {
    // Import only what you need from lodash
    lodash: {
      debounce: () => import('lodash/debounce'),
      throttle: () => import('lodash/throttle'),
      chunk: () => import('lodash/chunk')
    },

    // Import only needed date-fns functions
    dateFns: {
      format: () => import('date-fns/format'),
      parseISO: () => import('date-fns/parseISO'),
      formatDistanceToNow: () => import('date-fns/formatDistanceToNow')
    }
  }
};

/**
 * Memory optimization
 */
export const memoryOptimization = {
  // Cleanup large objects
  cleanup: (obj) => {
    Object.keys(obj).forEach(key => {
      delete obj[key];
    });
  },

  // Weak references for large data
  createWeakCache: () => {
    return new WeakMap();
  }
};

/**
 * Request optimization
 */
export const requestOptimization = {
  // Batch API requests
  batchRequests: async (requests, batchSize = 5) => {
    const batches = optimizeArray.chunkArray(requests, batchSize);
    const results = [];

    for (const batch of batches) {
      const batchResults = await Promise.all(batch);
      results.push(...batchResults);
    }

    return results;
  },

  // Request deduplication
  dedupeRequests: (() => {
    const cache = new Map();

    return async (key, requestFn) => {
      if (cache.has(key)) {
        return cache.get(key);
      }

      const promise = requestFn();
      cache.set(key, promise);

      try {
        const result = await promise;
        cache.delete(key);
        return result;
      } catch (error) {
        cache.delete(key);
        throw error;
      }
    };
  })()
};

/**
 * Render optimization hooks
 */
export const useRenderOptimization = () => {
  // Prevent unnecessary re-renders
  const useMemoCallback = useCallback;
  const useMemoValue = useMemo;

  // Track component renders (development only)
  const renderCount = useRef(0);
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      renderCount.current += 1;
      console.log(`Component rendered ${renderCount.current} times`);
    }
  });

  return {
    useMemoCallback,
    useMemoValue,
    renderCount: renderCount.current
  };
};

/**
 * Performance monitoring
 */
export const performanceMonitoring = {
  // Measure component render time
  measureRender: (componentName) => {
    const start = performance.now();

    return () => {
      const end = performance.now();
      const duration = end - start;

      if (process.env.NODE_ENV === 'development') {
        console.log(`${componentName} rendered in ${duration.toFixed(2)}ms`);
      }

      return duration;
    };
  },

  // Track long tasks
  trackLongTasks: (threshold = 50) => {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.duration > threshold) {
            console.warn(`Long task detected: ${entry.duration.toFixed(2)}ms`);
          }
        }
      });

      observer.observe({ entryTypes: ['longtask'] });
      return observer;
    }
  },

  // Get performance metrics
  getMetrics: () => {
    if (!window.performance) return null;

    const navigation = performance.getEntriesByType('navigation')[0];
    const paint = performance.getEntriesByType('paint');

    return {
      // Time to First Byte
      ttfb: navigation?.responseStart - navigation?.requestStart,

      // First Contentful Paint
      fcp: paint.find(entry => entry.name === 'first-contentful-paint')?.startTime,

      // Largest Contentful Paint (needs PerformanceObserver)
      // First Input Delay (needs PerformanceObserver)

      // DOM Content Loaded
      domContentLoaded: navigation?.domContentLoadedEventEnd - navigation?.domContentLoadedEventStart,

      // Page Load Time
      loadTime: navigation?.loadEventEnd - navigation?.loadEventStart
    };
  }
};

/**
 * Service Worker helpers
 */
export const serviceWorkerHelpers = {
  // Register service worker
  register: async (swPath = '/service-worker.js') => {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register(swPath);
        console.log('Service Worker registered:', registration);
        return registration;
      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    }
  },

  // Unregister service worker
  unregister: async () => {
    if ('serviceWorker' in navigator) {
      const registrations = await navigator.serviceWorker.getRegistrations();
      for (const registration of registrations) {
        await registration.unregister();
      }
    }
  }
};

// Export all utilities
export default {
  debounce,
  throttle,
  useDebounce,
  useThrottle,
  useLazyLoad,
  memoize,
  optimizeArray,
  imageOptimization,
  codeSplitting,
  bundleOptimization,
  memoryOptimization,
  requestOptimization,
  useRenderOptimization,
  performanceMonitoring,
  serviceWorkerHelpers
};
