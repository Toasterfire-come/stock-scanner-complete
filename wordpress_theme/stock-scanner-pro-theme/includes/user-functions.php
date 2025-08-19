<?php
/**
 * User management and authentication functions
 *
 * @package StockScannerPro
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Get user portfolio summary
 */
function stock_scanner_get_user_portfolio_summary($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return false;
    }
    
    $cache_key = "portfolio_summary_{$user_id}";
    $cached = get_transient($cache_key);
    
    if ($cached !== false) {
        return $cached;
    }
    
    $portfolio_data = stock_scanner_get_user_portfolio($user_id);
    
    if (!isset($portfolio_data['success']) || !$portfolio_data['success']) {
        return false;
    }
    
    $summary = array(
        'total_value' => 0,
        'total_cost' => 0,
        'total_return' => 0,
        'total_return_percent' => 0,
        'top_performer' => null,
        'worst_performer' => null,
        'holdings_count' => 0,
        'last_updated' => current_time('mysql'),
    );
    
    if (isset($portfolio_data['data']['holdings']) && is_array($portfolio_data['data']['holdings'])) {
        $holdings = $portfolio_data['data']['holdings'];
        $summary['holdings_count'] = count($holdings);
        
        $best_return = -PHP_FLOAT_MAX;
        $worst_return = PHP_FLOAT_MAX;
        
        foreach ($holdings as $holding) {
            $market_value = isset($holding['market_value']) ? floatval($holding['market_value']) : 0;
            $cost_basis = isset($holding['cost_basis']) ? floatval($holding['cost_basis']) : 0;
            $return_percent = isset($holding['return_percent']) ? floatval($holding['return_percent']) : 0;
            
            $summary['total_value'] += $market_value;
            $summary['total_cost'] += $cost_basis;
            
            if ($return_percent > $best_return) {
                $best_return = $return_percent;
                $summary['top_performer'] = $holding;
            }
            
            if ($return_percent < $worst_return) {
                $worst_return = $return_percent;
                $summary['worst_performer'] = $holding;
            }
        }
        
        if ($summary['total_cost'] > 0) {
            $summary['total_return'] = $summary['total_value'] - $summary['total_cost'];
            $summary['total_return_percent'] = ($summary['total_return'] / $summary['total_cost']) * 100;
        }
    }
    
    set_transient($cache_key, $summary, 300); // Cache for 5 minutes
    return $summary;
}

/**
 * Get user watchlist with current prices
 */
function stock_scanner_get_user_watchlist_with_prices($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return false;
    }
    
    $watchlist_data = stock_scanner_get_user_watchlist($user_id);
    
    if (!isset($watchlist_data['success']) || !$watchlist_data['success']) {
        return false;
    }
    
    $watchlist = array();
    
    if (isset($watchlist_data['data']['items']) && is_array($watchlist_data['data']['items'])) {
        foreach ($watchlist_data['data']['items'] as $item) {
            if (isset($item['ticker'])) {
                $stock_data = stock_scanner_get_stock_safe($item['ticker']);
                
                if ($stock_data) {
                    $watchlist_item = array_merge($item, $stock_data);
                    $watchlist_item['added_date'] = isset($item['added_at']) ? $item['added_at'] : '';
                    $watchlist_item['notes'] = isset($item['notes']) ? $item['notes'] : '';
                    
                    $watchlist[] = $watchlist_item;
                }
            }
        }
    }
    
    return $watchlist;
}

/**
 * Get user preferences
 */
function stock_scanner_get_user_preferences($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return array();
    }
    
    $default_preferences = array(
        'theme' => 'light',
        'currency' => 'USD',
        'timezone' => 'America/New_York',
        'notifications' => array(
            'price_alerts' => true,
            'news_updates' => true,
            'portfolio_summary' => true,
            'market_hours' => false,
        ),
        'dashboard' => array(
            'show_portfolio' => true,
            'show_watchlist' => true,
            'show_market_overview' => true,
            'show_news' => true,
        ),
        'privacy' => array(
            'public_portfolio' => false,
            'share_analytics' => true,
        ),
    );
    
    $user_preferences = get_user_meta($user_id, 'stock_scanner_preferences', true);
    
    if (empty($user_preferences) || !is_array($user_preferences)) {
        $user_preferences = array();
    }
    
    return wp_parse_args($user_preferences, $default_preferences);
}

/**
 * Update user preferences
 */
function stock_scanner_update_user_preferences($preferences, $user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return false;
    }
    
    $current_preferences = stock_scanner_get_user_preferences($user_id);
    $updated_preferences = wp_parse_args($preferences, $current_preferences);
    
    return update_user_meta($user_id, 'stock_scanner_preferences', $updated_preferences);
}

/**
 * Get user subscription status
 */
function stock_scanner_get_user_subscription($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return array(
            'plan' => 'free',
            'status' => 'inactive',
            'expires_at' => null,
        );
    }
    
    $subscription = get_user_meta($user_id, 'stock_scanner_subscription', true);
    
    if (empty($subscription) || !is_array($subscription)) {
        return array(
            'plan' => 'free',
            'status' => 'active',
            'expires_at' => null,
            'features' => stock_scanner_get_plan_features('free'),
        );
    }
    
    // Check if subscription is expired
    if (isset($subscription['expires_at']) && !empty($subscription['expires_at'])) {
        $expires_at = strtotime($subscription['expires_at']);
        if ($expires_at < time()) {
            $subscription['status'] = 'expired';
        }
    }
    
    return $subscription;
}

/**
 * Get plan features
 */
function stock_scanner_get_plan_features($plan) {
    $features = array(
        'free' => array(
            'watchlist_limit' => 10,
            'portfolio_limit' => 1,
            'alerts_limit' => 5,
            'real_time_data' => false,
            'advanced_charts' => false,
            'news_sentiment' => false,
            'api_access' => false,
        ),
        'basic' => array(
            'watchlist_limit' => 50,
            'portfolio_limit' => 5,
            'alerts_limit' => 25,
            'real_time_data' => true,
            'advanced_charts' => true,
            'news_sentiment' => false,
            'api_access' => false,
        ),
        'pro' => array(
            'watchlist_limit' => 200,
            'portfolio_limit' => 20,
            'alerts_limit' => 100,
            'real_time_data' => true,
            'advanced_charts' => true,
            'news_sentiment' => true,
            'api_access' => true,
        ),
        'enterprise' => array(
            'watchlist_limit' => -1, // Unlimited
            'portfolio_limit' => -1,
            'alerts_limit' => -1,
            'real_time_data' => true,
            'advanced_charts' => true,
            'news_sentiment' => true,
            'api_access' => true,
        ),
    );
    
    return isset($features[$plan]) ? $features[$plan] : $features['free'];
}

/**
 * Check if user can access feature
 */
function stock_scanner_user_can_access($feature, $user_id = null) {
    $subscription = stock_scanner_get_user_subscription($user_id);
    
    if ($subscription['status'] !== 'active') {
        // If subscription expired or inactive, fall back to free plan
        $features = stock_scanner_get_plan_features('free');
    } else {
        $features = isset($subscription['features']) ? $subscription['features'] : stock_scanner_get_plan_features($subscription['plan']);
    }
    
    return isset($features[$feature]) ? $features[$feature] : false;
}

/**
 * Get user usage statistics
 */
function stock_scanner_get_user_usage($user_id = null, $period = 'month') {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return array();
    }
    
    // This would typically come from the API or be stored in wp_usermeta
    $usage_key = "stock_scanner_usage_{$period}_{$user_id}";
    $usage = get_transient($usage_key);
    
    if ($usage === false) {
        $usage = array(
            'api_calls' => 0,
            'watchlist_items' => 0,
            'portfolio_items' => 0,
            'active_alerts' => 0,
            'last_login' => get_user_meta($user_id, 'last_login', true),
            'period' => $period,
        );
        
        // In a real implementation, you would fetch this data from your API or database
        set_transient($usage_key, $usage, HOUR_IN_SECONDS);
    }
    
    return $usage;
}

/**
 * Log user activity
 */
function stock_scanner_log_user_activity($activity, $data = array(), $user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return false;
    }
    
    $log_entry = array(
        'timestamp' => current_time('mysql'),
        'activity' => sanitize_text_field($activity),
        'data' => is_array($data) ? $data : array(),
        'ip_address' => $_SERVER['REMOTE_ADDR'],
        'user_agent' => $_SERVER['HTTP_USER_AGENT'],
    );
    
    $activity_log = get_user_meta($user_id, 'stock_scanner_activity_log', true);
    
    if (!is_array($activity_log)) {
        $activity_log = array();
    }
    
    // Keep only last 100 entries
    array_unshift($activity_log, $log_entry);
    $activity_log = array_slice($activity_log, 0, 100);
    
    return update_user_meta($user_id, 'stock_scanner_activity_log', $activity_log);
}

/**
 * Get user's favorite stocks
 */
function stock_scanner_get_user_favorites($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return array();
    }
    
    $favorites = get_user_meta($user_id, 'stock_scanner_favorites', true);
    
    if (!is_array($favorites)) {
        $favorites = array();
    }
    
    return $favorites;
}

/**
 * Add stock to user favorites
 */
function stock_scanner_add_favorite($ticker, $user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return false;
    }
    
    $ticker = strtoupper(sanitize_text_field($ticker));
    $favorites = stock_scanner_get_user_favorites($user_id);
    
    if (!in_array($ticker, $favorites)) {
        $favorites[] = $ticker;
        return update_user_meta($user_id, 'stock_scanner_favorites', $favorites);
    }
    
    return true;
}

/**
 * Remove stock from user favorites
 */
function stock_scanner_remove_favorite($ticker, $user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return false;
    }
    
    $ticker = strtoupper(sanitize_text_field($ticker));
    $favorites = stock_scanner_get_user_favorites($user_id);
    
    $index = array_search($ticker, $favorites);
    if ($index !== false) {
        unset($favorites[$index]);
        $favorites = array_values($favorites); // Reindex array
        return update_user_meta($user_id, 'stock_scanner_favorites', $favorites);
    }
    
    return true;
}

/**
 * Check if stock is in user favorites
 */
function stock_scanner_is_favorite($ticker, $user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return false;
    }
    
    $ticker = strtoupper(sanitize_text_field($ticker));
    $favorites = stock_scanner_get_user_favorites($user_id);
    
    return in_array($ticker, $favorites);
}

/**
 * Generate user dashboard data
 */
function stock_scanner_generate_dashboard_data($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return array();
    }
    
    $dashboard_data = array(
        'portfolio_summary' => stock_scanner_get_user_portfolio_summary($user_id),
        'watchlist_preview' => array_slice(stock_scanner_get_user_watchlist_with_prices($user_id) ?: array(), 0, 5),
        'recent_activity' => array_slice(get_user_meta($user_id, 'stock_scanner_activity_log', true) ?: array(), 0, 10),
        'subscription' => stock_scanner_get_user_subscription($user_id),
        'preferences' => stock_scanner_get_user_preferences($user_id),
        'usage' => stock_scanner_get_user_usage($user_id),
        'favorites' => stock_scanner_get_user_favorites($user_id),
    );
    
    return $dashboard_data;
}

/**
 * Handle user login
 */
function stock_scanner_on_user_login($user_login, $user) {
    // Update last login timestamp
    update_user_meta($user->ID, 'last_login', current_time('mysql'));
    
    // Log login activity
    stock_scanner_log_user_activity('login', array(), $user->ID);
    
    // Clear user-specific caches
    $cache_keys = array(
        "portfolio_summary_{$user->ID}",
        "stock_scanner_usage_month_{$user->ID}",
    );
    
    foreach ($cache_keys as $key) {
        delete_transient($key);
    }
}
add_action('wp_login', 'stock_scanner_on_user_login', 10, 2);

/**
 * Handle user logout
 */
function stock_scanner_on_user_logout($user_id) {
    // Log logout activity
    stock_scanner_log_user_activity('logout', array(), $user_id);
}
add_action('wp_logout', 'stock_scanner_on_user_logout');