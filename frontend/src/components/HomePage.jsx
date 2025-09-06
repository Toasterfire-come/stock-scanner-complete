import React from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, BarChart3, Users, Zap, Star, ArrowRight, Check } from 'lucide-react';

const HomePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">Stock Scanner</span>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <Link to="/stocks" className="text-gray-600 hover:text-gray-900 transition-colors">
                Browse Stocks
              </Link>
              <Link to="/trending" className="text-gray-600 hover:text-gray-900 transition-colors">
                Trending
              </Link>
              <Link to="/market-stats" className="text-gray-600 hover:text-gray-900 transition-colors">
                Market Stats
              </Link>
              <Link to="/about" className="text-gray-600 hover:text-gray-900 transition-colors">
                About
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

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
            Professional Stock Scanner
            <span className="block text-blue-600">For Smart Investors</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Discover trending stocks, analyze market data, and make informed investment decisions 
            with our comprehensive stock scanning platform.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link
              to="/stocks"
              className="bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition-colors font-semibold flex items-center justify-center"
            >
              Browse Stocks
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
            <Link
              to="/trending"
              className="border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-lg hover:border-gray-400 transition-colors font-semibold"
            >
              View Trending
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">3,500+</div>
              <div className="text-gray-600">Stocks Tracked</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">Real-time</div>
              <div className="text-gray-600">Market Data</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">24/7</div>
              <div className="text-gray-600">Market Analysis</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">Free</div>
              <div className="text-gray-600">Basic Access</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Everything You Need to Scan the Market
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              From real-time data to advanced filtering, we provide all the tools 
              you need to find your next investment opportunity.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="text-center p-6">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Real-time Data</h3>
              <p className="text-gray-600">
                Get up-to-the-minute stock prices, volume data, and market movements 
                across all major exchanges.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Advanced Filters</h3>
              <p className="text-gray-600">
                Filter stocks by price, volume, market cap, P/E ratio, and dozens 
                of other technical indicators.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Trending Analysis</h3>
              <p className="text-gray-600">
                Discover what stocks are gaining momentum with our trending stocks 
                and volume leaders sections.
              </p>
            </div>
          </div>

          {/* Feature List */}
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Free Features</h3>
              <div className="space-y-4">
                {[
                  'Browse 3,500+ stocks',
                  'Real-time price quotes',
                  'Basic market data',
                  'Trending stocks list',
                  'Simple stock search',
                  'Mobile responsive design'
                ].map((feature, index) => (
                  <div key={index} className="flex items-center">
                    <Check className="h-5 w-5 text-green-500 mr-3" />
                    <span className="text-gray-700">{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Premium Features</h3>
              <div className="space-y-4">
                {[
                  'Advanced filtering & screening',
                  'Portfolio tracking',
                  'Price alerts & notifications',
                  'Historical data analysis',
                  'Export capabilities',
                  'Priority customer support'
                ].map((feature, index) => (
                  <div key={index} className="flex items-center">
                    <Star className="h-5 w-5 text-yellow-500 mr-3" />
                    <span className="text-gray-700">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Start Scanning?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of investors who use Stock Scanner to find their next opportunity.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/auth"
              className="bg-white text-blue-600 px-8 py-4 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
            >
              Start Free Account
            </Link>
            <Link
              to="/stocks"
              className="border-2 border-white text-white px-8 py-4 rounded-lg hover:bg-white hover:text-blue-600 transition-colors font-semibold"
            >
              Browse Stocks Now
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <TrendingUp className="h-6 w-6 text-blue-400" />
                <span className="ml-2 text-lg font-bold">Stock Scanner</span>
              </div>
              <p className="text-gray-400">
                Professional stock scanning platform for smart investors.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Platform</h3>
              <div className="space-y-2">
                <Link to="/stocks" className="block text-gray-400 hover:text-white transition-colors">
                  Browse Stocks
                </Link>
                <Link to="/trending" className="block text-gray-400 hover:text-white transition-colors">
                  Trending
                </Link>
                <Link to="/market-stats" className="block text-gray-400 hover:text-white transition-colors">
                  Market Stats
                </Link>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Account</h3>
              <div className="space-y-2">
                <Link to="/auth" className="block text-gray-400 hover:text-white transition-colors">
                  Sign In
                </Link>
                <Link to="/auth" className="block text-gray-400 hover:text-white transition-colors">
                  Create Account
                </Link>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <div className="space-y-2">
                <Link to="/about" className="block text-gray-400 hover:text-white transition-colors">
                  About Us
                </Link>
                <Link to="/contact" className="block text-gray-400 hover:text-white transition-colors">
                  Contact
                </Link>
              </div>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Stock Scanner. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;