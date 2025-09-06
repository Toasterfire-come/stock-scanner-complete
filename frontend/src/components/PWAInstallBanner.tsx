import React, { useState, useEffect } from 'react';
import { X, Download, Smartphone, Monitor } from 'lucide-react';
import { usePWA } from '../hooks/usePWA';

const PWAInstallBanner: React.FC = () => {
  const [pwaState, pwaActions] = usePWA();
  const [isVisible, setIsVisible] = useState(false);
  const [isIOS, setIsIOS] = useState(false);

  useEffect(() => {
    // Detect iOS
    const ios = /iPad|iPhone|iPod/.test(navigator.userAgent);
    setIsIOS(ios);

    // Show banner if installable and not recently dismissed
    if (pwaState.isInstallable && !pwaState.isInstalled) {
      // Delay showing the banner to avoid interrupting user flow
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, 3000);

      return () => clearTimeout(timer);
    }
    
    return undefined;
  }, [pwaState.isInstallable, pwaState.isInstalled]);

  const handleInstall = async () => {
    const success = await pwaActions.install();
    if (success) {
      setIsVisible(false);
    }
  };

  const handleDismiss = () => {
    setIsVisible(false);
    pwaActions.dismissInstall();
  };

  // Don't show if not installable, already installed, or in standalone mode
  if (!isVisible || pwaState.isInstalled || pwaState.isStandalone) {
    return null;
  }

  // iOS install instructions
  if (isIOS) {
    return (
      <div className="fixed bottom-0 left-0 right-0 bg-blue-600 text-white p-4 shadow-lg z-50 animate-slide-up">
        <div className="max-w-4xl mx-auto flex items-start justify-between">
          <div className="flex-1 pr-4">
            <div className="flex items-center mb-2">
              <Smartphone className="w-5 h-5 mr-2" />
              <h3 className="font-semibold">Install Stock Scanner</h3>
            </div>
            <p className="text-sm text-blue-100 mb-3">
              Add to your home screen for the best experience:
            </p>
            <ol className="text-xs text-blue-100 space-y-1">
              <li>1. Tap the share button <span className="inline-block w-4 h-4 bg-blue-500 rounded text-center">⬆</span></li>
              <li>2. Scroll down and tap "Add to Home Screen"</li>
              <li>3. Tap "Add" to install</li>
            </ol>
          </div>
          <button
            onClick={handleDismiss}
            className="flex-shrink-0 p-1 text-blue-200 hover:text-white"
            aria-label="Dismiss install banner"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>
    );
  }

  // Standard install banner
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-2xl z-50 animate-slide-up">
      <div className="max-w-4xl mx-auto p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="hidden sm:block">
              <div className="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center">
                <Monitor className="w-6 h-6" />
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-lg">Install Stock Scanner</h3>
              <p className="text-blue-100 text-sm">
                Get the full app experience with offline access and faster loading
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleInstall}
              className="bg-white text-blue-600 px-4 sm:px-6 py-2 rounded-lg font-medium hover:bg-blue-50 transition-colors flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span className="hidden sm:inline">Install App</span>
              <span className="sm:hidden">Install</span>
            </button>
            <button
              onClick={handleDismiss}
              className="p-2 text-blue-200 hover:text-white transition-colors"
              aria-label="Dismiss install banner"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PWAInstallBanner;