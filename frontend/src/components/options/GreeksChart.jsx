/**
 * Greeks Chart Component
 * Visualizes Delta, Gamma, Theta, Vega vs Strike Price
 */

import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { Info } from 'lucide-react';

const GreeksChart = ({ greeksData, ticker, expiration }) => {
  const [selectedGreek, setSelectedGreek] = useState('all'); // all, delta, gamma, theta, vega
  const [optionType, setOptionType] = useState('calls'); // calls, puts, both

  if (!greeksData || !greeksData.strikes || greeksData.strikes.length === 0) {
    return (
      <div className="empty-greeks">
        <p>No Greeks data available</p>
      </div>
    );
  }

  const { strikes, calls, puts, spot_price } = greeksData;

  // Prepare chart data
  const chartData = strikes.map((strike, index) => {
    const dataPoint = { strike };

    if (optionType === 'calls' || optionType === 'both') {
      dataPoint.callDelta = calls.delta[index];
      dataPoint.callGamma = calls.gamma[index];
      dataPoint.callTheta = calls.theta[index];
      dataPoint.callVega = calls.vega[index];
    }

    if (optionType === 'puts' || optionType === 'both') {
      dataPoint.putDelta = puts.delta[index];
      dataPoint.putGamma = puts.gamma[index];
      dataPoint.putTheta = puts.theta[index];
      dataPoint.putVega = puts.vega[index];
    }

    return dataPoint;
  });

  // Greek definitions for tooltips
  const greekInfo = {
    delta: 'Rate of change in option price with respect to $1 change in underlying price',
    gamma: 'Rate of change in delta with respect to $1 change in underlying price',
    theta: 'Rate of time decay - option value loss per day',
    vega: 'Sensitivity to 1% change in implied volatility'
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="greeks-tooltip">
          <p className="tooltip-label">Strike: ${label.toFixed(2)}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value?.toFixed(4) || '-'}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Render individual Greek chart
  const renderGreekChart = (greekName, greekTitle) => {
    const callKey = `call${greekName.charAt(0).toUpperCase() + greekName.slice(1)}`;
    const putKey = `put${greekName.charAt(0).toUpperCase() + greekName.slice(1)}`;

    return (
      <div key={greekName} className="greek-chart-container">
        <div className="chart-header">
          <h3>{greekTitle}</h3>
          <div className="greek-info">
            <Info size={16} />
            <span className="greek-tooltip-text">{greekInfo[greekName]}</span>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis
              dataKey="strike"
              label={{ value: 'Strike Price', position: 'insideBottom', offset: -5 }}
              stroke="#666"
            />
            <YAxis
              label={{ value: greekTitle, angle: -90, position: 'insideLeft' }}
              stroke="#666"
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <ReferenceLine x={spot_price} stroke="#ff6b6b" strokeDasharray="5 5" label="Spot" />

            {(optionType === 'calls' || optionType === 'both') && (
              <Line
                type="monotone"
                dataKey={callKey}
                stroke="#10b981"
                strokeWidth={2}
                dot={false}
                name={`Call ${greekTitle}`}
              />
            )}

            {(optionType === 'puts' || optionType === 'both') && (
              <Line
                type="monotone"
                dataKey={putKey}
                stroke="#ef4444"
                strokeWidth={2}
                dot={false}
                name={`Put ${greekTitle}`}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  };

  return (
    <div className="greeks-chart-wrapper">
      {/* Controls */}
      <div className="greeks-controls">
        <div className="control-group">
          <label>Option Type:</label>
          <div className="btn-group">
            <button
              className={`control-btn ${optionType === 'calls' ? 'active' : ''}`}
              onClick={() => setOptionType('calls')}
            >
              Calls
            </button>
            <button
              className={`control-btn ${optionType === 'puts' ? 'active' : ''}`}
              onClick={() => setOptionType('puts')}
            >
              Puts
            </button>
            <button
              className={`control-btn ${optionType === 'both' ? 'active' : ''}`}
              onClick={() => setOptionType('both')}
            >
              Both
            </button>
          </div>
        </div>

        <div className="control-group">
          <label>Display:</label>
          <div className="btn-group">
            <button
              className={`control-btn ${selectedGreek === 'all' ? 'active' : ''}`}
              onClick={() => setSelectedGreek('all')}
            >
              All Greeks
            </button>
            <button
              className={`control-btn ${selectedGreek === 'delta' ? 'active' : ''}`}
              onClick={() => setSelectedGreek('delta')}
            >
              Delta
            </button>
            <button
              className={`control-btn ${selectedGreek === 'gamma' ? 'active' : ''}`}
              onClick={() => setSelectedGreek('gamma')}
            >
              Gamma
            </button>
            <button
              className={`control-btn ${selectedGreek === 'theta' ? 'active' : ''}`}
              onClick={() => setSelectedGreek('theta')}
            >
              Theta
            </button>
            <button
              className={`control-btn ${selectedGreek === 'vega' ? 'active' : ''}`}
              onClick={() => setSelectedGreek('vega')}
            >
              Vega
            </button>
          </div>
        </div>
      </div>

      {/* Info Bar */}
      <div className="greeks-info-bar">
        <span>Ticker: <strong>{ticker}</strong></span>
        <span>Expiration: <strong>{new Date(expiration).toLocaleDateString()}</strong></span>
        <span>Spot: <strong>${spot_price.toFixed(2)}</strong></span>
      </div>

      {/* Charts */}
      <div className="greeks-charts-grid">
        {selectedGreek === 'all' ? (
          <>
            {renderGreekChart('delta', 'Delta (Δ)')}
            {renderGreekChart('gamma', 'Gamma (Γ)')}
            {renderGreekChart('theta', 'Theta (Θ)')}
            {renderGreekChart('vega', 'Vega (ν)')}
          </>
        ) : (
          renderGreekChart(
            selectedGreek,
            selectedGreek.charAt(0).toUpperCase() + selectedGreek.slice(1)
          )
        )}
      </div>

      {/* Greeks Explanation */}
      <div className="greeks-explanation">
        <h4>Understanding the Greeks</h4>
        <div className="explanation-grid">
          <div className="explanation-item">
            <strong>Delta (Δ):</strong> Measures how much the option price changes for a $1 move in the underlying.
            Calls: 0 to 1, Puts: -1 to 0.
          </div>
          <div className="explanation-item">
            <strong>Gamma (Γ):</strong> Measures the rate of change of delta. Higher gamma means delta changes faster.
            Highest for ATM options.
          </div>
          <div className="explanation-item">
            <strong>Theta (Θ):</strong> Time decay - how much value the option loses each day.
            Always negative (options lose value over time).
          </div>
          <div className="explanation-item">
            <strong>Vega (ν):</strong> Sensitivity to volatility changes. How much the option price changes for a 1% change in IV.
            Highest for ATM options with longer expiration.
          </div>
        </div>
      </div>
    </div>
  );
};

export default GreeksChart;
