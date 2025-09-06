import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';
import { queryClient, invalidateQueries } from '../lib/queryClient';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [sessionExpired, setSessionExpired] = useState(false);

    // Initialize authentication state
    useEffect(() => {
        const initializeAuth = async () => {
            try {
                if (authService.isAuthenticated()) {
                    const userData = authService.getCurrentUser();
                    setUser(userData);
                    
                    // Validate token and refresh if needed
                    try {
                        await authService.getValidToken();
                    } catch (error) {
                        console.error('Token validation failed:', error);
                        handleLogout();
                    }
                } else {
                    // Clear any stale data
                    authService.clearTokens();
                }
            } catch (error) {
                console.error('Auth initialization error:', error);
                setError(error.message);
            } finally {
                setLoading(false);
            }
        };

        initializeAuth();
    }, []);

    // Handle session expiration
    useEffect(() => {
        const handleTokenExpiration = () => {
            setSessionExpired(true);
            setUser(null);
            queryClient.clear(); // Clear all cached data
        };

        // Listen for storage events (logout from other tabs)
        const handleStorageChange = (e) => {
            if (e.key === 'rts_token' && !e.newValue) {
                handleTokenExpiration();
            }
        };

        window.addEventListener('storage', handleStorageChange);
        return () => window.removeEventListener('storage', handleStorageChange);
    }, []);

    // Enhanced login function
    const login = useCallback(async (credentials) => {
        setLoading(true);
        setError(null);
        setSessionExpired(false);

        try {
            // Check rate limiting
            authService.checkRateLimit('login');
            
            const userData = await authService.login(credentials);
            setUser(userData);
            
            // Clear rate limiting on successful login
            authService.clearRateLimit('login');
            
            // Clear any stale query cache
            queryClient.clear();
            
            return userData;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    // Enhanced register function
    const register = useCallback(async (userData) => {
        setLoading(true);
        setError(null);

        try {
            // Check rate limiting
            authService.checkRateLimit('register');
            
            const newUser = await authService.register(userData);
            setUser(newUser);
            
            // Clear rate limiting on successful registration
            authService.clearRateLimit('register');
            
            // Clear any stale query cache
            queryClient.clear();
            
            return newUser;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    // Enhanced logout function
    const handleLogout = useCallback(() => {
        setUser(null);
        setError(null);
        setSessionExpired(false);
        
        // Clear all cached data
        queryClient.clear();
        
        // Clear tokens and notify server
        authService.logout();
    }, []);

    // Logout alias for backward compatibility
    const logout = handleLogout;

    // Refresh user data
    const refreshUser = useCallback(async () => {
        if (!authService.isAuthenticated()) {
            return null;
        }

        try {
            // This would typically fetch fresh user data from the server
            const headers = await authService.getAuthHeaders();
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/profile/`, {
                headers,
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    const updatedUser = data.data;
                    setUser(updatedUser);
                    localStorage.setItem('user_data', JSON.stringify(updatedUser));
                    return updatedUser;
                }
            } else if (response.status === 401) {
                // Token expired, handle logout
                handleLogout();
            }
        } catch (error) {
            console.error('Error refreshing user data:', error);
        }
        
        return null;
    }, [handleLogout]);

    // Get authentication headers
    const getAuthHeaders = useCallback(async () => {
        try {
            return await authService.getAuthHeaders();
        } catch (error) {
            // If token refresh fails, logout user
            handleLogout();
            throw error;
        }
    }, [handleLogout]);

    // Update user profile
    const updateUser = useCallback((updatedData) => {
        if (user) {
            const newUser = { ...user, ...updatedData };
            setUser(newUser);
            localStorage.setItem('user_data', JSON.stringify(newUser));
        }
    }, [user]);

    // Clear session expired state
    const clearSessionExpired = useCallback(() => {
        setSessionExpired(false);
    }, []);

    // Validate current session
    const validateSession = useCallback(async () => {
        if (!user || !authService.isAuthenticated()) {
            return false;
        }

        try {
            await authService.getValidToken();
            return true;
        } catch (error) {
            handleLogout();
            return false;
        }
    }, [user, handleLogout]);

    // Context value
    const value = {
        // State
        user,
        loading,
        error,
        sessionExpired,
        isAuthenticated: !!user && authService.isAuthenticated(),
        
        // Actions
        login,
        register,
        logout,
        refreshUser,
        updateUser,
        clearSessionExpired,
        validateSession,
        getAuthHeaders,
        
        // Utilities
        isTokenExpiringSoon: () => {
            const token = authService.getToken();
            return authService.isTokenExpiringSoon(token);
        },
        
        getUserPlan: () => user?.plan || 'free',
        getUserLimits: () => user?.limits || { daily: 15, monthly: 15 },
        getUserUsage: () => user?.usage || { daily_calls: 0, monthly_calls: 0 },
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};

// Hook for authenticated API calls
export const useAuthenticatedFetch = () => {
    const { getAuthHeaders, logout } = useAuth();
    
    return useCallback(async (url, options = {}) => {
        try {
            const headers = await getAuthHeaders();
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...headers,
                    ...options.headers,
                },
            });
            
            if (response.status === 401) {
                // Token expired, logout user
                logout();
                throw new Error('Session expired. Please log in again.');
            }
            
            return response;
        } catch (error) {
            if (error.message.includes('No token available')) {
                logout();
            }
            throw error;
        }
    }, [getAuthHeaders, logout]);
};