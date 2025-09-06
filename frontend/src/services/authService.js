import { jwtDecode } from 'jwt-decode';

class AuthService {
    constructor() {
        this.baseURL = process.env.REACT_APP_BACKEND_URL;
        this.tokenKey = 'rts_token';
        this.userDataKey = 'user_data';
        this.refreshTokenKey = 'rts_refresh_token';
        this.isRefreshing = false;
        this.failedQueue = [];
    }

    // Token management
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    getRefreshToken() {
        return localStorage.getItem(this.refreshTokenKey);
    }

    setTokens(accessToken, refreshToken) {
        localStorage.setItem(this.tokenKey, accessToken);
        if (refreshToken) {
            localStorage.setItem(this.refreshTokenKey, refreshToken);
        }
    }

    clearTokens() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.refreshTokenKey);
        localStorage.removeItem(this.userDataKey);
    }

    // Token validation (Django backend uses simple API tokens, not JWTs)
    isTokenValid(token) {
        if (!token) return false;
        
        // For Django API tokens, we just check if the token exists
        // The backend will validate the token on each request
        return typeof token === 'string' && token.length > 0;
    }

    isTokenExpiringSoon(token) {
        // Django API tokens don't expire by default
        // Return false to avoid unnecessary refresh attempts
        return false;
    }

    // Refresh token logic
    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        try {
            const response = await fetch(`${this.baseURL}/api/auth/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh_token: refreshToken }),
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();
            
            if (data.success) {
                this.setTokens(data.access_token, data.refresh_token);
                return data.access_token;
            } else {
                throw new Error(data.error || 'Token refresh failed');
            }
        } catch (error) {
            this.clearTokens();
            throw error;
        }
    }

    // Queue management for concurrent refresh requests
    processQueue(error, token = null) {
        this.failedQueue.forEach(({ resolve, reject }) => {
            if (error) {
                reject(error);
            } else {
                resolve(token);
            }
        });
        
        this.failedQueue = [];
    }

    // Get valid token (simplified for Django API tokens)
    async getValidToken() {
        const token = this.getToken();
        
        if (!token) {
            throw new Error('No token available');
        }

        // Django API tokens don't expire, so we just return the token
        return token;
    }

    // Enhanced authentication headers (simplified for Django)
    async getAuthHeaders() {
        try {
            const token = await this.getValidToken();
            return {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-Requested-With': 'XMLHttpRequest', // CSRF protection
            };
        } catch (error) {
            return {
                'Content-Type': 'application/json',
            };
        }
    }

    // Login with enhanced security
    async login(credentials) {
        // Input validation
        if (!credentials.username || !credentials.password) {
            throw new Error('Username and password are required');
        }

        // Sanitize inputs
        const sanitizedCredentials = {
            username: credentials.username.trim().toLowerCase(),
            password: credentials.password,
        };

        try {
            const response = await fetch(`${this.baseURL}/api/auth/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(sanitizedCredentials),
            });

            const data = await response.json();

            if (data.success) {
                // Store tokens securely (Django only returns api_token)
                this.setTokens(data.data.api_token, null);
                localStorage.setItem(this.userDataKey, JSON.stringify(data.data));
                
                return data.data;
            } else {
                throw new Error(data.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    // Register with input validation
    async register(userData) {
        // Input validation
        const requiredFields = ['username', 'email', 'password', 'firstName', 'lastName'];
        for (const field of requiredFields) {
            if (!userData[field] || userData[field].trim() === '') {
                throw new Error(`${field} is required`);
            }
        }

        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(userData.email)) {
            throw new Error('Please enter a valid email address');
        }

        // Password strength validation
        if (userData.password.length < 8) {
            throw new Error('Password must be at least 8 characters long');
        }

        if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(userData.password)) {
            throw new Error('Password must contain at least one uppercase letter, one lowercase letter, and one number');
        }

        // Sanitize inputs
        const sanitizedData = {
            username: userData.username.trim().toLowerCase(),
            email: userData.email.trim().toLowerCase(),
            password: userData.password,
            first_name: userData.firstName.trim(),
            last_name: userData.lastName.trim(),
        };

        try {
            const response = await fetch(`${this.baseURL}/api/auth/register/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(sanitizedData),
            });

            const data = await response.json();

            if (data.success) {
                // Store tokens securely (Django only returns api_token)
                this.setTokens(data.data.api_token, null);
                localStorage.setItem(this.userDataKey, JSON.stringify(data.data));
                
                return data.data;
            } else {
                throw new Error(data.error || 'Registration failed');
            }
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }

    // Schedule automatic token refresh
    scheduleTokenRefresh(token) {
        if (!token) return;

        try {
            const decoded = jwtDecode(token);
            const currentTime = Date.now() / 1000;
            const expirationTime = decoded.exp;
            
            // Schedule refresh 10 minutes before expiration
            const refreshTime = (expirationTime - currentTime - 600) * 1000;
            
            if (refreshTime > 0) {
                setTimeout(async () => {
                    try {
                        await this.refreshAccessToken();
                    } catch (error) {
                        console.error('Scheduled token refresh failed:', error);
                        this.logout();
                    }
                }, refreshTime);
            }
        } catch (error) {
            console.error('Error scheduling token refresh:', error);
        }
    }

    // Logout with cleanup
    logout() {
        this.clearTokens();
        
        // Clear any scheduled refreshes
        this.isRefreshing = false;
        this.failedQueue = [];
        
        // Optional: Notify server of logout
        this.notifyServerLogout();
    }

    // Notify server of logout (optional)
    async notifyServerLogout() {
        try {
            const token = localStorage.getItem(this.tokenKey);
            if (token) {
                await fetch(`${this.baseURL}/api/auth/logout/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                });
            }
        } catch (error) {
            // Ignore logout notification errors
            console.debug('Logout notification failed:', error);
        }
    }

    // Check if user is authenticated (simplified for Django API tokens)
    isAuthenticated() {
        const token = this.getToken();
        const userData = localStorage.getItem(this.userDataKey);
        
        return !!(token && userData);
    }

    // Get current user data
    getCurrentUser() {
        const userData = localStorage.getItem(this.userDataKey);
        return userData ? JSON.parse(userData) : null;
    }

    // Security utilities
    generateCSRFToken() {
        return Math.random().toString(36).substring(2, 15) + 
               Math.random().toString(36).substring(2, 15);
    }

    // Rate limiting for authentication attempts
    checkRateLimit(action) {
        const key = `${action}_attempts`;
        const timestamp = Date.now();
        const attempts = JSON.parse(localStorage.getItem(key) || '[]');
        
        // Remove attempts older than 15 minutes
        const recentAttempts = attempts.filter(attempt => 
            timestamp - attempt < 15 * 60 * 1000
        );
        
        if (recentAttempts.length >= 5) {
            throw new Error('Too many attempts. Please try again in 15 minutes.');
        }
        
        recentAttempts.push(timestamp);
        localStorage.setItem(key, JSON.stringify(recentAttempts));
    }

    // Clear rate limit (called on successful authentication)
    clearRateLimit(action) {
        localStorage.removeItem(`${action}_attempts`);
    }
}

export const authService = new AuthService();