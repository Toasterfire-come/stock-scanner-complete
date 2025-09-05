import React from 'react';
import { Card, CardContent } from './ui/card';
import { Download, X, Smartphone, Monitor } from 'lucide-react';
import { useInstallBanner } from '../hooks/usePWA';

const PWAInstallBanner: React.FC = () => {
  const { showBanner, hideBanner, handleInstall } = useInstallBanner({
    minVisits: 2, // Show after 2 visits
    delayAfterVisit: 3000, // Show 3 seconds after page load
    daysToHide: 30, // Hide for 30 days if dismissed
  });

  if (!showBanner) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 z-50 md:left-auto md:right-4 md:w-96">
      <Card className="shadow-lg border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 p-2 bg-blue-100 rounded-full">
              <Download className="w-5 h-5 text-blue-600" />
            </div>
            
            <div className="flex-grow min-w-0">
              <h3 className="font-semibold text-gray-900 text-sm mb-1">
                Install Stock Scanner
              </h3>
              <p className="text-xs text-gray-600 mb-3">
                Get faster access and work offline. Install our app for the best experience.
              </p>
              
              <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                <Smartphone className="w-3 h-3" />
                <span>Mobile friendly</span>
                <Monitor className="w-3 h-3 ml-2" />
                <span>Works offline</span>
              </div>
              
              <div className="flex gap-2">
                <button
                  onClick={handleInstall}
                  className="flex items-center px-3 py-1.5 bg-blue-600 text-white text-xs rounded-md hover:bg-blue-700 transition-colors"
                >
                  <Download className="w-3 h-3 mr-1" />
                  Install
                </button>
                <button
                  onClick={hideBanner}
                  className="px-3 py-1.5 text-gray-500 text-xs rounded-md hover:bg-gray-100 transition-colors"
                >
                  Not now
                </button>
              </div>
            </div>
            
            <button
              onClick={hideBanner}
              className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Close install banner"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PWAInstallBanner;