<?php
/**
 * API Tester for Stock Scanner Professional
 * 
 * Tests all API endpoints to ensure they work correctly
 */

class StockScannerAPITester {
    
    private $test_results = [];
    private $test_count = 0;
    private $passed_count = 0;
    
    public function __construct() {
        add_action('wp_ajax_test_stock_scanner_api', [$this, 'run_api_tests']);
        add_action('admin_menu', [$this, 'add_test_menu']);
    }
    
    /**
     * Add test menu to admin
     */
    public function add_test_menu() {
        add_submenu_page(
            'stock-scanner-pro',
            'API Tests',
            'API Tests',
            'manage_options',
            'stock-scanner-api-tests',
            [$this, 'test_page']
        );
    }
    
    /**
     * Test page HTML
     */
    public function test_page() {
        ?>
        <div class="wrap">
            <h1>Stock Scanner API Tests</h1>
            <p>Click the button below to test all API endpoints and ensure they're working correctly.</p>
            
            <button id="run-api-tests" class="button button-primary">Run All Tests</button>
            <button id="test-single-endpoint" class="button">Test Single Endpoint</button>
            
            <div id="test-results" style="margin-top: 20px;"></div>
        </div>
        
        <script>
        jQuery(document).ready(function($) {
            $('#run-api-tests').on('click', function() {
                const button = $(this);
                button.prop('disabled', true).text('Running Tests...');
                
                $('#test-results').html('<div class="notice notice-info"><p>Running API tests...</p></div>');
                
                $.ajax({
                    url: ajaxurl,
                    type: 'POST',
                    data: {
                        action: 'test_stock_scanner_api',
                        nonce: '<?php echo wp_create_nonce("test_api"); ?>',
                        test_type: 'all'
                    },
                    success: function(response) {
                        $('#test-results').html(response.data || response);
                        button.prop('disabled', false).text('Run All Tests');
                    },
                    error: function() {
                        $('#test-results').html('<div class="notice notice-error"><p>Test failed to run</p></div>');
                        button.prop('disabled', false).text('Run All Tests');
                    }
                });
            });
            
            $('#test-single-endpoint').on('click', function() {
                const endpoint = prompt('Enter endpoint to test (get_stock_quote, search_stocks, get_market_data, etc.):');
                if (endpoint) {
                    testSingleEndpoint(endpoint);
                }
            });
            
            function testSingleEndpoint(endpoint) {
                $.ajax({
                    url: ajaxurl,
                    type: 'POST',
                    data: {
                        action: 'test_stock_scanner_api',
                        nonce: '<?php echo wp_create_nonce("test_api"); ?>',
                        test_type: 'single',
                        endpoint: endpoint
                    },
                    success: function(response) {
                        $('#test-results').html(response.data || response);
                    }
                });
            }
        });
        </script>
        <?php
    }
    
    /**
     * Run API tests
     */
    public function run_api_tests() {
        if (!wp_verify_nonce($_POST['nonce'], 'test_api')) {
            wp_die('Security check failed');
        }
        
        if (!current_user_can('manage_options')) {
            wp_die('Insufficient permissions');
        }
        
        $test_type = sanitize_text_field($_POST['test_type'] ?? 'all');
        $endpoint = sanitize_text_field($_POST['endpoint'] ?? '');
        
        $this->test_results = [];
        $this->test_count = 0;
        $this->passed_count = 0;
        
        if ($test_type === 'single' && $endpoint) {
            $this->test_single_endpoint($endpoint);
        } else {
            $this->run_all_tests();
        }
        
        $this->output_results();
        wp_die();
    }
    
    /**
     * Run all API endpoint tests
     */
    private function run_all_tests() {
        $this->log_test_start('Stock Scanner API Comprehensive Tests');
        
        // Test basic endpoints
        $this->test_get_stock_quote();
        $this->test_search_stocks();
        $this->test_get_market_data();
        $this->test_get_technical_indicators();
        $this->test_get_stock_news();
        
        // Test premium endpoints
        $this->test_get_options_data();
        $this->test_get_level2_data();
        
        // Test error handling
        $this->test_error_handling();
        
        // Test security
        $this->test_security();
        
        $this->log_test_complete();
    }
    
    /**
     * Test single endpoint
     */
    private function test_single_endpoint($endpoint) {
        $this->log_test_start("Testing endpoint: {$endpoint}");
        
        switch ($endpoint) {
            case 'get_stock_quote':
                $this->test_get_stock_quote();
                break;
            case 'search_stocks':
                $this->test_search_stocks();
                break;
            case 'get_market_data':
                $this->test_get_market_data();
                break;
            case 'get_technical_indicators':
                $this->test_get_technical_indicators();
                break;
            case 'get_stock_news':
                $this->test_get_stock_news();
                break;
            case 'get_options_data':
                $this->test_get_options_data();
                break;
            case 'get_level2_data':
                $this->test_get_level2_data();
                break;
            default:
                $this->log_test('Unknown endpoint', false, "Endpoint '{$endpoint}' not recognized");
        }
    }
    
    /**
     * Test get_stock_quote endpoint
     */
    private function test_get_stock_quote() {
        $this->log_test_start('Testing get_stock_quote endpoint');
        
        // Test valid request
        $response = $this->make_api_request('get_stock_quote', [
            'symbol' => 'AAPL',
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ]);
        
        $this->validate_response($response, 'get_stock_quote valid request', [
            'success' => true,
            'data' => 'required',
            'data.symbol' => 'AAPL',
            'data.price' => 'numeric',
            'data.timestamp' => 'numeric'
        ]);
        
        // Test missing symbol
        $response = $this->make_api_request('get_stock_quote', [
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ]);
        
        $this->validate_response($response, 'get_stock_quote missing symbol', [
            'success' => false,
            'error' => 'Stock symbol is required'
        ]);
        
        // Test invalid symbol format
        $response = $this->make_api_request('get_stock_quote', [
            'symbol' => 'INVALID123',
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ]);
        
        $this->validate_response($response, 'get_stock_quote invalid symbol', [
            'success' => false,
            'error' => 'Invalid stock symbol format'
        ]);
    }
    
    /**
     * Test search_stocks endpoint
     */
    private function test_search_stocks() {
        $this->log_test_start('Testing search_stocks endpoint');
        
        // Test valid search
        $response = $this->make_api_request('search_stocks', [
            'query' => 'Apple',
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ]);
        
        $this->validate_response($response, 'search_stocks valid request', [
            'success' => true,
            'data' => 'required',
            'data.results' => 'array',
            'data.query' => 'Apple'
        ]);
        
        // Test empty query
        $response = $this->make_api_request('search_stocks', [
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ]);
        
        $this->validate_response($response, 'search_stocks empty query', [
            'success' => false,
            'error' => 'Search query is required'
        ]);
    }
    
    /**
     * Test get_market_data endpoint
     */
    private function test_get_market_data() {
        $this->log_test_start('Testing get_market_data endpoint');
        
        $response = $this->make_api_request('get_market_data', [
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ]);
        
        $this->validate_response($response, 'get_market_data request', [
            'success' => true,
            'data' => 'required',
            'data.indices' => 'required',
            'data.market_status' => 'required'
        ]);
    }
    
    /**
     * Test get_technical_indicators endpoint
     */
    private function test_get_technical_indicators() {
        $this->log_test_start('Testing get_technical_indicators endpoint');
        
        $response = $this->make_api_request('get_technical_indicators', [
            'symbol' => 'AAPL',
            'indicators' => ['RSI', 'MACD'],
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ]);
        
        $this->validate_response($response, 'get_technical_indicators request', [
            'success' => true,
            'data' => 'required',
            'data.symbol' => 'AAPL',
            'data.indicators' => 'required'
        ]);
    }
    
    /**
     * Test get_stock_news endpoint
     */
    private function test_get_stock_news() {
        $this->log_test_start('Testing get_stock_news endpoint');
        
        $response = $this->make_api_request('get_stock_news', [
            'symbol' => 'AAPL',
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ]);
        
        $this->validate_response($response, 'get_stock_news request', [
            'success' => true,
            'data' => 'required',
            'data.symbol' => 'AAPL',
            'data.news' => 'array'
        ]);
    }
    
    /**
     * Test get_options_data endpoint
     */
    private function test_get_options_data() {
        $this->log_test_start('Testing get_options_data endpoint');
        
        $response = $this->make_api_request('get_options_data', [
            'symbol' => 'AAPL',
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ]);
        
        // This should require login for non-premium users
        $expected = is_user_logged_in() ? [
            'success' => true,
            'data' => 'required'
        ] : [
            'success' => false,
            'error' => 'Please log in to access options data'
        ];
        
        $this->validate_response($response, 'get_options_data request', $expected);
    }
    
    /**
     * Test get_level2_data endpoint
     */
    private function test_get_level2_data() {
        $this->log_test_start('Testing get_level2_data endpoint');
        
        $response = $this->make_api_request('get_level2_data', [
            'symbol' => 'AAPL',
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ]);
        
        // This should require login for non-premium users
        $expected = is_user_logged_in() ? [
            'success' => true,
            'data' => 'required'
        ] : [
            'success' => false,
            'error' => 'Please log in to access Level 2 data'
        ];
        
        $this->validate_response($response, 'get_level2_data request', $expected);
    }
    
    /**
     * Test error handling
     */
    private function test_error_handling() {
        $this->log_test_start('Testing error handling');
        
        // Test missing nonce
        $response = $this->make_api_request('get_stock_quote', [
            'symbol' => 'AAPL'
            // No nonce
        ]);
        
        $this->validate_response($response, 'Missing nonce handling', [
            'success' => false,
            'error' => 'Security check failed'
        ]);
    }
    
    /**
     * Test security
     */
    private function test_security() {
        $this->log_test_start('Testing security measures');
        
        // Test invalid nonce
        $response = $this->make_api_request('get_stock_quote', [
            'symbol' => 'AAPL',
            'nonce' => 'invalid_nonce'
        ]);
        
        $this->validate_response($response, 'Invalid nonce handling', [
            'success' => false,
            'error' => 'Security check failed'
        ]);
        
        // Test SQL injection attempt
        $response = $this->make_api_request('get_stock_quote', [
            'symbol' => "'; DROP TABLE wp_users; --",
            'nonce' => wp_create_nonce('stock_scanner_nonce')
        ]);
        
        $this->validate_response($response, 'SQL injection protection', [
            'success' => false,
            'error' => 'Invalid stock symbol format'
        ]);
    }
    
    /**
     * Make API request simulation
     */
    private function make_api_request($action, $data = []) {
        // Simulate AJAX request
        $_POST = array_merge(['action' => $action], $data);
        
        ob_start();
        
        try {
            // Call the action hook
            do_action("wp_ajax_{$action}");
            do_action("wp_ajax_nopriv_{$action}");
        } catch (Exception $e) {
            return ['success' => false, 'error' => $e->getMessage()];
        }
        
        $output = ob_get_clean();
        
        // Try to decode JSON response
        $decoded = json_decode($output, true);
        if ($decoded !== null) {
            return $decoded;
        }
        
        return ['raw_output' => $output];
    }
    
    /**
     * Validate API response
     */
    private function validate_response($response, $test_name, $expected) {
        $this->test_count++;
        
        $passed = true;
        $errors = [];
        
        foreach ($expected as $key => $expected_value) {
            if (strpos($key, '.') !== false) {
                // Nested key check
                $keys = explode('.', $key);
                $current = $response;
                
                foreach ($keys as $nested_key) {
                    if (!isset($current[$nested_key])) {
                        $passed = false;
                        $errors[] = "Missing nested key: {$key}";
                        break;
                    }
                    $current = $current[$nested_key];
                }
                
                if ($passed && $expected_value !== 'required' && $current !== $expected_value) {
                    if ($expected_value === 'numeric' && !is_numeric($current)) {
                        $passed = false;
                        $errors[] = "Key {$key} should be numeric, got: " . gettype($current);
                    } elseif ($expected_value === 'array' && !is_array($current)) {
                        $passed = false;
                        $errors[] = "Key {$key} should be array, got: " . gettype($current);
                    } elseif (!in_array($expected_value, ['numeric', 'array', 'required']) && $current !== $expected_value) {
                        $passed = false;
                        $errors[] = "Key {$key} expected '{$expected_value}', got '{$current}'";
                    }
                }
            } else {
                // Simple key check
                if (!isset($response[$key])) {
                    $passed = false;
                    $errors[] = "Missing key: {$key}";
                } elseif ($expected_value !== 'required' && $response[$key] !== $expected_value) {
                    $passed = false;
                    $errors[] = "Key {$key} expected '{$expected_value}', got '{$response[$key]}'";
                }
            }
        }
        
        if ($passed) {
            $this->passed_count++;
        }
        
        $this->log_test($test_name, $passed, implode(', ', $errors), $response);
    }
    
    /**
     * Log test result
     */
    private function log_test($name, $passed, $error = '', $response = null) {
        $this->test_results[] = [
            'name' => $name,
            'passed' => $passed,
            'error' => $error,
            'response' => $response
        ];
    }
    
    /**
     * Log test start
     */
    private function log_test_start($message) {
        $this->test_results[] = [
            'type' => 'section',
            'message' => $message
        ];
    }
    
    /**
     * Log test completion
     */
    private function log_test_complete() {
        $this->test_results[] = [
            'type' => 'summary',
            'total' => $this->test_count,
            'passed' => $this->passed_count,
            'failed' => $this->test_count - $this->passed_count
        ];
    }
    
    /**
     * Output test results
     */
    private function output_results() {
        echo '<div class="test-results">';
        
        foreach ($this->test_results as $result) {
            if (isset($result['type'])) {
                if ($result['type'] === 'section') {
                    echo "<h3 style='color: #0073aa; margin-top: 20px;'>{$result['message']}</h3>";
                } elseif ($result['type'] === 'summary') {
                    $success_rate = $result['total'] > 0 ? round(($result['passed'] / $result['total']) * 100, 1) : 0;
                    $status_class = $result['failed'] === 0 ? 'notice-success' : 'notice-warning';
                    
                    echo "<div class='notice {$status_class}' style='margin-top: 20px;'>";
                    echo "<h3>Test Summary</h3>";
                    echo "<p><strong>Total Tests:</strong> {$result['total']}</p>";
                    echo "<p><strong>Passed:</strong> {$result['passed']}</p>";
                    echo "<p><strong>Failed:</strong> {$result['failed']}</p>";
                    echo "<p><strong>Success Rate:</strong> {$success_rate}%</p>";
                    echo "</div>";
                }
            } else {
                $status_icon = $result['passed'] ? '✅' : '❌';
                $status_color = $result['passed'] ? 'green' : 'red';
                
                echo "<div style='padding: 10px; border-left: 4px solid {$status_color}; margin: 5px 0; background: #f9f9f9;'>";
                echo "<strong>{$status_icon} {$result['name']}</strong>";
                
                if (!$result['passed'] && $result['error']) {
                    echo "<br><span style='color: red;'>Error: {$result['error']}</span>";
                }
                
                if ($result['response'] && !$result['passed']) {
                    echo "<br><details><summary>Response Data</summary>";
                    echo "<pre style='background: #f0f0f0; padding: 10px; margin: 10px 0;'>";
                    echo htmlspecialchars(json_encode($result['response'], JSON_PRETTY_PRINT));
                    echo "</pre></details>";
                }
                
                echo "</div>";
            }
        }
        
        echo '</div>';
    }
}

// Initialize API tester
if (is_admin()) {
    new StockScannerAPITester();
}