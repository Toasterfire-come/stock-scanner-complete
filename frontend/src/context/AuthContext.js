import React, { createContext, useContext, useState, useEffect } from 'react';
import * as djangoAPI from '../api/django-client';

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
  const [subscription, setSubscription] = useState(null);

  useEffect(() => {
    // Check if user is authenticated with Django backend
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Check if we have auth tokens
      if (djangoAPI.isAuthenticated()) {
        // Try to get user profile
        const profileResponse = await djangoAPI.getUserProfile();
        if (profileResponse.success && profileResponse.data) {
          setUser(profileResponse.data);
          setIsAuthenticated(true);
          
          // Get subscription details
          try {
            const planResponse = await djangoAPI.getCurrentPlan();
            if (planResponse.success) {
              setSubscription(planResponse.data);
            }
          } catch (error) {
            console.error('Failed to fetch subscription details:', error);
          }
        }
      }
    } catch (error) {
      // If profile fetch fails, clear auth
      djangoAPI.clearAuthData();
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username, password) => {
    setIsLoading(true);
    try {
      const response = await djangoAPI.login(username, password);
      
      if (response.success) {
        setUser(response.data);
        setIsAuthenticated(true);
        
        // Fetch subscription details after login
        try {
          const planResponse = await djangoAPI.getCurrentPlan();
          if (planResponse.success) {
            setSubscription(planResponse.data);
          }
        } catch (error) {
          console.error('Failed to fetch subscription after login:', error);
        }
        
        return { success: true };
      } else {
        return { 
          success: false, 
          error: response.message || 'Login failed' 
        };
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.message || 'An error occurred during login' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData) => {
    setIsLoading(true);
    try {
      const response = await djangoAPI.register(userData);
      
      if (response.success) {
        // Auto-login after successful registration
        const loginResponse = await login(userData.username, userData.password);
        return loginResponse;
      } else {
        return { 
          success: false, 
          error: response.message || 'Registration failed' 
        };
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.message || 'An error occurred during registration' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await djangoAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
      setSubscription(null);
      setIsLoading(false);
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await djangoAPI.updateUserProfile(profileData);
      if (response.success) {
        setUser(response.data);
        return { success: true };
      }
      return { 
        success: false, 
        error: response.message || 'Failed to update profile' 
      };
    } catch (error) {
      return { 
        success: false, 
        error: error.message || 'An error occurred' 
      };
    }
  };

  const changePassword = async (currentPassword, newPassword, confirmPassword) => {
    try {
      const response = await djangoAPI.changePassword(
        currentPassword, 
        newPassword, 
        confirmPassword
      );
      return response;
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Failed to change password' 
      };
    }
  };

  const updateSubscription = async (planType, billingCycle) => {
    try {
      const response = await djangoAPI.changePlan(planType, billingCycle);
      if (response.success) {
        setSubscription(response.data);
        
        // Update user's premium status
        setUser(prev => ({
          ...prev,
          is_premium: response.data.is_premium
        }));
        
        return { success: true };
      }
      return { 
        success: false, 
        error: response.message || 'Failed to update subscription' 
      };
    } catch (error) {
      return { 
        success: false, 
        error: error.message || 'An error occurred' 
      };
    }
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    subscription,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    updateSubscription,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;