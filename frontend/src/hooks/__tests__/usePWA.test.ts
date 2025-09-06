import { renderHook, act } from '@testing-library/react';
import { usePWA } from '../usePWA';

// Mock navigator
const mockNavigator = {
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  onLine: true,
  serviceWorker: {
    getRegistration: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  },
  storage: {
    persist: jest.fn(),
  },
};

Object.defineProperty(window, 'navigator', {
  value: mockNavigator,
  writable: true,
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

describe('usePWA', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize with correct default state', () => {
    const { result } = renderHook(() => usePWA());
    const [state] = result.current;
    
    expect(state.isInstallable).toBe(false);
    expect(state.isInstalled).toBe(false);
    expect(state.isStandalone).toBe(false);
    expect(state.isOnline).toBe(true);
    expect(state.platform).toBe('windows');
    expect(state.installPrompt).toBe(null);
  });

  it('should detect platform correctly', () => {
    // Test iOS detection
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
      writable: true,
    });
    
    const { result } = renderHook(() => usePWA());
    const [state] = result.current;
    
    expect(state.platform).toBe('ios');
  });

  it('should handle install prompt correctly', async () => {
    const mockPrompt = jest.fn().mockResolvedValue(undefined);
    const mockUserChoice = Promise.resolve({ outcome: 'accepted', platform: 'web' });
    
    const mockInstallPrompt = {
      prompt: mockPrompt,
      userChoice: mockUserChoice,
      platforms: ['web'],
    };

    const { result } = renderHook(() => usePWA());
    const [, actions] = result.current;
    
    // Simulate install prompt event
    act(() => {
      const event = new Event('beforeinstallprompt');
      Object.assign(event, mockInstallPrompt);
      window.dispatchEvent(event);
    });

    // Test install action
    await act(async () => {
      const success = await actions.install();
      expect(success).toBe(true);
    });

    expect(mockPrompt).toHaveBeenCalled();
  });

  it('should handle dismiss install correctly', () => {
    const { result } = renderHook(() => usePWA());
    const [, actions] = result.current;
    
    act(() => {
      actions.dismissInstall();
    });
    
    // Check that localStorage was called
    expect(localStorage.setItem).toHaveBeenCalledWith(
      'pwa-install-dismissed',
      expect.any(String)
    );
  });

  it('should check for updates', async () => {
    const mockUpdate = jest.fn().mockResolvedValue(undefined);
    const mockRegistration = {
      update: mockUpdate,
      waiting: null,
    };
    
    mockNavigator.serviceWorker.getRegistration.mockResolvedValue(mockRegistration);
    
    const { result } = renderHook(() => usePWA());
    const [, actions] = result.current;
    
    await act(async () => {
      const hasUpdate = await actions.checkForUpdates();
      expect(hasUpdate).toBe(false);
    });

    expect(mockUpdate).toHaveBeenCalled();
  });

  it('should request persistent storage', async () => {
    mockNavigator.storage.persist.mockResolvedValue(true);
    
    const { result } = renderHook(() => usePWA());
    const [, actions] = result.current;
    
    await act(async () => {
      const persistent = await actions.requestPersistentStorage();
      expect(persistent).toBe(true);
    });

    expect(mockNavigator.storage.persist).toHaveBeenCalled();
  });
});