import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, ArrowUpRight, ArrowDownRight, Volume2, Crown } from 'lucide-react';

const TrendingStocks = () => {
  const [trendingData, setTrendingData] = useState({
    high_volume: [],
    top_gainers: [],
    most_active: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrendingData();
  }, []);

  const fetchTrendingData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/trending/`);
      const data = await response.json();
      if (data.success) {
        setTrendingData(data);
      }
    } catch (error) {
      console.error('Error fetching trending data:', error);
    } finally {
      setLoading(false);
    }
  };

  const StockCard = ({ stock, type }) => {
    const getIcon = () => {
      switch (type) {
        case 'volume':
          return <Volume2 className="h-5 w-5 text-blue-600" />;
        case 'gainer':
          return <ArrowUpRight className="h-5 w-5 text-green-600" />;
        case 'active':
          return <Crown className="h-5 w-5 text-purple-600" />;
        default:
          return <TrendingUp className="h-5 w-5 text-gray-600" />;
      }
    };

    return (
      <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center">
            {getIcon()}
            <span className="ml-2 font-semibold text-gray-900">{stock.symbol}</span>
          </div>
          <div className="text-right">
            <div className="font-medium text-gray-900">${stock.price?.toFixed(2) || 'N/A'}</div>
            {stock.change_percent !== undefined && (
              <div className={`text-sm ${stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
              </div>
            )}
          </div>
        </div>
        
        {stock.volume && (
          <div className="text-sm text-gray-600">
            Volume: {stock.volume.toLocaleString()}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center">
              <TrendingUp className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">Stock Scanner</span>
            </Link>
            
            <div className="hidden md:flex items-center space-x-8">
              <Link to="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                Home
              </Link>
              <Link to="/stocks" className="text-gray-600 hover:text-gray-900 transition-colors">
                Browse Stocks
              </Link>
              <Link to="/market-stats" className="text-gray-600 hover:text-gray-900 transition-colors">
                Market Stats
              </Link>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link
                to="/auth"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/auth"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Trending Stocks</h1>
          <p className="text-gray-600">Discover the most active and trending stocks in the market</p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading trending data...</p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Top Gainers */}
            <section>
              <div className="flex items-center mb-4">
                <ArrowUpRight className="h-6 w-6 text-green-600 mr-2" />
                <h2 className="text-2xl font-bold text-gray-900">Top Gainers</h2>
              </div>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {trendingData.top_gainers.slice(0, 8).map((stock) => (
                  <StockCard key={stock.symbol} stock={stock} type="gainer" />
                ))}
              </div>
              {trendingData.top_gainers.length === 0 && (
                <p className="text-gray-600 text-center py-8">No top gainers data available.</p>
              )}
            </section>

            {/* High Volume */}
            <section>
              <div className="flex items-center mb-4">
                <Volume2 className="h-6 w-6 text-blue-600 mr-2" />
                <h2 className="text-2xl font-bold text-gray-900">High Volume</h2>
              </div>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {trendingData.high_volume.slice(0, 8).map((stock) => (
                  <StockCard key={stock.symbol} stock={stock} type="volume" />
                ))}
              </div>
              {trendingData.high_volume.length === 0 && (
                <p className="text-gray-600 text-center py-8">No high volume data available.</p>
              )}
            </section>

            {/* Most Active */}
            <section>
              <div className="flex items-center mb-4">
                <Crown className="h-6 w-6 text-purple-600 mr-2" />
                <h2 className="text-2xl font-bold text-gray-900">Most Active</h2>
              </div>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {trendingData.most_active.slice(0, 8).map((stock) => (
                  <StockCard key={stock.symbol} stock={stock} type="active" />
                ))}
              </div>
              {trendingData.most_active.length === 0 && (
                <p className="text-gray-600 text-center py-8">No most active data available.</p>
              )}
            </section>
          </div>
        )}

        {/* Call to Action */}
        <div className="mt-12 text-center">
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Track Your Favorite Stocks
            </h3>
            <p className="text-gray-600 mb-6">
              Create a free account to build watchlists, set price alerts, and track your portfolio performance.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/auth"
                className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
              >
                Create Free Account
              </Link>
              <Link
                to="/stocks"
                className="border-2 border-gray-300 text-gray-700 px-8 py-3 rounded-lg hover:border-gray-400 transition-colors font-semibold"
              >
                Browse All Stocks
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrendingStocks;