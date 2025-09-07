import axios from "axios";
import { getCache, setCache } from "../lib/cache";
import security, { apiRateLimiter, requestQueue, sessionManager, secureStorage, validateSecurityHeaders, sanitizeError } from "../lib/security";

// Environment configuration
// Prefer external API by default in production if env not set
const BASE_URL = (
  process.env.REACT_APP_BACKEND_URL ||
  (process.env.NODE_ENV === 'production' ? 'https://api.retailtradescanner.com' : '')
).trim();
const isProd = process.env.NODE_ENV === 'production';

if (!BASE_URL) {
  console.error("REACT_APP_BACKEND_URL is not set. API calls will fail.");
  if (isProd) {
    throw new Error("Backend URL configuration missing");
  }
}

export const API_ROOT = `${BASE_URL}/api`;
export const REVENUE_ROOT = `${BASE_URL}/revenue`;

// Network event bus for latency monitoring
(function initNetBus(){
  if (typeof window === 'undefined') return;
  if (!window.__NET) {
    const listeners = { start: new Set(), end: new Set(), slow: new Set(), error: new Set() };
    window.__NET = {
      on(evt, cb){ listeners[evt]?.add(cb); },
      off(evt, cb){ listeners[evt]?.delete(cb); },
      emit(evt, payload){ listeners[evt]?.forEach(cb=>{ try{ cb(payload); } catch{} }); },
    };
  }
})();

// Create secure axios instance
export const api = axios.create({
  baseURL: API_ROOT,
  withCredentials: false,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  }
});

// CSRF token management
function getCsrfToken() {
  try {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : null;
  } catch { 
    return null; 
  }
}

// Token refresh management
let tokenRefreshPromise = null;

const refreshTokenIfNeeded = async () => {
  const token = secureStorage.get(security.SECURITY_CONFIG.TOKEN_STORAGE_KEY);
  if (!token) return null;
  
  try {
    // Decode token to check expiry (simplified JWT check)
    const payload = JSON.parse(atob(token.split('.')[1]));
    const now = Date.now() / 1000;
    const timeUntilExpiry = payload.exp - now;
    
    // Refresh if token expires within threshold
    if (timeUntilExpiry < security.SECURITY_CONFIG.TOKEN_REFRESH_THRESHOLD / 1000) {
      if (!tokenRefreshPromise) {
        tokenRefreshPromise = api.post('/auth/refresh-token/')
          .then(response => {
            const newToken = response.data.token;
            secureStorage.set(security.SECURITY_CONFIG.TOKEN_STORAGE_KEY, newToken);
            return newToken;
          })
          .catch(error => {
            console.error('Token refresh failed:', error);
            // Force logout on refresh failure
            secureStorage.remove(security.SECURITY_CONFIG.TOKEN_STORAGE_KEY);
            secureStorage.remove(security.SECURITY_CONFIG.USER_STORAGE_KEY);
            window.location.href = '/auth/sign-in?token_expired=true';
            throw error;
          })
          .finally(() => {
            tokenRefreshPromise = null;
          });
      }
      return await tokenRefreshPromise;
    }
    
    return token;
  } catch (error) {
    console.error('Token validation failed:', error);
    return token; // Return original token if validation fails
  }
};

// Request interceptor with security enhancements
api.interceptors.request.use(async (config) => {
  try {
    // Rate limiting check
    if (!apiRateLimiter.canMakeRequest()) {
      const resetTime = apiRateLimiter.getResetTime();
      const waitTime = Math.max(0, resetTime - Date.now());
      throw new Error(`Rate limit exceeded. Try again in ${Math.ceil(waitTime / 1000)} seconds.`);
    }
    
    // Session validation
    if (!sessionManager.isSessionValid()) {
      sessionManager.endSession();
      window.location.href = '/auth/sign-in?session_expired=true';
      throw new Error('Session expired');
    }
    
    // CSRF protection
    const csrf = getCsrfToken();
    if (csrf) {
      config.headers[security.SECURITY_CONFIG.CSRF_HEADER] = csrf;
    }
    
    // Token management with refresh
    const token = await refreshTokenIfNeeded();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add security headers
    config.headers['X-Client-Version'] = process.env.REACT_APP_VERSION || '1.0.0';
    config.headers['X-Client-Environment'] = process.env.NODE_ENV;
    
    // Request tracking for monitoring
    config.metadata = { 
      start: Date.now(), 
      url: `${config.baseURL || ''}${config.url || ''}`,
      method: config.method?.toUpperCase()
    };
    
    // Update session activity
    sessionManager.updateActivity();
    
    // Emit network start event
    window.__NET?.emit('start', { 
      url: config.metadata.url, 
      method: config.metadata.method 
    });
    
    return config;
  } catch (error) {
    window.__NET?.emit('error', { error: error.message });
    throw error;
  }
}, (error) => {
  window.__NET?.emit('error', { error: error.message });
  return Promise.reject(sanitizeError(error));
});

// Response interceptor with security enhancements
api.interceptors.response.use(
  (response) => {
    try {
      // Calculate request duration
      const dur = Date.now() - (response.config.metadata?.start || Date.now());
      
      // Validate security headers
      validateSecurityHeaders(response);
      
      // Emit network events
      if (dur > 1000) {
        window.__NET?.emit('slow', { 
          url: response.config.metadata?.url, 
          duration: dur, 
          status: response.status 
        });
      }
      
      window.__NET?.emit('end', { 
        duration: dur, 
        status: response.status 
      });
      
      // Update rate limit headers if present
      const rateLimitUsed = response.headers['x-ratelimit-used'];
      const rateLimitLimit = response.headers['x-ratelimit-limit'];
      const rateLimitReset = response.headers['x-ratelimit-reset'];
      
      if (rateLimitUsed && rateLimitLimit) {
        const remaining = rateLimitLimit - rateLimitUsed;
        if (remaining < 10) {
          console.warn(`Rate limit warning: ${remaining} requests remaining`);
        }
      }
      
      return response;
    } catch (error) {
      console.error('Response processing error:', error);
      return response;
    }
  },
  (error) => {
    try {
      const cfg = error.config || {};
      const dur = Date.now() - (cfg.metadata?.start || Date.now());
      
      // Emit network events for errors
      if (dur > 1000) {
        window.__NET?.emit('slow', { 
          url: cfg.metadata?.url, 
          duration: dur, 
          status: error.response?.status 
        });
      }
      
      window.__NET?.emit('end', { 
        duration: dur, 
        status: error.response?.status,
        error: true 
      });
      
      // Handle authentication errors
      if (error.response?.status === 401) {
        secureStorage.remove(security.SECURITY_CONFIG.TOKEN_STORAGE_KEY);
        secureStorage.remove(security.SECURITY_CONFIG.USER_STORAGE_KEY);
        sessionManager.endSession();
        
        if (!window.location.pathname.startsWith('/auth')) {
          window.location.href = "/auth/sign-in?auth_required=true";
        }
      }
      
      // Handle rate limiting errors
      if (error.response?.status === 429) {
        const retryAfter = error.response.headers['retry-after'];
        if (retryAfter) {
          console.warn(`Rate limited. Retry after ${retryAfter} seconds`);
        }
      }
      
      // Emit error event
      window.__NET?.emit('error', { 
        status: error.response?.status,
        message: error.message 
      });
      
      return Promise.reject(sanitizeError(error));
    } catch (processingError) {
      console.error('Error processing error:', processingError);
      return Promise.reject(sanitizeError(error));
    }
  }
);

// Secure API call wrapper with request queuing
const secureApiCall = async (requestFn) => {
  try {
    return await requestQueue.add(requestFn);
  } catch (error) {
    throw sanitizeError(error);
  }
};

// Client-side error logging with security
export async function logClientError(payload) {
  try {
    const sanitizedPayload = {
      message: payload.message || 'Unknown error',
      stack: isProd ? 'Stack trace hidden in production' : payload.stack,
      url: window.location.pathname,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString(),
      userId: secureStorage.get(security.SECURITY_CONFIG.USER_STORAGE_KEY)?.id || 'anonymous'
    };
    
    await secureApiCall(() => api.post('/logs/client/', sanitizedPayload));
  } catch (error) {
    console.error('Failed to log client error:', error);
  }
}

// Enhanced metric logging
export async function logClientMetric(payload) {
  try {
    const sanitizedPayload = {
      metric: payload.metric || 'unknown',
      value: payload.value || 0,
      tags: payload.tags || {},
      timestamp: new Date().toISOString(),
      userId: secureStorage.get(security.SECURITY_CONFIG.USER_STORAGE_KEY)?.id || 'anonymous'
    };
    
    await secureApiCall(() => api.post('/logs/metrics/', sanitizedPayload));
  } catch (error) {
    console.error('Failed to log metric:', error);
  }
}

// Expose secure logging to window for error boundaries
if (typeof window !== 'undefined') {
  window.logClientError = logClientError;
  window.logClientMetric = logClientMetric;
}

// Export secure API functions
export { secureApiCall, api as default };