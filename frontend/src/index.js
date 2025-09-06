import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";

// Import the secure version instead of the regular App
import SecureApp from "./SecureApp";
import { initSentry } from './sentry';

// Initialize performance monitoring
const startTime = performance.now();

// Init Sentry early
initSentry();

// Create root with security enhancements
const root = ReactDOM.createRoot(document.getElementById("root"));

// Add performance monitoring
const renderApp = () => {
  root.render(
    <React.StrictMode>
      <SecureApp />
    </React.StrictMode>
  );
  
  // Log render performance
  const renderTime = performance.now() - startTime;
  if (renderTime > 1000) {
    console.warn(`Slow app render: ${renderTime.toFixed(2)}ms`);
  }
};

// Render with error handling
try {
  renderApp();
} catch (error) {
  console.error('App render failed:', error);
  
  // Fallback error UI
  root.render(
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      flexDirection: 'column',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1 style={{ color: '#dc2626', marginBottom: '1rem' }}>
        Application Error
      </h1>
      <p style={{ color: '#6b7280', textAlign: 'center', maxWidth: '400px' }}>
        The application failed to load. Please refresh the page or contact support if the issue persists.
      </p>
      <button 
        onClick={() => window.location.reload()}
        style={{
          marginTop: '1rem',
          padding: '0.5rem 1rem',
          backgroundColor: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '0.375rem',
          cursor: 'pointer'
        }}
      >
        Refresh Page
      </button>
    </div>
  );
}

// Performance monitoring
if (process.env.NODE_ENV === 'production') {
  // Log page load performance
  window.addEventListener('load', () => {
    const loadTime = performance.now();
    console.info(`Page load time: ${loadTime.toFixed(2)}ms`);
    
    // Send performance metrics to backend
    if (window.logClientMetric) {
      window.logClientMetric({
        metric: 'page_load_time',
        value: loadTime,
        tags: { page: window.location.pathname }
      });
    }
  });
  
  // Monitor runtime performance
  const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      if (entry.entryType === 'measure' && entry.duration > 100) {
        console.warn(`Slow operation: ${entry.name} took ${entry.duration.toFixed(2)}ms`);
      }
    }
  });
  
  try {
    observer.observe({ entryTypes: ['measure'] });
  } catch (e) {
    // Performance API not supported
  }
}

// Service Worker registration for production
if (process.env.NODE_ENV === 'production' && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}