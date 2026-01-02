import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp, TrendingDown, DollarSign, Target, BarChart3,
  PieChart, Activity, RefreshCw, Plus, X, ArrowUpRight,
  ArrowDownRight, Calendar, Award, AlertCircle, CheckCircle2
} from 'lucide-react';
import './PaperTrading.css';

const PaperTrading = () => {
  const [account, setAccount] = useState(null);
  const [positions, setPositions] = useState([]);
  const [tradeHistory, setTradeHistory] = useState([]);
  const [performanceMetrics, setPerformanceMetrics] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [orderForm, setOrderForm] = useState({
    ticker: '',
    shares: '',
    orderType: 'market',
    side: 'long',
    limitPrice: '',
    takeProfitPrice: '',
    stopLossPrice: '',
    notes: ''
  });
  const [orderError, setOrderError] = useState('');
  const [orderSuccess, setOrderSuccess] = useState('');

  useEffect(() => {
    fetchAccountData();
  }, []);

  const fetchAccountData = async () => {
    try {
      setLoading(true);
      const [accountRes, positionsRes, historyRes, metricsRes, leaderboardRes] = await Promise.all([
        axios.get('/api/stocks/paper-trading/account/'),
        axios.get('/api/stocks/paper-trading/positions/'),
        axios.get('/api/stocks/paper-trading/history/?limit=20'),
        axios.get('/api/stocks/paper-trading/performance/?period_type=daily&limit=30'),
        axios.get('/api/stocks/paper-trading/leaderboard/?limit=10')
      ]);

      setAccount(accountRes.data.account);
      setPositions(positionsRes.data.positions || []);
      setTradeHistory(historyRes.data.trades || []);
      setPerformanceMetrics(metricsRes.data.metrics || []);
      setLeaderboard(leaderboardRes.data.leaderboard || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching account data:', error);
      setLoading(false);
    }
  };

  const handleOrderSubmit = async (e) => {
    e.preventDefault();
    setOrderError('');
    setOrderSuccess('');

    try {
      const orderData = {
        ticker: orderForm.ticker.toUpperCase(),
        shares: parseFloat(orderForm.shares),
        order_type: orderForm.orderType,
        side: orderForm.side,
        notes: orderForm.notes
      };

      if (orderForm.orderType === 'limit') {
        orderData.limit_price = parseFloat(orderForm.limitPrice);
      } else if (orderForm.orderType === 'bracket') {
        orderData.take_profit_price = parseFloat(orderForm.takeProfitPrice);
        orderData.stop_loss_price = parseFloat(orderForm.stopLossPrice);
      }

      const response = await axios.post('/api/stocks/paper-trading/orders/place/', orderData);

      if (response.data.success) {
        setOrderSuccess(response.data.message);
        setTimeout(() => {
          setShowOrderModal(false);
          resetOrderForm();
          fetchAccountData();
        }, 2000);
      }
    } catch (error) {
      setOrderError(error.response?.data?.error || 'Failed to place order');
    }
  };

  const handleClosePosition = async (tradeId) => {
    if (!window.confirm('Are you sure you want to close this position at current market price?')) {
      return;
    }

    try {
      const response = await axios.post(`/api/stocks/paper-trading/positions/${tradeId}/close/`);
      if (response.data.success) {
        fetchAccountData();
      }
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to close position');
    }
  };

  const handleResetAccount = async () => {
    if (!window.confirm('Are you sure you want to reset your paper trading account? This will close all positions and reset your balance.')) {
      return;
    }

    try {
      const response = await axios.post('/api/stocks/paper-trading/account/reset/');
      if (response.data.success) {
        fetchAccountData();
      }
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to reset account');
    }
  };

  const resetOrderForm = () => {
    setOrderForm({
      ticker: '',
      shares: '',
      orderType: 'market',
      side: 'long',
      limitPrice: '',
      takeProfitPrice: '',
      stopLossPrice: '',
      notes: ''
    });
    setOrderError('');
    setOrderSuccess('');
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="paper-trading-loading">
        <div className="loading-spinner"></div>
        <p>Loading Paper Trading Account...</p>
      </div>
    );
  }

  return (
    <div className="paper-trading-container">
      {/* Header */}
      <div className="paper-trading-header">
        <div>
          <h1 className="page-title">
            <Activity className="title-icon" />
            Paper Trading
          </h1>
          <p className="page-subtitle">
            Practice trading with virtual funds - No real money at risk
          </p>
        </div>
        <div className="header-actions">
          <button
            className="btn-refresh"
            onClick={fetchAccountData}
            title="Refresh"
          >
            <RefreshCw size={18} />
          </button>
          <button
            className="btn-new-order"
            onClick={() => setShowOrderModal(true)}
          >
            <Plus size={18} />
            New Order
          </button>
          <button
            className="btn-reset"
            onClick={handleResetAccount}
            title="Reset Account"
          >
            Reset Account
          </button>
        </div>
      </div>

      {/* Account Summary Cards */}
      {account && (
        <div className="account-summary-grid">
          <div className="summary-card">
            <div className="summary-icon blue">
              <DollarSign size={24} />
            </div>
            <div className="summary-content">
              <div className="summary-label">Total Value</div>
              <div className="summary-value">{formatCurrency(account.account_value)}</div>
              <div className={`summary-change ${account.total_return >= 0 ? 'positive' : 'negative'}`}>
                {formatPercent(account.total_return)} all-time
              </div>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon green">
              <TrendingUp size={24} />
            </div>
            <div className="summary-content">
              <div className="summary-label">Cash Balance</div>
              <div className="summary-value">{formatCurrency(account.cash_balance)}</div>
              <div className="summary-meta">
                {account.equity_value > 0 && `${formatCurrency(account.equity_value)} in positions`}
              </div>
            </div>
          </div>

          <div className="summary-card">
            <div className={`summary-icon ${account.total_profit_loss >= 0 ? 'green' : 'red'}`}>
              {account.total_profit_loss >= 0 ? <ArrowUpRight size={24} /> : <ArrowDownRight size={24} />}
            </div>
            <div className="summary-content">
              <div className="summary-label">Total P/L</div>
              <div className={`summary-value ${account.total_profit_loss >= 0 ? 'positive' : 'negative'}`}>
                {formatCurrency(account.total_profit_loss)}
              </div>
              <div className="summary-meta">
                {formatCurrency(account.realized_pl)} realized, {formatCurrency(account.unrealized_pl)} unrealized
              </div>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon purple">
              <Target size={24} />
            </div>
            <div className="summary-content">
              <div className="summary-label">Win Rate</div>
              <div className="summary-value">{account.win_rate.toFixed(1)}%</div>
              <div className="summary-meta">
                {account.winning_trades}W / {account.losing_trades}L of {account.total_trades} trades
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="tabs-container">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <BarChart3 size={18} />
            Overview
          </button>
          <button
            className={`tab ${activeTab === 'positions' ? 'active' : ''}`}
            onClick={() => setActiveTab('positions')}
          >
            <PieChart size={18} />
            Positions ({positions.length})
          </button>
          <button
            className={`tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <Calendar size={18} />
            History
          </button>
          <button
            className={`tab ${activeTab === 'leaderboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('leaderboard')}
          >
            <Award size={18} />
            Leaderboard
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && account && (
          <div className="overview-tab">
            <div className="performance-chart-placeholder">
              <h3>Account Performance (30 Days)</h3>
              <p className="chart-placeholder-text">
                📊 Performance chart with equity curve would go here
              </p>
              {performanceMetrics.length > 0 && (
                <div className="metrics-preview">
                  <p>Latest daily return: {formatPercent(performanceMetrics[0].period_return)}</p>
                  <p>Trades today: {performanceMetrics[0].trades_closed}</p>
                </div>
              )}
            </div>

            <div className="quick-stats-grid">
              <div className="stat-box">
                <div className="stat-label">Today's P/L</div>
                <div className={`stat-value ${account.today_pl >= 0 ? 'positive' : 'negative'}`}>
                  {formatCurrency(account.today_pl)}
                </div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Open Positions</div>
                <div className="stat-value">{account.open_positions_count}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Max Drawdown</div>
                <div className="stat-value negative">{formatPercent(account.max_drawdown)}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Sharpe Ratio</div>
                <div className="stat-value">
                  {account.sharpe_ratio ? account.sharpe_ratio.toFixed(2) : 'N/A'}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'positions' && (
          <div className="positions-tab">
            {positions.length === 0 ? (
              <div className="empty-state">
                <AlertCircle size={48} />
                <h3>No Open Positions</h3>
                <p>Place your first order to start practicing trading</p>
                <button className="btn-primary" onClick={() => setShowOrderModal(true)}>
                  <Plus size={18} />
                  Place Order
                </button>
              </div>
            ) : (
              <div className="positions-table-container">
                <table className="positions-table">
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Side</th>
                      <th>Shares</th>
                      <th>Entry Price</th>
                      <th>Current Price</th>
                      <th>Market Value</th>
                      <th>Unrealized P/L</th>
                      <th>Unrealized %</th>
                      <th>Stop/Target</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {positions.map((position) => (
                      <tr key={position.id}>
                        <td className="symbol-cell">
                          <strong>{position.ticker}</strong>
                          <div className="company-name">{position.company_name}</div>
                        </td>
                        <td>
                          <span className={`side-badge ${position.side}`}>
                            {position.side.toUpperCase()}
                          </span>
                        </td>
                        <td>{position.shares}</td>
                        <td>{formatCurrency(position.entry_price)}</td>
                        <td>{formatCurrency(position.current_price)}</td>
                        <td>{formatCurrency(position.current_value)}</td>
                        <td className={position.unrealized_pl >= 0 ? 'positive' : 'negative'}>
                          {formatCurrency(position.unrealized_pl)}
                        </td>
                        <td className={position.unrealized_pl_pct >= 0 ? 'positive' : 'negative'}>
                          {formatPercent(position.unrealized_pl_pct)}
                        </td>
                        <td className="bracket-prices">
                          {position.stop_loss_price && (
                            <div className="stop-loss">SL: {formatCurrency(position.stop_loss_price)}</div>
                          )}
                          {position.take_profit_price && (
                            <div className="take-profit">TP: {formatCurrency(position.take_profit_price)}</div>
                          )}
                          {!position.stop_loss_price && !position.take_profit_price && '-'}
                        </td>
                        <td>
                          <button
                            className="btn-close-position"
                            onClick={() => handleClosePosition(position.id)}
                          >
                            Close
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="history-tab">
            {tradeHistory.length === 0 ? (
              <div className="empty-state">
                <Calendar size={48} />
                <h3>No Trade History</h3>
                <p>Your closed trades will appear here</p>
              </div>
            ) : (
              <div className="history-table-container">
                <table className="history-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Symbol</th>
                      <th>Side</th>
                      <th>Shares</th>
                      <th>Entry</th>
                      <th>Exit</th>
                      <th>P/L</th>
                      <th>%</th>
                      <th>Hold Time</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tradeHistory.map((trade) => (
                      <tr key={trade.id}>
                        <td>{formatDate(trade.closed_at || trade.created_at)}</td>
                        <td>
                          <strong>{trade.ticker}</strong>
                        </td>
                        <td>
                          <span className={`side-badge ${trade.side}`}>
                            {trade.side.toUpperCase()}
                          </span>
                        </td>
                        <td>{trade.shares}</td>
                        <td>{formatCurrency(trade.entry_price)}</td>
                        <td>{trade.exit_price ? formatCurrency(trade.exit_price) : '-'}</td>
                        <td className={trade.realized_pl >= 0 ? 'positive' : 'negative'}>
                          {trade.realized_pl ? formatCurrency(trade.realized_pl) : '-'}
                        </td>
                        <td className={trade.realized_pl_pct >= 0 ? 'positive' : 'negative'}>
                          {trade.realized_pl_pct ? formatPercent(trade.realized_pl_pct) : '-'}
                        </td>
                        <td>
                          {trade.holding_period_days !== null
                            ? `${trade.holding_period_days}d`
                            : '-'}
                        </td>
                        <td>
                          <span className={`status-badge ${trade.status}`}>
                            {trade.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'leaderboard' && (
          <div className="leaderboard-tab">
            <div className="leaderboard-header">
              <h3>Top Paper Traders</h3>
              <p>See how you rank against other traders</p>
            </div>
            {leaderboard.length === 0 ? (
              <div className="empty-state">
                <Award size={48} />
                <h3>Leaderboard Coming Soon</h3>
                <p>Start trading to see your ranking</p>
              </div>
            ) : (
              <div className="leaderboard-list">
                {leaderboard.map((entry) => (
                  <div key={entry.rank} className="leaderboard-item">
                    <div className="rank-badge">#{entry.rank}</div>
                    <div className="leaderboard-info">
                      <div className="username">{entry.username}</div>
                      <div className="account-name">{entry.account_name}</div>
                    </div>
                    <div className="leaderboard-stats">
                      <div className={`return ${entry.total_return >= 0 ? 'positive' : 'negative'}`}>
                        {formatPercent(entry.total_return)}
                      </div>
                      <div className="trades-count">{entry.total_trades} trades</div>
                      <div className="win-rate">{entry.win_rate.toFixed(1)}% WR</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Order Modal */}
      <AnimatePresence>
        {showOrderModal && (
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowOrderModal(false)}
          >
            <motion.div
              className="modal-content"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-header">
                <h2>Place Order</h2>
                <button className="modal-close" onClick={() => setShowOrderModal(false)}>
                  <X size={20} />
                </button>
              </div>

              <form onSubmit={handleOrderSubmit} className="order-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>Symbol</label>
                    <input
                      type="text"
                      value={orderForm.ticker}
                      onChange={(e) => setOrderForm({...orderForm, ticker: e.target.value.toUpperCase()})}
                      placeholder="AAPL"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Shares</label>
                    <input
                      type="number"
                      value={orderForm.shares}
                      onChange={(e) => setOrderForm({...orderForm, shares: e.target.value})}
                      placeholder="100"
                      min="1"
                      step="1"
                      required
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Order Type</label>
                    <select
                      value={orderForm.orderType}
                      onChange={(e) => setOrderForm({...orderForm, orderType: e.target.value})}
                    >
                      <option value="market">Market</option>
                      <option value="limit">Limit</option>
                      <option value="bracket">Bracket (TP/SL)</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Side</label>
                    <select
                      value={orderForm.side}
                      onChange={(e) => setOrderForm({...orderForm, side: e.target.value})}
                    >
                      <option value="long">Long (Buy)</option>
                      {account?.allow_shorting && <option value="short">Short (Sell)</option>}
                    </select>
                  </div>
                </div>

                {orderForm.orderType === 'limit' && (
                  <div className="form-group">
                    <label>Limit Price</label>
                    <input
                      type="number"
                      value={orderForm.limitPrice}
                      onChange={(e) => setOrderForm({...orderForm, limitPrice: e.target.value})}
                      placeholder="150.00"
                      min="0.01"
                      step="0.01"
                      required
                    />
                  </div>
                )}

                {orderForm.orderType === 'bracket' && (
                  <div className="form-row">
                    <div className="form-group">
                      <label>Take Profit Price</label>
                      <input
                        type="number"
                        value={orderForm.takeProfitPrice}
                        onChange={(e) => setOrderForm({...orderForm, takeProfitPrice: e.target.value})}
                        placeholder="160.00"
                        min="0.01"
                        step="0.01"
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Stop Loss Price</label>
                      <input
                        type="number"
                        value={orderForm.stopLossPrice}
                        onChange={(e) => setOrderForm({...orderForm, stopLossPrice: e.target.value})}
                        placeholder="140.00"
                        min="0.01"
                        step="0.01"
                        required
                      />
                    </div>
                  </div>
                )}

                <div className="form-group">
                  <label>Notes (Optional)</label>
                  <textarea
                    value={orderForm.notes}
                    onChange={(e) => setOrderForm({...orderForm, notes: e.target.value})}
                    placeholder="Why are you making this trade?"
                    rows="3"
                  />
                </div>

                {orderError && (
                  <div className="alert alert-error">
                    <AlertCircle size={18} />
                    {orderError}
                  </div>
                )}

                {orderSuccess && (
                  <div className="alert alert-success">
                    <CheckCircle2 size={18} />
                    {orderSuccess}
                  </div>
                )}

                <div className="form-actions">
                  <button type="button" className="btn-secondary" onClick={() => setShowOrderModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary">
                    Place Order
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PaperTrading;
