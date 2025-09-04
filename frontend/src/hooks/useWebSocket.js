/**
 * WebSocket hook for real-time data
 * Connects to Django Channels if available
 */

import { useEffect, useRef, useState, useCallback } from 'react';

const WS_URL = process.env.REACT_APP_WS_URL || 'wss://api.retailtradescanner.com/ws';

export function useWebSocket(endpoint, options = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  
  const {
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnect = true,
    reconnectInterval = 5000,
    maxReconnectAttempts = 5
  } = options;
  
  const connect = useCallback(() => {
    try {
      // Clean up existing connection
      if (wsRef.current) {
        wsRef.current.close();
      }
      
      // Get auth token
      const token = localStorage.getItem('django_auth_token');
      const wsUrl = token 
        ? `${WS_URL}/${endpoint}?token=${token}`
        : `${WS_URL}/${endpoint}`;
      
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = (event) => {
        console.log('WebSocket connected:', endpoint);
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        
        if (onOpen) {
          onOpen(event);
        }
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          
          if (onMessage) {
            onMessage(data);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };
      
      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
        
        if (onError) {
          onError(event);
        }
      };
      
      ws.onclose = (event) => {
        console.log('WebSocket closed:', endpoint);
        setIsConnected(false);
        
        if (onClose) {
          onClose(event);
        }
        
        // Attempt to reconnect if enabled
        if (reconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`Reconnecting in ${reconnectInterval}ms... (Attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };
      
      wsRef.current = ws;
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setError('Failed to establish WebSocket connection');
    }
  }, [endpoint, onMessage, onOpen, onClose, onError, reconnect, reconnectInterval, maxReconnectAttempts]);
  
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
  }, []);
  
  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const data = typeof message === 'string' ? message : JSON.stringify(message);
      wsRef.current.send(data);
      return true;
    } else {
      console.warn('WebSocket is not connected');
      return false;
    }
  }, []);
  
  useEffect(() => {
    // Only connect if endpoint is provided
    if (endpoint) {
      connect();
    }
    
    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [endpoint]); // Only reconnect if endpoint changes
  
  return {
    isConnected,
    lastMessage,
    error,
    sendMessage,
    connect,
    disconnect
  };
}

// Specific hooks for different data streams
export function useStockPriceStream(ticker) {
  return useWebSocket(`stock/${ticker}`, {
    onMessage: (data) => {
      // Handle stock price updates
      console.log('Stock price update:', data);
    },
    reconnect: true
  });
}

export function useMarketDataStream() {
  return useWebSocket('market', {
    onMessage: (data) => {
      // Handle market data updates
      console.log('Market data update:', data);
    },
    reconnect: true
  });
}

export function useNotificationStream() {
  return useWebSocket('notifications', {
    onMessage: (data) => {
      // Handle notification updates
      console.log('New notification:', data);
      
      // Show toast notification if needed
      if (data.type === 'alert') {
        // Show notification to user
      }
    },
    reconnect: true
  });
}