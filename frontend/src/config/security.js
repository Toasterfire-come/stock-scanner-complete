/**
 * Security configuration for production
 */

// Content Security Policy
export const CSP_HEADER = {
  'default-src': ["'self'"],
  'script-src': [
    "'self'",
    "'unsafe-inline'", // Required for React
    'https://api.retailtradescanner.com',
    'https://www.google-analytics.com',
    'https://www.googletagmanager.com'
  ],
  'style-src': [
    "'self'",
    "'unsafe-inline'", // Required for styled-components/emotion
    'https://fonts.googleapis.com'
  ],
  'img-src': [
    "'self'",
    'data:',
    'https:',
    'blob:'
  ],
  'font-src': [
    "'self'",
    'https://fonts.gstatic.com'
  ],
  'connect-src': [
    "'self'",
    'https://api.retailtradescanner.com',
    'wss://api.retailtradescanner.com', // For WebSocket if needed
    'https://www.google-analytics.com'
  ],
  'media-src': ["'self'"],
  'object-src': ["'none'"],
  'frame-src': [
    "'self'",
    'https://js.stripe.com', // For Stripe checkout
    'https://checkout.stripe.com'
  ],
  'worker-src': ["'self'", 'blob:'],
  'form-action': ["'self'"],
  'base-uri': ["'self'"],
  'manifest-src': ["'self'"],
  'upgrade-insecure-requests': []
};

// Security Headers
export const SECURITY_HEADERS = {
  'X-Frame-Options': 'SAMEORIGIN',
  'X-Content-Type-Options': 'nosniff',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
};

// CORS Configuration
export const CORS_CONFIG = {
  origin: process.env.REACT_APP_ENV === 'production' 
    ? ['https://retailtradescanner.com', 'https://www.retailtradescanner.com']
    : ['http://localhost:3000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: [
    'Content-Type',
    'Authorization',
    'X-Requested-With',
    'X-CSRFToken',
    'X-Session-ID',
    'X-API-Key'
  ],
  exposedHeaders: ['X-Total-Count', 'X-Page-Count'],
  maxAge: 86400 // 24 hours
};

// Rate Limiting Configuration
export const RATE_LIMITS = {
  api: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP, please try again later.'
  },
  auth: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // Limit login attempts
    skipSuccessfulRequests: true
  },
  payment: {
    windowMs: 60 * 60 * 1000, // 1 hour
    max: 10 // Limit payment attempts
  }
};

// Input Validation Rules
export const VALIDATION_RULES = {
  username: {
    minLength: 3,
    maxLength: 20,
    pattern: /^[a-zA-Z0-9_]+$/,
    message: 'Username must be 3-20 characters and contain only letters, numbers, and underscores'
  },
  email: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    maxLength: 255,
    message: 'Please enter a valid email address'
  },
  password: {
    minLength: 8,
    maxLength: 128,
    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
    message: 'Password must be at least 8 characters with uppercase, lowercase, number, and special character'
  }
};

// Sanitization functions
export const sanitize = {
  html: (input) => {
    // Remove any HTML tags
    return input.replace(/<[^>]*>?/gm, '');
  },
  sql: (input) => {
    // Basic SQL injection prevention
    return input.replace(/['";\\]/g, '');
  },
  xss: (input) => {
    // XSS prevention
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#x27;',
      '/': '&#x2F;'
    };
    return input.replace(/[&<>"'/]/g, (s) => map[s]);
  }
};

// Encryption configuration
export const ENCRYPTION = {
  algorithm: 'AES-256-GCM',
  keyDerivation: 'PBKDF2',
  iterations: 100000,
  saltLength: 32,
  tagLength: 16,
  ivLength: 16
};

// Session configuration
export const SESSION_CONFIG = {
  name: 'rts_session',
  secret: process.env.REACT_APP_SESSION_SECRET || 'change-this-in-production',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.REACT_APP_ENV === 'production',
    httpOnly: true,
    maxAge: 1000 * 60 * 60 * 24 * 7, // 7 days
    sameSite: 'strict'
  }
};

// API Security
export const API_SECURITY = {
  timeout: 30000, // 30 seconds
  retries: 3,
  retryDelay: 1000,
  validateStatus: (status) => status >= 200 && status < 300,
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken'
};

// File Upload Security
export const FILE_UPLOAD = {
  maxSize: 5 * 1024 * 1024, // 5MB
  allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'],
  allowedExtensions: ['.jpg', '.jpeg', '.png', '.gif', '.pdf'],
  scanForVirus: true // Implement virus scanning in production
};

export default {
  CSP_HEADER,
  SECURITY_HEADERS,
  CORS_CONFIG,
  RATE_LIMITS,
  VALIDATION_RULES,
  sanitize,
  ENCRYPTION,
  SESSION_CONFIG,
  API_SECURITY,
  FILE_UPLOAD
};