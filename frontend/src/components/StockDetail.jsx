import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ArrowLeft, TrendingUp, TrendingDown, Loader2, Plus, Heart } from 'lucide-react';
import { stockAPI } from '../services/stockAPI';
import { useAuth } from '../context/AuthContext';

const StockDetail = ({ stock, onBack }) => {
    const [quote, setQuote] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { isAuthenticated } = useAuth();

    useEffect(() => {
        const fetchQuote = async () => {
            try {
                setLoading(true);
                const response = await stockAPI.getStockQuote(stock.symbol);
                setQuote(response);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchQuote();
        
        // Set up polling for real-time updates
        const interval = setInterval(fetchQuote, 30000); // Update every 30 seconds
        
        return () => clearInterval(interval);
    }, [stock.symbol]);

    const handleAddToWatchlist = async () => {
        if (!isAuthenticated) {
            alert('Please log in to add stocks to your watchlist');
            return;
        }

        try {
            await stockAPI.addToWatchlist(stock.symbol);
            alert(`${stock.symbol} added to watchlist!`);
        } catch (error) {
            alert('Error adding to watchlist: ' + error.message);
        }
    };

    const handleAddToPortfolio = async () => {
        if (!isAuthenticated) {
            alert('Please log in to add stocks to your portfolio');
            return;
        }

        try {
            await stockAPI.addToPortfolio(stock.symbol);
            alert(`${stock.symbol} added to portfolio!`);
        } catch (error) {
            alert('Error adding to portfolio: ' + error.message);
        }
    };

    const isGaining = quote ? quote.change > 0 : stock.is_gaining;
    const changeColor = isGaining ? 'text-green-600' : 'text-red-600';
    const bgColor = isGaining ? 'bg-green-50' : 'bg-red-50';

    return (
        <div className="min-h-screen bg-gray-50 p-4">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="flex items-center mb-6">
                    <button 
                        onClick={onBack}
                        className="flex items-center text-blue-600 hover:text-blue-800 mr-4"
                    >
                        <ArrowLeft className="w-5 h-5 mr-1" />
                        Back to Dashboard
                    </button>
                </div>

                {/* Stock Info Header */}
                <Card className={`mb-6 ${bgColor} border-l-4 ${isGaining ? 'border-l-green-500' : 'border-l-red-500'}`}>
                    <CardHeader>
                        <div className="flex justify-between items-start">
                            <div>
                                <CardTitle className="text-2xl font-bold">{stock.symbol}</CardTitle>
                                <p className="text-lg text-gray-600">{stock.company_name}</p>
                                <p className="text-sm text-gray-500">{stock.exchange}</p>
                            </div>
                            <div className="text-right">
                                {loading ? (
                                    <Loader2 className="w-6 h-6 animate-spin" />
                                ) : quote ? (
                                    <>
                                        <div className="text-3xl font-bold">${quote.price.toFixed(2)}</div>
                                        <div className={`text-lg flex items-center justify-end ${changeColor}`}>
                                            {isGaining ? <TrendingUp className="w-5 h-5 mr-1" /> : <TrendingDown className="w-5 h-5 mr-1" />}
                                            {quote.change >= 0 ? '+' : ''}${quote.change.toFixed(2)} ({quote.change_percent.toFixed(2)}%)
                                        </div>
                                    </>
                                ) : (
                                    <>
                                        <div className="text-3xl font-bold">{stock.formatted_price}</div>
                                        <div className={`text-lg flex items-center justify-end ${changeColor}`}>
                                            {isGaining ? <TrendingUp className="w-5 h-5 mr-1" /> : <TrendingDown className="w-5 h-5 mr-1" />}
                                            {stock.formatted_change}
                                        </div>
                                    </>
                                )}
                            </div>
                        </div>
                        
                        {/* Action Buttons */}
                        <div className="flex space-x-2 mt-4">
                            <button
                                onClick={handleAddToWatchlist}
                                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                            >
                                <Heart className="w-4 h-4 mr-2" />
                                Add to Watchlist
                            </button>
                            <button
                                onClick={handleAddToPortfolio}
                                className="flex items-center px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                            >
                                <Plus className="w-4 h-4 mr-2" />
                                Add to Portfolio
                            </button>
                        </div>
                    </CardHeader>
                </Card>

                {/* Market Data */}
                {quote && (
                    <Card className="mb-6">
                        <CardHeader>
                            <CardTitle>Market Data</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div>
                                    <div className="text-sm text-gray-500">Open</div>
                                    <div className="text-lg font-semibold">${quote.market_data.open?.toFixed(2) || 'N/A'}</div>
                                </div>
                                <div>
                                    <div className="text-sm text-gray-500">High</div>
                                    <div className="text-lg font-semibold">${quote.market_data.high?.toFixed(2) || 'N/A'}</div>
                                </div>
                                <div>
                                    <div className="text-sm text-gray-500">Low</div>
                                    <div className="text-lg font-semibold">${quote.market_data.low?.toFixed(2) || 'N/A'}</div>
                                </div>
                                <div>
                                    <div className="text-sm text-gray-500">Previous Close</div>
                                    <div className="text-lg font-semibold">${quote.market_data.previous_close?.toFixed(2) || 'N/A'}</div>
                                </div>
                                <div>
                                    <div className="text-sm text-gray-500">Volume</div>
                                    <div className="text-lg font-semibold">{quote.volume.toLocaleString()}</div>
                                </div>
                                <div>
                                    <div className="text-sm text-gray-500">Market Cap</div>
                                    <div className="text-lg font-semibold">
                                        {quote.market_data.market_cap ? 
                                            `$${(quote.market_data.market_cap / 1e9).toFixed(2)}B` : 'N/A'}
                                    </div>
                                </div>
                                <div>
                                    <div className="text-sm text-gray-500">P/E Ratio</div>
                                    <div className="text-lg font-semibold">
                                        {quote.market_data.pe_ratio ? quote.market_data.pe_ratio.toFixed(2) : 'N/A'}
                                    </div>
                                </div>
                                <div>
                                    <div className="text-sm text-gray-500">Data Source</div>
                                    <div className="text-lg font-semibold">{quote.source}</div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Extended Stock Data */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Financial Metrics</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {stock.pe_ratio && (
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">P/E Ratio:</span>
                                        <span className="font-semibold">{stock.pe_ratio.toFixed(2)}</span>
                                    </div>
                                )}
                                {stock.dividend_yield && (
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Dividend Yield:</span>
                                        <span className="font-semibold">{stock.dividend_yield.toFixed(2)}%</span>
                                    </div>
                                )}
                                {stock.earnings_per_share && (
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">EPS:</span>
                                        <span className="font-semibold">${stock.earnings_per_share.toFixed(2)}</span>
                                    </div>
                                )}
                                {stock.book_value && (
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Book Value:</span>
                                        <span className="font-semibold">${stock.book_value.toFixed(2)}</span>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>52-Week Range</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {stock.week_52_low && (
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">52-Week Low:</span>
                                        <span className="font-semibold">${stock.week_52_low.toFixed(2)}</span>
                                    </div>
                                )}
                                {stock.week_52_high && (
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">52-Week High:</span>
                                        <span className="font-semibold">${stock.week_52_high.toFixed(2)}</span>
                                    </div>
                                )}
                                {stock.one_year_target && (
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">1-Year Target:</span>
                                        <span className="font-semibold">${stock.one_year_target.toFixed(2)}</span>
                                    </div>
                                )}
                                <div className="mt-4">
                                    <div className="text-sm text-gray-500 mb-2">Current Position in 52-Week Range</div>
                                    <div className="w-full bg-gray-200 rounded-full h-3">
                                        <div 
                                            className="bg-blue-600 h-3 rounded-full" 
                                            style={{ 
                                                width: `${stock.price_position_52_week || 50}%` 
                                            }}
                                        ></div>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {error && (
                    <Card className="mt-6 bg-red-50 border-red-200">
                        <CardContent className="p-4">
                            <div className="text-red-700">Error loading real-time data: {error}</div>
                        </CardContent>
                    </Card>
                )}

                {quote && (
                    <div className="mt-6 text-center text-sm text-gray-500">
                        Last updated: {new Date(quote.timestamp).toLocaleString()}
                        {quote.cached && ' (Cached)'}
                    </div>
                )}
            </div>
        </div>
    );
};

export default StockDetail;