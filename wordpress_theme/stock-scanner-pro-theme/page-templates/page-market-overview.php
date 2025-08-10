<?php
/**
 * Template Name: Market Overview Page
 * Individual page for comprehensive market data and analysis
 */

get_header(); ?>

<div class="market-overview-page">
    <div class="container">
        <div class="page-header">
            <h1>📊 Market Overview</h1>
            <p class="page-description">Real-time market data, indices performance, and comprehensive market analysis</p>
        </div>

        <div class="market-container">
            <!-- Market Status Banner -->
            <div class="market-status-section mb-6">
                <div class="card p-6">
                    <div class="market-status-banner" id="market-status" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: var(--space-4);">
                        <div class="status-indicator" style="display: flex; align-items: center; gap: var(--space-3);">
                            <span class="status-light open" id="status-light" style="width: 12px; height: 12px; border-radius: 50%; background: var(--color-success); display: inline-block;"></span>
                            <span class="status-text" id="status-text" style="font-weight: 600; color: var(--color-text);">Market Open</span>
                        </div>
                        <div class="market-time" id="market-time" style="color: var(--color-text-muted);">
                            Eastern Time: <span id="current-time">Loading...</span>
                        </div>
                        <div class="next-session" id="next-session" style="color: var(--color-text-muted); font-size: 0.875rem;">
                            Next: Pre-market opens at 4:00 AM ET
                        </div>
                    </div>
                </div>
            </div>

            <!-- Major Indices -->
            <div class="indices-section mb-6">
                <div class="card p-6">
                    <h2 style="margin-bottom: var(--space-5); color: var(--color-text);">📈 Major Indices</h2>
                    <div class="indices-grid" id="indices-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--space-4);">
                        <!-- Indices will be loaded here -->
                    </div>
                </div>
            </div>

            <!-- Market Movers -->
            <div class="movers-section mb-6">
                <div class="card p-6">
                    <div class="movers-tabs" style="display: flex; gap: var(--space-2); margin-bottom: var(--space-5); border-bottom: 2px solid var(--color-border);">
                        <button class="tab-btn active" data-tab="gainers" style="padding: var(--space-3) var(--space-4); border: none; background: none; color: var(--color-primary); border-bottom: 2px solid var(--color-primary); cursor: pointer; font-weight: 600;">🚀 Top Gainers</button>
                        <button class="tab-btn" data-tab="losers" style="padding: var(--space-3) var(--space-4); border: none; background: none; color: var(--color-text-muted); border-bottom: 2px solid transparent; cursor: pointer;">📉 Top Losers</button>
                        <button class="tab-btn" data-tab="active" style="padding: var(--space-3) var(--space-4); border: none; background: none; color: var(--color-text-muted); border-bottom: 2px solid transparent; cursor: pointer;">⚡ Most Active</button>
                    </div>
                    <div class="movers-content">
                        <div id="gainers-content" class="tab-content active" style="display: block;">
                            <div class="movers-grid" id="gainers-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--space-4);">
                                <!-- Top gainers will be loaded here -->
                            </div>
                        </div>
                        <div id="losers-content" class="tab-content" style="display: none;">
                            <div class="movers-grid" id="losers-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--space-4);">
                                <!-- Top losers will be loaded here -->
                            </div>
                        </div>
                        <div id="active-content" class="tab-content" style="display: none;">
                            <div class="movers-grid" id="active-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--space-4);">
                                <!-- Most active will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sector Performance -->
            <div class="sectors-section mb-6">
                <div class="card p-6">
                    <h2 style="margin-bottom: var(--space-5); color: var(--color-text);">🏢 Sector Performance</h2>
                    <div class="sectors-grid" id="sectors-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--space-4);">
                        <!-- Sector performance will be loaded here -->
                    </div>
                </div>
            </div>

            <!-- Market Breadth -->
            <div class="breadth-section mb-6">
                <div class="card p-6">
                    <h2 style="margin-bottom: var(--space-5); color: var(--color-text);">📊 Market Breadth</h2>
                    <div class="breadth-cards" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: var(--space-5);">
                        <div class="breadth-card card p-4">
                            <h3 style="margin-bottom: var(--space-4); color: var(--color-text);">Advance/Decline</h3>
                            <div class="breadth-chart" style="margin-bottom: var(--space-4);">
                                <canvas id="advance-decline-chart" style="max-height: 200px;"></canvas>
                            </div>
                            <div class="breadth-stats" id="advance-decline-stats">
                                <!-- Stats will be loaded here -->
                            </div>
                        </div>
                        
                        <div class="breadth-card card p-4">
                            <h3 style="margin-bottom: var(--space-4); color: var(--color-text);">New Highs/Lows</h3>
                            <div class="breadth-chart" style="margin-bottom: var(--space-4);">
                                <canvas id="highs-lows-chart" style="max-height: 200px;"></canvas>
                            </div>
                            <div class="breadth-stats" id="highs-lows-stats">
                                <!-- Stats will be loaded here -->
                            </div>
                        </div>
                        
                        <div class="breadth-card card p-4">
                            <h3 style="margin-bottom: var(--space-4); color: var(--color-text);">Volume Analysis</h3>
                            <div class="breadth-chart" style="margin-bottom: var(--space-4);">
                                <canvas id="volume-analysis-chart" style="max-height: 200px;"></canvas>
                            </div>
                            <div class="breadth-stats" id="volume-analysis-stats">
                                <!-- Stats will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Economic Calendar -->
            <div class="calendar-section mb-6">
                <div class="card p-6">
                    <h2 style="margin-bottom: var(--space-5); color: var(--color-text);">📅 Economic Calendar</h2>
                    <div class="calendar-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-5); background: var(--color-bg-light); padding: var(--space-4); border-radius: var(--border-radius-lg); box-shadow: var(--shadow-sm);">
                        <div class="date-selector" style="display: flex; align-items: center; gap: var(--space-3);">
                            <button id="prev-day" class="btn btn-outline" style="padding: var(--space-2) var(--space-3); border: 2px solid var(--color-primary); border-radius: var(--border-radius-md); color: var(--color-primary); background: none; font-weight: 600; cursor: pointer; transition: all 0.3s ease;">← Previous</button>
                            <span id="selected-date" style="font-weight: 600; color: var(--color-text); min-width: 100px; text-align: center;">Today</span>
                            <button id="next-day" class="btn btn-outline" style="padding: var(--space-2) var(--space-3); border: 2px solid var(--color-primary); border-radius: var(--border-radius-md); color: var(--color-primary); background: none; font-weight: 600; cursor: pointer; transition: all 0.3s ease;">Next →</button>
                        </div>
                        <div class="importance-filter" style="display: flex; gap: var(--space-3);">
                            <label style="display: flex; align-items: center; gap: var(--space-2); font-size: 0.9rem; color: var(--color-text-muted); cursor: pointer;">
                                <input type="checkbox" checked> High Impact
                            </label>
                            <label style="display: flex; align-items: center; gap: var(--space-2); font-size: 0.9rem; color: var(--color-text-muted); cursor: pointer;">
                                <input type="checkbox" checked> Medium Impact
                            </label>
                            <label style="display: flex; align-items: center; gap: var(--space-2); font-size: 0.9rem; color: var(--color-text-muted); cursor: pointer;">
                                <input type="checkbox"> Low Impact
                            </label>
                        </div>
                    </div>
                    <div class="calendar-events" id="calendar-events" style="background: var(--color-bg-light); border-radius: var(--border-radius-lg); box-shadow: var(--shadow-sm); overflow: hidden;">
                        <!-- Economic events will be loaded here -->
                    </div>
                </div>
            </div>

            <!-- Market News Summary -->
            <div class="news-summary-section mb-6">
                <div class="card p-6">
                    <h2 style="margin-bottom: var(--space-5); color: var(--color-text);">📰 Market News Summary</h2>
                    <div class="news-summary-cards" id="news-summary" style="display: grid; gap: var(--space-4); margin-bottom: var(--space-5);">
                        <!-- News summary will be loaded here -->
                    </div>
                    <div class="news-actions" style="text-align: center;">
                        <a href="/stock-news/" class="btn btn-primary" style="padding: var(--space-3) var(--space-4); border: none; border-radius: var(--border-radius-md); font-weight: 600; cursor: pointer; transition: all 0.3s ease; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2);">View All News</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.market-overview-page {
    padding: 40px 0;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    min-height: 100vh;
}

.page-header {
    text-align: center;
    margin-bottom: 40px;
}

.page-header h1 {
    color: #2271b1;
    font-size: 2.5rem;
    margin-bottom: 10px;
}

.page-description {
    color: #646970;
    font-size: 1.1rem;
    max-width: 700px;
    margin: 0 auto;
}

.market-container {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    gap: 40px;
}

/* Market Status */
.market-status-banner {
    background: linear-gradient(135deg, #2271b1 0%, #135e96 100%);
    color: white;
    padding: 25px;
    border-radius: 12px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    align-items: center;
    box-shadow: 0 4px 12px rgba(34, 113, 177, 0.3);
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
}

.status-light {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #00a32a;
    animation: pulse-status 2s infinite;
}

.status-light.closed {
    background: #d63638;
}

@keyframes pulse-status {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.status-text {
    font-weight: 600;
    font-size: 1.1rem;
}

.market-time, .next-session {
    font-size: 0.9rem;
    opacity: 0.9;
}

/* Indices */
.indices-section h2,
.movers-section h2,
.sectors-section h2,
.breadth-section h2,
.calendar-section h2,
.news-summary-section h2 {
    color: #1d2327;
    font-size: 1.5rem;
    margin-bottom: 25px;
}

.indices-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
}

.index-card {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border: 1px solid #e1e1e1;
    transition: all 0.3s ease;
}

.index-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}

.index-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.index-name {
    font-weight: 600;
    color: #1d2327;
    font-size: 1.1rem;
}

.index-symbol {
    color: #646970;
    font-size: 0.9rem;
}

.index-price {
    font-size: 1.8rem;
    font-weight: bold;
    color: #1d2327;
    margin-bottom: 5px;
}

.index-change {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
}

.index-change.positive {
    color: #00a32a;
}

.index-change.negative {
    color: #d63638;
}

.index-chart {
    height: 60px;
    margin-top: 15px;
    background: #f8f9fa;
    border-radius: 4px;
    position: relative;
    overflow: hidden;
}

/* Market Movers */
.movers-tabs {
    display: flex;
    gap: 5px;
    margin-bottom: 25px;
    background: white;
    padding: 5px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.tab-btn {
    flex: 1;
    padding: 12px 16px;
    border: none;
    background: transparent;
    color: #646970;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.tab-btn.active {
    background: #2271b1;
    color: white;
}

.tab-btn:hover:not(.active) {
    background: #f0f6ff;
    color: #2271b1;
}

.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
}

.movers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
}

.mover-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border: 1px solid #e1e1e1;
    cursor: pointer;
    transition: all 0.3s ease;
}

.mover-card:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.mover-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.mover-symbol {
    font-weight: 600;
    color: #2271b1;
    font-size: 1rem;
}

.mover-price {
    font-weight: 600;
    color: #1d2327;
}

.mover-change {
    font-weight: 600;
    font-size: 0.9rem;
}

.mover-change.positive {
    color: #00a32a;
}

.mover-change.negative {
    color: #d63638;
}

.mover-company {
    color: #646970;
    font-size: 0.9rem;
    margin-bottom: 8px;
}

.mover-volume {
    color: #646970;
    font-size: 0.8rem;
}

/* Sectors */
.sectors-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
}

.sector-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border: 1px solid #e1e1e1;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.sector-card:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.sector-name {
    font-weight: 600;
    color: #1d2327;
    margin-bottom: 10px;
}

.sector-performance {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 5px;
}

.sector-performance.positive {
    color: #00a32a;
}

.sector-performance.negative {
    color: #d63638;
}

.sector-companies {
    color: #646970;
    font-size: 0.8rem;
}

/* Market Breadth */
.breadth-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 25px;
}

.breadth-card {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border: 1px solid #e1e1e1;
}

.breadth-card h3 {
    margin: 0 0 20px 0;
    color: #1d2327;
    font-size: 1.2rem;
}

.breadth-chart {
    height: 200px;
    margin-bottom: 15px;
}

.breadth-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 15px;
    text-align: center;
}

.stat-item {
    padding: 10px;
    background: #f8f9fa;
    border-radius: 6px;
}

.stat-value {
    font-size: 1.2rem;
    font-weight: bold;
    color: #1d2327;
    margin-bottom: 3px;
}

.stat-label {
    font-size: 0.8rem;
    color: #646970;
}

.volume-metrics {
    display: grid;
    gap: 15px;
}

.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
}

.metric-label {
    color: #646970;
    font-weight: 500;
}

.metric-value {
    color: #1d2327;
    font-weight: 600;
}

/* Economic Calendar */
.calendar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.date-selector {
    display: flex;
    align-items: center;
    gap: 15px;
}

#selected-date {
    font-weight: 600;
    color: #1d2327;
    min-width: 100px;
    text-align: center;
}

.importance-filter {
    display: flex;
    gap: 15px;
}

.importance-filter label {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.9rem;
    color: #646970;
    cursor: pointer;
}

.calendar-events {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    overflow: hidden;
}

.event-item {
    padding: 15px 20px;
    border-bottom: 1px solid #f0f0f0;
    display: grid;
    grid-template-columns: 80px 1fr auto auto;
    gap: 15px;
    align-items: center;
}

.event-time {
    font-weight: 600;
    color: #1d2327;
}

.event-description {
    color: #1d2327;
}

.event-impact {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}

.event-impact.high {
    background: #fef2f2;
    color: #d63638;
}

.event-impact.medium {
    background: #fffbeb;
    color: #d97706;
}

.event-impact.low {
    background: #f0fdf4;
    color: #16a34a;
}

.event-forecast {
    color: #646970;
    font-size: 0.9rem;
}

/* News Summary */
.news-summary-cards {
    display: grid;
    gap: 15px;
    margin-bottom: 25px;
}

.news-summary-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border: 1px solid #e1e1e1;
    cursor: pointer;
    transition: all 0.3s ease;
}

.news-summary-card:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.news-summary-title {
    font-weight: 600;
    color: #1d2327;
    margin-bottom: 8px;
    line-height: 1.4;
}

.news-summary-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #646970;
    font-size: 0.9rem;
}

.news-actions {
    text-align: center;
}

.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
}

.btn-primary {
    background: #2271b1;
    color: white;
}

.btn-primary:hover {
    background: #135e96;
    transform: translateY(-1px);
}

.btn-outline {
    background: transparent;
    color: #2271b1;
    border: 2px solid #2271b1;
}

.btn-outline:hover {
    background: #2271b1;
    color: white;
}

@media (max-width: 768px) {
    .market-status-banner {
        grid-template-columns: 1fr;
        text-align: center;
        gap: 15px;
    }
    
    .movers-tabs {
        flex-direction: column;
    }
    
    .calendar-header {
        flex-direction: column;
        gap: 15px;
    }
    
    .event-item {
        grid-template-columns: 1fr;
        gap: 10px;
        text-align: center;
    }
    
    .breadth-cards {
        grid-template-columns: 1fr;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeMarketStatus();
    loadIndices();
    loadMarketMovers();
    loadSectorPerformance();
    initializeMarketBreadth();
    loadEconomicCalendar();
    loadNewsummary();
    
    // Set up event listeners
    setupTabNavigation();
    setupCalendarNavigation();
    
    // Auto-refresh data every 30 seconds
    setInterval(() => {
        loadIndices();
        loadMarketMovers();
        loadSectorPerformance();
        updateMarketStatus();
    }, 30000);
    
    // Update time every second
    setInterval(updateCurrentTime, 1000);
});

function initializeMarketStatus() {
    updateMarketStatus();
    updateCurrentTime();
}

function updateMarketStatus() {
    const now = new Date();
    const currentHour = now.getHours();
    const isWeekday = now.getDay() >= 1 && now.getDay() <= 5;
    
    const statusLight = document.getElementById('status-light');
    const statusText = document.getElementById('status-text');
    const nextSession = document.getElementById('next-session');
    
    // Simplified market hours (9:30 AM - 4:00 PM ET)
    const isMarketOpen = isWeekday && currentHour >= 9 && currentHour < 16;
    
    if (isMarketOpen) {
        statusLight.className = 'status-light open';
        statusText.textContent = 'Market Open';
        nextSession.textContent = 'Market closes at 4:00 PM ET';
    } else {
        statusLight.className = 'status-light closed';
        statusText.textContent = 'Market Closed';
        nextSession.textContent = isWeekday ? 'Pre-market opens at 4:00 AM ET' : 'Next session: Monday 4:00 AM ET';
    }
}

function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        timeZone: 'America/New_York',
        hour12: true,
        hour: 'numeric',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('current-time').textContent = timeString;
}

function loadIndices() {
    const mockIndices = [
        { name: 'S&P 500', symbol: 'SPX', price: 4756.50, change: 24.85, changePercent: 0.53 },
        { name: 'Dow Jones', symbol: 'DJI', price: 37863.80, change: -45.20, changePercent: -0.12 },
        { name: 'NASDAQ', symbol: 'IXIC', price: 14906.85, change: 67.30, changePercent: 0.45 },
        { name: 'Russell 2000', symbol: 'RUT', price: 2086.45, change: 12.75, changePercent: 0.61 },
        { name: 'VIX', symbol: 'VIX', price: 14.23, change: -0.85, changePercent: -5.64 },
        { name: 'USD Index', symbol: 'DXY', price: 103.45, change: 0.12, changePercent: 0.12 }
    ];
    
    const indicesGrid = document.getElementById('indices-grid');
    indicesGrid.innerHTML = mockIndices.map(index => createIndexCard(index)).join('');
}

function createIndexCard(index) {
    const changeClass = index.change >= 0 ? 'positive' : 'negative';
    const changeIcon = index.change >= 0 ? '↗' : '↘';
    
    return `
        <div class="index-card" onclick="viewIndex('${index.symbol}')">
            <div class="index-header">
                <div>
                    <div class="index-name">${index.name}</div>
                    <div class="index-symbol">${index.symbol}</div>
                </div>
            </div>
            <div class="index-price">${index.price.toLocaleString()}</div>
            <div class="index-change ${changeClass}">
                <span>${changeIcon} ${Math.abs(index.change).toFixed(2)}</span>
                <span>(${index.changePercent.toFixed(2)}%)</span>
            </div>
            <div class="index-chart">
                <!-- Mini chart would go here -->
            </div>
        </div>
    `;
}

function loadMarketMovers() {
    const gainers = [
        { symbol: 'NVDA', company: 'NVIDIA Corp', price: 875.28, change: 45.32, changePercent: 5.46, volume: '38.9M' },
        { symbol: 'TSLA', company: 'Tesla Inc', price: 248.50, change: 18.75, changePercent: 8.16, volume: '95.2M' },
        { symbol: 'AMD', company: 'Advanced Micro Devices', price: 154.20, change: 12.80, changePercent: 9.05, volume: '42.1M' }
    ];
    
    const losers = [
        { symbol: 'META', company: 'Meta Platforms', price: 484.20, change: -15.75, changePercent: -3.15, volume: '18.3M' },
        { symbol: 'NFLX', company: 'Netflix Inc', price: 456.80, change: -12.40, changePercent: -2.64, volume: '8.7M' },
        { symbol: 'PYPL', company: 'PayPal Holdings', price: 58.25, change: -2.85, changePercent: -4.66, volume: '15.2M' }
    ];
    
    const mostActive = [
        { symbol: 'AAPL', company: 'Apple Inc', price: 175.43, change: 2.15, changePercent: 1.24, volume: '152.3M' },
        { symbol: 'TSLA', company: 'Tesla Inc', price: 248.50, change: 18.75, changePercent: 8.16, volume: '95.2M' },
        { symbol: 'SQQQ', company: 'ProShares UltraPro Short QQQ', price: 8.45, change: -0.25, changePercent: -2.87, volume: '89.4M' }
    ];
    
    document.getElementById('gainers-grid').innerHTML = gainers.map(createMoverCard).join('');
    document.getElementById('losers-grid').innerHTML = losers.map(createMoverCard).join('');
    document.getElementById('active-grid').innerHTML = mostActive.map(createMoverCard).join('');
}

function createMoverCard(stock) {
    const changeClass = stock.change >= 0 ? 'positive' : 'negative';
    const changeIcon = stock.change >= 0 ? '↗' : '↘';
    
    return `
        <div class="mover-card" onclick="viewStock('${stock.symbol}')">
            <div class="mover-header">
                <div class="mover-symbol">${stock.symbol}</div>
                <div class="mover-price">$${stock.price.toFixed(2)}</div>
            </div>
            <div class="mover-company">${stock.company}</div>
            <div class="mover-change ${changeClass}">
                ${changeIcon} $${Math.abs(stock.change).toFixed(2)} (${stock.changePercent.toFixed(2)}%)
            </div>
            <div class="mover-volume">Volume: ${stock.volume}</div>
        </div>
    `;
}

function loadSectorPerformance() {
    const sectors = [
        { name: 'Technology', performance: 2.45, companies: '67 companies' },
        { name: 'Healthcare', performance: 1.23, companies: '52 companies' },
        { name: 'Financial', performance: -0.85, companies: '45 companies' },
        { name: 'Consumer Disc.', performance: 3.12, companies: '38 companies' },
        { name: 'Industrial', performance: 0.67, companies: '41 companies' },
        { name: 'Energy', performance: -1.45, companies: '23 companies' },
        { name: 'Materials', performance: 0.23, companies: '19 companies' },
        { name: 'Utilities', performance: -0.12, companies: '28 companies' },
        { name: 'Real Estate', performance: 1.89, companies: '31 companies' },
        { name: 'Communication', performance: 1.56, companies: '25 companies' }
    ];
    
    const sectorsGrid = document.getElementById('sectors-grid');
    sectorsGrid.innerHTML = sectors.map(createSectorCard).join('');
}

function createSectorCard(sector) {
    const performanceClass = sector.performance >= 0 ? 'positive' : 'negative';
    const performanceIcon = sector.performance >= 0 ? '+' : '';
    
    return `
        <div class="sector-card" onclick="viewSector('${sector.name}')">
            <div class="sector-name">${sector.name}</div>
            <div class="sector-performance ${performanceClass}">
                ${performanceIcon}${sector.performance.toFixed(2)}%
            </div>
            <div class="sector-companies">${sector.companies}</div>
        </div>
    `;
}

function initializeMarketBreadth() {
    // Mock data for market breadth
    const advanceDeclineStats = document.getElementById('advance-decline-stats');
    advanceDeclineStats.innerHTML = `
        <div class="stat-item">
            <div class="stat-value" style="color: #00a32a;">2,456</div>
            <div class="stat-label">Advancing</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color: #d63638;">1,234</div>
            <div class="stat-label">Declining</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">345</div>
            <div class="stat-label">Unchanged</div>
        </div>
    `;
    
    const highsLowsStats = document.getElementById('highs-lows-stats');
    highsLowsStats.innerHTML = `
        <div class="stat-item">
            <div class="stat-value" style="color: #00a32a;">156</div>
            <div class="stat-label">New Highs</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color: #d63638;">23</div>
            <div class="stat-label">New Lows</div>
        </div>
    `;
    
    const volumeMetrics = document.getElementById('volume-analysis-stats');
    volumeMetrics.innerHTML = `
        <div class="stat-item">
            <div class="stat-value">4.2B shares</div>
            <div class="stat-label">Total Volume</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">2.8B shares</div>
            <div class="stat-label">Up Volume</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">1.4B shares</div>
            <div class="stat-label">Down Volume</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">2.0</div>
            <div class="stat-label">Up/Down Ratio</div>
        </div>
    `;
}

function loadEconomicCalendar() {
    const mockEvents = [
        { time: '8:30 AM', description: 'Initial Jobless Claims', impact: 'medium', forecast: '220K' },
        { time: '10:00 AM', description: 'Consumer Price Index (CPI)', impact: 'high', forecast: '3.2%' },
        { time: '2:00 PM', description: 'Federal Reserve Interest Rate Decision', impact: 'high', forecast: '5.25%' },
        { time: '2:30 PM', description: 'Fed Chair Powell Press Conference', impact: 'high', forecast: 'N/A' }
    ];
    
    const calendarEvents = document.getElementById('calendar-events');
    calendarEvents.innerHTML = mockEvents.map(createEventItem).join('');
}

function createEventItem(event) {
    return `
        <div class="event-item">
            <div class="event-time">${event.time}</div>
            <div class="event-description">${event.description}</div>
            <div class="event-impact ${event.impact}">${event.impact}</div>
            <div class="event-forecast">${event.forecast}</div>
        </div>
    `;
}

function loadNewsummary() {
    const mockNews = [
        {
            title: 'Federal Reserve Signals Potential Rate Changes in Upcoming Meeting',
            source: 'Reuters',
            time: '2 hours ago'
        },
        {
            title: 'Tech Giants Report Strong Q4 Earnings Despite Market Volatility',
            source: 'Bloomberg',
            time: '4 hours ago'
        },
        {
            title: 'Energy Sector Sees Major Investment Shift Toward Renewables',
            source: 'Wall Street Journal',
            time: '6 hours ago'
        }
    ];
    
    const newsSummary = document.getElementById('news-summary');
    newsSummary.innerHTML = mockNews.map(createNewsSummaryCard).join('');
}

function createNewsSummaryCard(news) {
    return `
        <div class="news-summary-card" onclick="openNews('${news.title}')">
            <div class="news-summary-title">${news.title}</div>
            <div class="news-summary-meta">
                <span>${news.source}</span>
                <span>${news.time}</span>
            </div>
        </div>
    `;
}

function setupTabNavigation() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;
            
            // Update active tab button
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update active tab content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${targetTab}-content`) {
                    content.classList.add('active');
                }
            });
        });
    });
}

function setupCalendarNavigation() {
    const prevDayBtn = document.getElementById('prev-day');
    const nextDayBtn = document.getElementById('next-day');
    const selectedDate = document.getElementById('selected-date');
    
    let currentDate = new Date();
    
    prevDayBtn.addEventListener('click', () => {
        currentDate.setDate(currentDate.getDate() - 1);
        updateSelectedDate();
    });
    
    nextDayBtn.addEventListener('click', () => {
        currentDate.setDate(currentDate.getDate() + 1);
        updateSelectedDate();
    });
    
    function updateSelectedDate() {
        const today = new Date();
        if (currentDate.toDateString() === today.toDateString()) {
            selectedDate.textContent = 'Today';
        } else {
            selectedDate.textContent = currentDate.toLocaleDateString('en-US', {
                weekday: 'short',
                month: 'short',
                day: 'numeric'
            });
        }
        loadEconomicCalendar(); // Reload events for selected date
    }
}

// Global functions for onclick handlers
window.viewIndex = function(symbol) {
    window.location.href = `/technical-analysis/?symbol=${symbol}`;
};

window.viewStock = function(symbol) {
    window.location.href = `/stock-lookup/?symbol=${symbol}`;
};

window.viewSector = function(sector) {
    window.location.href = `/stock-screener/?sector=${encodeURIComponent(sector)}`;
};

window.openNews = function(title) {
    window.location.href = `/stock-news/?search=${encodeURIComponent(title)}`;
};
</script>

<?php get_footer(); ?>