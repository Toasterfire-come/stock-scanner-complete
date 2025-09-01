import React, { createContext, useContext, useState, useEffect } from "react";
import { getProfile, login as apiLogin, logout as apiLogout } from "../api/client";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if user is logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("rts_token");
      
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const profileResponse = await getProfile();
        if (profileResponse.success) {
          setUser(profileResponse.data);
          setIsAuthenticated(true);
        } else {
          localStorage.removeItem("rts_token");
        }
      } catch (error) {
        localStorage.removeItem("rts_token");
        console.error("Auth check failed:", error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (username, password) => {
    try {
      const result = await apiLogin(username, password);
      
      if (result.success && result.token) {
        setUser(result.data);
        setIsAuthenticated(true);
        localStorage.setItem("rts_token", result.token);
        return { success: true };
      } else {
        return { 
          success: false, 
          message: result.message || "Login failed" 
        };
      }
    } catch (error) {
      return { 
        success: false, 
        message: "An error occurred during login" 
      };
    }
  };

  const logout = async () => {
    try {
      await apiLogout();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
      localStorage.removeItem("rts_token");
    }
  };

  const updateUser = (userData) => {
    setUser(prev => ({ ...prev, ...userData }));
  };

  const value = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};