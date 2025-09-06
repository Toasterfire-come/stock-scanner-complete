import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Filter } from 'lucide-react';

const StockFilters = ({ onFilterChange, currentFilters }) => {
    const [localFilters, setLocalFilters] = useState(currentFilters);

    const handleFilterChange = (key, value) => {
        const newFilters = { ...localFilters, [key]: value };
        setLocalFilters(newFilters);
        onFilterChange(newFilters);
    };

    const categories = [
        { value: 'gainers', label: 'Top Gainers' },
        { value: 'losers', label: 'Top Losers' },
        { value: 'high_volume', label: 'High Volume' },
        { value: 'large_cap', label: 'Large Cap' },
        { value: 'small_cap', label: 'Small Cap' }
    ];

    const exchanges = [
        { value: '', label: 'All Exchanges' },
        { value: 'NASDAQ', label: 'NASDAQ' },
        { value: 'NYSE', label: 'NYSE' }
    ];

    const limits = [
        { value: 10, label: '10' },
        { value: 20, label: '20' },
        { value: 50, label: '50' },
        { value: 100, label: '100' }
    ];

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center text-lg">
                    <Filter className="w-5 h-5 mr-2" />
                    Filters
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Category Filter */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Category
                    </label>
                    <select
                        value={localFilters.category || ''}
                        onChange={(e) => handleFilterChange('category', e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        {categories.map(cat => (
                            <option key={cat.value} value={cat.value}>
                                {cat.label}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Exchange Filter */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Exchange
                    </label>
                    <select
                        value={localFilters.exchange || ''}
                        onChange={(e) => handleFilterChange('exchange', e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        {exchanges.map(exchange => (
                            <option key={exchange.value} value={exchange.value}>
                                {exchange.label}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Limit Filter */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Results Limit
                    </label>
                    <select
                        value={localFilters.limit || 20}
                        onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        {limits.map(limit => (
                            <option key={limit.value} value={limit.value}>
                                {limit.label}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Price Range Filters */}
                <div className="grid grid-cols-2 gap-2">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Min Price
                        </label>
                        <input
                            type="number"
                            placeholder="$0"
                            value={localFilters.min_price || ''}
                            onChange={(e) => handleFilterChange('min_price', e.target.value ? parseFloat(e.target.value) : null)}
                            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Max Price
                        </label>
                        <input
                            type="number"
                            placeholder="No limit"
                            value={localFilters.max_price || ''}
                            onChange={(e) => handleFilterChange('max_price', e.target.value ? parseFloat(e.target.value) : null)}
                            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>
                </div>

                {/* Volume Filter */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Min Volume
                    </label>
                    <input
                        type="number"
                        placeholder="No minimum"
                        value={localFilters.min_volume || ''}
                        onChange={(e) => handleFilterChange('min_volume', e.target.value ? parseInt(e.target.value) : null)}
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>
            </CardContent>
        </Card>
    );
};

export default StockFilters;