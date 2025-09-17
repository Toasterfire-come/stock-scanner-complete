import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin, registerUser as apiRegister, logout as apiLogout, getProfile as apiGetProfile } from '../api/client';
import security, { secureStorage, validateEmail, validatePassword, sessionManager } from '../lib/security';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    // Graceful fallback to prevent crashes if provider is missing in some routes
    return {
      user: null,
      isAuthenticated: false,
      isLoading: false,
      authError: null,
      login: async () => ({ success: false, error: 'Auth unavailable' }),
      register: async () => ({ success: false, error: 'Auth unavailable' }),
      logout: () => {},
      updateUser: () => {},
      clearError: () => {},
      refreshSession: () => {},
      isPremium: false,
      hasVerifiedEmail: false,
    };
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  // Helper to safely retrieve stored user (handles encrypted and plain storage)
  const getStoredUserSafe = () => {
    try {
      const decrypted = secureStorage.get(security.SECURITY_CONFIG.USER_STORAGE_KEY, true);
      if (decrypted) return decrypted;
    } catch (_) {}
    const raw = secureStorage.get(security.SECURITY_CONFIG.USER_STORAGE_KEY);
    if (!raw) return null;
    if (typeof raw === 'string') {
      try {
        return JSON.parse(raw);
      } catch (_) {
        return null;
      }
    }
    return raw;
  };

  // Initialize authentication state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Check for stored user data (encrypted or plain) and a valid local session
        const storedUser = getStoredUserSafe();
        const token = secureStorage.get(security.SECURITY_CONFIG.TOKEN_STORAGE_KEY);

        if (storedUser && token) {
          // If we have both user and token, consider authenticated
          setUser(storedUser);
          setIsAuthenticated(true);
          
          // Start or update the session
          sessionManager.startSession();
          sessionManager.updateActivity();
        } else if (storedUser && sessionManager.isSessionValid()) {
          // Fallback to session check if no token
          setUser(storedUser);
          setIsAuthenticated(true);
          sessionManager.updateActivity();
        } else {
          // Attempt to hydrate auth from server session cookie
          try {
            const prof = await apiGetProfile();
            if (prof && (prof.success === true || prof.data)) {
              const d = prof.data || prof;
              const hydratedUser = {
                id: d.user_id || d.id,
                username: d.username,
                email: d.email,
                name: d.first_name && d.last_name ? `${d.first_name} ${d.last_name}`.trim() : (d.username || ''),
                plan: d.plan || d.plan_type || 'free',
                isVerified: d.is_verified || false,
                joinDate: d.date_joined || new Date().toISOString(),
                lastLogin: d.last_login || null,
              };
              secureStorage.set(security.SECURITY_CONFIG.USER_STORAGE_KEY, hydratedUser, true);
              setUser(hydratedUser);
              setIsAuthenticated(true);
              sessionManager.startSession();
              sessionManager.updateActivity();
            } else {
              await logout();
            }
          } catch {
            // Not authenticated server-side
            await logout();
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        await logout();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();

    // Set up session monitoring
    const sessionCheckInterval = setInterval(() => {
      if (isAuthenticated && !sessionManager.isSessionValid()) {
        handleSessionExpiry();
      }
    }, 60000); // Check every minute

    return () => clearInterval(sessionCheckInterval);
  }, [isAuthenticated]);

  const handleSessionExpiry = async () => {
    setAuthError('Your session has expired. Please sign in again.');
    await logout();
    // Redirect to login with session expired flag
    window.location.href = '/auth/sign-in?session_expired=true';
  };

  const login = async (username, password) => {
    setIsLoading(true);
    setAuthError(null);
    
    try {
      // Input validation
      if (!username || !password) {
        throw new Error('Username and password are required');
      }

      // Validate email format if username is email
      if (username.includes('@') && !validateEmail(username)) {
        throw new Error('Please enter a valid email address');
      }

      // Basic password validation
      if (password.length < 6) {
        throw new Error('Password must be at least 6 characters long');
      }

      // Call API login
      const response = await apiLogin(username, password);
      console.log('API login response:', response); // Debug log
      
      if (response.success && response.data) {
        const userData = {
          id: response.data.user_id || response.data.id,
          username: response.data.username,
          email: response.data.email,
          name: response.data.first_name && response.data.last_name 
            ? `${response.data.first_name} ${response.data.last_name}`.trim()
            : response.data.username,
          plan: response.data.plan || 'free',
          isVerified: response.data.is_verified || false,
          joinDate: response.data.date_joined || new Date().toISOString(),
          lastLogin: new Date().toISOString()
        };

        // Store user data and token securely
        secureStorage.set(security.SECURITY_CONFIG.USER_STORAGE_KEY, userData, true);
        
        // Store token - prefer session key (api_token) from backend for Authorization: Bearer
        const token = response.data.api_token || response.data.token || response.data.access_token;
        if (token) {
          secureStorage.set(security.SECURITY_CONFIG.TOKEN_STORAGE_KEY, token);
        }
        
        // Start session
        sessionManager.startSession();
        
        // Update state immediately
        setUser(userData);
        setIsAuthenticated(true);
        setAuthError(null);
        
        console.log('Login successful, user:', userData); // Debug log
        return { success: true, user: userData };
      } else {
        const errorMsg = response.message || 'Login failed';
        console.error('Login failed:', errorMsg); // Debug log
        throw new Error(errorMsg);
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
      setAuthError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData) => {
    setIsLoading(true);
    setAuthError(null);
    
    try {
      // Input validation
      const requiredFields = ['username', 'email', 'password', 'first_name', 'last_name'];
      for (const field of requiredFields) {
        if (!userData[field] || typeof userData[field] !== 'string' || !userData[field].trim()) {
          throw new Error(`${field.replace('_', ' ')} is required`);
        }
      }

      // Email validation
      if (!validateEmail(userData.email)) {
        throw new Error('Please enter a valid email address');
      }

      // Password validation
      const passwordValidation = validatePassword(userData.password);
      if (!passwordValidation.valid) {
        throw new Error(passwordValidation.message);
      }

      // Username validation (basic)
      if (userData.username.length < 3 || userData.username.length > 30) {
        throw new Error('Username must be between 3 and 30 characters');
      }

      // Call API register
      const response = await apiRegister(userData);
      
      if (response.success && response.data) {
        const newUserData = {
          id: response.data.user_id,
          username: response.data.username,
          email: response.data.email,
          name: `${response.data.first_name} ${response.data.last_name}`.trim(),
          // Force newly registered users into free plan by default
          plan: 'free',
          isVerified: response.data.is_verified || false,
          joinDate: response.data.date_joined || new Date().toISOString(),
          lastLogin: new Date().toISOString()
        };

        // Store user data and token securely
        secureStorage.set(security.SECURITY_CONFIG.USER_STORAGE_KEY, newUserData, true);
        if (response.data.api_token) {
          secureStorage.set(security.SECURITY_CONFIG.TOKEN_STORAGE_KEY, response.data.api_token);
        }
        
        // Start session
        sessionManager.startSession();
        
        // Update state
        setUser(newUserData);
        setIsAuthenticated(true);
        
        return { success: true, user: newUserData, message: response.message };
      } else {
        throw new Error(response.message || 'Registration failed');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          'Registration failed';
      setAuthError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    
    try {
      // Call API logout only if a token exists (avoid 403 noise)
      const token = secureStorage.get(security.SECURITY_CONFIG.TOKEN_STORAGE_KEY);
      if (token) {
        apiLogout().catch(error => {
          console.warn('Logout API call failed:', error);
          // Continue with local logout even if API call fails
        });
      }
    } catch (error) {
      console.warn('Logout error:', error);
    } finally {
      // Clear all local data
      secureStorage.remove(security.SECURITY_CONFIG.TOKEN_STORAGE_KEY);
      secureStorage.remove(security.SECURITY_CONFIG.USER_STORAGE_KEY);
      sessionManager.endSession();
      
      // Update state
      setUser(null);
      setIsAuthenticated(false);
      setAuthError(null);
      setIsLoading(false);
    }
  };

  const updateUser = (updatedUserData) => {
    if (!isAuthenticated) return;
    
    const updatedUser = { ...user, ...updatedUserData };
    setUser(updatedUser);
    secureStorage.set(security.SECURITY_CONFIG.USER_STORAGE_KEY, updatedUser, true);
    sessionManager.updateActivity();
  };

  const clearError = () => {
    setAuthError(null);
  };

  const refreshSession = () => {
    if (isAuthenticated) {
      sessionManager.updateActivity();
    }
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    authError,
    login,
    register,
    logout,
    updateUser,
    clearError,
    refreshSession,
    
    // Computed properties
    isPremium: user?.plan && user.plan !== 'free',
    hasVerifiedEmail: user?.isVerified || false,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};