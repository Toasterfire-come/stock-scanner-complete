// Strategy Ranking Leaderboard Component - Phase 6
import React, { useState, useEffect } from 'react';
import { getApiClient } from '../../api/client';

const StrategyLeaderboard = () => {
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedTimeframe, setSelectedTimeframe] = useState('3m');
  const [sortBy, setSortBy] = useState('score');
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [pagination, setPagination] = useState({ page: 1, total_pages: 1 });
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    fetchCategories();
    fetchLeaderboard();
  }, [selectedCategory, selectedTimeframe, sortBy, pagination.page]);

  const fetchCategories = async () => {
    try {
      const api = getApiClient();
      const response = await api.get('/api/strategy-ranking/categories/');
      if (response.data.success) {
        setCategories(response.data.data.categories);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      const api = getApiClient();
      const params = new URLSearchParams({
        category: selectedCategory,
        timeframe: selectedTimeframe,
        sort_by: sortBy,
        page: pagination.page,
        limit: 10
      });
      
      const response = await api.get(`/api/strategy-ranking/leaderboard/?${params}`);
      if (response.data.success) {
        setStrategies(response.data.data.strategies);
        setPagination(prev => ({
          ...prev,
          total_pages: response.data.data.pagination.total_pages
        }));
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStrategyDetail = async (strategyId) => {
    try {
      const api = getApiClient();
      const response = await api.get(`/api/strategy-ranking/${strategyId}/`);
      if (response.data.success) {
        setSelectedStrategy(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching strategy detail:', error);
    }
  };

  const handleCloneStrategy = async (strategyId) => {
    try {
      const api = getApiClient();
      await api.post(`/api/strategy-ranking/${strategyId}/clone/`, {
        keep_symbols: true,
        keep_timeframe: true,
        keep_parameters: true
      });
      alert('Strategy cloned successfully!');
    } catch (error) {
      console.error('Error cloning strategy:', error);
      alert('Failed to clone strategy. Please try again.');
    }
  };

  const getCategoryLabel = (value) => {
    const cat = categories.find(c => c.value === value);
    return cat ? cat.label : value.replace('_', ' ');
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-[#089981]';
    if (score >= 60) return 'text-[#2962FF]';
    if (score >= 40) return 'text-[#FF9800]';
    return 'text-[#F23645]';
  };

  return (
    <div className="min-h-screen bg-[#131722] text-[#D1D4DC]" data-testid="strategy-leaderboard">
      {/* Header */}
      <div className="bg-[#1E222D] border-b border-[#2A2E39] py-8">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-3xl font-bold mb-2">Strategy Leaderboard</h1>
          <p className="text-[#787B86]">
            Discover and clone top-performing trading strategies
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex flex-wrap gap-4 mb-8">
          <div className="flex-1 min-w-[150px]">
            <label className="block text-sm text-[#787B86] mb-2">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full bg-[#1E222D] border border-[#2A2E39] rounded-lg px-4 py-2
                       text-[#D1D4DC] focus:outline-none focus:border-[#2962FF]"
            >
              <option value="all">All Strategies</option>
              <option value="day_trading">Day Trading</option>
              <option value="swing_trading">Swing Trading</option>
              <option value="long_term">Long-Term</option>
            </select>
          </div>

          <div className="flex-1 min-w-[150px]">
            <label className="block text-sm text-[#787B86] mb-2">Timeframe</label>
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="w-full bg-[#1E222D] border border-[#2A2E39] rounded-lg px-4 py-2
                       text-[#D1D4DC] focus:outline-none focus:border-[#2962FF]"
            >
              <option value="1m">1 Month</option>
              <option value="3m">3 Months</option>
              <option value="6m">6 Months</option>
              <option value="1y">1 Year</option>
              <option value="all">All Time</option>
            </select>
          </div>

          <div className="flex-1 min-w-[150px]">
            <label className="block text-sm text-[#787B86] mb-2">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full bg-[#1E222D] border border-[#2A2E39] rounded-lg px-4 py-2
                       text-[#D1D4DC] focus:outline-none focus:border-[#2962FF]"
            >
              <option value="score">Composite Score</option>
              <option value="returns">Returns</option>
              <option value="risk_adjusted">Risk-Adjusted</option>
              <option value="popularity">Popularity</option>
            </select>
          </div>
        </div>

        {/* Strategy Detail Modal */}
        {selectedStrategy && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-[#1E222D] border border-[#2A2E39] rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-[#D1D4DC]">{selectedStrategy.name}</h2>
                    <p className="text-[#787B86]">by {selectedStrategy.creator}</p>
                  </div>
                  <button
                    onClick={() => setSelectedStrategy(null)}
                    className="text-[#787B86] hover:text-[#D1D4DC]"
                  >
                    ✕
                  </button>
                </div>

                <p className="text-[#D1D4DC] mb-6">{selectedStrategy.description}</p>

                {/* Score Breakdown */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-4">Score Breakdown</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-[#131722] rounded-lg p-3">
                      <div className="text-sm text-[#787B86]">Performance</div>
                      <div className={`text-xl font-bold ${getScoreColor(selectedStrategy.score_breakdown?.performance_score || 0)}`}>
                        {selectedStrategy.score_breakdown?.performance_score || 0}/30
                      </div>
                    </div>
                    <div className="bg-[#131722] rounded-lg p-3">
                      <div className="text-sm text-[#787B86]">Risk Management</div>
                      <div className={`text-xl font-bold ${getScoreColor((selectedStrategy.score_breakdown?.risk_score || 0) * 4)}`}>
                        {selectedStrategy.score_breakdown?.risk_score || 0}/25
                      </div>
                    </div>
                    <div className="bg-[#131722] rounded-lg p-3">
                      <div className="text-sm text-[#787B86]">Consistency</div>
                      <div className={`text-xl font-bold ${getScoreColor((selectedStrategy.score_breakdown?.consistency_score || 0) * 5)}`}>
                        {selectedStrategy.score_breakdown?.consistency_score || 0}/20
                      </div>
                    </div>
                    <div className="bg-[#131722] rounded-lg p-3">
                      <div className="text-sm text-[#787B86]">Efficiency</div>
                      <div className={`text-xl font-bold ${getScoreColor((selectedStrategy.score_breakdown?.efficiency_score || 0) * 6.67)}`}>
                        {selectedStrategy.score_breakdown?.efficiency_score || 0}/15
                      </div>
                    </div>
                  </div>
                </div>

                {/* Key Metrics */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-4">Key Metrics</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-[#089981]">
                        {selectedStrategy.annual_return}%
                      </div>
                      <div className="text-sm text-[#787B86]">Annual Return</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-[#D1D4DC]">
                        {selectedStrategy.sharpe_ratio}
                      </div>
                      <div className="text-sm text-[#787B86]">Sharpe Ratio</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-[#F23645]">
                        {selectedStrategy.max_drawdown}%
                      </div>
                      <div className="text-sm text-[#787B86]">Max Drawdown</div>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-4">
                  <button
                    onClick={() => {
                      handleCloneStrategy(selectedStrategy.id);
                      setSelectedStrategy(null);
                    }}
                    className="flex-1 bg-[#2962FF] text-white py-3 rounded-lg
                             hover:bg-[#1E53E5] transition-colors font-medium"
                  >
                    Clone Strategy
                  </button>
                  <button
                    onClick={() => setSelectedStrategy(null)}
                    className="flex-1 bg-[#2A2E39] text-[#D1D4DC] py-3 rounded-lg
                             hover:bg-[#3A3E49] transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Strategy List */}
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-[#1E222D] rounded-lg p-6 animate-pulse">
                <div className="h-4 bg-[#2A2E39] rounded w-1/4 mb-4"></div>
                <div className="h-3 bg-[#2A2E39] rounded w-full mb-2"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {strategies.map((strategy, index) => (
              <div
                key={strategy.id}
                className="bg-[#1E222D] border border-[#2A2E39] rounded-lg p-6
                         hover:border-[#3A3E49] transition-all cursor-pointer"
                onClick={() => fetchStrategyDetail(strategy.id)}
                data-testid={`strategy-card-${strategy.id}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-4">
                    <div className="text-3xl font-bold text-[#787B86]">
                      #{(pagination.page - 1) * 10 + index + 1}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-[#D1D4DC] mb-1">
                        {strategy.name}
                        {strategy.is_verified && (
                          <span className="ml-2 text-[#2962FF]">✓</span>
                        )}
                      </h3>
                      <p className="text-sm text-[#787B86]">
                        by {strategy.creator} · {getCategoryLabel(strategy.category)}
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className={`text-3xl font-bold ${getScoreColor(strategy.composite_score)}`}>
                      {strategy.composite_score}
                    </div>
                    <div className="text-sm text-[#787B86]">Score</div>
                  </div>
                </div>

                <div className="mt-4 flex items-center gap-6 text-sm">
                  <div>
                    <span className="text-[#787B86]">Return: </span>
                    <span className={strategy.annual_return >= 0 ? 'text-[#089981]' : 'text-[#F23645]'}>
                      {strategy.annual_return >= 0 ? '+' : ''}{strategy.annual_return}%
                    </span>
                  </div>
                  <div>
                    <span className="text-[#787B86]">Win Rate: </span>
                    <span className="text-[#D1D4DC]">{strategy.win_rate}%</span>
                  </div>
                  <div>
                    <span className="text-[#787B86]">Sharpe: </span>
                    <span className="text-[#D1D4DC]">{strategy.sharpe_ratio}</span>
                  </div>
                  <div>
                    <span className="text-[#787B86]">Drawdown: </span>
                    <span className="text-[#F23645]">-{strategy.max_drawdown}%</span>
                  </div>
                  <div>
                    <span className="text-[#787B86]">Clones: </span>
                    <span className="text-[#D1D4DC]">{strategy.clone_count}</span>
                  </div>
                </div>

                <div className="mt-4 flex items-center gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCloneStrategy(strategy.id);
                    }}
                    className="bg-[#2962FF] text-white px-4 py-2 rounded-lg text-sm
                             hover:bg-[#1E53E5] transition-colors"
                  >
                    Clone Strategy
                  </button>
                  <div className="flex items-center gap-1 text-[#FF9800]">
                    {'★'.repeat(Math.round(strategy.user_rating))}
                    {'☆'.repeat(5 - Math.round(strategy.user_rating))}
                    <span className="text-sm text-[#787B86] ml-1">({strategy.user_rating})</span>
                  </div>
                </div>
              </div>
            ))}

            {strategies.length === 0 && (
              <div className="text-center py-12">
                <p className="text-[#787B86]">No strategies found matching your criteria.</p>
              </div>
            )}
          </div>
        )}

        {/* Pagination */}
        {pagination.total_pages > 1 && (
          <div className="flex justify-center gap-2 mt-8">
            <button
              onClick={() => setPagination(prev => ({ ...prev, page: Math.max(1, prev.page - 1) }))}
              disabled={pagination.page === 1}
              className="px-4 py-2 bg-[#1E222D] border border-[#2A2E39] rounded-lg
                       hover:border-[#3A3E49] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-[#787B86]">
              Page {pagination.page} of {pagination.total_pages}
            </span>
            <button
              onClick={() => setPagination(prev => ({ ...prev, page: Math.min(prev.total_pages, prev.page + 1) }))}
              disabled={pagination.page === pagination.total_pages}
              className="px-4 py-2 bg-[#1E222D] border border-[#2A2E39] rounded-lg
                       hover:border-[#3A3E49] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default StrategyLeaderboard;
