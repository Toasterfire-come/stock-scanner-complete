// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({}),
  })
);

// Mock navigator
Object.defineProperty(navigator, 'onLine', {
  writable: true,
  value: true,
});

Object.defineProperty(navigator, 'share', {
  writable: true,
  value: jest.fn(() => Promise.resolve()),
});

Object.defineProperty(navigator, 'clipboard', {
  writable: true,
  value: {
    writeText: jest.fn(() => Promise.resolve()),
    readText: jest.fn(() => Promise.resolve('')),
  },
});

// Mock Notification
global.Notification = class Notification {
  constructor(title, options) {
    this.title = title;
    this.options = options;
  }
  static permission = 'default';
  static requestPermission = jest.fn(() => Promise.resolve('granted'));
};

// Mock serviceWorker
Object.defineProperty(navigator, 'serviceWorker', {
  writable: true,
  value: {
    register: jest.fn(() => Promise.resolve({
      installing: null,
      waiting: null,
      active: null,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    })),
    getRegistration: jest.fn(() => Promise.resolve(null)),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  },
});

// Suppress console warnings during tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});

// Global test utilities
global.testUtils = {
  createMockUser: () => ({
    user_id: 1,
    username: 'testuser',
    email: 'test@example.com',
    first_name: 'Test',
    last_name: 'User',
    plan: 'free',
    api_token: 'mock-token',
    is_premium: false,
    limits: { monthly: 15, daily: 15 },
    usage: { monthly_calls: 0, daily_calls: 0 },
    subscription: { active: false, end_date: null, trial_used: false },
  }),
  
  createMockStock: () => ({
    ticker: 'AAPL',
    symbol: 'AAPL',
    company_name: 'Apple Inc.',
    name: 'Apple Inc.',
    exchange: 'NASDAQ',
    current_price: 150.00,
    price_change_today: 2.50,
    change_percent: 1.69,
    volume: 1000000,
    volume_today: 1000000,
    formatted_price: '$150.00',
    formatted_change: '+$2.50 (1.69%)',
    formatted_volume: '1.0M',
    last_updated: new Date().toISOString(),
    created_at: new Date().toISOString(),
    is_gaining: true,
    is_losing: false,
  }),
  
  mockApiResponse: (data, success = true) => ({
    success,
    data,
    timestamp: new Date().toISOString(),
  }),
};