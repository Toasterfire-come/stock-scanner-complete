<?php
/**
 * Template Name: Market Overview
 * 
 * Market overview with statistics, indices, and trending stocks
 *
 * @package StockScannerPro
 */

get_header(); ?>

<div class="market-overview-container">
    <!-- Page Header -->
    <div class="page-header mb-8">
        <div class="container">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-4xl font-bold text-gray-900">Market Overview</h1>
                    <p class="text-gray-600 mt-2">Real-time market statistics and trending stocks</p>
                </div>
                <div class="page-actions">
                    <button class="btn btn-outline-primary btn-sm" data-action="refresh-market-data">
                        <i class="fas fa-sync-alt mr-2"></i>
                        Refresh Data
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Market Statistics -->
        <div class="market-stats-section mb-8">
            <h2 class="section-title mb-4">Market Statistics</h2>
            <div id="market-statistics" class="market-stats-grid">
                <!-- Populated by JavaScript -->
            </div>
        </div>

        <!-- Market Indices -->
        <div class="market-indices-section mb-8">
            <h2 class="section-title mb-4">Major Indices</h2>
            <div id="market-indices" class="indices-grid">
                <!-- Populated by JavaScript -->
            </div>
        </div>

        <!-- Top Movers -->
        <div class="market-movers-section mb-8">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- Top Gainers -->
                <div class="movers-card">
                    <h3 class="card-title text-success">
                        <i class="fas fa-arrow-up mr-2"></i>
                        Top Gainers
                    </h3>
                    <div id="top-gainers" class="movers-list">
                        <!-- Populated by JavaScript -->
                    </div>
                </div>

                <!-- Top Losers -->
                <div class="movers-card">
                    <h3 class="card-title text-danger">
                        <i class="fas fa-arrow-down mr-2"></i>
                        Top Losers
                    </h3>
                    <div id="top-losers" class="movers-list">
                        <!-- Populated by JavaScript -->
                    </div>
                </div>
            </div>
        </div>

        <!-- Most Active -->
        <div class="most-active-section mb-8">
            <h2 class="section-title mb-4">Most Active Stocks</h2>
            <div id="most-active" class="active-stocks-grid">
                <!-- Populated by JavaScript -->
            </div>
        </div>

        <!-- Market Heatmap -->
        <div class="market-heatmap-section mb-8">
            <h2 class="section-title mb-4">Market Heatmap</h2>
            <div id="market-heatmap" class="heatmap-container">
                <!-- Populated by JavaScript -->
            </div>
        </div>

        <!-- Sector Performance -->
        <div class="sector-performance-section">
            <h2 class="section-title mb-4">Sector Performance</h2>
            <div id="sector-performance" class="sectors-grid">
                <!-- Populated by JavaScript -->
            </div>
        </div>
    </div>
</div>

<script>
// Initialize market overview when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (typeof StockScannerMarketOverview !== 'undefined') {
        StockScannerMarketOverview.init();
    }
});
</script>

<?php get_footer(); ?>