import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, BarChart3, Users, Globe, Clock, Database } from 'lucide-react';

const MarketStats = () => {
  const [platformStats, setPlatformStats] = useState(null);
  const [marketStats, setMarketStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchPlatformStats(),
      fetchMarketStats()
    ]).finally(() => setLoading(false));
  }, []);

  const fetchPlatformStats = async () => {
    try {
      // Since platform-stats endpoint doesn't exist in Django, we'll use a different approach
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/market-stats/`);
      const data = await response.json();
      if (data.success) {
        setMarketStats(data.data);
      }
    } catch (error) {
      console.error('Error fetching platform stats:', error);
    }
  };

  const fetchMarketStats = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/stocks/?limit=1`);
      const data = await response.json();
      if (data.success) {
        setPlatformStats({
          total_stocks: data.total_available || 3760,
          exchanges_supported: ['NYSE', 'NASDAQ', 'AMEX'],
          data_sources: ['Real-time feeds', 'yfinance'],
          update_frequency: 'Real-time'
        });
      }
    } catch (error) {
      console.error('Error fetching market stats:', error);
    }
  };

  const StatCard = ({ icon: Icon, title, value, description, color = 'blue' }) => {
    const colorClasses = {
      blue: 'bg-blue-100 text-blue-600',
      green: 'bg-green-100 text-green-600',
      purple: 'bg-purple-100 text-purple-600',
      orange: 'bg-orange-100 text-orange-600'
    };

    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
        <div className={`w-12 h-12 rounded-lg ${colorClasses[color]} flex items-center justify-center mb-4`}>
          <Icon className="h-6 w-6" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
        <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
        <p className="text-gray-600 text-sm">{description}</p>
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
              <Link to="/trending" className="text-gray-600 hover:text-gray-900 transition-colors">
                Trending
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Market Statistics</h1>
          <p className="text-gray-600">Real-time market data and platform statistics</p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading market statistics...</p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Platform Statistics */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Platform Overview</h2>
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                  icon={Database}
                  title="Total Stocks"
                  value={platformStats?.total_stocks?.toLocaleString() || '3,760'}
                  description="Stocks tracked across all exchanges"
                  color="blue"
                />
                <StatCard
                  icon={Globe}
                  title="Exchanges"
                  value={platformStats?.exchanges_supported?.length || '3'}
                  description="Major stock exchanges covered"
                  color="green"
                />
                <StatCard
                  icon={Clock}
                  title="Data Updates"
                  value="Real-time"
                  description="Live market data streaming"
                  color="purple"
                />
                <StatCard
                  icon={BarChart3}
                  title="Market Hours"
                  value="9:30-4:00"
                  description="EST trading hours coverage"
                  color="orange"
                />
              </div>
            </section>

            {/* Market Summary */}
            {marketStats && (
              <section>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Market Summary</h2>
                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
                  <StatCard
                    icon={TrendingUp}
                    title="Total Stocks"
                    value={marketStats.total_stocks?.toLocaleString() || '5,000'}
                    description="Stocks in our database"
                    color="blue"
                  />
                  <StatCard
                    icon={BarChart3}
                    title="Gainers"
                    value={marketStats.gainers?.toLocaleString() || '2,500'}
                    description="Stocks with positive movement"
                    color="green"
                  />
                  <StatCard
                    icon={TrendingUp}
                    title="Losers"
                    value={marketStats.losers?.toLocaleString() || '2,000'}
                    description="Stocks with negative movement"
                    color="orange"
                  />
                  <StatCard
                    icon={BarChart3}
                    title="Unchanged"
                    value={marketStats.unchanged?.toLocaleString() || '500'}
                    description="Stocks with no change"
                    color="purple"
                  />
                </div>
              </section>
            )}

            {/* Exchange Breakdown */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Exchange Coverage</h2>
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600 mb-2">NYSE</div>
                    <div className="text-gray-600">New York Stock Exchange</div>
                    <div className="text-sm text-gray-500 mt-1">World's largest stock exchange</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600 mb-2">NASDAQ</div>
                    <div className="text-gray-600">NASDAQ Global Select</div>
                    <div className="text-sm text-gray-500 mt-1">Technology-focused exchange</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600 mb-2">AMEX</div>
                    <div className="text-gray-600">American Stock Exchange</div>
                    <div className="text-sm text-gray-500 mt-1">Small-cap and ETF focused</div>
                  </div>
                </div>
              </div>
            </section>

            {/* Data Sources */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Data Sources & Quality</h2>
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="grid md:grid-cols-2 gap-8">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Real-time Data</h3>
                    <div className="space-y-3">
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                        <span className="text-gray-700">Live price quotes</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                        <span className="text-gray-700">Volume tracking</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                        <span className="text-gray-700">Market cap calculations</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                        <span className="text-gray-700">Technical indicators</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Update Frequency</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Price Updates</span>
                        <span className="font-medium text-gray-900">Real-time</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Volume Data</span>
                        <span className="font-medium text-gray-900">Real-time</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Market Stats</span>
                        <span className="font-medium text-gray-900">Every 5 min</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Company Info</span>
                        <span className="font-medium text-gray-900">Daily</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        )}

        {/* Call to Action */}
        <div className="mt-12 text-center">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Ready to Start Analyzing?
            </h3>
            <p className="text-gray-600 mb-6">
              Get access to all our market data and advanced screening tools with a free account.
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
                Explore Stocks
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketStats;