import React, { useState, useEffect } from 'react';
import { useStockData, usePlatformStats, useTrendingStocks } from '../hooks/useStockData';
import StockCard from './StockCard';
import StockSearch from './StockSearch';
import StockFilters from './StockFilters';
import StockDetail from './StockDetail';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Loader2, BarChart3, TrendingUp, Users, Database } from 'lucide-react';

const StockDashboard = () => {
    const { stocks, loading, error, fetchStocks } = useStockData();
    const { stats, loading: statsLoading } = usePlatformStats();
    const { trending, loading: trendingLoading } = useTrendingStocks();
    const [selectedStock, setSelectedStock] = useState(null);
    const [filters, setFilters] = useState({
        limit: 20,
        category: 'gainers'
    });

    useEffect(() => {
        fetchStocks(filters);
    }, [fetchStocks, filters]);

    const handleStockClick = (stock) => {
        setSelectedStock(stock);
    };

    const handleFilterChange = (newFilters) => {
        setFilters(prev => ({ ...prev, ...newFilters }));
    };

    if (selectedStock) {
        return (
            <StockDetail 
                stock={selectedStock} 
                onBack={() => setSelectedStock(null)} 
            />
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Stock Scanner</h1>
                    <p className="text-gray-600">Real-time stock market data and analysis</p>
                </div>

                {/* Platform Stats */}
                {stats && !statsLoading && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Total Stocks</CardTitle>
                                <Database className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.total_stocks}</div>
                                <p className="text-xs text-muted-foreground">
                                    NYSE: {stats.nyse_stocks} | NASDAQ: {stats.nasdaq_stocks}
                                </p>
                            </CardContent>
                        </Card>
                        
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                                <Users className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.platform_stats.total_users}</div>
                                <p className="text-xs text-muted-foreground">
                                    Premium: {stats.platform_stats.premium_users}
                                </p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Indicators</CardTitle>
                                <BarChart3 className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.total_indicators}</div>
                                <p className="text-xs text-muted-foreground">
                                    {stats.scanner_combinations} combinations
                                </p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Data Sources</CardTitle>
                                <TrendingUp className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.market_stats.data_sources.length}</div>
                                <p className="text-xs text-muted-foreground">
                                    {stats.market_stats.update_frequency}
                                </p>
                            </CardContent>
                        </Card>
                    </div>
                )}

                {/* Search and Filters */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
                    <div className="lg:col-span-2">
                        <StockSearch onSelect={handleStockClick} />
                    </div>
                    <div>
                        <StockFilters onFilterChange={handleFilterChange} currentFilters={filters} />
                    </div>
                </div>

                {/* Trending Stocks */}
                {trending && !trendingLoading && (
                    <div className="mb-8">
                        <h2 className="text-xl font-semibold mb-4">Trending Stocks</h2>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <Card>
                                <CardHeader>
                                    <CardTitle className="text-lg">Top Gainers</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-2">
                                        {trending.top_gainers?.slice(0, 3).map((stock, index) => (
                                            <div key={index} className="flex justify-between items-center p-2 bg-green-50 rounded">
                                                <span className="font-medium">{stock.symbol}</span>
                                                <span className="text-green-600">+{stock.change_percent.toFixed(2)}%</span>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle className="text-lg">High Volume</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-2">
                                        {trending.high_volume?.slice(0, 3).map((stock, index) => (
                                            <div key={index} className="flex justify-between items-center p-2 bg-blue-50 rounded">
                                                <span className="font-medium">{stock.symbol}</span>
                                                <span className="text-blue-600">{(stock.volume / 1000000).toFixed(1)}M</span>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle className="text-lg">Most Active</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-2">
                                        {trending.most_active?.slice(0, 3).map((stock, index) => (
                                            <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                                                <span className="font-medium">{stock.symbol}</span>
                                                <span className="text-gray-600">${stock.price.toFixed(2)}</span>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                )}

                {/* Stock Grid */}
                <div className="mb-8">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-semibold">
                            {filters.category === 'gainers' ? 'Top Gainers' : 
                             filters.category === 'losers' ? 'Top Losers' : 
                             filters.category === 'high_volume' ? 'High Volume' : 'Stocks'}
                        </h2>
                        {loading && <Loader2 className="h-5 w-5 animate-spin" />}
                    </div>

                    {error && (
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                            Error: {error}
                        </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                        {stocks.map((stock) => (
                            <StockCard 
                                key={stock.ticker} 
                                stock={stock} 
                                onClick={handleStockClick}
                            />
                        ))}
                    </div>

                    {!loading && stocks.length === 0 && (
                        <div className="text-center py-8 text-gray-500">
                            No stocks found matching your criteria.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default StockDashboard;