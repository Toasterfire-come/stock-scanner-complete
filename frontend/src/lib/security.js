// Security utilities for production deployment
import DOMPurify from 'dompurify';

// Environment check
export const isProd = process.env.NODE_ENV === 'production';
export const isDev = process.env.NODE_ENV === 'development';

// Security configuration
export const SECURITY_CONFIG = {
  // Token settings
  TOKEN_STORAGE_KEY: 'rts_token',
  USER_STORAGE_KEY: 'rts_user',
  SESSION_TIMEOUT: parseInt(process.env.REACT_APP_SESSION_TIMEOUT_MINUTES || '30') * 60 * 1000,
  TOKEN_REFRESH_THRESHOLD: parseInt(process.env.REACT_APP_TOKEN_REFRESH_THRESHOLD_MINUTES || '5') * 60 * 1000,
  
  // Rate limiting
  MAX_API_CALLS_PER_MINUTE: parseInt(process.env.REACT_APP_MAX_API_CALLS_PER_MINUTE || '60'),
  MAX_CONCURRENT_REQUESTS: parseInt(process.env.REACT_APP_MAX_CONCURRENT_REQUESTS || '5'),
  
  // Input validation
  MAX_INPUT_LENGTH: 1000,
  MAX_SEARCH_LENGTH: 100,
  
  // CSRF protection
  CSRF_HEADER: 'X-CSRFToken',
  
  // Content Security Policy
  CSP_NONCE: Math.random().toString(36).substring(2, 15),
};

// Input validation and sanitization
export const validateInput = (input, type = 'general') => {
  if (typeof input !== 'string') return '';
  
  // Length validation
  const maxLength = type === 'search' ? SECURITY_CONFIG.MAX_SEARCH_LENGTH : SECURITY_CONFIG.MAX_INPUT_LENGTH;
  if (input.length > maxLength) {
    input = input.substring(0, maxLength);
  }
  
  // Basic XSS prevention
  input = DOMPurify.sanitize(input, { ALLOWED_TAGS: [] });
  
  // SQL injection prevention patterns
  const sqlPatterns = [
    /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)|(--)|(\/\*)/gi,
    /[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g
  ];
  
  for (const pattern of sqlPatterns) {
    if (pattern.test(input)) {
      console.warn('Potentially malicious input detected and blocked');
      return '';
    }
  }
  
  return input.trim();
};

// Email validation
export const validateEmail = (email) => {
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
  return emailRegex.test(email) && email.length <= 254;
};

// Password strength validation
export const validatePassword = (password) => {
  if (typeof password !== 'string') return { valid: false, message: 'Password must be a string' };
  if (password.length < 8) return { valid: false, message: 'Password must be at least 8 characters' };
  if (!/[A-Z]/.test(password)) return { valid: false, message: 'Password must contain at least one uppercase letter' };
  if (!/[a-z]/.test(password)) return { valid: false, message: 'Password must contain at least one lowercase letter' };
  if (!/[0-9]/.test(password)) return { valid: false, message: 'Password must contain at least one number' };
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) return { valid: false, message: 'Password must contain at least one special character' };
  return { valid: true, message: 'Password is strong' };
};

// Secure token storage
export const secureStorage = {
  set: (key, value, encrypt = false) => {
    try {
      let valueToStore = value;
      if (encrypt && typeof value === 'object') {
        // Basic encryption for sensitive data (in production, use proper encryption)
        valueToStore = btoa(JSON.stringify(value));
      } else if (typeof value === 'object') {
        valueToStore = JSON.stringify(value);
      }
      
      localStorage.setItem(key, valueToStore);
    } catch (error) {
      console.error('Failed to store data securely:', error);
    }
  },
  
  get: (key, decrypt = false) => {
    try {
      const value = localStorage.getItem(key);
      if (!value) return null;
      
      if (decrypt) {
        // Basic decryption (in production, use proper decryption)
        return JSON.parse(atob(value));
      }
      
      try {
        return JSON.parse(value);
      } catch {
        return value;
      }
    } catch (error) {
      console.error('Failed to retrieve data securely:', error);
      return null;
    }
  },
  
  remove: (key) => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to remove data:', error);
    }
  },
  
  clear: () => {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Failed to clear storage:', error);
    }
  }
};

// Rate limiting for API calls
class RateLimiter {
  constructor() {
    this.calls = [];
    this.maxCalls = SECURITY_CONFIG.MAX_API_CALLS_PER_MINUTE;
    this.windowMs = 60 * 1000; // 1 minute
  }
  
  canMakeRequest() {
    const now = Date.now();
    // Remove old calls outside the window
    this.calls = this.calls.filter(timestamp => now - timestamp < this.windowMs);
    
    if (this.calls.length >= this.maxCalls) {
      return false;
    }
    
    this.calls.push(now);
    return true;
  }
  
  getRemainingCalls() {
    const now = Date.now();
    this.calls = this.calls.filter(timestamp => now - timestamp < this.windowMs);
    return Math.max(0, this.maxCalls - this.calls.length);
  }
  
  getResetTime() {
    if (this.calls.length === 0) return 0;
    const oldestCall = Math.min(...this.calls);
    return oldestCall + this.windowMs;
  }
}

export const apiRateLimiter = new RateLimiter();

// Request queue for concurrent request limiting
class RequestQueue {
  constructor() {
    this.queue = [];
    this.active = 0;
    this.maxConcurrent = SECURITY_CONFIG.MAX_CONCURRENT_REQUESTS;
  }
  
  async add(requestFn) {
    return new Promise((resolve, reject) => {
      this.queue.push({ requestFn, resolve, reject });
      this.process();
    });
  }
  
  async process() {
    if (this.active >= this.maxConcurrent || this.queue.length === 0) {
      return;
    }
    
    this.active++;
    const { requestFn, resolve, reject } = this.queue.shift();
    
    try {
      const result = await requestFn();
      resolve(result);
    } catch (error) {
      reject(error);
    } finally {
      this.active--;
      this.process(); // Process next request
    }
  }
}

export const requestQueue = new RequestQueue();

// Session management
export const sessionManager = {
  startSession: () => {
    const sessionData = {
      startTime: Date.now(),
      lastActivity: Date.now(),
      isActive: true
    };
    secureStorage.set('session', sessionData);
  },
  
  updateActivity: () => {
    const session = secureStorage.get('session');
    if (session) {
      session.lastActivity = Date.now();
      secureStorage.set('session', session);
    }
  },
  
  isSessionValid: () => {
    const session = secureStorage.get('session');
    if (!session || !session.isActive) return false;
    
    const now = Date.now();
    const timeSinceActivity = now - session.lastActivity;
    
    return timeSinceActivity < SECURITY_CONFIG.SESSION_TIMEOUT;
  },
  
  endSession: () => {
    secureStorage.remove('session');
    secureStorage.remove(SECURITY_CONFIG.TOKEN_STORAGE_KEY);
    secureStorage.remove(SECURITY_CONFIG.USER_STORAGE_KEY);
  }
};

// Security headers validation
export const validateSecurityHeaders = (response) => {
  const requiredHeaders = [
    'x-frame-options',
    'x-content-type-options',
    'x-xss-protection',
    'strict-transport-security'
  ];
  
  const missingHeaders = requiredHeaders.filter(header => 
    !response.headers[header] && !response.headers[header.toLowerCase()]
  );
  
  if (missingHeaders.length > 0 && isDev) {
    console.warn('Missing security headers:', missingHeaders);
  }
  
  return missingHeaders.length === 0;
};

// Content Security Policy helper
export const generateCSPMeta = () => {
  const csp = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${SECURITY_CONFIG.CSP_NONCE}' https://www.paypal.com https://www.google-analytics.com`,
    `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com`,
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: https: blob:",
    "connect-src 'self' https://api.retailtradescanner.com https://www.paypal.com https://www.google-analytics.com https://query1.finance.yahoo.com https://www.alphavantage.com",
    "frame-src https://www.paypal.com",
    "object-src 'none'",
    "base-uri 'self'"
  ].join('; ');
  
  return csp;
};

// Error sanitization for production
export const sanitizeError = (error) => {
  if (!isProd) return error;
  
  // In production, don't expose sensitive error details
  const sanitizedError = {
    message: 'An error occurred',
    status: error?.status || 500,
    timestamp: new Date().toISOString()
  };
  
  // Log full error server-side but return sanitized version to client
  console.error('Full error (server-side only):', error);
  return sanitizedError;
};

// Client-side error logging (placeholder - will be implemented in secureClient.js)
export const logClientError = async (payload) => {
  console.warn('Error logged:', payload);
};
// Environment validation
export const validateEnvironment = () => {
  const requiredVars = [
    'REACT_APP_BACKEND_URL',
    'REACT_APP_API_PASSWORD'
  ];
  
  const missing = requiredVars.filter(varName => !process.env[varName]);
  
  if (missing.length > 0) {
    console.error('Missing required environment variables:', missing);
    return false;
  }
  
  return true;
};

// Initialize security measures
export const initializeSecurity = () => {
  // Validate environment
  if (!validateEnvironment()) {
    throw new Error('Security initialization failed: Missing required environment variables');
  }
  
  // Disable console in production
  if (isProd && !process.env.REACT_APP_ENABLE_CONSOLE_LOGS) {
    console.log = () => {};
    console.warn = () => {};
    console.error = () => {};
  }
  
  // Disable React DevTools in production
  if (isProd && !process.env.REACT_APP_ENABLE_DEVTOOLS) {
    if (typeof window !== 'undefined') {
      window.__REACT_DEVTOOLS_GLOBAL_HOOK__ = { isDisabled: true };
    }
  }
  
  // Start session monitoring
  if (typeof window !== 'undefined') {
    sessionManager.startSession();
    
    // Update activity on user interactions
    ['click', 'keypress', 'scroll', 'mousemove'].forEach(event => {
      document.addEventListener(event, sessionManager.updateActivity, { passive: true });
    });
    
    // Check session validity periodically
    setInterval(() => {
      if (!sessionManager.isSessionValid()) {
        sessionManager.endSession();
        // Redirect to login or show session expired message
        if (window.location.pathname.startsWith('/app/')) {
          window.location.href = '/auth/sign-in?session_expired=true';
        }
      }
    }, 60000); // Check every minute
  }
};

export default {
  validateInput,
  validateEmail,
  validatePassword,
  secureStorage,
  apiRateLimiter,
  requestQueue,
  sessionManager,
  validateSecurityHeaders,
  generateCSPMeta,
  sanitizeError,
  initializeSecurity,
  logClientError,
  validateEnvironment,
  SECURITY_CONFIG
};