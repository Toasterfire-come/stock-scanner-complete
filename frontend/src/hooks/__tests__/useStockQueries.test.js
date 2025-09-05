import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useStocks, useStockDetail, useStockQuote } from '../useStockQueries';
import { stockAPI } from '../../services/stockAPI';

// Mock the stockAPI
jest.mock('../../services/stockAPI');

// Create a test query client
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
    mutations: {
      retry: false,
    },
  },
});

// Test wrapper with QueryClient
const createWrapper = () => {
  const queryClient = createTestQueryClient();
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useStockQueries', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('useStocks', () => {
    it('fetches stocks with default filters', async () => {
      const mockStocks = [global.testUtils.createMockStock()];
      const mockResponse = global.testUtils.mockApiResponse(mockStocks);
      
      stockAPI.getStocks.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useStocks(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockStocks);
      });

      expect(stockAPI.getStocks).toHaveBeenCalledWith({});
    });

    it('fetches stocks with custom filters', async () => {
      const filters = { limit: 10, category: 'gainers' };
      const mockStocks = [global.testUtils.createMockStock()];
      const mockResponse = global.testUtils.mockApiResponse(mockStocks);
      
      stockAPI.getStocks.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useStocks(filters), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockStocks);
      });

      expect(stockAPI.getStocks).toHaveBeenCalledWith(filters);
    });

    it('handles API errors gracefully', async () => {
      const error = new Error('API Error');
      stockAPI.getStocks.mockRejectedValue(error);

      const { result } = renderHook(() => useStocks(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.error).toBeTruthy();
      });

      expect(result.current.data).toEqual([]);
    });
  });

  describe('useStockDetail', () => {
    it('fetches stock detail for valid symbol', async () => {
      const mockStock = global.testUtils.createMockStock();
      const mockResponse = global.testUtils.mockApiResponse(mockStock);
      
      stockAPI.getStockDetails.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useStockDetail('AAPL'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockStock);
      });

      expect(stockAPI.getStockDetails).toHaveBeenCalledWith('AAPL');
    });

    it('does not fetch when symbol is not provided', () => {
      stockAPI.getStockDetails.mockResolvedValue({});

      renderHook(() => useStockDetail(''), {
        wrapper: createWrapper(),
      });

      expect(stockAPI.getStockDetails).not.toHaveBeenCalled();
    });
  });

  describe('useStockQuote', () => {
    it('fetches stock quote for valid symbol', async () => {
      const mockQuote = {
        success: true,
        symbol: 'AAPL',
        price: 150.00,
        change: 2.50,
        change_percent: 1.69,
        volume: 1000000,
        timestamp: new Date().toISOString(),
        market_data: {},
      };
      
      stockAPI.getStockQuote.mockResolvedValue(mockQuote);

      const { result } = renderHook(() => useStockQuote('AAPL'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockQuote);
      });

      expect(stockAPI.getStockQuote).toHaveBeenCalledWith('AAPL');
    });

    it('supports real-time updates with custom interval', async () => {
      const mockQuote = {
        success: true,
        symbol: 'AAPL',
        price: 150.00,
        change: 2.50,
        change_percent: 1.69,
        volume: 1000000,
        timestamp: new Date().toISOString(),
        market_data: {},
      };
      
      stockAPI.getStockQuote.mockResolvedValue(mockQuote);

      const { result } = renderHook(
        () => useStockQuote('AAPL', { realTime: true }),
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(result.current.data).toEqual(mockQuote);
      });

      expect(stockAPI.getStockQuote).toHaveBeenCalledWith('AAPL');
    });
  });
});