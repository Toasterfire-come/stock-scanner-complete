import React, { memo, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { TrendingUp, TrendingDown, Plus, Heart } from 'lucide-react';
import { useOptimisticPortfolio, useOptimisticWatchlist } from '../../hooks/useStockQueries';

const MemoizedStockCard = memo(({ stock, onClick, showActions = false }) => {
    const { addWithOptimisticUpdate: addToPortfolio } = useOptimisticPortfolio();
    const { addWithOptimisticUpdate: addToWatchlist } = useOptimisticWatchlist();

    // Memoize calculated values
    const stockData = useMemo(() => {
        const isGaining = stock.is_gaining;
        const changeColor = isGaining ? 'text-green-600' : 'text-red-600';
        const bgColor = isGaining ? 'bg-green-50' : 'bg-red-50';
        const borderColor = isGaining ? 'border-l-green-500' : 'border-l-red-500';
        
        return {
            isGaining,
            changeColor,
            bgColor,
            borderColor,
        };
    }, [stock.is_gaining]);

    // Memoize click handlers
    const handleCardClick = useCallback(() => {
        onClick?.(stock);
    }, [onClick, stock]);

    const handleAddToPortfolio = useCallback((e) => {
        e.stopPropagation();
        addToPortfolio(stock.symbol);
    }, [addToPortfolio, stock.symbol]);

    const handleAddToWatchlist = useCallback((e) => {
        e.stopPropagation();
        addToWatchlist(stock.symbol);
    }, [addToWatchlist, stock.symbol]);

    // Memoize formatted values
    const formattedData = useMemo(() => ({
        price: stock.formatted_price || `$${stock.current_price?.toFixed(2) || '0.00'}`,
        change: stock.formatted_change || `${stock.price_change_today >= 0 ? '+' : ''}$${stock.price_change_today?.toFixed(2) || '0.00'} (${stock.change_percent?.toFixed(2) || '0.00'}%)`,
        volume: stock.formatted_volume || (stock.volume ? `${(stock.volume / 1000000).toFixed(1)}M` : 'N/A'),
        marketCap: stock.formatted_market_cap || (stock.market_cap ? `$${(stock.market_cap / 1e9).toFixed(2)}B` : 'N/A'),
        peRatio: stock.pe_ratio ? stock.pe_ratio.toFixed(2) : 'N/A',
    }), [stock]);

    return (
        <Card 
            className={`cursor-pointer hover:shadow-md transition-all duration-200 transform hover:-translate-y-1 ${stockData.bgColor} border-l-4 ${stockData.borderColor}`}
            onClick={handleCardClick}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleCardClick();
                }
            }}
            aria-label={`Stock information for ${stock.symbol} - ${stock.company_name}`}
        >
            <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                    <div className="flex-grow min-w-0">
                        <CardTitle className="text-lg font-bold truncate">
                            {stock.symbol || stock.ticker}
                        </CardTitle>
                        <p className="text-sm text-gray-600 truncate" title={stock.company_name || stock.name}>
                            {stock.company_name || stock.name}
                        </p>
                    </div>
                    <div className="text-right flex-shrink-0 ml-2">
                        <div className="text-lg font-semibold">{formattedData.price}</div>
                        <div className={`text-sm flex items-center justify-end ${stockData.changeColor}`}>
                            {stockData.isGaining ? 
                                <TrendingUp className="w-4 h-4 mr-1" aria-hidden="true" /> : 
                                <TrendingDown className="w-4 h-4 mr-1" aria-hidden="true" />
                            }
                            {formattedData.change}
                        </div>
                    </div>
                </div>
                
                {showActions && (
                    <div className="flex space-x-2 mt-3 pt-3 border-t border-gray-200">
                        <button
                            onClick={handleAddToWatchlist}
                            className="flex items-center px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
                            aria-label={`Add ${stock.symbol} to watchlist`}
                        >
                            <Heart className="w-3 h-3 mr-1" />
                            Watchlist
                        </button>
                        <button
                            onClick={handleAddToPortfolio}
                            className="flex items-center px-3 py-1 text-xs bg-green-100 text-green-700 rounded-full hover:bg-green-200 transition-colors"
                            aria-label={`Add ${stock.symbol} to portfolio`}
                        >
                            <Plus className="w-3 h-3 mr-1" />
                            Portfolio
                        </button>
                    </div>
                )}
            </CardHeader>
            <CardContent className="pt-0">
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex justify-between">
                        <span className="text-gray-500 font-medium">Volume:</span>
                        <span className="font-semibold">{formattedData.volume}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-500 font-medium">Market Cap:</span>
                        <span className="font-semibold">{formattedData.marketCap}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-500 font-medium">P/E:</span>
                        <span className="font-semibold">{formattedData.peRatio}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-500 font-medium">Exchange:</span>
                        <span className="font-semibold">{stock.exchange || 'N/A'}</span>
                    </div>
                </div>
                
                {/* Performance indicator */}
                <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>Performance</span>
                        <span className={stockData.changeColor}>
                            {stockData.isGaining ? '📈' : '📉'} 
                            {Math.abs(stock.change_percent || 0).toFixed(2)}%
                        </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                        <div 
                            className={`h-1 rounded-full transition-all duration-500 ${stockData.isGaining ? 'bg-green-500' : 'bg-red-500'}`}
                            style={{ 
                                width: `${Math.min(Math.abs(stock.change_percent || 0) * 10, 100)}%` 
                            }}
                        />
                    </div>
                </div>
            </CardContent>
        </Card>
    );
});

MemoizedStockCard.displayName = 'MemoizedStockCard';

export default MemoizedStockCard;