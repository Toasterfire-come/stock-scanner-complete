import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin, registerUser as apiRegister, logout as apiLogout } from '../api/client';
import security, { secureStorage, validateEmail, validatePassword, sessionManager } from '../lib/security';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  // Initialize authentication state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Check for stored user data and token
        const storedUser = secureStorage.get(security.SECURITY_CONFIG.USER_STORAGE_KEY);
        const storedToken = secureStorage.get(security.SECURITY_CONFIG.TOKEN_STORAGE_KEY);
        
        if (storedUser && storedToken && sessionManager.isSessionValid()) {
          setUser(storedUser);
          setIsAuthenticated(true);
          sessionManager.updateActivity();
        } else {
          // Clear invalid session data
          await logout();
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
      
      if (response.success && response.data) {
        const userData = {
          id: response.data.user_id,
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
        secureStorage.set(security.SECURITY_CONFIG.TOKEN_STORAGE_KEY, response.data.api_token);
        
        // Start session
        sessionManager.startSession();
        
        // Update state
        setUser(userData);
        setIsAuthenticated(true);
        
        return { success: true, user: userData };
      } else {
        throw new Error(response.message || 'Login failed');
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
          plan: response.data.plan || 'free',
          isVerified: response.data.is_verified || false,
          joinDate: response.data.date_joined || new Date().toISOString(),
          lastLogin: new Date().toISOString()
        };

        // Store user data and token securely
        secureStorage.set(security.SECURITY_CONFIG.USER_STORAGE_KEY, newUserData, true);
        secureStorage.set(security.SECURITY_CONFIG.TOKEN_STORAGE_KEY, response.data.api_token);
        
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
      // Call API logout (don't wait for response)
      apiLogout().catch(error => {
        console.warn('Logout API call failed:', error);
        // Continue with local logout even if API call fails
      });
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