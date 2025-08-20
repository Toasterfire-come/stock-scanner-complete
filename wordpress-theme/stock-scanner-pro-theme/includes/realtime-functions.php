<?php
/**
 * Real-time Data Management Functions
 *
 * @package StockScannerPro
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Real-time data manager class
 */
class Stock_Scanner_RealTime_Manager {
    
    private static $instance = null;
    private $active_subscriptions = array();
    private $update_interval = 30; // seconds
    
    public static function getInstance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    /**
     * Initialize real-time manager
     */
    public function init() {
        // Schedule real-time updates
        if (!wp_next_scheduled('stock_scanner_realtime_update')) {
            wp_schedule_event(time(), 'stock_scanner_30_seconds', 'stock_scanner_realtime_update');
        }
        
        add_action('stock_scanner_realtime_update', array($this, 'process_realtime_updates'));
        add_action('wp_ajax_stock_scanner_subscribe_realtime', array($this, 'handle_realtime_subscription'));
        add_action('wp_ajax_nopriv_stock_scanner_subscribe_realtime', array($this, 'handle_realtime_subscription'));
    }
    
    /**
     * Handle real-time subscription requests
     */
    public function handle_realtime_subscription() {
        check_ajax_referer('stock_scanner_nonce', 'nonce');
        
        $user_id = get_current_user_id();
        $tickers = isset($_POST['tickers']) ? sanitize_text_field($_POST['tickers']) : '';
        $action_type = isset($_POST['action_type']) ? sanitize_text_field($_POST['action_type']) : 'subscribe';
        
        if (empty($tickers)) {
            wp_send_json_error('No tickers specified');
            return;
        }
        
        $ticker_array = array_map('trim', array_map('strtoupper', explode(',', $tickers)));
        
        switch ($action_type) {
            case 'subscribe':
                $this->subscribe_to_tickers($user_id, $ticker_array);
                wp_send_json_success('Subscribed to real-time updates');
                break;
                
            case 'unsubscribe':
                $this->unsubscribe_from_tickers($user_id, $ticker_array);
                wp_send_json_success('Unsubscribed from real-time updates');
                break;
                
            default:
                wp_send_json_error('Invalid action type');
        }
    }
    
    /**
     * Subscribe to ticker updates
     */
    public function subscribe_to_tickers($user_id, $tickers) {
        $session_id = $this->get_session_id();
        
        if (!isset($this->active_subscriptions[$session_id])) {
            $this->active_subscriptions[$session_id] = array(
                'user_id' => $user_id,
                'tickers' => array(),
                'last_update' => time(),
            );
        }
        
        foreach ($tickers as $ticker) {
            if (!in_array($ticker, $this->active_subscriptions[$session_id]['tickers'])) {
                $this->active_subscriptions[$session_id]['tickers'][] = $ticker;
            }
        }
        
        $this->save_active_subscriptions();
    }
    
    /**
     * Unsubscribe from ticker updates
     */
    public function unsubscribe_from_tickers($user_id, $tickers) {
        $session_id = $this->get_session_id();
        
        if (isset($this->active_subscriptions[$session_id])) {
            foreach ($tickers as $ticker) {
                $key = array_search($ticker, $this->active_subscriptions[$session_id]['tickers']);
                if ($key !== false) {
                    unset($this->active_subscriptions[$session_id]['tickers'][$key]);
                }
            }
            
            // Re-index array
            $this->active_subscriptions[$session_id]['tickers'] = array_values(
                $this->active_subscriptions[$session_id]['tickers']
            );
            
            // Remove subscription if no tickers left
            if (empty($this->active_subscriptions[$session_id]['tickers'])) {
                unset($this->active_subscriptions[$session_id]);
            }
            
            $this->save_active_subscriptions();
        }
    }
    
    /**
     * Process real-time updates
     */
    public function process_realtime_updates() {
        $this->load_active_subscriptions();
        
        if (empty($this->active_subscriptions)) {
            return;
        }
        
        // Clean up old subscriptions (older than 5 minutes)
        $current_time = time();
        foreach ($this->active_subscriptions as $session_id => $subscription) {
            if ($current_time - $subscription['last_update'] > 300) {
                unset($this->active_subscriptions[$session_id]);
            }
        }
        
        // Get all unique tickers
        $all_tickers = array();
        foreach ($this->active_subscriptions as $subscription) {
            $all_tickers = array_merge($all_tickers, $subscription['tickers']);
        }
        $all_tickers = array_unique($all_tickers);
        
        if (empty($all_tickers)) {
            return;
        }
        
        // Fetch updated data
        $updated_data = $this->fetch_bulk_stock_data($all_tickers);
        
        if (!empty($updated_data)) {
            // Store updates in cache for quick retrieval
            $this->cache_realtime_data($updated_data);
            
            // Send updates to subscribers (if WebSocket is implemented)
            $this->broadcast_updates($updated_data);
        }
        
        $this->save_active_subscriptions();
    }
    
    /**
     * Fetch bulk stock data
     */
    private function fetch_bulk_stock_data($tickers) {
        $updated_data = array();
        
        foreach ($tickers as $ticker) {
            $stock_data = stock_scanner_api_request('stock/' . $ticker . '/', array(
                'bypass_cache' => true,
                'timeout' => 10,
            ));
            
            if (isset($stock_data['success']) && $stock_data['success']) {
                $updated_data[$ticker] = $stock_data['data'];
            }
        }
        
        return $updated_data;
    }
    
    /**
     * Cache real-time data
     */
    private function cache_realtime_data($data) {
        foreach ($data as $ticker => $stock_data) {
            $cache_key = 'stock_realtime_' . $ticker;
            set_transient($cache_key, $stock_data, 60); // Cache for 1 minute
        }
        
        // Also update the main stock data cache
        foreach ($data as $ticker => $stock_data) {
            $cache_key = 'stock_data_' . $ticker;
            set_transient($cache_key, $stock_data, 300); // Update main cache
        }
    }
    
    /**
     * Broadcast updates to subscribers
     */
    private function broadcast_updates($data) {
        // This would typically send WebSocket messages
        // For now, we'll just log the updates
        error_log('Broadcasting real-time updates for tickers: ' . implode(', ', array_keys($data)));
        
        // Update global JavaScript variable for polling-based updates
        $this->update_client_data($data);
    }
    
    /**
     * Update client data for JavaScript polling
     */
    private function update_client_data($data) {
        $formatted_data = array();
        
        foreach ($data as $ticker => $stock_data) {
            $formatted_data[$ticker] = array(
                'ticker' => $ticker,
                'current_price' => $stock_data['current_price'] ?? 0,
                'price_change' => $stock_data['price_change_today'] ?? 0,
                'change_percent' => $stock_data['change_percent'] ?? 0,
                'volume' => $stock_data['volume'] ?? 0,
                'last_updated' => current_time('mysql'),
            );
        }
        
        // Store in option for JavaScript retrieval
        update_option('stock_scanner_realtime_data', $formatted_data);
    }
    
    /**
     * Get session ID
     */
    private function get_session_id() {
        if (!session_id()) {
            session_start();
        }
        return session_id();
    }
    
    /**
     * Save active subscriptions
     */
    private function save_active_subscriptions() {
        update_option('stock_scanner_active_subscriptions', $this->active_subscriptions);
    }
    
    /**
     * Load active subscriptions
     */
    private function load_active_subscriptions() {
        $subscriptions = get_option('stock_scanner_active_subscriptions', array());
        if (is_array($subscriptions)) {
            $this->active_subscriptions = $subscriptions;
        }
    }
    
    /**
     * Get real-time data for tickers
     */
    public function get_realtime_data($tickers) {
        if (!is_array($tickers)) {
            $tickers = array($tickers);
        }
        
        $data = array();
        
        foreach ($tickers as $ticker) {
            $cache_key = 'stock_realtime_' . strtoupper($ticker);
            $cached_data = get_transient($cache_key);
            
            if ($cached_data !== false) {
                $data[$ticker] = $cached_data;
            } else {
                // Fallback to regular stock data
                $stock_data = stock_scanner_get_stock_safe($ticker);
                if ($stock_data) {
                    $data[$ticker] = $stock_data;
                }
            }
        }
        
        return $data;
    }
    
    /**
     * Check if ticker has real-time updates
     */
    public function has_realtime_updates($ticker) {
        $cache_key = 'stock_realtime_' . strtoupper($ticker);
        return get_transient($cache_key) !== false;
    }
}

/**
 * Initialize real-time manager
 */
function stock_scanner_init_realtime_manager() {
    $manager = Stock_Scanner_RealTime_Manager::getInstance();
    $manager->init();
}
add_action('init', 'stock_scanner_init_realtime_manager');

/**
 * Add custom cron schedule for 30 seconds
 */
function stock_scanner_add_cron_intervals($schedules) {
    $schedules['stock_scanner_30_seconds'] = array(
        'interval' => 30,
        'display' => __('Every 30 Seconds', 'stock-scanner-pro')
    );
    
    return $schedules;
}
add_filter('cron_schedules', 'stock_scanner_add_cron_intervals');

/**
 * AJAX handler for getting real-time data
 */
function stock_scanner_ajax_get_realtime_data() {
    check_ajax_referer('stock_scanner_nonce', 'nonce');
    
    $tickers = isset($_POST['tickers']) ? sanitize_text_field($_POST['tickers']) : '';
    
    if (empty($tickers)) {
        wp_send_json_error('No tickers specified');
        return;
    }
    
    $ticker_array = array_map('trim', array_map('strtoupper', explode(',', $tickers)));
    $manager = Stock_Scanner_RealTime_Manager::getInstance();
    $data = $manager->get_realtime_data($ticker_array);
    
    wp_send_json_success($data);
}
add_action('wp_ajax_stock_scanner_get_realtime_data', 'stock_scanner_ajax_get_realtime_data');
add_action('wp_ajax_nopriv_stock_scanner_get_realtime_data', 'stock_scanner_ajax_get_realtime_data');

/**
 * WebSocket server integration (placeholder for future implementation)
 */
class Stock_Scanner_WebSocket_Server {
    
    private $port = 8080;
    private $clients = array();
    
    public function start() {
        // WebSocket server implementation would go here
        // This is a placeholder for future WebSocket integration
        error_log('WebSocket server would start on port ' . $this->port);
    }
    
    public function broadcast_to_clients($data) {
        // Broadcast data to all connected WebSocket clients
        error_log('Broadcasting to ' . count($this->clients) . ' WebSocket clients');
    }
}

/**
 * Server-Sent Events (SSE) endpoint for real-time updates
 */
function stock_scanner_sse_endpoint() {
    if (!isset($_GET['tickers']) || !isset($_GET['nonce'])) {
        return;
    }
    
    if (!wp_verify_nonce($_GET['nonce'], 'stock_scanner_nonce')) {
        return;
    }
    
    $tickers = sanitize_text_field($_GET['tickers']);
    $ticker_array = array_map('trim', array_map('strtoupper', explode(',', $tickers)));
    
    // Set headers for SSE
    header('Content-Type: text/event-stream');
    header('Cache-Control: no-cache');
    header('Connection: keep-alive');
    
    // Disable output buffering
    if (ob_get_level()) {
        ob_end_clean();
    }
    
    $manager = Stock_Scanner_RealTime_Manager::getInstance();
    
    while (true) {
        $data = $manager->get_realtime_data($ticker_array);
        
        if (!empty($data)) {
            echo "data: " . json_encode($data) . "\n\n";
            flush();
        }
        
        sleep(5); // Update every 5 seconds
        
        // Check if connection is still alive
        if (connection_aborted()) {
            break;
        }
    }
}

// Hook for SSE endpoint
function stock_scanner_handle_sse_request() {
    if (isset($_GET['stock_scanner_sse'])) {
        stock_scanner_sse_endpoint();
        exit;
    }
}
add_action('init', 'stock_scanner_handle_sse_request');

/**
 * Enhanced caching with Redis support
 */
class Stock_Scanner_Advanced_Cache {
    
    private $redis = null;
    private $use_redis = false;
    
    public function __construct() {
        if (class_exists('Redis')) {
            try {
                $this->redis = new Redis();
                $this->redis->connect('127.0.0.1', 6379);
                $this->use_redis = true;
            } catch (Exception $e) {
                error_log('Redis connection failed: ' . $e->getMessage());
                $this->use_redis = false;
            }
        }
    }
    
    public function set($key, $data, $expiration = 300) {
        if ($this->use_redis) {
            return $this->redis->setex($key, $expiration, serialize($data));
        } else {
            return set_transient($key, $data, $expiration);
        }
    }
    
    public function get($key) {
        if ($this->use_redis) {
            $data = $this->redis->get($key);
            return $data !== false ? unserialize($data) : false;
        } else {
            return get_transient($key);
        }
    }
    
    public function delete($key) {
        if ($this->use_redis) {
            return $this->redis->del($key);
        } else {
            return delete_transient($key);
        }
    }
    
    public function flush() {
        if ($this->use_redis) {
            return $this->redis->flushDB();
        } else {
            stock_scanner_clear_api_cache();
        }
    }
}

/**
 * Initialize advanced cache
 */
$GLOBALS['stock_scanner_cache'] = new Stock_Scanner_Advanced_Cache();

/**
 * Helper function to get advanced cache instance
 */
function stock_scanner_get_cache() {
    return $GLOBALS['stock_scanner_cache'];
}