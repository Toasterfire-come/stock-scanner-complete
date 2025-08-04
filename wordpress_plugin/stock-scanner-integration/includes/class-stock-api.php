<?php
/**
 * Stock API Integration with Membership Controls
 * 
 * Handles API calls to external stock data providers with proper authentication,
 * rate limiting, and membership level enforcement
 */

class StockScannerAPI {
    
    private $membership_manager;
    private $api_endpoints;
    private $rate_limits;
    
    public function __construct() {
        $this->membership_manager = new StockScannerMembershipManager();
        $this->init_api_endpoints();
        $this->init_rate_limits();
        $this->add_hooks();
    }
    
    /**
     * Initialize API endpoints
     */
    private function init_api_endpoints() {
        $this->api_endpoints = [
            'stock_quote' => get_option('stock_api_quote_endpoint', ''),
            'stock_search' => get_option('stock_api_search_endpoint', ''),
            'market_data' => get_option('stock_api_market_endpoint', ''),
            'technical_indicators' => get_option('stock_api_technical_endpoint', ''),
            'news' => get_option('stock_api_news_endpoint', ''),
            'options' => get_option('stock_api_options_endpoint', ''),
            'level2' => get_option('stock_api_level2_endpoint', '')
        ];
    }
    
    /**
     * Initialize rate limits per membership level
     */
    private function init_rate_limits() {
        $this->rate_limits = [
            'free' => [
                'requests_per_minute' => 5,
                'requests_per_hour' => 10,
                'requests_per_day' => 100
            ],
            'bronze' => [
                'requests_per_minute' => 20,
                'requests_per_hour' => 100,
                'requests_per_day' => 1500
            ],
            'silver' => [
                'requests_per_minute' => 50,
                'requests_per_hour' => 500,
                'requests_per_day' => 5000
            ],
            'gold' => [
                'requests_per_minute' => -1, // unlimited
                'requests_per_hour' => -1,   // unlimited
                'requests_per_day' => -1     // unlimited
            ]
        ];
    }
    
    /**
     * Add WordPress hooks
     */
    private function add_hooks() {
        // AJAX endpoints for API calls
        add_action('wp_ajax_get_stock_quote', [$this, 'get_stock_quote_ajax']);
        add_action('wp_ajax_nopriv_get_stock_quote', [$this, 'get_stock_quote_ajax']);
        
        add_action('wp_ajax_search_stocks', [$this, 'search_stocks_ajax']);
        add_action('wp_ajax_nopriv_search_stocks', [$this, 'search_stocks_ajax']);
        
        add_action('wp_ajax_get_market_data', [$this, 'get_market_data_ajax']);
        add_action('wp_ajax_nopriv_get_market_data', [$this, 'get_market_data_ajax']);
        
        add_action('wp_ajax_get_technical_indicators', [$this, 'get_technical_indicators_ajax']);
        add_action('wp_ajax_nopriv_get_technical_indicators', [$this, 'get_technical_indicators_ajax']);
        
        add_action('wp_ajax_get_stock_news', [$this, 'get_stock_news_ajax']);
        add_action('wp_ajax_nopriv_get_stock_news', [$this, 'get_stock_news_ajax']);
        
        add_action('wp_ajax_get_options_data', [$this, 'get_options_data_ajax']);
        add_action('wp_ajax_get_level2_data', [$this, 'get_level2_data_ajax']);
    }
    
    /**
     * Check if user can make API call
     */
    private function can_make_api_call($user_id, $endpoint_type) {
        // Check if user is logged in for premium features
        if (!$user_id && in_array($endpoint_type, ['options', 'level2', 'technical_advanced'])) {
            return [
                'allowed' => false,
                'error' => 'Please log in to access premium features',
                'upgrade_required' => true
            ];
        }
        
        // Get user's membership level
        $membership_level = $this->membership_manager->get_user_membership_level($user_id);
        
        // Check feature access
        $feature_map = [
            'stock_quote' => 'realtime_data',
            'technical_indicators' => 'technical_indicators',
            'options' => 'options_data',
            'level2' => 'level2_data'
        ];
        
        if (isset($feature_map[$endpoint_type])) {
            $has_feature = $this->membership_manager->user_has_feature($feature_map[$endpoint_type], $user_id);
            
            if (!$has_feature) {
                return [
                    'allowed' => false,
                    'error' => 'This feature requires a premium subscription',
                    'upgrade_required' => true,
                    'required_level' => $this->get_minimum_level_for_feature($feature_map[$endpoint_type])
                ];
            }
        }
        
        // Check rate limits
        if (!$this->check_rate_limit($user_id, $membership_level)) {
            return [
                'allowed' => false,
                'error' => 'Rate limit exceeded. Please upgrade your plan or wait before making more requests.',
                'rate_limited' => true,
                'current_usage' => $this->get_usage_stats($user_id)
            ];
        }
        
        return ['allowed' => true];
    }
    
    /**
     * Check rate limits for user
     */
    private function check_rate_limit($user_id, $membership_level) {
        $limits = $this->rate_limits[$membership_level] ?? $this->rate_limits['free'];
        
        // Check daily limit
        if ($limits['requests_per_day'] !== -1) {
            if (!$this->membership_manager->check_user_limit('api_calls_per_day', $user_id)) {
                return false;
            }
        }
        
        // Check hourly limit
        if ($limits['requests_per_hour'] !== -1) {
            if (!$this->membership_manager->check_user_limit('api_calls_per_hour', $user_id)) {
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Get minimum membership level required for a feature
     */
    private function get_minimum_level_for_feature($feature) {
        $levels = $this->membership_manager->get_membership_levels();
        
        foreach (['bronze', 'silver', 'gold'] as $level) {
            if ($levels[$level]['features'][$feature] ?? false) {
                return $level;
            }
        }
        
        return 'bronze';
    }
    
    /**
     * Get stock quote with membership validation
     */
    public function get_stock_quote_ajax() {
        $user_id = get_current_user_id();
        $symbol = sanitize_text_field($_POST['symbol'] ?? '');
        
        if (empty($symbol)) {
            wp_die(json_encode(['success' => false, 'error' => 'Stock symbol is required']));
        }
        
        // Check permissions
        $permission_check = $this->can_make_api_call($user_id, 'stock_quote');
        if (!$permission_check['allowed']) {
            wp_die(json_encode(['success' => false] + $permission_check));
        }
        
        try {
            // Make API call
            $quote_data = $this->fetch_stock_quote($symbol, $user_id);
            
            // Increment usage counter
            $this->membership_manager->check_user_limit('api_calls_per_day', $user_id, true);
            
            wp_die(json_encode([
                'success' => true,
                'data' => $quote_data,
                'usage' => $this->get_usage_stats($user_id)
            ]));
            
        } catch (Exception $e) {
            error_log('Stock API Error: ' . $e->getMessage());
            wp_die(json_encode([
                'success' => false,
                'error' => 'Unable to fetch stock data. Please try again later.'
            ]));
        }
    }
    
    /**
     * Fetch stock quote from external API
     */
    private function fetch_stock_quote($symbol, $user_id = null) {
        $membership_level = $this->membership_manager->get_user_membership_level($user_id);
        $is_realtime = $this->membership_manager->user_has_feature('realtime_data', $user_id);
        
        // Mock data for demonstration - replace with actual API call
        $mock_data = [
            'symbol' => strtoupper($symbol),
            'price' => 150.25 + (rand(-1000, 1000) / 100),
            'change' => rand(-500, 500) / 100,
            'change_percent' => rand(-1000, 1000) / 100,
            'volume' => rand(1000000, 50000000),
            'market_cap' => rand(10000000000, 3000000000000),
            'pe_ratio' => rand(10, 50) + (rand(0, 99) / 100),
            'high' => 155.75,
            'low' => 148.30,
            'open' => 152.10,
            'previous_close' => 151.80,
            'timestamp' => $is_realtime ? time() : (time() - 900), // 15 min delay for free users
            'is_realtime' => $is_realtime,
            'membership_level' => $membership_level
        ];
        
        // Add delayed data notice for free users
        if (!$is_realtime) {
            $mock_data['data_notice'] = 'Data delayed by 15 minutes. Upgrade for real-time access.';
        }
        
        return $mock_data;
    }
    
    /**
     * Search stocks with membership validation
     */
    public function search_stocks_ajax() {
        $user_id = get_current_user_id();
        $query = sanitize_text_field($_POST['query'] ?? '');
        
        if (empty($query)) {
            wp_die(json_encode(['success' => false, 'error' => 'Search query is required']));
        }
        
        // Check permissions
        $permission_check = $this->can_make_api_call($user_id, 'stock_search');
        if (!$permission_check['allowed']) {
            wp_die(json_encode(['success' => false] + $permission_check));
        }
        
        try {
            $search_results = $this->search_stocks($query, $user_id);
            
            // Increment usage counter
            $this->membership_manager->check_user_limit('api_calls_per_day', $user_id, true);
            
            wp_die(json_encode([
                'success' => true,
                'data' => $search_results,
                'usage' => $this->get_usage_stats($user_id)
            ]));
            
        } catch (Exception $e) {
            error_log('Stock Search Error: ' . $e->getMessage());
            wp_die(json_encode([
                'success' => false,
                'error' => 'Unable to search stocks. Please try again later.'
            ]));
        }
    }
    
    /**
     * Search stocks
     */
    private function search_stocks($query, $user_id = null) {
        $membership_level = $this->membership_manager->get_user_membership_level($user_id);
        
        // Mock search results - replace with actual API call
        $mock_results = [
            [
                'symbol' => 'AAPL',
                'name' => 'Apple Inc.',
                'exchange' => 'NASDAQ',
                'price' => 150.25,
                'change_percent' => 1.25,
                'market_cap' => 2400000000000
            ],
            [
                'symbol' => 'MSFT',
                'name' => 'Microsoft Corporation',
                'exchange' => 'NASDAQ',
                'price' => 330.50,
                'change_percent' => -0.75,
                'market_cap' => 2500000000000
            ],
            [
                'symbol' => 'GOOGL',
                'name' => 'Alphabet Inc.',
                'exchange' => 'NASDAQ',
                'price' => 2750.80,
                'change_percent' => 2.10,
                'market_cap' => 1800000000000
            ]
        ];
        
        // Limit results based on membership level
        $result_limits = [
            'free' => 5,
            'bronze' => 25,
            'silver' => 100,
            'gold' => -1 // unlimited
        ];
        
        $limit = $result_limits[$membership_level] ?? 5;
        if ($limit !== -1 && count($mock_results) > $limit) {
            $mock_results = array_slice($mock_results, 0, $limit);
        }
        
        return [
            'results' => $mock_results,
            'total_found' => count($mock_results),
            'membership_level' => $membership_level,
            'result_limit' => $limit
        ];
    }
    
    /**
     * Get market data
     */
    public function get_market_data_ajax() {
        $user_id = get_current_user_id();
        
        // Check permissions
        $permission_check = $this->can_make_api_call($user_id, 'market_data');
        if (!$permission_check['allowed']) {
            wp_die(json_encode(['success' => false] + $permission_check));
        }
        
        try {
            $market_data = $this->fetch_market_data($user_id);
            
            // Increment usage counter
            $this->membership_manager->check_user_limit('api_calls_per_day', $user_id, true);
            
            wp_die(json_encode([
                'success' => true,
                'data' => $market_data,
                'usage' => $this->get_usage_stats($user_id)
            ]));
            
        } catch (Exception $e) {
            error_log('Market Data Error: ' . $e->getMessage());
            wp_die(json_encode([
                'success' => false,
                'error' => 'Unable to fetch market data. Please try again later.'
            ]));
        }
    }
    
    /**
     * Fetch market data
     */
    private function fetch_market_data($user_id = null) {
        $is_realtime = $this->membership_manager->user_has_feature('realtime_data', $user_id);
        
        // Mock market data
        return [
            'indices' => [
                'SPY' => ['price' => 425.50, 'change' => 2.75, 'change_percent' => 0.65],
                'QQQ' => ['price' => 350.80, 'change' => -1.25, 'change_percent' => -0.35],
                'DIA' => ['price' => 340.20, 'change' => 1.50, 'change_percent' => 0.44]
            ],
            'sectors' => [
                'Technology' => ['change_percent' => 1.25],
                'Healthcare' => ['change_percent' => 0.85],
                'Financial' => ['change_percent' => -0.45]
            ],
            'market_status' => $this->get_market_status(),
            'is_realtime' => $is_realtime,
            'timestamp' => $is_realtime ? time() : (time() - 900)
        ];
    }
    
    /**
     * Get technical indicators
     */
    public function get_technical_indicators_ajax() {
        $user_id = get_current_user_id();
        $symbol = sanitize_text_field($_POST['symbol'] ?? '');
        $indicators = $_POST['indicators'] ?? [];
        
        if (empty($symbol)) {
            wp_die(json_encode(['success' => false, 'error' => 'Stock symbol is required']));
        }
        
        // Check permissions
        $permission_check = $this->can_make_api_call($user_id, 'technical_indicators');
        if (!$permission_check['allowed']) {
            wp_die(json_encode(['success' => false] + $permission_check));
        }
        
        try {
            $technical_data = $this->fetch_technical_indicators($symbol, $indicators, $user_id);
            
            // Increment usage counter
            $this->membership_manager->check_user_limit('api_calls_per_day', $user_id, true);
            
            wp_die(json_encode([
                'success' => true,
                'data' => $technical_data,
                'usage' => $this->get_usage_stats($user_id)
            ]));
            
        } catch (Exception $e) {
            error_log('Technical Indicators Error: ' . $e->getMessage());
            wp_die(json_encode([
                'success' => false,
                'error' => 'Unable to fetch technical indicators. Please try again later.'
            ]));
        }
    }
    
    /**
     * Fetch technical indicators
     */
    private function fetch_technical_indicators($symbol, $indicators, $user_id = null) {
        $membership_level = $this->membership_manager->get_user_membership_level($user_id);
        $available_indicators = $this->membership_manager->user_has_feature('technical_indicators', $user_id);
        
        // Mock technical indicator data
        $all_indicators = [
            'RSI' => ['value' => 65.5, 'signal' => 'neutral'],
            'MACD' => ['value' => 0.25, 'signal' => 'bullish'],
            'SMA_20' => ['value' => 148.75, 'signal' => 'bullish'],
            'SMA_50' => ['value' => 145.20, 'signal' => 'bullish'],
            'EMA_12' => ['value' => 149.80, 'signal' => 'bullish'],
            'Bollinger_Upper' => ['value' => 155.50, 'signal' => 'resistance'],
            'Bollinger_Lower' => ['value' => 142.30, 'signal' => 'support'],
            'Volume_SMA' => ['value' => 25000000, 'signal' => 'above_average']
        ];
        
        // Filter indicators based on membership level
        $indicator_limits = [
            'free' => ['RSI', 'SMA_20', 'SMA_50'],
            'bronze' => ['RSI', 'MACD', 'SMA_20', 'SMA_50', 'EMA_12'],
            'silver' => array_keys($all_indicators),
            'gold' => array_keys($all_indicators)
        ];
        
        $allowed_indicators = $indicator_limits[$membership_level] ?? $indicator_limits['free'];
        $filtered_indicators = array_intersect_key($all_indicators, array_flip($allowed_indicators));
        
        return [
            'symbol' => $symbol,
            'indicators' => $filtered_indicators,
            'membership_level' => $membership_level,
            'available_count' => count($allowed_indicators),
            'total_available' => count($all_indicators)
        ];
    }
    
    /**
     * Get stock news
     */
    public function get_stock_news_ajax() {
        $user_id = get_current_user_id();
        $symbol = sanitize_text_field($_POST['symbol'] ?? '');
        
        // Check permissions
        $permission_check = $this->can_make_api_call($user_id, 'news');
        if (!$permission_check['allowed']) {
            wp_die(json_encode(['success' => false] + $permission_check));
        }
        
        try {
            $news_data = $this->fetch_stock_news($symbol, $user_id);
            
            // Increment usage counter
            $this->membership_manager->check_user_limit('api_calls_per_day', $user_id, true);
            
            wp_die(json_encode([
                'success' => true,
                'data' => $news_data,
                'usage' => $this->get_usage_stats($user_id)
            ]));
            
        } catch (Exception $e) {
            error_log('Stock News Error: ' . $e->getMessage());
            wp_die(json_encode([
                'success' => false,
                'error' => 'Unable to fetch news. Please try again later.'
            ]));
        }
    }
    
    /**
     * Fetch stock news
     */
    private function fetch_stock_news($symbol, $user_id = null) {
        // Mock news data
        $news_items = [
            [
                'title' => 'Stock Shows Strong Performance in Q4',
                'summary' => 'Company reports better than expected earnings...',
                'url' => 'https://example.com/news/1',
                'source' => 'Financial Times',
                'published' => time() - 3600
            ],
            [
                'title' => 'Analyst Upgrades Stock Rating',
                'summary' => 'Leading analyst firm raises price target...',
                'url' => 'https://example.com/news/2',
                'source' => 'Reuters',
                'published' => time() - 7200
            ]
        ];
        
        return [
            'symbol' => $symbol,
            'news' => $news_items,
            'count' => count($news_items)
        ];
    }
    
    /**
     * Get options data (premium feature)
     */
    public function get_options_data_ajax() {
        $user_id = get_current_user_id();
        $symbol = sanitize_text_field($_POST['symbol'] ?? '');
        
        if (!$user_id) {
            wp_die(json_encode(['success' => false, 'error' => 'Please log in to access options data']));
        }
        
        // Check permissions
        $permission_check = $this->can_make_api_call($user_id, 'options');
        if (!$permission_check['allowed']) {
            wp_die(json_encode(['success' => false] + $permission_check));
        }
        
        try {
            $options_data = $this->fetch_options_data($symbol, $user_id);
            
            // Increment usage counter
            $this->membership_manager->check_user_limit('api_calls_per_day', $user_id, true);
            
            wp_die(json_encode([
                'success' => true,
                'data' => $options_data,
                'usage' => $this->get_usage_stats($user_id)
            ]));
            
        } catch (Exception $e) {
            error_log('Options Data Error: ' . $e->getMessage());
            wp_die(json_encode([
                'success' => false,
                'error' => 'Unable to fetch options data. Please try again later.'
            ]));
        }
    }
    
    /**
     * Fetch options data
     */
    private function fetch_options_data($symbol, $user_id) {
        // Mock options data
        return [
            'symbol' => $symbol,
            'options_chain' => [
                'calls' => [
                    ['strike' => 145, 'bid' => 6.50, 'ask' => 6.75, 'volume' => 1250],
                    ['strike' => 150, 'bid' => 2.25, 'ask' => 2.50, 'volume' => 2500],
                    ['strike' => 155, 'bid' => 0.75, 'ask' => 1.00, 'volume' => 800]
                ],
                'puts' => [
                    ['strike' => 145, 'bid' => 1.25, 'ask' => 1.50, 'volume' => 900],
                    ['strike' => 150, 'bid' => 3.75, 'ask' => 4.00, 'volume' => 1800],
                    ['strike' => 155, 'bid' => 7.50, 'ask' => 7.75, 'volume' => 650]
                ]
            ],
            'iv' => 28.5,
            'expiration' => date('Y-m-d', strtotime('+30 days'))
        ];
    }
    
    /**
     * Get Level 2 data (premium feature)
     */
    public function get_level2_data_ajax() {
        $user_id = get_current_user_id();
        $symbol = sanitize_text_field($_POST['symbol'] ?? '');
        
        if (!$user_id) {
            wp_die(json_encode(['success' => false, 'error' => 'Please log in to access Level 2 data']));
        }
        
        // Check permissions
        $permission_check = $this->can_make_api_call($user_id, 'level2');
        if (!$permission_check['allowed']) {
            wp_die(json_encode(['success' => false] + $permission_check));
        }
        
        try {
            $level2_data = $this->fetch_level2_data($symbol, $user_id);
            
            // Increment usage counter
            $this->membership_manager->check_user_limit('api_calls_per_day', $user_id, true);
            
            wp_die(json_encode([
                'success' => true,
                'data' => $level2_data,
                'usage' => $this->get_usage_stats($user_id)
            ]));
            
        } catch (Exception $e) {
            error_log('Level 2 Data Error: ' . $e->getMessage());
            wp_die(json_encode([
                'success' => false,
                'error' => 'Unable to fetch Level 2 data. Please try again later.'
            ]));
        }
    }
    
    /**
     * Fetch Level 2 data
     */
    private function fetch_level2_data($symbol, $user_id) {
        // Mock Level 2 data
        return [
            'symbol' => $symbol,
            'bid_ask' => [
                'bids' => [
                    ['price' => 150.25, 'size' => 500],
                    ['price' => 150.24, 'size' => 750],
                    ['price' => 150.23, 'size' => 1000]
                ],
                'asks' => [
                    ['price' => 150.26, 'size' => 400],
                    ['price' => 150.27, 'size' => 600],
                    ['price' => 150.28, 'size' => 800]
                ]
            ],
            'time_and_sales' => [
                ['time' => time(), 'price' => 150.25, 'size' => 100],
                ['time' => time() - 10, 'price' => 150.24, 'size' => 200],
                ['time' => time() - 25, 'price' => 150.26, 'size' => 150]
            ]
        ];
    }
    
    /**
     * Get user's API usage statistics
     */
    public function get_usage_stats($user_id = null) {
        if (!$user_id) {
            $user_id = get_current_user_id();
        }
        
        return $this->membership_manager->get_user_usage_stats($user_id);
    }
    
    /**
     * Get current market status
     */
    private function get_market_status() {
        $now = new DateTime('now', new DateTimeZone('America/New_York'));
        $current_time = $now->format('H:i');
        $day_of_week = $now->format('N');
        
        // Weekend check
        if ($day_of_week >= 6) {
            return [
                'status' => 'closed',
                'message' => 'Market is closed (Weekend)',
                'next_open' => 'Monday 9:30 AM ET'
            ];
        }
        
        // Pre-market (4:00 AM - 9:30 AM ET)
        if ($current_time >= '04:00' && $current_time < '09:30') {
            return [
                'status' => 'pre_market',
                'message' => 'Pre-market trading',
                'next_change' => '9:30 AM ET (Market Open)'
            ];
        }
        
        // Regular market hours (9:30 AM - 4:00 PM ET)
        if ($current_time >= '09:30' && $current_time < '16:00') {
            return [
                'status' => 'open',
                'message' => 'Market is open',
                'next_change' => '4:00 PM ET (Market Close)'
            ];
        }
        
        // After-hours (4:00 PM - 8:00 PM ET)
        if ($current_time >= '16:00' && $current_time < '20:00') {
            return [
                'status' => 'after_hours',
                'message' => 'After-hours trading',
                'next_change' => '8:00 PM ET (Market Close)'
            ];
        }
        
        // Market closed
        return [
            'status' => 'closed',
            'message' => 'Market is closed',
            'next_open' => 'Tomorrow 9:30 AM ET'
        ];
    }
    
    /**
     * Validate API configuration
     */
    public function validate_api_config() {
        $errors = [];
        
        foreach ($this->api_endpoints as $endpoint_name => $endpoint_url) {
            if (empty($endpoint_url)) {
                $errors[] = "Missing {$endpoint_name} endpoint configuration";
            }
        }
        
        return [
            'valid' => empty($errors),
            'errors' => $errors
        ];
    }
}

// Initialize Stock API
new StockScannerAPI();