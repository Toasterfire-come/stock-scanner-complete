import { authService } from '../authService';

// Mock fetch
global.fetch = jest.fn();

// Mock jwt-decode
jest.mock('jwt-decode', () => ({
  jwtDecode: jest.fn(() => ({
    exp: Math.floor(Date.now() / 1000) + 3600 // 1 hour from now
  }))
}));

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    global.fetch.mockClear();
  });

  describe('Token Management', () => {
    it('stores and retrieves tokens correctly', () => {
      const accessToken = 'access-token';
      const refreshToken = 'refresh-token';

      authService.setTokens(accessToken, refreshToken);

      expect(authService.getToken()).toBe(accessToken);
      expect(authService.getRefreshToken()).toBe(refreshToken);
    });

    it('clears tokens correctly', () => {
      authService.setTokens('access-token', 'refresh-token');
      authService.clearTokens();

      expect(authService.getToken()).toBeNull();
      expect(authService.getRefreshToken()).toBeNull();
    });

    it('validates tokens correctly', () => {
      // Mock jwt-decode to return a valid token
      const { jwtDecode } = require('jwt-decode');
      jwtDecode.mockReturnValue({
        exp: Math.floor(Date.now() / 1000) + 3600 // 1 hour from now
      });

      expect(authService.isTokenValid('valid-token')).toBe(true);

      // Mock expired token
      jwtDecode.mockReturnValue({
        exp: Math.floor(Date.now() / 1000) - 3600 // 1 hour ago
      });

      expect(authService.isTokenValid('expired-token')).toBe(false);
    });
  });

  describe('Authentication', () => {
    it('logs in successfully with valid credentials', async () => {
      const credentials = {
        username: 'testuser',
        password: 'password123'
      };

      const mockResponse = {
        success: true,
        data: {
          api_token: 'access-token',
          refresh_token: 'refresh-token',
          ...global.testUtils.createMockUser()
        }
      };

      global.fetch.mockResolvedValue({
        json: () => Promise.resolve(mockResponse)
      });

      const result = await authService.login(credentials);

      expect(result).toEqual(mockResponse.data);
      expect(localStorage.getItem('rts_token')).toBe('access-token');
      expect(localStorage.getItem('rts_refresh_token')).toBe('refresh-token');
    });

    it('throws error for invalid credentials', async () => {
      const credentials = {
        username: 'testuser',
        password: 'wrongpassword'
      };

      const mockResponse = {
        success: false,
        error: 'Invalid credentials'
      };

      global.fetch.mockResolvedValue({
        json: () => Promise.resolve(mockResponse)
      });

      await expect(authService.login(credentials)).rejects.toThrow('Invalid credentials');
    });

    it('validates and sanitizes login inputs', async () => {
      const credentials = {
        username: '  TestUser  ',
        password: 'password123'
      };

      const mockResponse = {
        success: true,
        data: {
          api_token: 'access-token',
          ...global.testUtils.createMockUser()
        }
      };

      global.fetch.mockResolvedValue({
        json: () => Promise.resolve(mockResponse)
      });

      await authService.login(credentials);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({
            username: 'testuser', // Should be trimmed and lowercased
            password: 'password123'
          })
        })
      );
    });
  });

  describe('Registration', () => {
    it('registers user successfully with valid data', async () => {
      const userData = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'Password123!',
        firstName: 'New',
        lastName: 'User'
      };

      const mockResponse = {
        success: true,
        data: {
          api_token: 'access-token',
          refresh_token: 'refresh-token',
          ...global.testUtils.createMockUser()
        }
      };

      global.fetch.mockResolvedValue({
        json: () => Promise.resolve(mockResponse)
      });

      const result = await authService.register(userData);

      expect(result).toEqual(mockResponse.data);
      expect(localStorage.getItem('rts_token')).toBe('access-token');
    });

    it('validates email format', async () => {
      const userData = {
        username: 'newuser',
        email: 'invalid-email',
        password: 'Password123!',
        firstName: 'New',
        lastName: 'User'
      };

      await expect(authService.register(userData)).rejects.toThrow('Please enter a valid email address');
    });

    it('validates password strength', async () => {
      const userData = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'weak',
        firstName: 'New',
        lastName: 'User'
      };

      await expect(authService.register(userData)).rejects.toThrow('Password must be at least 8 characters long');
    });

    it('validates required fields', async () => {
      const userData = {
        username: '',
        email: 'new@example.com',
        password: 'Password123!',
        firstName: 'New',
        lastName: 'User'
      };

      await expect(authService.register(userData)).rejects.toThrow('username is required');
    });
  });

  describe('Rate Limiting', () => {
    it('tracks login attempts', () => {
      expect(() => authService.checkRateLimit('login')).not.toThrow();
      expect(() => authService.checkRateLimit('login')).not.toThrow();
      expect(() => authService.checkRateLimit('login')).not.toThrow();
      expect(() => authService.checkRateLimit('login')).not.toThrow();
      expect(() => authService.checkRateLimit('login')).not.toThrow();
      
      // 6th attempt should throw
      expect(() => authService.checkRateLimit('login')).toThrow('Too many attempts');
    });

    it('clears rate limit after successful authentication', () => {
      // Make 5 attempts
      for (let i = 0; i < 5; i++) {
        authService.checkRateLimit('login');
      }

      // Clear rate limit
      authService.clearRateLimit('login');

      // Should be able to make attempts again
      expect(() => authService.checkRateLimit('login')).not.toThrow();
    });
  });

  describe('Logout', () => {
    it('clears all stored data on logout', () => {
      authService.setTokens('access-token', 'refresh-token');
      localStorage.setItem('user_data', JSON.stringify(global.testUtils.createMockUser()));

      authService.logout();

      expect(authService.getToken()).toBeNull();
      expect(authService.getRefreshToken()).toBeNull();
      expect(localStorage.getItem('user_data')).toBeNull();
    });
  });

  describe('Authentication Status', () => {
    it('returns true when user is authenticated', () => {
      const { jwtDecode } = require('jwt-decode');
      jwtDecode.mockReturnValue({
        exp: Math.floor(Date.now() / 1000) + 3600 // 1 hour from now
      });

      authService.setTokens('valid-token');
      localStorage.setItem('user_data', JSON.stringify(global.testUtils.createMockUser()));

      expect(authService.isAuthenticated()).toBe(true);
    });

    it('returns false when user is not authenticated', () => {
      authService.clearTokens();
      expect(authService.isAuthenticated()).toBe(false);
    });
  });
});