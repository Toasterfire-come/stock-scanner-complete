<?php
/**
 * Stock-specific utility functions
 *
 * @package StockScannerPro
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Get stock data with caching and error handling
 */
function stock_scanner_get_stock_safe($ticker, $use_cache = true) {
    if (empty($ticker)) {
        return false;
    }
    
    $ticker = strtoupper(sanitize_text_field($ticker));
    $cache_key = "stock_data_{$ticker}";
    
    if ($use_cache) {
        $cached = get_transient($cache_key);
        if ($cached !== false) {
            return $cached;
        }
    }
    
    $stock_data = stock_scanner_get_stock_data($ticker);
    
    if (isset($stock_data['success']) && $stock_data['success'] && isset($stock_data['data'])) {
        $processed_data = stock_scanner_process_stock_data($stock_data['data']);
        set_transient($cache_key, $processed_data, 300); // Cache for 5 minutes
        return $processed_data;
    }
    
    return false;
}

/**
 * Process and normalize stock data
 */
function stock_scanner_process_stock_data($data) {
    $processed = array(
        'ticker' => isset($data['ticker']) ? strtoupper($data['ticker']) : '',
        'company_name' => isset($data['company_name']) ? sanitize_text_field($data['company_name']) : '',
        'current_price' => isset($data['current_price']) ? floatval($data['current_price']) : 0,
        'price_change' => isset($data['price_change_today']) ? floatval($data['price_change_today']) : 0,
        'price_change_percent' => isset($data['change_percent']) ? floatval($data['change_percent']) : 0,
        'volume' => isset($data['volume']) ? intval($data['volume']) : 0,
        'market_cap' => isset($data['market_cap']) ? intval($data['market_cap']) : 0,
        'pe_ratio' => isset($data['pe_ratio']) ? floatval($data['pe_ratio']) : null,
        'dividend_yield' => isset($data['dividend_yield']) ? floatval($data['dividend_yield']) : null,
        'day_low' => isset($data['days_low']) ? floatval($data['days_low']) : null,
        'day_high' => isset($data['days_high']) ? floatval($data['days_high']) : null,
        'week_52_low' => isset($data['week_52_low']) ? floatval($data['week_52_low']) : null,
        'week_52_high' => isset($data['week_52_high']) ? floatval($data['week_52_high']) : null,
        'last_updated' => isset($data['last_updated']) ? $data['last_updated'] : current_time('mysql'),
    );
    
    // Calculate additional metrics
    $processed['change_direction'] = stock_scanner_get_change_direction($processed['price_change']);
    $processed['formatted_price'] = stock_scanner_format_currency($processed['current_price']);
    $processed['formatted_change'] = stock_scanner_format_currency($processed['price_change'], 2);
    $processed['formatted_change_percent'] = stock_scanner_format_percentage($processed['price_change_percent']);
    $processed['formatted_volume'] = stock_scanner_format_number($processed['volume']);
    $processed['formatted_market_cap'] = stock_scanner_format_market_cap($processed['market_cap']);
    $processed['price_class'] = stock_scanner_get_price_change_class($processed['price_change']);
    
    return $processed;
}

/**
 * Get price change direction
 */
function stock_scanner_get_change_direction($change) {
    if (!is_numeric($change)) {
        return 'neutral';
    }
    
    $change = floatval($change);
    
    if ($change > 0) {
        return 'up';
    } elseif ($change < 0) {
        return 'down';
    } else {
        return 'neutral';
    }
}

/**
 * Format large numbers with appropriate suffixes
 */
function stock_scanner_format_number($number) {
    if (!is_numeric($number)) {
        return '0';
    }
    
    $number = intval($number);
    
    if ($number >= 1000000000) {
        return number_format($number / 1000000000, 1) . 'B';
    } elseif ($number >= 1000000) {
        return number_format($number / 1000000, 1) . 'M';
    } elseif ($number >= 1000) {
        return number_format($number / 1000, 1) . 'K';
    } else {
        return number_format($number);
    }
}

/**
 * Format market cap with appropriate suffixes
 */
function stock_scanner_format_market_cap($market_cap) {
    if (!is_numeric($market_cap) || $market_cap <= 0) {
        return 'N/A';
    }
    
    $market_cap = floatval($market_cap);
    
    if ($market_cap >= 1000000000000) {
        return '$' . number_format($market_cap / 1000000000000, 2) . 'T';
    } elseif ($market_cap >= 1000000000) {
        return '$' . number_format($market_cap / 1000000000, 2) . 'B';
    } elseif ($market_cap >= 1000000) {
        return '$' . number_format($market_cap / 1000000, 2) . 'M';
    } else {
        return '$' . number_format($market_cap);
    }
}

/**
 * Get market cap category
 */
function stock_scanner_get_market_cap_category($market_cap) {
    if (!is_numeric($market_cap)) {
        return 'unknown';
    }
    
    $market_cap = floatval($market_cap);
    
    if ($market_cap >= 200000000000) {
        return 'mega-cap';
    } elseif ($market_cap >= 10000000000) {
        return 'large-cap';
    } elseif ($market_cap >= 2000000000) {
        return 'mid-cap';
    } elseif ($market_cap >= 300000000) {
        return 'small-cap';
    } elseif ($market_cap >= 50000000) {
        return 'micro-cap';
    } else {
        return 'nano-cap';
    }
}

/**
 * Calculate price performance metrics
 */
function stock_scanner_calculate_performance($current_price, $reference_price) {
    if (!is_numeric($current_price) || !is_numeric($reference_price) || $reference_price == 0) {
        return array(
            'absolute_change' => 0,
            'percentage_change' => 0,
            'direction' => 'neutral',
        );
    }
    
    $absolute_change = $current_price - $reference_price;
    $percentage_change = ($absolute_change / $reference_price) * 100;
    
    return array(
        'absolute_change' => $absolute_change,
        'percentage_change' => $percentage_change,
        'direction' => stock_scanner_get_change_direction($absolute_change),
        'formatted_absolute' => stock_scanner_format_currency($absolute_change, 2),
        'formatted_percentage' => stock_scanner_format_percentage($percentage_change),
    );
}

/**
 * Get stock sector and industry information
 */
function stock_scanner_get_stock_sector($ticker) {
    // This would typically come from the API, but for now we'll use a simple mapping
    $sector_mapping = array(
        'AAPL' => array('sector' => 'Technology', 'industry' => 'Consumer Electronics'),
        'MSFT' => array('sector' => 'Technology', 'industry' => 'Software'),
        'GOOGL' => array('sector' => 'Technology', 'industry' => 'Internet Services'),
        'AMZN' => array('sector' => 'Consumer Discretionary', 'industry' => 'E-commerce'),
        'TSLA' => array('sector' => 'Consumer Discretionary', 'industry' => 'Electric Vehicles'),
        'NVDA' => array('sector' => 'Technology', 'industry' => 'Semiconductors'),
        'META' => array('sector' => 'Technology', 'industry' => 'Social Media'),
        'NFLX' => array('sector' => 'Communication Services', 'industry' => 'Streaming'),
    );
    
    $ticker = strtoupper($ticker);
    
    if (isset($sector_mapping[$ticker])) {
        return $sector_mapping[$ticker];
    }
    
    return array(
        'sector' => 'Unknown',
        'industry' => 'Unknown',
    );
}

/**
 * Generate stock chart data for Chart.js
 */
function stock_scanner_generate_chart_data($ticker, $period = '1d') {
    // This is a placeholder - in production, you'd fetch historical data from the API
    $base_price = 100;
    $data_points = array();
    $labels = array();
    
    // Generate sample data based on period
    switch ($period) {
        case '1d':
            $intervals = 24;
            $interval_name = 'hour';
            break;
        case '1w':
            $intervals = 7;
            $interval_name = 'day';
            break;
        case '1m':
            $intervals = 30;
            $interval_name = 'day';
            break;
        case '3m':
            $intervals = 90;
            $interval_name = 'day';
            break;
        case '1y':
            $intervals = 12;
            $interval_name = 'month';
            break;
        default:
            $intervals = 24;
            $interval_name = 'hour';
    }
    
    for ($i = $intervals; $i >= 0; $i--) {
        $price = $base_price + (rand(-500, 500) / 100);
        $data_points[] = round($price, 2);
        
        if ($interval_name === 'hour') {
            $labels[] = date('H:i', strtotime("-{$i} hours"));
        } elseif ($interval_name === 'day') {
            $labels[] = date('M j', strtotime("-{$i} days"));
        } else {
            $labels[] = date('M Y', strtotime("-{$i} months"));
        }
    }
    
    return array(
        'labels' => $labels,
        'datasets' => array(
            array(
                'label' => strtoupper($ticker) . ' Price',
                'data' => $data_points,
                'borderColor' => '#3b82f6',
                'backgroundColor' => 'rgba(59, 130, 246, 0.1)',
                'borderWidth' => 2,
                'fill' => true,
                'tension' => 0.4,
            ),
        ),
    );
}

/**
 * Get popular stock tickers
 */
function stock_scanner_get_popular_tickers() {
    return array(
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
        'NVDA', 'META', 'NFLX', 'ORCL', 'CRM',
        'ADBE', 'INTC', 'AMD', 'PYPL', 'SHOP',
        'SQ', 'ROKU', 'ZOOM', 'DOCU', 'TWLO',
    );
}

/**
 * Validate ticker symbol format
 */
function stock_scanner_validate_ticker($ticker) {
    if (empty($ticker)) {
        return false;
    }
    
    $ticker = trim(strtoupper($ticker));
    
    // Basic validation: 1-5 letters, no special characters
    if (!preg_match('/^[A-Z]{1,5}$/', $ticker)) {
        return false;
    }
    
    return $ticker;
}

/**
 * Get stock recommendation based on metrics
 */
function stock_scanner_get_stock_recommendation($data) {
    if (!is_array($data) || empty($data)) {
        return array(
            'recommendation' => 'neutral',
            'confidence' => 0,
            'reasons' => array('Insufficient data'),
        );
    }
    
    $score = 0;
    $reasons = array();
    
    // Price momentum
    if (isset($data['price_change_percent']) && is_numeric($data['price_change_percent'])) {
        $change = floatval($data['price_change_percent']);
        if ($change > 5) {
            $score += 2;
            $reasons[] = 'Strong positive momentum';
        } elseif ($change > 0) {
            $score += 1;
            $reasons[] = 'Positive momentum';
        } elseif ($change < -5) {
            $score -= 2;
            $reasons[] = 'Strong negative momentum';
        } elseif ($change < 0) {
            $score -= 1;
            $reasons[] = 'Negative momentum';
        }
    }
    
    // Volume analysis
    if (isset($data['volume']) && isset($data['avg_volume_3mon'])) {
        $current_volume = floatval($data['volume']);
        $avg_volume = floatval($data['avg_volume_3mon']);
        
        if ($avg_volume > 0 && $current_volume > $avg_volume * 2) {
            $score += 1;
            $reasons[] = 'High trading volume';
        }
    }
    
    // PE ratio analysis
    if (isset($data['pe_ratio']) && is_numeric($data['pe_ratio'])) {
        $pe = floatval($data['pe_ratio']);
        if ($pe > 0 && $pe < 15) {
            $score += 1;
            $reasons[] = 'Attractive valuation';
        } elseif ($pe > 30) {
            $score -= 1;
            $reasons[] = 'High valuation';
        }
    }
    
    // Determine recommendation
    if ($score >= 3) {
        $recommendation = 'buy';
        $confidence = min(90, 60 + ($score * 5));
    } elseif ($score >= 1) {
        $recommendation = 'hold';
        $confidence = min(80, 50 + ($score * 5));
    } elseif ($score <= -3) {
        $recommendation = 'sell';
        $confidence = min(90, 60 + (abs($score) * 5));
    } elseif ($score <= -1) {
        $recommendation = 'hold';
        $confidence = min(80, 50 + (abs($score) * 5));
    } else {
        $recommendation = 'neutral';
        $confidence = 40;
    }
    
    if (empty($reasons)) {
        $reasons[] = 'No significant indicators';
    }
    
    return array(
        'recommendation' => $recommendation,
        'confidence' => $confidence,
        'reasons' => $reasons,
        'score' => $score,
    );
}

/**
 * Get user subscription details
 */
function stock_scanner_get_user_subscription($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return array(
            'plan' => 'free',
            'status' => 'inactive',
            'api_calls_used' => 0,
            'api_calls_limit' => 100,
        );
    }
    
    // Get subscription from user meta (in production, this would come from payment processor)
    $subscription_plan = get_user_meta($user_id, 'stock_scanner_subscription_plan', true);
    $subscription_status = get_user_meta($user_id, 'stock_scanner_subscription_status', true);
    $api_calls_used = get_user_meta($user_id, 'stock_scanner_api_calls_used', true);
    
    // Default values
    if (empty($subscription_plan)) {
        $subscription_plan = 'free';
    }
    if (empty($subscription_status)) {
        $subscription_status = 'active';
    }
    if (empty($api_calls_used)) {
        $api_calls_used = 0;
    }
    
    // Define plan limits
    $plan_limits = array(
        'free' => 100,
        'basic' => 1000,
        'pro' => 10000,
        'unlimited' => PHP_INT_MAX,
    );
    
    $api_calls_limit = isset($plan_limits[$subscription_plan]) ? $plan_limits[$subscription_plan] : 100;
    
    return array(
        'plan' => $subscription_plan,
        'status' => $subscription_status,
        'api_calls_used' => intval($api_calls_used),
        'api_calls_limit' => $api_calls_limit,
        'user_id' => $user_id,
    );
}