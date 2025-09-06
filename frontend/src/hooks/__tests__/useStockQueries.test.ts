import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useStocks, useStock, useStockQuote } from '../useStockQueries';

// Create a wrapper for React Query
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useStockQueries', () => {
  describe('useStocks', () => {
    it('should fetch stocks successfully', async () => {
      const wrapper = createWrapper();
      
      const { result } = renderHook(() => useStocks(), { wrapper });
      
      expect(result.current.isLoading).toBe(true);
      
      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });
      
      expect(result.current.data).toBeDefined();
      expect(Array.isArray(result.current.data)).toBe(true);
    });

    it('should apply filters correctly', async () => {
      const wrapper = createWrapper();
      const filters = { limit: 10, search: 'AAPL' };
      
      const { result } = renderHook(() => useStocks(filters), { wrapper });
      
      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });
      
      expect(result.current.data).toBeDefined();
    });
  });

  describe('useStock', () => {
    it('should fetch individual stock data', async () => {
      const wrapper = createWrapper();
      
      const { result } = renderHook(() => useStock('AAPL'), { wrapper });
      
      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });
      
      expect(result.current.data).toBeDefined();
      expect(result.current.data?.symbol).toBe('AAPL');
    });

    it('should not fetch when symbol is empty', () => {
      const wrapper = createWrapper();
      
      const { result } = renderHook(() => useStock(''), { wrapper });
      
      expect(result.current.isLoading).toBe(false);
      expect(result.current.data).toBeUndefined();
    });
  });

  describe('useStockQuote', () => {
    it('should fetch stock quote data', async () => {
      const wrapper = createWrapper();
      
      const { result } = renderHook(() => useStockQuote('AAPL'), { wrapper });
      
      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });
      
      expect(result.current.data).toBeDefined();
      expect(result.current.data?.symbol).toBe('AAPL');
      expect(typeof result.current.data?.price).toBe('number');
    });
  });
});