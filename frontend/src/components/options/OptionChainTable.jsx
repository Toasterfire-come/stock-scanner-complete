/**
 * Option Chain Table Component
 * Displays calls and puts side-by-side with Greeks
 */

import React, { useState, useMemo } from 'react';
import { TrendingUp, TrendingDown, Filter } from 'lucide-react';

const OptionChainTable = ({ chainData, selectedExpiration, ticker }) => {
  const [filterType, setFilterType] = useState('all'); // all, itm, otm, atm
  const [sortBy, setSortBy] = useState('strike'); // strike, volume, oi, delta

  if (!chainData || !chainData.chains || chainData.chains.length === 0) {
    return (
      <div className="empty-chain">
        <p>No option chain data available</p>
      </div>
    );
  }

  // Get the chain for selected expiration
  const selectedChain = chainData.chains.find(
    (chain) => chain.expiration_date === selectedExpiration
  );

  if (!selectedChain) {
    return (
      <div className="empty-chain">
        <p>No data available for selected expiration</p>
      </div>
    );
  }

  const { calls, puts } = selectedChain;
  const spotPrice = chainData.spot_price;

  // Get all unique strikes from both calls and puts
  const allStrikes = useMemo(() => {
    const callStrikes = calls.map((c) => c.strike);
    const putStrikes = puts.map((p) => p.strike);
    const uniqueStrikes = [...new Set([...callStrikes, ...putStrikes])];
    return uniqueStrikes.sort((a, b) => a - b);
  }, [calls, puts]);

  // Filter strikes based on moneyness
  const filteredStrikes = useMemo(() => {
    return allStrikes.filter((strike) => {
      if (filterType === 'all') return true;
      if (filterType === 'itm') {
        return strike < spotPrice; // ITM calls or ITM puts
      }
      if (filterType === 'otm') {
        return strike > spotPrice;
      }
      if (filterType === 'atm') {
        return Math.abs(strike - spotPrice) <= spotPrice * 0.02; // Within 2% of spot
      }
      return true;
    });
  }, [allStrikes, filterType, spotPrice]);

  // Helper to find contract by strike
  const findContract = (contracts, strike) => {
    return contracts.find((c) => c.strike === strike);
  };

  // Helper to format numbers
  const formatPrice = (val) => (val ? `$${val.toFixed(2)}` : '-');
  const formatPercent = (val) => (val ? `${(val * 100).toFixed(2)}%` : '-');
  const formatGreek = (val, decimals = 4) => (val !== null && val !== undefined ? val.toFixed(decimals) : '-');
  const formatVolume = (val) => (val ? val.toLocaleString() : '-');

  // Get moneyness class
  const getMoneyness = (strike, optionType) => {
    if (optionType === 'call') {
      return strike < spotPrice ? 'itm' : strike > spotPrice ? 'otm' : 'atm';
    } else {
      return strike > spotPrice ? 'itm' : strike < spotPrice ? 'otm' : 'atm';
    }
  };

  return (
    <div className="option-chain-wrapper">
      {/* Controls */}
      <div className="chain-controls">
        <div className="filter-group">
          <Filter size={16} />
          <span>Filter:</span>
          <button
            className={`filter-btn ${filterType === 'all' ? 'active' : ''}`}
            onClick={() => setFilterType('all')}
          >
            All
          </button>
          <button
            className={`filter-btn ${filterType === 'itm' ? 'active' : ''}`}
            onClick={() => setFilterType('itm')}
          >
            ITM
          </button>
          <button
            className={`filter-btn ${filterType === 'atm' ? 'active' : ''}`}
            onClick={() => setFilterType('atm')}
          >
            ATM
          </button>
          <button
            className={`filter-btn ${filterType === 'otm' ? 'active' : ''}`}
            onClick={() => setFilterType('otm')}
          >
            OTM
          </button>
        </div>

        <div className="info-text">
          Spot Price: <strong>${spotPrice.toFixed(2)}</strong> |
          Expiration: <strong>{new Date(selectedExpiration).toLocaleDateString()}</strong> |
          Strikes: <strong>{filteredStrikes.length}</strong>
        </div>
      </div>

      {/* Option Chain Table */}
      <div className="option-chain-table-container">
        <table className="option-chain-table">
          <thead>
            <tr>
              <th colSpan="9" className="section-header calls-header">
                <TrendingUp size={18} />
                CALLS
              </th>
              <th className="strike-column">STRIKE</th>
              <th colSpan="9" className="section-header puts-header">
                <TrendingDown size={18} />
                PUTS
              </th>
            </tr>
            <tr>
              {/* Calls columns */}
              <th>Last</th>
              <th>Bid</th>
              <th>Ask</th>
              <th>Volume</th>
              <th>OI</th>
              <th>IV</th>
              <th>Delta</th>
              <th>Gamma</th>
              <th>Theta</th>

              {/* Strike column */}
              <th className="strike-column">Strike</th>

              {/* Puts columns */}
              <th>Theta</th>
              <th>Gamma</th>
              <th>Delta</th>
              <th>IV</th>
              <th>OI</th>
              <th>Volume</th>
              <th>Ask</th>
              <th>Bid</th>
              <th>Last</th>
            </tr>
          </thead>
          <tbody>
            {filteredStrikes.map((strike) => {
              const callContract = findContract(calls, strike);
              const putContract = findContract(puts, strike);
              const isAtmStrike = Math.abs(strike - spotPrice) < 0.5;

              return (
                <tr key={strike} className={isAtmStrike ? 'atm-row' : ''}>
                  {/* CALLS DATA */}
                  {callContract ? (
                    <>
                      <td className={`price-cell ${getMoneyness(strike, 'call')}`}>
                        {formatPrice(callContract.last_price)}
                      </td>
                      <td>{formatPrice(callContract.bid)}</td>
                      <td>{formatPrice(callContract.ask)}</td>
                      <td className="volume-cell">{formatVolume(callContract.volume)}</td>
                      <td className="oi-cell">{formatVolume(callContract.open_interest)}</td>
                      <td className="iv-cell">{formatPercent(callContract.implied_volatility)}</td>
                      <td className={`delta-cell ${callContract.delta > 0.5 ? 'high' : 'low'}`}>
                        {formatGreek(callContract.delta)}
                      </td>
                      <td className="gamma-cell">{formatGreek(callContract.gamma)}</td>
                      <td className="theta-cell negative">{formatGreek(callContract.theta)}</td>
                    </>
                  ) : (
                    <>
                      <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                    </>
                  )}

                  {/* STRIKE */}
                  <td className={`strike-cell ${isAtmStrike ? 'atm-strike' : ''}`}>
                    ${strike.toFixed(2)}
                  </td>

                  {/* PUTS DATA */}
                  {putContract ? (
                    <>
                      <td className="theta-cell negative">{formatGreek(putContract.theta)}</td>
                      <td className="gamma-cell">{formatGreek(putContract.gamma)}</td>
                      <td className={`delta-cell ${Math.abs(putContract.delta) > 0.5 ? 'high' : 'low'}`}>
                        {formatGreek(putContract.delta)}
                      </td>
                      <td className="iv-cell">{formatPercent(putContract.implied_volatility)}</td>
                      <td className="oi-cell">{formatVolume(putContract.open_interest)}</td>
                      <td className="volume-cell">{formatVolume(putContract.volume)}</td>
                      <td>{formatPrice(putContract.ask)}</td>
                      <td>{formatPrice(putContract.bid)}</td>
                      <td className={`price-cell ${getMoneyness(strike, 'put')}`}>
                        {formatPrice(putContract.last_price)}
                      </td>
                    </>
                  ) : (
                    <>
                      <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td>
                    </>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="chain-legend">
        <div className="legend-item">
          <span className="legend-color itm"></span>
          <span>In The Money (ITM)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color atm"></span>
          <span>At The Money (ATM)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color otm"></span>
          <span>Out of The Money (OTM)</span>
        </div>
      </div>
    </div>
  );
};

export default OptionChainTable;
