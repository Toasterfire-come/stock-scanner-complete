import React, { createContext, useContext, useState, useEffect } from 'react';
import { pingHealth } from '../api/client';

const BackendStatusContext = createContext();

export const useBackendStatus = () => {
  const context = useContext(BackendStatusContext);
  if (!context) {
    throw new Error('useBackendStatus must be used within a BackendStatusProvider');
  }
  return context;
};

export const BackendStatusProvider = ({ children }) => {
  const [isBackendUp, setIsBackendUp] = useState(true);
  const [lastCheck, setLastCheck] = useState(null);

  const checkBackendStatus = async () => {
    try {
      await pingHealth();
      setIsBackendUp(true);
      setLastCheck(new Date());
    } catch (error) {
      console.warn('Backend health check failed:', error);
      setIsBackendUp(false);
      setLastCheck(new Date());
    }
  };

  useEffect(() => {
    // Initial check
    checkBackendStatus();

    // Check every 30 seconds
    const interval = setInterval(checkBackendStatus, 30000);

    return () => clearInterval(interval);
  }, []);

  const value = {
    isBackendUp,
    lastCheck,
    checkBackendStatus
  };

  return (
    <BackendStatusContext.Provider value={value}>
      {children}
    </BackendStatusContext.Provider>
  );
};