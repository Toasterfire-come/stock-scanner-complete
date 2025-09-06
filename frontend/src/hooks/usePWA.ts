import { useState, useEffect, useCallback } from 'react';

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
  prompt(): Promise<void>;
}

interface PWAInstallState {
  isInstallable: boolean;
  isInstalled: boolean;
  isStandalone: boolean;
  installPrompt: BeforeInstallPromptEvent | null;
  isOnline: boolean;
  updateAvailable: boolean;
}

export const usePWA = () => {
  const [state, setState] = useState<PWAInstallState>({
    isInstallable: false,
    isInstalled: false,
    isStandalone: false,
    installPrompt: null,
    isOnline: navigator.onLine,
    updateAvailable: false,
  });

  // Check if app is running in standalone mode
  useEffect(() => {
    const checkStandaloneMode = () => {
      const isStandalone = 
        window.matchMedia('(display-mode: standalone)').matches ||
        (window.navigator as any).standalone === true ||
        document.referrer.includes('android-app://');
      
      setState(prev => ({ ...prev, isStandalone }));
    };

    checkStandaloneMode();
    
    // Listen for display mode changes
    window.matchMedia('(display-mode: standalone)').addEventListener('change', checkStandaloneMode);
    
    return () => {
      window.matchMedia('(display-mode: standalone)').removeEventListener('change', checkStandaloneMode);
    };
  }, []);

  // Handle beforeinstallprompt event
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      const installEvent = e as BeforeInstallPromptEvent;
      
      setState(prev => ({
        ...prev,
        isInstallable: true,
        installPrompt: installEvent,
      }));
    };

    const handleAppInstalled = () => {
      setState(prev => ({
        ...prev,
        isInstalled: true,
        isInstallable: false,
        installPrompt: null,
      }));
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  // Handle online/offline status
  useEffect(() => {
    const handleOnline = () => setState(prev => ({ ...prev, isOnline: true }));
    const handleOffline = () => setState(prev => ({ ...prev, isOnline: false }));

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Handle service worker updates
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      const handleControllerChange = () => {
        setState(prev => ({ ...prev, updateAvailable: true }));
      };

      navigator.serviceWorker.addEventListener('controllerchange', handleControllerChange);
      
      return () => {
        navigator.serviceWorker.removeEventListener('controllerchange', handleControllerChange);
      };
    }
  }, []);

  // Install the PWA
  const installPWA = useCallback(async () => {
    if (!state.installPrompt) {
      throw new Error('Install prompt not available');
    }

    try {
      await state.installPrompt.prompt();
      const choice = await state.installPrompt.userChoice;
      
      if (choice.outcome === 'accepted') {
        setState(prev => ({
          ...prev,
          isInstalled: true,
          isInstallable: false,
          installPrompt: null,
        }));
        return true;
      }
      return false;
    } catch (error) {
      console.error('PWA install failed:', error);
      throw error;
    }
  }, [state.installPrompt]);

  // Update the app
  const updateApp = useCallback(async () => {
    if ('serviceWorker' in navigator) {
      const registration = await navigator.serviceWorker.getRegistration();
      if (registration?.waiting) {
        registration.waiting.postMessage({ type: 'SKIP_WAITING' });
        window.location.reload();
      }
    }
  }, []);

  // Share API
  const shareContent = useCallback(async (data: {
    title?: string;
    text?: string;
    url?: string;
  }) => {
    if (navigator.share) {
      try {
        await navigator.share(data);
        return true;
      } catch (error) {
        if ((error as Error).name !== 'AbortError') {
          console.error('Share failed:', error);
        }
        return false;
      }
    }
    
    // Fallback to clipboard
    if (navigator.clipboard && data.url) {
      try {
        await navigator.clipboard.writeText(data.url);
        return true;
      } catch (error) {
        console.error('Clipboard write failed:', error);
        return false;
      }
    }
    
    return false;
  }, []);

  // Check if device supports PWA features
  const getPWACapabilities = useCallback(() => {
    return {
      canInstall: 'beforeinstallprompt' in window,
      hasServiceWorker: 'serviceWorker' in navigator,
      hasNotifications: 'Notification' in window,
      hasShare: 'share' in navigator,
      hasClipboard: 'clipboard' in navigator,
      hasGeolocation: 'geolocation' in navigator,
      hasCamera: 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices,
      hasVibration: 'vibrate' in navigator,
      hasBatteryAPI: 'getBattery' in navigator,
      hasNetworkInformation: 'connection' in navigator,
    };
  }, []);

  return {
    ...state,
    installPWA,
    updateApp,
    shareContent,
    getPWACapabilities,
    canInstall: state.isInstallable && !state.isInstalled && !state.isStandalone,
  };
};

// Hook for PWA installation banner
export const useInstallBanner = (options: {
  minVisits?: number;
  delayAfterVisit?: number;
  daysToHide?: number;
} = {}) => {
  const { minVisits = 3, delayAfterVisit = 2000, daysToHide = 7 } = options;
  const { canInstall, installPWA } = usePWA();
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    if (!canInstall) return;

    const visits = parseInt(localStorage.getItem('pwa_visits') || '0') + 1;
    const lastHidden = localStorage.getItem('pwa_banner_hidden');
    const hideUntil = lastHidden ? new Date(lastHidden) : null;
    
    localStorage.setItem('pwa_visits', visits.toString());

    // Check if banner should be shown
    const shouldShow = visits >= minVisits && 
                      (!hideUntil || hideUntil < new Date());

    if (shouldShow) {
      const timer = setTimeout(() => {
        setShowBanner(true);
      }, delayAfterVisit);

      return () => clearTimeout(timer);
    }
  }, [canInstall, minVisits, delayAfterVisit]);

  const hideBanner = useCallback(() => {
    setShowBanner(false);
    const hideUntil = new Date();
    hideUntil.setDate(hideUntil.getDate() + daysToHide);
    localStorage.setItem('pwa_banner_hidden', hideUntil.toISOString());
  }, [daysToHide]);

  const handleInstall = useCallback(async () => {
    try {
      await installPWA();
      setShowBanner(false);
    } catch (error) {
      console.error('Installation failed:', error);
    }
  }, [installPWA]);

  return {
    showBanner: showBanner && canInstall,
    hideBanner,
    handleInstall,
  };
};

// Hook for network status
export const useNetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [networkInfo, setNetworkInfo] = useState<{
    effectiveType?: string;
    downlink?: number;
    rtt?: number;
    saveData?: boolean;
  }>({});

  useEffect(() => {
    const updateOnlineStatus = () => setIsOnline(navigator.onLine);
    
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);

    // Network Information API (experimental)
    const connection = (navigator as any).connection || 
                      (navigator as any).mozConnection || 
                      (navigator as any).webkitConnection;

    if (connection) {
      const updateNetworkInfo = () => {
        setNetworkInfo({
          effectiveType: connection.effectiveType,
          downlink: connection.downlink,
          rtt: connection.rtt,
          saveData: connection.saveData,
        });
      };

      updateNetworkInfo();
      connection.addEventListener('change', updateNetworkInfo);

      return () => {
        window.removeEventListener('online', updateOnlineStatus);
        window.removeEventListener('offline', updateOnlineStatus);
        connection.removeEventListener('change', updateNetworkInfo);
      };
    }

    return () => {
      window.removeEventListener('online', updateOnlineStatus);
      window.removeEventListener('offline', updateOnlineStatus);
    };
  }, []);

  return {
    isOnline,
    ...networkInfo,
    isSlowConnection: networkInfo.effectiveType === '2g' || networkInfo.effectiveType === 'slow-2g',
    isSaveDataEnabled: networkInfo.saveData,
  };
};

// Hook for app notifications
export const useNotifications = () => {
  const [permission, setPermission] = useState<NotificationPermission>(
    'Notification' in window ? Notification.permission : 'denied'
  );

  const requestPermission = useCallback(async () => {
    if (!('Notification' in window)) {
      throw new Error('Notifications not supported');
    }

    const result = await Notification.requestPermission();
    setPermission(result);
    return result;
  }, []);

  const showNotification = useCallback(async (
    title: string,
    options?: NotificationOptions
  ) => {
    if (permission !== 'granted') {
      const newPermission = await requestPermission();
      if (newPermission !== 'granted') {
        throw new Error('Notification permission denied');
      }
    }

    const notification = new Notification(title, {
      icon: '/logo192.png',
      badge: '/logo192.png',
      ...options,
    });

    return notification;
  }, [permission, requestPermission]);

  return {
    permission,
    requestPermission,
    showNotification,
    isSupported: 'Notification' in window,
  };
};