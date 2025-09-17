// Security utilities
export const SECURITY_CONFIG = {
  TOKEN_STORAGE_KEY: 'rts_token',
  USER_STORAGE_KEY: 'rts_user',
  CSRF_HEADER: 'X-CSRFToken',
  TOKEN_REFRESH_THRESHOLD: 300000, // 5 minutes
};

export const secureStorage = {
  get: (key) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch {
      return null;
    }
  },
  
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      console.warn('Storage failed:', e);
    }
  },
  
  remove: (key) => {
    try {
      localStorage.removeItem(key);
    } catch (e) {
      console.warn('Storage removal failed:', e);
    }
  }
};

export const apiRateLimiter = {
  requests: [],
  maxRequests: 100,
  windowMs: 60000,
  
  canMakeRequest() {
    const now = Date.now();
    this.requests = this.requests.filter(time => now - time < this.windowMs);
    
    if (this.requests.length >= this.maxRequests) {
      return false;
    }
    
    this.requests.push(now);
    return true;
  },
  
  getResetTime() {
    if (this.requests.length === 0) return Date.now();
    return this.requests[0] + this.windowMs;
  }
};

export const sessionManager = {
  lastActivity: Date.now(),
  maxInactiveTime: 30 * 60 * 1000, // 30 minutes
  
  updateActivity() {
    this.lastActivity = Date.now();
  },
  
  isSessionValid() {
    return Date.now() - this.lastActivity < this.maxInactiveTime;
  },
  
  endSession() {
    secureStorage.remove(SECURITY_CONFIG.TOKEN_STORAGE_KEY);
    secureStorage.remove(SECURITY_CONFIG.USER_STORAGE_KEY);
  }
};

export const requestQueue = {
  queue: [],
  processing: false,
  
  async add(requestFn) {
    return new Promise((resolve, reject) => {
      this.queue.push({ requestFn, resolve, reject });
      this.process();
    });
  },
  
  async process() {
    if (this.processing || this.queue.length === 0) return;
    
    this.processing = true;
    
    while (this.queue.length > 0) {
      const { requestFn, resolve, reject } = this.queue.shift();
      
      try {
        const result = await requestFn();
        resolve(result);
      } catch (error) {
        reject(error);
      }
    }
    
    this.processing = false;
  }
};

export function validateSecurityHeaders(response) {
  const requiredHeaders = [
    'X-Content-Type-Options',
    'X-Frame-Options',
    'X-XSS-Protection'
  ];
  
  for (const header of requiredHeaders) {
    if (!response.headers[header.toLowerCase()]) {
      console.warn(`Missing security header: ${header}`);
    }
  }
}

export function sanitizeError(error) {
  return {
    message: error.message || 'An error occurred',
    status: error.response?.status || 500,
    timestamp: new Date().toISOString()
  };
}

export function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function validatePassword(password) {
  return password && password.length >= 8;
}

export async function logClientError(payload) {
  // This will be overridden by the API client
  console.error('Client error:', payload);
}

const security = {
  SECURITY_CONFIG,
  secureStorage,
  apiRateLimiter,
  sessionManager,
  requestQueue,
  validateSecurityHeaders,
  sanitizeError,
  logClientError
};

export default security;