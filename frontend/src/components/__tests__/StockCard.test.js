import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import MemoizedStockCard from '../optimized/MemoizedStockCard';

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

// Test wrapper with providers
const TestWrapper = ({ children }) => {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('MemoizedStockCard', () => {
  const mockStock = global.testUtils.createMockStock();
  const mockOnClick = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders stock information correctly', () => {
    render(
      <TestWrapper>
        <MemoizedStockCard stock={mockStock} onClick={mockOnClick} />
      </TestWrapper>
    );

    expect(screen.getByText('AAPL')).toBeInTheDocument();
    expect(screen.getByText('Apple Inc.')).toBeInTheDocument();
    expect(screen.getByText('$150.00')).toBeInTheDocument();
    expect(screen.getByText('+$2.50 (1.69%)')).toBeInTheDocument();
  });

  it('displays correct styling for gaining stocks', () => {
    const gainingStock = { ...mockStock, is_gaining: true };
    
    render(
      <TestWrapper>
        <MemoizedStockCard stock={gainingStock} onClick={mockOnClick} />
      </TestWrapper>
    );

    const card = screen.getByRole('button');
    expect(card).toHaveClass('bg-green-50', 'border-l-green-500');
  });

  it('displays correct styling for losing stocks', () => {
    const losingStock = { 
      ...mockStock, 
      is_gaining: false, 
      is_losing: true,
      price_change_today: -2.50,
      change_percent: -1.69
    };
    
    render(
      <TestWrapper>
        <MemoizedStockCard stock={losingStock} onClick={mockOnClick} />
      </TestWrapper>
    );

    const card = screen.getByRole('button');
    expect(card).toHaveClass('bg-red-50', 'border-l-red-500');
  });

  it('calls onClick when card is clicked', () => {
    render(
      <TestWrapper>
        <MemoizedStockCard stock={mockStock} onClick={mockOnClick} />
      </TestWrapper>
    );

    const card = screen.getByRole('button');
    fireEvent.click(card);

    expect(mockOnClick).toHaveBeenCalledWith(mockStock);
  });

  it('supports keyboard navigation', () => {
    render(
      <TestWrapper>
        <MemoizedStockCard stock={mockStock} onClick={mockOnClick} />
      </TestWrapper>
    );

    const card = screen.getByRole('button');
    fireEvent.keyDown(card, { key: 'Enter' });

    expect(mockOnClick).toHaveBeenCalledWith(mockStock);
  });

  it('shows action buttons when showActions is true', () => {
    render(
      <TestWrapper>
        <MemoizedStockCard stock={mockStock} onClick={mockOnClick} showActions={true} />
      </TestWrapper>
    );

    expect(screen.getByText('Watchlist')).toBeInTheDocument();
    expect(screen.getByText('Portfolio')).toBeInTheDocument();
  });

  it('hides action buttons when showActions is false', () => {
    render(
      <TestWrapper>
        <MemoizedStockCard stock={mockStock} onClick={mockOnClick} showActions={false} />
      </TestWrapper>
    );

    expect(screen.queryByText('Watchlist')).not.toBeInTheDocument();
    expect(screen.queryByText('Portfolio')).not.toBeInTheDocument();
  });

  it('displays market data correctly', () => {
    render(
      <TestWrapper>
        <MemoizedStockCard stock={mockStock} onClick={mockOnClick} />
      </TestWrapper>
    );

    expect(screen.getByText('Volume:')).toBeInTheDocument();
    expect(screen.getByText('1.0M')).toBeInTheDocument();
    expect(screen.getByText('Market Cap:')).toBeInTheDocument();
    expect(screen.getByText('Exchange:')).toBeInTheDocument();
    expect(screen.getByText('NASDAQ')).toBeInTheDocument();
  });

  it('handles missing optional data gracefully', () => {
    const incompleteStock = {
      ...mockStock,
      market_cap: null,
      pe_ratio: null,
      formatted_market_cap: null,
    };

    render(
      <TestWrapper>
        <MemoizedStockCard stock={incompleteStock} onClick={mockOnClick} />
      </TestWrapper>
    );

    expect(screen.getByText('N/A')).toBeInTheDocument(); // For missing market cap and P/E
  });
});