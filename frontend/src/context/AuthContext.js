import React, { createContext, useContext, useState, useEffect } from 'react';

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

  useEffect(() => {
    // Check if user is stored in localStorage (mock authentication)
    const storedUser = localStorage.getItem('trade_scan_user');
    if (storedUser) {
      const userData = JSON.parse(storedUser);
      setUser(userData);
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  const login = async (email, password) => {
    // Mock login - replace with actual API call
    setIsLoading(true);
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockUser = {
        id: 1,
        email,
        name: email.split('@')[0],
        plan: 'Bronze',
        joinDate: new Date().toISOString()
      };
      
      setUser(mockUser);
      setIsAuthenticated(true);
      localStorage.setItem('trade_scan_user', JSON.stringify(mockUser));
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email, password, name) => {
    // Mock registration - replace with actual API call
    setIsLoading(true);
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockUser = {
        id: 1,
        email,
        name,
        plan: 'Bronze',
        joinDate: new Date().toISOString()
      };
      
      setUser(mockUser);
      setIsAuthenticated(true);
      localStorage.setItem('trade_scan_user', JSON.stringify(mockUser));
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('trade_scan_user');
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};