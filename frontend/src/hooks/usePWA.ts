import { useState, useEffect, useCallback } from 'react';

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
  prompt(): Promise<void>;
}

export interface PWAInstallState {
  isInstallable: boolean;
  isInstalled: boolean;
  isStandalone: boolean;
  isOnline: boolean;
  platform: string | null;
  installPrompt: BeforeInstallPromptEvent | null;
}

export interface PWAActions {
  install: () => Promise<boolean>;
  dismissInstall: () => void;
  checkForUpdates: () => Promise<boolean>;
  requestPersistentStorage: () => Promise<boolean>;
}

export const usePWA = (): [PWAInstallState, PWAActions] => {
  const [installPrompt, setInstallPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // Detect platform
  const getPlatform = useCallback((): string | null => {
    if (window.navigator.userAgent.includes('iPhone') || window.navigator.userAgent.includes('iPad')) {
      return 'ios';
    }
    if (window.navigator.userAgent.includes('Android')) {
      return 'android';
    }
    if (window.navigator.userAgent.includes('Windows')) {
      return 'windows';
    }
    if (window.navigator.userAgent.includes('Mac')) {
      return 'macos';
    }
    return 'unknown';
  }, []);

  // Check if app is in standalone mode
  const isStandalone = useCallback((): boolean => {
    return (
      window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as any).standalone === true ||
      document.referrer.includes('android-app://')
    );
  }, []);

  // Install PWA
  const install = useCallback(async (): Promise<boolean> => {
    if (!installPrompt) {
      console.warn('PWA: Install prompt not available');
      return false;
    }

    try {
      // Show the install prompt
      await installPrompt.prompt();
      
      // Wait for user choice
      const choiceResult = await installPrompt.userChoice;
      
      if (choiceResult.outcome === 'accepted') {
        console.log('PWA: User accepted install prompt');
        setIsInstalled(true);
        setIsInstallable(false);
        setInstallPrompt(null);
        
        // Store install date
        localStorage.setItem('pwa-installed-date', new Date().toISOString());
        
        return true;
      } else {
        console.log('PWA: User dismissed install prompt');
        // Don't show install prompt again for a while
        localStorage.setItem('pwa-install-dismissed', Date.now().toString());
        setIsInstallable(false);
        setInstallPrompt(null);
        return false;
      }
    } catch (error) {
      console.error('PWA: Error during installation:', error);
      return false;
    }
  }, [installPrompt]);

  // Dismiss install prompt
  const dismissInstall = useCallback(() => {
    setIsInstallable(false);
    setInstallPrompt(null);
    localStorage.setItem('pwa-install-dismissed', Date.now().toString());
  }, []);

  // Check for service worker updates
  const checkForUpdates = useCallback(async (): Promise<boolean> => {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.getRegistration();
        if (registration) {
          await registration.update();
          
          // Check if there's a waiting service worker
          if (registration.waiting) {
            setHasUpdate(true);
            return true;
          }
        }
      } catch (error) {
        console.error('PWA: Error checking for updates:', error);
      }
    }
    return false;
  }, []);

  // Request persistent storage
  const requestPersistentStorage = useCallback(async (): Promise<boolean> => {
    if ('storage' in navigator && 'persist' in navigator.storage) {
      try {
        const persistent = await navigator.storage.persist();
        console.log(`PWA: Persistent storage ${persistent ? 'granted' : 'denied'}`);
        return persistent;
      } catch (error) {
        console.error('PWA: Error requesting persistent storage:', error);
      }
    }
    return false;
  }, []);

  // Setup event listeners
  useEffect(() => {
    // Before install prompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      const promptEvent = e as BeforeInstallPromptEvent;
      
      // Check if install was recently dismissed
      const dismissedTime = localStorage.getItem('pwa-install-dismissed');
      if (dismissedTime) {
        const timeSinceDismissed = Date.now() - parseInt(dismissedTime, 10);
        // Don't show again for 7 days
        if (timeSinceDismissed < 7 * 24 * 60 * 60 * 1000) {
          return;
        }
      }
      
      setInstallPrompt(promptEvent);
      setIsInstallable(true);
      console.log('PWA: Install prompt available');
    };

    // App installed event
    const handleAppInstalled = () => {
      console.log('PWA: App installed successfully');
      setIsInstalled(true);
      setIsInstallable(false);
      setInstallPrompt(null);
      localStorage.setItem('pwa-installed-date', new Date().toISOString());
    };

    // Online/offline events
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    // Service worker update events
    const handleServiceWorkerUpdate = () => {
      console.log('PWA: Service worker updated');
      setHasUpdate(true);
    };

    // Add event listeners
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Service worker events
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('controllerchange', handleServiceWorkerUpdate);
    }

    // Check if already installed
    setIsInstalled(isStandalone());

    // Request persistent storage on first load
    requestPersistentStorage();

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.removeEventListener('controllerchange', handleServiceWorkerUpdate);
      }
    };
  }, [isStandalone, requestPersistentStorage]);

  // Periodic update checks
  useEffect(() => {
    const interval = setInterval(() => {
      checkForUpdates();
    }, 10 * 60 * 1000); // Check every 10 minutes

    return () => clearInterval(interval);
  }, [checkForUpdates]);

  const state: PWAInstallState = {
    isInstallable,
    isInstalled,
    isStandalone: isStandalone(),
    isOnline,
    platform: getPlatform(),
    installPrompt,
  };

  const actions: PWAActions = {
    install,
    dismissInstall,
    checkForUpdates,
    requestPersistentStorage,
  };

  return [state, actions];
};