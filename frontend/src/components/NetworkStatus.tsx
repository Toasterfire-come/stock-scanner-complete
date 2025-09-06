import React from 'react';
import { useNetworkStatus } from '../hooks/usePWA';
import { WifiOff, Wifi, Signal } from 'lucide-react';

const NetworkStatus: React.FC = () => {
  const { isOnline, effectiveType, isSlowConnection, isSaveDataEnabled } = useNetworkStatus();

  if (isOnline) {
    // Only show network info if connection is slow or save data is enabled
    if (!isSlowConnection && !isSaveDataEnabled) {
      return null;
    }

    return (
      <div className="fixed top-16 right-4 z-40">
        <div className="flex items-center gap-2 px-3 py-2 bg-yellow-100 border border-yellow-300 rounded-md shadow-sm">
          <Signal className="w-4 h-4 text-yellow-600" />
          <div className="text-sm">
            {isSlowConnection && (
              <span className="text-yellow-800 font-medium">Slow connection</span>
            )}
            {isSaveDataEnabled && (
              <span className="text-yellow-700 ml-2">Data saver on</span>
            )}
            {effectiveType && (
              <span className="text-yellow-600 text-xs ml-2">({effectiveType})</span>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed top-16 right-4 z-40">
      <div className="flex items-center gap-2 px-3 py-2 bg-red-100 border border-red-300 rounded-md shadow-sm">
        <WifiOff className="w-4 h-4 text-red-600" />
        <div className="text-sm">
          <span className="text-red-800 font-medium">No internet connection</span>
          <div className="text-red-600 text-xs">Using cached data</div>
        </div>
      </div>
    </div>
  );
};

export default NetworkStatus;