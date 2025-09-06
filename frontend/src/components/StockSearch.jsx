import React, { useState, useCallback } from 'react';
import { Card, CardContent } from './ui/card';
import { Search, Loader2 } from 'lucide-react';
import { useStockData } from '../hooks/useStockData';
import { stockAPI } from '../services/stockAPI';

const StockSearch = ({ onSelect }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showResults, setShowResults] = useState(false);

    const handleSearch = useCallback(async (searchQuery) => {
        if (searchQuery.length < 2) {
            setResults([]);
            setShowResults(false);
            return;
        }

        setLoading(true);
        try {
            const response = await stockAPI.searchStocks(searchQuery);
            setResults(response.data || []);
            setShowResults(true);
        } catch (error) {
            console.error('Search error:', error);
            setResults([]);
        } finally {
            setLoading(false);
        }
    }, []);

    const handleInputChange = (e) => {
        const value = e.target.value;
        setQuery(value);
        handleSearch(value);
    };

    const handleSelectStock = async (result) => {
        try {
            const stockData = await stockAPI.getStockDetails(result.symbol);
            if (stockData.success) {
                onSelect(stockData.data);
            }
        } catch (error) {
            console.error('Error fetching stock details:', error);
        }
        setQuery('');
        setShowResults(false);
        setResults([]);
    };

    return (
        <div className="relative">
            <Card>
                <CardContent className="p-4">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                        <input
                            type="text"
                            placeholder="Search stocks by symbol or company name..."
                            value={query}
                            onChange={handleInputChange}
                            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        {loading && (
                            <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 animate-spin text-gray-400" />
                        )}
                    </div>
                </CardContent>
            </Card>

            {/* Search Results Dropdown */}
            {showResults && (
                <Card className="absolute top-full mt-1 w-full z-50 max-h-64 overflow-y-auto">
                    <CardContent className="p-0">
                        {results.length > 0 ? (
                            <div className="divide-y divide-gray-200">
                                {results.map((result, index) => (
                                    <div
                                        key={index}
                                        className="p-3 hover:bg-gray-50 cursor-pointer transition-colors"
                                        onClick={() => handleSelectStock(result)}
                                    >
                                        <div className="flex justify-between items-center">
                                            <div>
                                                <div className="font-semibold text-gray-900">{result.symbol}</div>
                                                <div className="text-sm text-gray-600 truncate">{result.name}</div>
                                            </div>
                                            <div className="text-sm text-gray-500">{result.exchange}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="p-4 text-center text-gray-500">
                                {loading ? 'Searching...' : 'No results found'}
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

export default StockSearch;