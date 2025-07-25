<?php
/**
 * Stock Scanner API Interceptor
 * Intercepts all API calls, enforces usage limits, and maintains professional styling
 */

if (!defined('ABSPATH')) {
    exit;
}

class StockScannerAPIInterceptor {
    
    private $usage_tracker;
    private $api_base_url;
    private $api_key;
    
    public function __construct() {
        global $stock_scanner_usage_tracker;
        $this->usage_tracker = $stock_scanner_usage_tracker;
        $this->api_base_url = get_option('stock_scanner_api_url', 'https://api.retailtradescanner.com/api/');
        $this->api_key = get_option('stock_scanner_api_key', '');
        
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_professional_assets'));
        
        // AJAX handlers for different API calls
        add_action('wp_ajax_stock_scanner_api', array($this, 'handle_api_request'));
        add_action('wp_ajax_nopriv_stock_scanner_api', array($this, 'handle_api_request'));
        
        // Shortcode handlers
        add_shortcode('stock_scanner_widget', array($this, 'render_stock_widget'));
        add_shortcode('stock_scanner_search', array($this, 'render_search_widget'));
        add_shortcode('stock_scanner_news', array($this, 'render_news_widget'));
        add_shortcode('stock_scanner_alerts', array($this, 'render_alerts_widget'));
        add_shortcode('stock_scanner_portfolio', array($this, 'render_portfolio_widget'));
        
        // Professional page content filters
        add_filter('the_content', array($this, 'enhance_professional_content'));
        
        // Add professional styling hooks
        add_action('wp_head', array($this, 'add_professional_styles'));
        add_action('wp_footer', array($this, 'add_professional_scripts'));
    }
    
    public function init() {
        // Register custom post types for professional features
        $this->register_professional_post_types();
        
        // Add professional menu items
        add_action('admin_menu', array($this, 'add_professional_admin_menu'));
    }
    
    /**
     * Enqueue professional assets
     */
    public function enqueue_professional_assets() {
        // Professional CSS
        wp_enqueue_style(
            'stock-scanner-professional',
            plugin_dir_url(__FILE__) . '../assets/professional.css',
            array(),
            '2.0.0'
        );
        
        // Professional JavaScript
        wp_enqueue_script(
            'stock-scanner-professional-js',
            plugin_dir_url(__FILE__) . '../assets/professional.js',
            array('jquery'),
            '2.0.0',
            true
        );
        
        // Chart.js for professional charts
        wp_enqueue_script(
            'chart-js',
            'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js',
            array(),
            '3.9.1',
            true
        );
        
        // Localize script with professional features
        wp_localize_script('stock-scanner-professional-js', 'stockScannerPro', array(
            'ajaxurl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('stock_scanner_nonce'),
            'api_base' => $this->api_base_url,
            'user_level' => $this->get_user_membership_level(),
            'features' => $this->get_available_features(),
            'limits' => $this->get_user_limits(),
            'messages' => array(
                'upgrade_required' => 'This feature requires a premium subscription. <a href="/premium-plans/" class="upgrade-link">Upgrade now</a>',
                'limit_exceeded' => 'Daily limit exceeded. <a href="/premium-plans/" class="upgrade-link">Upgrade for higher limits</a>',
                'system_busy' => 'System is busy. Premium users have priority access.',
                'loading' => 'Loading professional data...',
                'error' => 'Unable to load data. Please try again.',
                'retry' => 'Retry'
            )
        ));
    }
    
    /**
     * Handle API requests with usage tracking and professional features
     */
    public function handle_api_request() {
        check_ajax_referer('stock_scanner_nonce', 'nonce');
        
        $user_id = get_current_user_id();
        $action_type = sanitize_text_field($_POST['action_type'] ?? 'api_call');
        $endpoint = sanitize_text_field($_POST['endpoint'] ?? '');
        $params = $_POST['params'] ?? array();
        
        $start_time = microtime(true);
        
        // Check if user can make this request
        $permission_check = $this->usage_tracker->can_make_request($user_id, $action_type);
        
        if (!$permission_check['allowed']) {
            wp_send_json_error(array(
                'message' => $permission_check['message'],
                'reason' => $permission_check['reason'],
                'retry_after' => $permission_check['retry_after'] ?? null,
                'upgrade_url' => $permission_check['upgrade_url'] ?? null,
                'professional_content' => $this->render_upgrade_message($permission_check)
            ));
            return;
        }
        
        // Make the API request
        $response = $this->make_api_request($endpoint, $params);
        $response_time = microtime(true) - $start_time;
        
        // Track the usage
        $data_size = strlen(json_encode($response));
        $this->usage_tracker->track_usage(
            $user_id,
            $action_type,
            $endpoint,
            $response_time,
            $data_size
        );
        
        if (is_wp_error($response)) {
            wp_send_json_error(array(
                'message' => 'API request failed: ' . $response->get_error_message(),
                'professional_content' => $this->render_error_message($response->get_error_message())
            ));
            return;
        }
        
        // Enhance response with professional features
        $enhanced_response = $this->enhance_api_response($response, $action_type);
        
        wp_send_json_success(array(
            'data' => $enhanced_response,
            'usage_info' => array(
                'remaining' => $permission_check['remaining'] ?? null,
                'reset_time' => $permission_check['reset_time'] ?? null,
                'response_time' => round($response_time * 1000, 2) . 'ms'
            ),
            'professional_content' => $this->render_professional_content($enhanced_response, $action_type)
        ));
    }
    
    /**
     * Make API request to Django backend
     */
    private function make_api_request($endpoint, $params = array()) {
        $url = rtrim($this->api_base_url, '/') . '/' . ltrim($endpoint, '/');
        
        $args = array(
            'method' => 'GET',
            'timeout' => 30,
            'headers' => array(
                'Content-Type' => 'application/json',
                'User-Agent' => 'WordPress-StockScanner/2.0'
            )
        );
        
        if (!empty($this->api_key)) {
            $args['headers']['Authorization'] = 'Bearer ' . $this->api_key;
        }
        
        if (!empty($params)) {
            if ($args['method'] === 'GET') {
                $url .= '?' . http_build_query($params);
            } else {
                $args['body'] = json_encode($params);
                $args['method'] = 'POST';
            }
        }
        
        $response = wp_remote_request($url, $args);
        
        if (is_wp_error($response)) {
            return $response;
        }
        
        $status_code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);
        
        if ($status_code !== 200) {
            return new WP_Error('api_error', "API returned status code: {$status_code}");
        }
        
        $data = json_decode($body, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            return new WP_Error('json_error', 'Invalid JSON response from API');
        }
        
        return $data;
    }
    
    /**
     * Enhance API response with professional features
     */
    private function enhance_api_response($response, $action_type) {
        $user_level = $this->get_user_membership_level();
        
        switch ($action_type) {
            case 'stock_search':
                return $this->enhance_stock_data($response, $user_level);
            case 'news_request':
                return $this->enhance_news_data($response, $user_level);
            case 'portfolio_analysis':
                return $this->enhance_portfolio_data($response, $user_level);
            default:
                return $response;
        }
    }
    
    /**
     * Enhance stock data based on membership level
     */
    private function enhance_stock_data($data, $user_level) {
        if (!isset($data['results'])) {
            return $data;
        }
        
        foreach ($data['results'] as &$stock) {
            // Add professional indicators
            if ($user_level === 'professional') {
                $stock['professional_indicators'] = array(
                    'rsi' => $this->calculate_rsi($stock),
                    'macd' => $this->calculate_macd($stock),
                    'bollinger_bands' => $this->calculate_bollinger_bands($stock),
                    'volume_profile' => $this->calculate_volume_profile($stock)
                );
                
                $stock['advanced_metrics'] = array(
                    'sharpe_ratio' => $this->calculate_sharpe_ratio($stock),
                    'beta' => $this->calculate_beta($stock),
                    'alpha' => $this->calculate_alpha($stock)
                );
            } elseif ($user_level === 'premium') {
                $stock['premium_indicators'] = array(
                    'sma_20' => $this->calculate_sma($stock, 20),
                    'sma_50' => $this->calculate_sma($stock, 50),
                    'volume_trend' => $this->calculate_volume_trend($stock)
                );
            }
            
            // Add styling classes
            $stock['css_classes'] = $this->get_stock_css_classes($stock, $user_level);
        }
        
        return $data;
    }
    
    /**
     * Enhance news data based on membership level
     */
    private function enhance_news_data($data, $user_level) {
        if (!isset($data['results'])) {
            return $data;
        }
        
        foreach ($data['results'] as &$article) {
            if ($user_level === 'professional') {
                $article['sentiment_analysis'] = array(
                    'score' => $article['sentiment_score'] ?? 0,
                    'grade' => $article['sentiment_grade'] ?? 'N/A',
                    'confidence' => $this->calculate_sentiment_confidence($article),
                    'market_impact' => $this->calculate_market_impact($article)
                );
                
                $article['related_stocks'] = $article['mentioned_tickers'] ?? array();
            }
            
            // Add professional styling
            $article['css_classes'] = $this->get_news_css_classes($article, $user_level);
        }
        
        return $data;
    }
    
    /**
     * Render professional stock widget
     */
    public function render_stock_widget($atts) {
        $atts = shortcode_atts(array(
            'symbol' => 'AAPL',
            'style' => 'professional',
            'show_chart' => 'true',
            'show_indicators' => 'auto',
            'height' => '400px'
        ), $atts);
        
        $user_level = $this->get_user_membership_level();
        $widget_id = 'stock-widget-' . uniqid();
        
        ob_start();
        ?>
        <div class="stock-scanner-widget professional-widget" 
             id="<?php echo esc_attr($widget_id); ?>"
             data-symbol="<?php echo esc_attr($atts['symbol']); ?>"
             data-style="<?php echo esc_attr($atts['style']); ?>"
             data-user-level="<?php echo esc_attr($user_level); ?>">
            
            <div class="widget-header">
                <h3 class="widget-title">
                    <span class="symbol"><?php echo esc_html($atts['symbol']); ?></span>
                    <span class="membership-badge <?php echo esc_attr($user_level); ?>">
                        <?php echo esc_html(ucfirst($user_level)); ?>
                    </span>
                </h3>
                
                <div class="widget-controls">
                    <button class="refresh-btn" title="Refresh Data">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                    
                    <?php if ($user_level !== 'free'): ?>
                    <button class="fullscreen-btn" title="Fullscreen">
                        <i class="fas fa-expand"></i>
                    </button>
                    <?php endif; ?>
                </div>
            </div>
            
            <div class="widget-content">
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <p>Loading professional data...</p>
                </div>
                
                <div class="stock-data" style="display: none;">
                    <!-- Stock data will be populated here -->
                </div>
                
                <?php if ($atts['show_chart'] === 'true'): ?>
                <div class="stock-chart-container" style="height: <?php echo esc_attr($atts['height']); ?>;">
                    <canvas id="chart-<?php echo esc_attr($widget_id); ?>"></canvas>
                </div>
                <?php endif; ?>
                
                <?php if ($user_level === 'professional' && $atts['show_indicators'] !== 'false'): ?>
                <div class="professional-indicators">
                    <div class="indicators-grid">
                        <!-- Professional indicators will be populated here -->
                    </div>
                </div>
                <?php endif; ?>
            </div>
            
            <div class="widget-footer">
                <div class="last-updated">
                    Last updated: <span class="timestamp">--</span>
                </div>
                
                <?php if ($user_level === 'free'): ?>
                <div class="upgrade-notice">
                    <a href="/premium-plans/" class="upgrade-link">
                        Upgrade for real-time data and advanced features
                    </a>
                </div>
                <?php endif; ?>
            </div>
        </div>
        
        <script>
        jQuery(document).ready(function($) {
            StockScannerPro.initWidget('<?php echo esc_js($widget_id); ?>');
        });
        </script>
        <?php
        
        return ob_get_clean();
    }
    
    /**
     * Render professional search widget
     */
    public function render_search_widget($atts) {
        $atts = shortcode_atts(array(
            'style' => 'professional',
            'placeholder' => 'Search stocks, ETFs, or companies...',
            'show_filters' => 'true',
            'results_per_page' => '20'
        ), $atts);
        
        $user_level = $this->get_user_membership_level();
        $widget_id = 'search-widget-' . uniqid();
        
        ob_start();
        ?>
        <div class="stock-scanner-search professional-search" id="<?php echo esc_attr($widget_id); ?>">
            <div class="search-container">
                <div class="search-input-group">
                    <input type="text" 
                           class="search-input" 
                           placeholder="<?php echo esc_attr($atts['placeholder']); ?>"
                           data-user-level="<?php echo esc_attr($user_level); ?>">
                    
                    <button class="search-btn" type="button">
                        <i class="fas fa-search"></i>
                        <span>Search</span>
                    </button>
                </div>
                
                <?php if ($atts['show_filters'] === 'true' && $user_level !== 'free'): ?>
                <div class="search-filters">
                    <div class="filter-group">
                        <label>Market Cap:</label>
                        <select name="market_cap">
                            <option value="">All</option>
                            <option value="large">Large Cap (>$10B)</option>
                            <option value="mid">Mid Cap ($2B-$10B)</option>
                            <option value="small">Small Cap (<$2B)</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label>Sector:</label>
                        <select name="sector">
                            <option value="">All Sectors</option>
                            <option value="technology">Technology</option>
                            <option value="healthcare">Healthcare</option>
                            <option value="finance">Finance</option>
                            <option value="energy">Energy</option>
                            <option value="consumer">Consumer</option>
                        </select>
                    </div>
                    
                    <?php if ($user_level === 'professional'): ?>
                    <div class="filter-group">
                        <label>Technical Indicators:</label>
                        <div class="checkbox-group">
                            <label><input type="checkbox" name="rsi_oversold"> RSI Oversold</label>
                            <label><input type="checkbox" name="volume_spike"> Volume Spike</label>
                            <label><input type="checkbox" name="breakout"> Breakout Pattern</label>
                        </div>
                    </div>
                    <?php endif; ?>
                </div>
                <?php endif; ?>
            </div>
            
            <div class="search-results">
                <!-- Results will be populated here -->
            </div>
            
            <div class="usage-indicator">
                <div class="usage-bar">
                    <div class="usage-fill"></div>
                </div>
                <span class="usage-text">Searches remaining: <span class="count">--</span></span>
            </div>
        </div>
        
        <script>
        jQuery(document).ready(function($) {
            StockScannerPro.initSearch('<?php echo esc_js($widget_id); ?>');
        });
        </script>
        <?php
        
        return ob_get_clean();
    }
    
    /**
     * Add professional styles to head
     */
    public function add_professional_styles() {
        $user_level = $this->get_user_membership_level();
        ?>
        <style type="text/css">
        :root {
            --stock-scanner-primary: #667eea;
            --stock-scanner-secondary: #764ba2;
            --stock-scanner-success: #48bb78;
            --stock-scanner-danger: #f56565;
            --stock-scanner-warning: #ed8936;
            --stock-scanner-info: #4299e1;
            --stock-scanner-light: #f8fafc;
            --stock-scanner-dark: #2d3748;
        }
        
        .stock-scanner-widget.professional-widget {
            background: linear-gradient(135deg, #fff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .stock-scanner-widget.professional-widget:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        .widget-header {
            background: linear-gradient(135deg, var(--stock-scanner-primary) 0%, var(--stock-scanner-secondary) 100%);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .widget-title {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .membership-badge {
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .membership-badge.professional {
            background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%);
            color: #2d3748;
        }
        
        .membership-badge.premium {
            background: linear-gradient(135deg, #9f7aea 0%, #667eea 100%);
        }
        
        .widget-controls {
            display: flex;
            gap: 8px;
        }
        
        .widget-controls button {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 8px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .widget-controls button:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.05);
        }
        
        .widget-content {
            padding: 20px;
        }
        
        .loading-spinner {
            text-align: center;
            padding: 40px 20px;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #e2e8f0;
            border-top: 4px solid var(--stock-scanner-primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .stock-data {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .data-item {
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid var(--stock-scanner-primary);
        }
        
        .data-label {
            font-size: 12px;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }
        
        .data-value {
            font-size: 18px;
            font-weight: 600;
            color: #2d3748;
        }
        
        .data-value.positive {
            color: var(--stock-scanner-success);
        }
        
        .data-value.negative {
            color: var(--stock-scanner-danger);
        }
        
        .professional-indicators {
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
            margin-top: 20px;
        }
        
        .indicators-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .indicator-card {
            background: linear-gradient(135deg, #fff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 15px;
        }
        
        .indicator-title {
            font-size: 14px;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 10px;
        }
        
        .indicator-value {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .indicator-description {
            font-size: 12px;
            color: #718096;
        }
        
        .widget-footer {
            background: #f8fafc;
            padding: 15px 20px;
            border-top: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: #718096;
        }
        
        .upgrade-notice {
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
        }
        
        .upgrade-link {
            color: white;
            text-decoration: none;
            font-weight: 500;
        }
        
        .upgrade-link:hover {
            text-decoration: underline;
        }
        
        /* Search Widget Styles */
        .stock-scanner-search.professional-search {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            overflow: hidden;
        }
        
        .search-container {
            padding: 20px;
            background: linear-gradient(135deg, #f8fafc 0%, #fff 100%);
        }
        
        .search-input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .search-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .search-input:focus {
            outline: none;
            border-color: var(--stock-scanner-primary);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .search-btn {
            background: linear-gradient(135deg, var(--stock-scanner-primary) 0%, var(--stock-scanner-secondary) 100%);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .search-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .search-filters {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            padding: 15px;
            background: #f8fafc;
            border-radius: 8px;
        }
        
        .filter-group label {
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .filter-group select {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            background: white;
        }
        
        .checkbox-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .checkbox-group label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            font-weight: normal;
            text-transform: none;
            letter-spacing: normal;
        }
        
        .usage-indicator {
            padding: 15px 20px;
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .usage-bar {
            flex: 1;
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            overflow: hidden;
        }
        
        .usage-fill {
            height: 100%;
            background: linear-gradient(135deg, var(--stock-scanner-success) 0%, var(--stock-scanner-info) 100%);
            transition: width 0.3s ease;
        }
        
        .usage-text {
            font-size: 12px;
            color: #718096;
            white-space: nowrap;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .widget-header {
                padding: 12px 15px;
            }
            
            .widget-title {
                font-size: 16px;
            }
            
            .widget-content {
                padding: 15px;
            }
            
            .search-input-group {
                flex-direction: column;
            }
            
            .search-filters {
                grid-template-columns: 1fr;
            }
        }
        
        /* User Level Specific Styles */
        <?php if ($user_level === 'free'): ?>
        .professional-indicators,
        .advanced-features {
            opacity: 0.5;
            pointer-events: none;
            position: relative;
        }
        
        .professional-indicators::after,
        .advanced-features::after {
            content: "Upgrade to access professional features";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap;
        }
        <?php endif; ?>
        </style>
        <?php
    }
    
    /**
     * Add professional JavaScript functionality
     */
    public function add_professional_scripts() {
        ?>
        <script type="text/javascript">
        window.StockScannerPro = window.StockScannerPro || {};
        
        StockScannerPro.initWidget = function(widgetId) {
            const widget = document.getElementById(widgetId);
            if (!widget) return;
            
            const symbol = widget.dataset.symbol;
            const userLevel = widget.dataset.userLevel;
            
            // Load stock data
            this.loadStockData(widget, symbol, userLevel);
            
            // Set up refresh functionality
            const refreshBtn = widget.querySelector('.refresh-btn');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', () => {
                    this.loadStockData(widget, symbol, userLevel);
                });
            }
            
            // Set up fullscreen functionality
            const fullscreenBtn = widget.querySelector('.fullscreen-btn');
            if (fullscreenBtn && userLevel !== 'free') {
                fullscreenBtn.addEventListener('click', () => {
                    this.toggleFullscreen(widget);
                });
            }
        };
        
        StockScannerPro.loadStockData = function(widget, symbol, userLevel) {
            const loadingSpinner = widget.querySelector('.loading-spinner');
            const stockData = widget.querySelector('.stock-data');
            
            if (loadingSpinner) loadingSpinner.style.display = 'block';
            if (stockData) stockData.style.display = 'none';
            
            jQuery.ajax({
                url: stockScannerPro.ajaxurl,
                type: 'POST',
                data: {
                    action: 'stock_scanner_api',
                    action_type: 'stock_search',
                    endpoint: 'stocks/search/',
                    params: { q: symbol },
                    nonce: stockScannerPro.nonce
                },
                success: (response) => {
                    if (response.success) {
                        this.renderStockData(widget, response.data, userLevel);
                        this.updateUsageIndicator(widget, response.usage_info);
                    } else {
                        this.showError(widget, response.data.message);
                    }
                },
                error: () => {
                    this.showError(widget, 'Failed to load stock data');
                },
                complete: () => {
                    if (loadingSpinner) loadingSpinner.style.display = 'none';
                }
            });
        };
        
        StockScannerPro.renderStockData = function(widget, data, userLevel) {
            const stockDataContainer = widget.querySelector('.stock-data');
            if (!stockDataContainer || !data.results || !data.results.length) return;
            
            const stock = data.results[0];
            
            let html = '';
            
            // Basic data items
            html += this.renderDataItem('Price', this.formatPrice(stock.current_price), stock.change >= 0 ? 'positive' : 'negative');
            html += this.renderDataItem('Change', this.formatChange(stock.change, stock.change_percent), stock.change >= 0 ? 'positive' : 'negative');
            html += this.renderDataItem('Volume', this.formatVolume(stock.volume_today));
            html += this.renderDataItem('Market Cap', this.formatMarketCap(stock.market_cap));
            
            if (userLevel === 'premium' || userLevel === 'professional') {
                html += this.renderDataItem('P/E Ratio', stock.pe_ratio || 'N/A');
                html += this.renderDataItem('52W High', this.formatPrice(stock.week_52_high));
                html += this.renderDataItem('52W Low', this.formatPrice(stock.week_52_low));
            }
            
            stockDataContainer.innerHTML = html;
            stockDataContainer.style.display = 'grid';
            
            // Render professional indicators
            if (userLevel === 'professional' && stock.professional_indicators) {
                this.renderProfessionalIndicators(widget, stock.professional_indicators);
            }
            
            // Update chart
            this.updateChart(widget, stock);
            
            // Update timestamp
            const timestamp = widget.querySelector('.timestamp');
            if (timestamp) {
                timestamp.textContent = new Date().toLocaleTimeString();
            }
        };
        
        StockScannerPro.renderDataItem = function(label, value, className = '') {
            return `
                <div class="data-item">
                    <div class="data-label">${label}</div>
                    <div class="data-value ${className}">${value}</div>
                </div>
            `;
        };
        
        StockScannerPro.formatPrice = function(price) {
            return price ? '$' + parseFloat(price).toFixed(2) : 'N/A';
        };
        
        StockScannerPro.formatChange = function(change, changePercent) {
            if (!change) return 'N/A';
            const sign = change >= 0 ? '+' : '';
            return `${sign}$${parseFloat(change).toFixed(2)} (${sign}${parseFloat(changePercent).toFixed(2)}%)`;
        };
        
        StockScannerPro.formatVolume = function(volume) {
            if (!volume) return 'N/A';
            const vol = parseInt(volume);
            if (vol >= 1000000) {
                return (vol / 1000000).toFixed(1) + 'M';
            } else if (vol >= 1000) {
                return (vol / 1000).toFixed(1) + 'K';
            }
            return vol.toLocaleString();
        };
        
        StockScannerPro.formatMarketCap = function(marketCap) {
            if (!marketCap) return 'N/A';
            const cap = parseInt(marketCap);
            if (cap >= 1000000000) {
                return '$' + (cap / 1000000000).toFixed(1) + 'B';
            } else if (cap >= 1000000) {
                return '$' + (cap / 1000000).toFixed(1) + 'M';
            }
            return '$' + cap.toLocaleString();
        };
        
        StockScannerPro.showError = function(widget, message) {
            const stockData = widget.querySelector('.stock-data');
            if (stockData) {
                stockData.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>${message}</p>
                        <button class="retry-btn" onclick="StockScannerPro.loadStockData(this.closest('.stock-scanner-widget'), this.closest('.stock-scanner-widget').dataset.symbol, this.closest('.stock-scanner-widget').dataset.userLevel)">
                            Retry
                        </button>
                    </div>
                `;
                stockData.style.display = 'block';
            }
        };
        
        StockScannerPro.updateUsageIndicator = function(widget, usageInfo) {
            // Update usage indicators if present
            const usageFill = widget.querySelector('.usage-fill');
            const usageCount = widget.querySelector('.usage-text .count');
            
            if (usageFill && usageInfo && usageInfo.remaining) {
                const percentage = (usageInfo.remaining / 100) * 100; // Assuming 100 is the limit
                usageFill.style.width = percentage + '%';
            }
            
            if (usageCount && usageInfo && usageInfo.remaining) {
                usageCount.textContent = usageInfo.remaining;
            }
        };
        
        // Initialize all widgets on page load
        jQuery(document).ready(function($) {
            $('.stock-scanner-widget[id^="stock-widget-"]').each(function() {
                StockScannerPro.initWidget(this.id);
            });
        });
        </script>
        <?php
    }
    
    /**
     * Get user membership level
     */
    private function get_user_membership_level() {
        $user_id = get_current_user_id();
        
        if (function_exists('pmpro_getMembershipLevelForUser')) {
            $level = pmpro_getMembershipLevelForUser($user_id);
            if ($level && $level->id) {
                switch ($level->id) {
                    case 1: return 'free';
                    case 2: return 'premium';
                    case 3: return 'professional';
                    default: return 'free';
                }
            }
        }
        
        return $user_id > 0 ? 'free' : 'free';
    }
    
    /**
     * Get available features for user level
     */
    private function get_available_features() {
        $user_level = $this->get_user_membership_level();
        
        $features = array(
            'free' => array('basic_search', 'limited_data'),
            'premium' => array('advanced_search', 'real_time_data', 'basic_charts', 'email_alerts'),
            'professional' => array('all_features', 'professional_indicators', 'advanced_analytics', 'api_access', 'priority_support')
        );
        
        return $features[$user_level] ?? $features['free'];
    }
    
    /**
     * Get user limits
     */
    private function get_user_limits() {
        $user_level = $this->get_user_membership_level();
        
        $limits = array(
            'free' => array('searches' => 20, 'api_calls' => 100),
            'premium' => array('searches' => 500, 'api_calls' => 2500),
            'professional' => array('searches' => 2000, 'api_calls' => 10000)
        );
        
        return $limits[$user_level] ?? $limits['free'];
    }
    
    /**
     * Render upgrade message
     */
    private function render_upgrade_message($permission_check) {
        ob_start();
        ?>
        <div class="upgrade-message professional-message">
            <div class="message-icon">
                <i class="fas fa-lock"></i>
            </div>
            <div class="message-content">
                <h3><?php echo esc_html($permission_check['message']); ?></h3>
                
                <?php if (isset($permission_check['upgrade_url'])): ?>
                <a href="<?php echo esc_url($permission_check['upgrade_url']); ?>" class="upgrade-btn">
                    Upgrade Now
                </a>
                <?php endif; ?>
                
                <?php if (isset($permission_check['retry_after'])): ?>
                <p class="retry-info">
                    Try again in <?php echo esc_html($this->format_time($permission_check['retry_after'])); ?>
                </p>
                <?php endif; ?>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    /**
     * Format time duration
     */
    private function format_time($seconds) {
        if ($seconds < 60) {
            return $seconds . ' seconds';
        } elseif ($seconds < 3600) {
            return floor($seconds / 60) . ' minutes';
        } else {
            return floor($seconds / 3600) . ' hours';
        }
    }
    
    // Placeholder methods for professional calculations
    private function calculate_rsi($stock) { return rand(30, 70); }
    private function calculate_macd($stock) { return array('macd' => 0.5, 'signal' => 0.3, 'histogram' => 0.2); }
    private function calculate_bollinger_bands($stock) { return array('upper' => 150, 'middle' => 145, 'lower' => 140); }
    private function calculate_volume_profile($stock) { return array('poc' => 145, 'vah' => 150, 'val' => 140); }
    private function calculate_sharpe_ratio($stock) { return 1.2; }
    private function calculate_beta($stock) { return 1.1; }
    private function calculate_alpha($stock) { return 0.05; }
    private function calculate_sma($stock, $period) { return 145.50; }
    private function calculate_volume_trend($stock) { return 'increasing'; }
    private function calculate_sentiment_confidence($article) { return 85; }
    private function calculate_market_impact($article) { return 'medium'; }
    
    private function get_stock_css_classes($stock, $user_level) {
        $classes = array('stock-item', 'level-' . $user_level);
        if ($stock['change'] >= 0) $classes[] = 'positive';
        else $classes[] = 'negative';
        return implode(' ', $classes);
    }
    
    private function get_news_css_classes($article, $user_level) {
        $classes = array('news-item', 'level-' . $user_level);
        if (isset($article['sentiment_grade'])) {
            $classes[] = 'sentiment-' . strtolower($article['sentiment_grade']);
        }
        return implode(' ', $classes);
    }
}

// Initialize the API interceptor
new StockScannerAPIInterceptor();