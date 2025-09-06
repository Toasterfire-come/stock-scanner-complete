import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { TrendingUp, TrendingDown } from 'lucide-react';

const StockCard = ({ stock, onClick }) => {
    const isGaining = stock.is_gaining;
    const changeColor = isGaining ? 'text-green-600' : 'text-red-600';
    const bgColor = isGaining ? 'bg-green-50' : 'bg-red-50';
    
    return (
        <Card 
            className={`cursor-pointer hover:shadow-md transition-shadow ${bgColor} border-l-4 ${isGaining ? 'border-l-green-500' : 'border-l-red-500'}`}
            onClick={() => onClick(stock)}
        >
            <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                    <div>
                        <CardTitle className="text-lg font-bold">{stock.symbol}</CardTitle>
                        <p className="text-sm text-gray-600 truncate">{stock.company_name}</p>
                    </div>
                    <div className="text-right">
                        <div className="text-lg font-semibold">{stock.formatted_price}</div>
                        <div className={`text-sm flex items-center ${changeColor}`}>
                            {isGaining ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                            {stock.formatted_change}
                        </div>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="pt-0">
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <span className="text-gray-500">Volume:</span>
                        <span className="ml-1 font-medium">{stock.formatted_volume}</span>
                    </div>
                    <div>
                        <span className="text-gray-500">Market Cap:</span>
                        <span className="ml-1 font-medium">{stock.formatted_market_cap || 'N/A'}</span>
                    </div>
                    {stock.pe_ratio && (
                        <div>
                            <span className="text-gray-500">P/E:</span>
                            <span className="ml-1 font-medium">{stock.pe_ratio.toFixed(2)}</span>
                        </div>
                    )}
                    <div>
                        <span className="text-gray-500">Exchange:</span>
                        <span className="ml-1 font-medium">{stock.exchange}</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default StockCard;