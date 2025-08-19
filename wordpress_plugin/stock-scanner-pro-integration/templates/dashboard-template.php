<?php
// Render dashboard without recursion. Prefer the theme implementation if available.
if (function_exists('stock_scanner_dashboard_shortcode')) {
    echo stock_scanner_dashboard_shortcode([]);
} else {
    echo '<div id="stock-scanner-dashboard" class="stock-scanner-professional">Loading dashboard...</div>';
}