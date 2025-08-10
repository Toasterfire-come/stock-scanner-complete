<?php
/**
 * Template Name: Watchlist
 * Dedicated Watchlist Page Template
 */

global $post;
get_header(); ?>

<div class="watchlist-page">
    <div class="container">
        <div class="page-header">
            <h1>📋 My Watchlist</h1>
            <p class="page-description">Track your favorite stocks and get quick suggestions to start building your list</p>
        </div>

        <div class="watchlist-actions-bar panel">
            <div class="d-flex flex-wrap align-items-center gap-2">
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#createWatchlistModal">Create Watchlist</button>
                <button class="btn btn-outline" data-bs-toggle="modal" data-bs-target="#addStockModal">Add Stock</button>
                <a class="btn btn-secondary" href="/stock-screener/">Open Screener</a>
                <a class="btn btn-outline" href="/stock-news/">Market News</a>
            </div>
        </div>

        <div class="row" id="watchlists-container">
            <!-- Watchlists render here. If empty, an empty-state with suggestions appears. -->
        </div>

        <!-- Create Watchlist Modal -->
        <div class="modal fade" id="createWatchlistModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Create Watchlist</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="create-watchlist-form">
                            <div class="mb-3">
                                <label for="watchlist-name" class="form-label">Name</label>
                                <input type="text" id="watchlist-name" class="form-control" placeholder="e.g., Tech Growth" required>
                            </div>
                            <div class="mb-3">
                                <label for="watchlist-description" class="form-label">Description</label>
                                <textarea id="watchlist-description" class="form-control" rows="3" placeholder="Optional"></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="watchlistManager.createWatchlist()">Create</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add Stock Modal -->
        <div class="modal fade" id="addStockModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add Stock</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="add-stock-form">
                            <div class="mb-3">
                                <label for="target-watchlist-id" class="form-label">Watchlist</label>
                                <select id="target-watchlist-id" class="form-select"></select>
                            </div>
                            <div class="mb-3">
                                <label for="stock-ticker-add" class="form-label">Ticker</label>
                                <input type="text" id="stock-ticker-add" class="form-control" placeholder="AAPL" maxlength="8" required>
                            </div>
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label for="added-price" class="form-label">Added Price</label>
                                    <input type="number" step="0.01" id="added-price" class="form-control" placeholder="Optional">
                                </div>
                                <div class="col-md-6 d-flex align-items-end">
                                    <button type="button" class="btn btn-outline w-100" onclick="watchlistManager.useCurrentPrice()">Use Current Price</button>
                                </div>
                            </div>
                            <div class="row g-3 mt-1">
                                <div class="col-md-6">
                                    <label for="target-price" class="form-label">Target Price</label>
                                    <input type="number" step="0.01" id="target-price" class="form-control" placeholder="Optional">
                                </div>
                                <div class="col-md-6">
                                    <label for="stop-loss" class="form-label">Stop Loss</label>
                                    <input type="number" step="0.01" id="stop-loss" class="form-control" placeholder="Optional">
                                </div>
                            </div>
                            <div class="row g-3 mt-1">
                                <div class="col-md-6 form-check">
                                    <input class="form-check-input" type="checkbox" id="price-alert-enabled" checked>
                                    <label class="form-check-label" for="price-alert-enabled">Enable Price Alerts</label>
                                </div>
                                <div class="col-md-6 form-check">
                                    <input class="form-check-input" type="checkbox" id="news-alert-enabled" checked>
                                    <label class="form-check-label" for="news-alert-enabled">Enable News Alerts</label>
                                </div>
                            </div>
                            <div class="mt-3">
                                <label for="stock-notes" class="form-label">Notes</label>
                                <textarea id="stock-notes" class="form-control" rows="3" placeholder="Optional notes"></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="watchlistManager.addStock()">Add Stock</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<?php get_footer(); ?>