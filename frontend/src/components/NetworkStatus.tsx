import React, { useState, useEffect } from 'react';
import { WifiOff, CheckCircle, AlertCircle, Wifi } from 'lucide-react';
import { usePWA } from '../hooks/usePWA';

const NetworkStatus: React.FC = () => {
  const [pwaState] = usePWA();
  const [showStatus, setShowStatus] = useState(false);
  const [wasOffline, setWasOffline] = useState(false);

  useEffect(() => {
    // Show status when going offline
    if (!pwaState.isOnline && !wasOffline) {
      setShowStatus(true);
      setWasOffline(true);
    }
    
    // Show "back online" message briefly when reconnecting
    if (pwaState.isOnline && wasOffline) {
      setShowStatus(true);
      const timer = setTimeout(() => {
        setShowStatus(false);
        setWasOffline(false);
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [pwaState.isOnline, wasOffline]);

  // Don't show anything if online and never was offline
  if (pwaState.isOnline && !wasOffline) {
    return null;
  }

  // Don't show if status shouldn't be visible
  if (!showStatus) {
    return null;
  }

  const isOffline = !pwaState.isOnline;

  return (
    <div
      className={`fixed top-0 left-0 right-0 z-50 p-3 text-white text-center transition-transform duration-300 ${
        isOffline 
          ? 'bg-red-600 transform translate-y-0' 
          : 'bg-green-600 transform translate-y-0'
      }`}
    >
      <div className="max-w-4xl mx-auto flex items-center justify-center space-x-2">
        {isOffline ? (
          <>
            <WifiOff className="w-4 h-4" />
            <span className="text-sm font-medium">
              You're offline - some features may be limited
            </span>
          </>
        ) : (
          <>
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm font-medium">
              Back online! All features available
            </span>
          </>
        )}
      </div>
    </div>
  );
};

// Connection speed indicator component
export const ConnectionSpeed: React.FC = () => {
  const [connectionSpeed, setConnectionSpeed] = useState<string>('unknown');
  const [showSpeed, setShowSpeed] = useState(false);

  useEffect(() => {
    // Check connection speed using the Network Information API
    const checkConnectionSpeed = () => {
      if ('connection' in navigator) {
        const connection = (navigator as any).connection;
        if (connection) {
          const effectiveType = connection.effectiveType;
          setConnectionSpeed(effectiveType);
          
          // Show speed indicator for slow connections
          if (['slow-2g', '2g', '3g'].includes(effectiveType)) {
            setShowSpeed(true);
          }
        }
      }
    };

    checkConnectionSpeed();

    // Listen for connection changes
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      connection?.addEventListener('change', checkConnectionSpeed);
      
      return () => {
        connection?.removeEventListener('change', checkConnectionSpeed);
      };
    }
    
    return;
  }, []);

  if (!showSpeed || connectionSpeed === 'unknown') {
    return null;
  }

  const getSpeedInfo = (speed: string) => {
    switch (speed) {
      case 'slow-2g':
        return { label: 'Very Slow Connection', color: 'bg-red-500', icon: AlertCircle };
      case '2g':
        return { label: 'Slow Connection', color: 'bg-orange-500', icon: AlertCircle };
      case '3g':
        return { label: 'Moderate Connection', color: 'bg-yellow-500', icon: Wifi };
      default:
        return { label: 'Good Connection', color: 'bg-green-500', icon: Wifi };
    }
  };

  const speedInfo = getSpeedInfo(connectionSpeed);
  const IconComponent = speedInfo.icon;

  return (
    <div className={`fixed top-12 right-4 ${speedInfo.color} text-white px-3 py-2 rounded-lg shadow-lg z-40 text-xs flex items-center space-x-2`}>
      <IconComponent className="w-3 h-3" />
      <span>{speedInfo.label}</span>
      <button
        onClick={() => setShowSpeed(false)}
        className="ml-2 text-white/80 hover:text-white"
      >
        ×
      </button>
    </div>
  );
};

export default NetworkStatus;