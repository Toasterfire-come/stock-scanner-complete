<?php
/**
 * Stock Scanner Scheduler Management Script for Windows/Hosted Environment
 * 
 * This script manages the WordPress cron-based scheduler for hosted environments
 * where direct server access is not available.
 */

// Prevent direct access when not running from command line
if (!defined('WP_CLI') && php_sapi_name() !== 'cli') {
    // Load WordPress if running from command line in project directory
    $wp_load_paths = [
        __DIR__ . '/wordpress_plugin/stock-scanner-integration/stock-scanner-integration.php',
        __DIR__ . '/wp-load.php',
        dirname(__DIR__) . '/wp-load.php',
        dirname(dirname(__DIR__)) . '/wp-load.php'
    ];
    
    $wp_loaded = false;
    foreach ($wp_load_paths as $path) {
        if (file_exists($path)) {
            if (strpos($path, 'wp-load.php') !== false) {
                require_once $path;
                $wp_loaded = true;
                break;
            } elseif (strpos($path, 'stock-scanner-integration.php') !== false) {
                // Try to load WordPress from plugin directory
                $wp_path = dirname(dirname(dirname($path))) . '/wp-load.php';
                if (file_exists($wp_path)) {
                    require_once $wp_path;
                    $wp_loaded = true;
                    break;
                }
            }
        }
    }
    
    if (!$wp_loaded) {
        echo "Error: Could not load WordPress. Please run this script from your WordPress root directory.\n";
        echo "Alternative: Use WordPress WP-CLI: wp eval-file manage_scheduler_windows.php <command>\n";
        exit(1);
    }
}

// Ensure our plugin class is loaded
if (!class_exists('StockScannerScheduler')) {
    $plugin_path = dirname(__FILE__) . '/wordpress_plugin/stock-scanner-integration/includes/class-scheduler.php';
    if (file_exists($plugin_path)) {
        require_once $plugin_path;
    } else {
        echo "Error: Stock Scanner Scheduler class not found.\n";
        exit(1);
    }
}

// ANSI color codes for Windows-compatible output
function print_colored($text, $color = 'white') {
    $colors = [
        'red' => "\033[31m",
        'green' => "\033[32m",
        'yellow' => "\033[33m",
        'blue' => "\033[34m",
        'purple' => "\033[35m",
        'cyan' => "\033[36m",
        'light_gray' => "\033[37m",
        'white' => "\033[37m",
        'reset' => "\033[0m"
    ];
    
    $color_code = isset($colors[$color]) ? $colors[$color] : $colors['white'];
    echo $color_code . $text . $colors['reset'] . PHP_EOL;
}

/**
 * Print header
 */
function print_header() {
    print_colored("╔══════════════════════════════════════════════════════════════╗", 'cyan');
    print_colored("║           Stock Scanner Scheduler Manager (Windows)         ║", 'cyan');
    print_colored("║                    WordPress Cron Edition                    ║", 'cyan');
    print_colored("╚══════════════════════════════════════════════════════════════╝", 'cyan');
    echo PHP_EOL;
}

/**
 * Show help information
 */
function show_help() {
    print_colored("Usage:", 'yellow');
    print_colored("  php manage_scheduler_windows.php <command>", 'white');
    echo PHP_EOL;
    print_colored("Commands:", 'yellow');
    print_colored("  start      - Start WordPress cron-based scheduler", 'green');
    print_colored("  stop       - Stop all scheduled events", 'red');
    print_colored("  restart    - Restart scheduler", 'purple');
    print_colored("  status     - Check current scheduler and system status", 'blue');
    print_colored("  test       - Test API connectivity", 'cyan');
    print_colored("  logs       - Show recent scheduler logs", 'light_gray');
    print_colored("  syscheck   - Run comprehensive system check", 'yellow');
    print_colored("  market     - Show current market status", 'cyan');
    print_colored("  config     - Configure API settings", 'blue');
    echo PHP_EOL;
    print_colored("WordPress hosted environment compatible", 'green');
    print_colored("Uses WordPress cron instead of system processes", 'green');
    echo PHP_EOL;
}

/**
 * Start scheduler
 */
function start_scheduler() {
    global $stock_scanner_scheduler;
    
    print_colored("Starting WordPress cron-based scheduler...", 'green');
    
    if ($stock_scanner_scheduler->start()) {
        print_colored("✓ Scheduler started successfully", 'green');
        return true;
    } else {
        print_colored("✗ Failed to start scheduler", 'red');
        return false;
    }
}

/**
 * Stop scheduler
 */
function stop_scheduler() {
    global $stock_scanner_scheduler;
    
    print_colored("Stopping scheduler...", 'red');
    
    if ($stock_scanner_scheduler->stop()) {
        print_colored("✓ Scheduler stopped successfully", 'green');
        return true;
    } else {
        print_colored("✗ Failed to stop scheduler", 'red');
        return false;
    }
}

/**
 * Show scheduler status
 */
function show_status() {
    global $stock_scanner_scheduler;
    
    print_colored("Stock Scanner Scheduler Status (WordPress Cron)", 'yellow');
    print_colored("===============================================", 'yellow');
    
    $status = $stock_scanner_scheduler->get_status();
    $running = $status['running'];
    
    // Scheduler Status
    if ($running['scheduler_active']) {
        print_colored("🎯 Scheduler:         ACTIVE", 'green');
    } else {
        print_colored("🎯 Scheduler:         INACTIVE", 'red');
    }
    
    // Market Status
    $market_status = get_current_market_status_simple();
    echo PHP_EOL;
    print_colored("Market Information:", 'cyan');
    print_colored("  Current Time (ET):  " . $market_status['current_time'], 'white');
    
    if ($market_status['is_market_hours']) {
        print_colored("  Market Status:      OPEN (" . strtoupper($market_status['market_session']) . ")", 'green');
    } else {
        print_colored("  Market Status:      CLOSED", 'red');
        print_colored("  Next Open:          " . $market_status['next_open'], 'white');
    }
    
    echo PHP_EOL;
    
    // Data Collection Status
    print_colored("Data Collection:", 'cyan');
    if ($running['data_collection_active']) {
        print_colored("  📊 Collection:       ACTIVE", 'green');
        if ($running['stock']) {
            print_colored("  📈 Stock Updates:    SCHEDULED", 'green');
        } else {
            print_colored("  📈 Stock Updates:    NOT SCHEDULED", 'red');
        }
        if ($running['news']) {
            print_colored("  📰 News Updates:     SCHEDULED", 'green');
        } else {
            print_colored("  📰 News Updates:     NOT SCHEDULED", 'red');
        }
    } else {
        print_colored("  📊 Collection:       INACTIVE", 'red');
        print_colored("  📈 Stock Updates:    PAUSED", 'red');
        print_colored("  📰 News Updates:     PAUSED", 'red');
    }
    
    echo PHP_EOL;
    
    // WordPress Cron Status
    print_colored("WordPress Cron Jobs:", 'cyan');
    $next_stock = wp_next_scheduled('stock_scanner_update_stocks');
    $next_news = wp_next_scheduled('stock_scanner_update_news');
    $next_market = wp_next_scheduled('stock_scanner_market_check');
    
    if ($next_stock) {
        $time_to_next = $next_stock - time();
        print_colored("  📈 Next Stock:       " . date('H:i:s', $next_stock) . " (in " . max(0, $time_to_next) . "s)", 'white');
    } else {
        print_colored("  📈 Next Stock:       NOT SCHEDULED", 'red');
    }
    
    if ($next_news) {
        $time_to_next = $next_news - time();
        print_colored("  📰 Next News:        " . date('H:i:s', $next_news) . " (in " . max(0, $time_to_next) . "s)", 'white');
    } else {
        print_colored("  📰 Next News:        NOT SCHEDULED", 'red');
    }
    
    if ($next_market) {
        $time_to_next = $next_market - time();
        print_colored("  🏛️  Market Check:     " . date('H:i:s', $next_market) . " (in " . max(0, $time_to_next) . "s)", 'white');
    } else {
        print_colored("  🏛️  Market Check:     NOT SCHEDULED", 'red');
    }
    
    echo PHP_EOL;
    
    // API Configuration
    $api_url = get_option('stock_scanner_api_url', 'Not configured');
    print_colored("Configuration:", 'cyan');
    print_colored("  API URL:            " . $api_url, 'white');
    print_colored("  Update Interval:    180 seconds (3 minutes)", 'white');
    print_colored("  Market Hours:       4:00 AM - 8:00 PM ET", 'white');
    
    echo PHP_EOL;
    
    // Recent activity
    if (!empty($status['recent_logs'])) {
        print_colored("Recent Activity (last 10 entries):", 'cyan');
        $recent_logs = array_slice($status['recent_logs'], -10);
        foreach ($recent_logs as $log_entry) {
            if (strpos($log_entry, 'ERROR') !== false) {
                print_colored("  " . $log_entry, 'red');
            } elseif (strpos($log_entry, 'WARNING') !== false) {
                print_colored("  " . $log_entry, 'yellow');
            } elseif (strpos($log_entry, '✓') !== false || strpos($log_entry, 'completed') !== false) {
                print_colored("  " . $log_entry, 'green');
            } elseif (strpos($log_entry, 'Starting') !== false) {
                print_colored("  " . $log_entry, 'cyan');
            } else {
                print_colored("  " . $log_entry, 'light_gray');
            }
        }
    } else {
        print_colored("No recent activity logged", 'light_gray');
    }
}

/**
 * Test API connectivity
 */
function test_api() {
    global $stock_scanner_scheduler;
    
    print_colored("Testing API Connectivity...", 'cyan');
    echo PHP_EOL;
    
    $api_url = get_option('stock_scanner_api_url', '');
    if (empty($api_url)) {
        print_colored("✗ API URL not configured", 'red');
        print_colored("Run: php manage_scheduler_windows.php config", 'yellow');
        return;
    }
    
    print_colored("API URL: " . $api_url, 'white');
    
    try {
        $results = $stock_scanner_scheduler->test_execution();
        
        if ($results && $results['api_connectivity']['status']) {
            print_colored("✓ API connectivity: OK", 'green');
        } else {
            print_colored("✗ API connectivity: FAILED", 'red');
        }
        
        if ($results && $results['wordpress_health']['status']) {
            print_colored("✓ WordPress health: OK", 'green');
        } else {
            print_colored("✗ WordPress health: FAILED", 'red');
        }
        
    } catch (Exception $e) {
        print_colored("✗ Test failed: " . $e->getMessage(), 'red');
    }
}

/**
 * Show logs
 */
function show_logs() {
    global $stock_scanner_scheduler;
    
    print_colored("Recent Scheduler Logs", 'yellow');
    print_colored("=====================", 'yellow');
    
    $status = $stock_scanner_scheduler->get_status();
    
    if (empty($status['recent_logs'])) {
        print_colored("No logs available", 'light_gray');
        return;
    }
    
    foreach ($status['recent_logs'] as $log_entry) {
        if (strpos($log_entry, 'ERROR') !== false) {
            print_colored($log_entry, 'red');
        } elseif (strpos($log_entry, 'WARNING') !== false) {
            print_colored($log_entry, 'yellow');
        } elseif (strpos($log_entry, '✓') !== false || strpos($log_entry, 'completed') !== false) {
            print_colored($log_entry, 'green');
        } elseif (strpos($log_entry, 'Starting') !== false) {
            print_colored($log_entry, 'cyan');
        } else {
            print_colored($log_entry, 'white');
        }
    }
}

/**
 * Run system check
 */
function run_system_check() {
    global $stock_scanner_scheduler;
    
    print_colored("Comprehensive System Check", 'yellow');
    print_colored("==========================", 'yellow');
    
    print_colored("Running system diagnostics...", 'cyan');
    echo PHP_EOL;
    
    try {
        // Test API connectivity
        $api_url = get_option('stock_scanner_api_url', '');
        if (!empty($api_url)) {
            print_colored("🌐 API URL:           " . $api_url, 'white');
            
            $health_response = wp_remote_get($api_url . '/api/health/', ['timeout' => 10]);
            if (!is_wp_error($health_response) && wp_remote_retrieve_response_code($health_response) === 200) {
                print_colored("🌐 API Connectivity:  ONLINE", 'green');
            } else {
                print_colored("🌐 API Connectivity:  OFFLINE", 'red');
            }
        } else {
            print_colored("🌐 API URL:           NOT CONFIGURED", 'red');
        }
        
        // Check WordPress
        global $wpdb;
        $wp_check = $wpdb->get_var("SELECT 1");
        print_colored("🏠 WordPress DB:      " . ($wp_check == 1 ? "CONNECTED" : "ERROR"), 
                     $wp_check == 1 ? 'green' : 'red');
        
        // Check plugin status
        $plugin_active = is_plugin_active('stock-scanner-integration/stock-scanner-integration.php');
        print_colored("🔌 Plugin Status:     " . ($plugin_active ? "ACTIVE" : "INACTIVE"), 
                     $plugin_active ? 'green' : 'red');
        
        // Check WordPress cron
        $cron_disabled = defined('DISABLE_WP_CRON') && DISABLE_WP_CRON;
        print_colored("⏰ WordPress Cron:    " . ($cron_disabled ? "DISABLED" : "ENABLED"), 
                     $cron_disabled ? 'red' : 'green');
        
        if ($cron_disabled) {
            print_colored("   ⚠️  WordPress cron is disabled. Scheduler will not work!", 'yellow');
            print_colored("   Fix: Remove 'define(\"DISABLE_WP_CRON\", true);' from wp-config.php", 'yellow');
        }
        
        // Check file permissions
        $upload_dir = wp_upload_dir();
        $writable = is_writable($upload_dir['basedir']);
        print_colored("📁 Upload Directory:  " . ($writable ? "WRITABLE" : "NOT WRITABLE"), 
                     $writable ? 'green' : 'red');
        
        echo PHP_EOL;
        show_market_status();
        
    } catch (Exception $e) {
        print_colored("✗ System check failed: " . $e->getMessage(), 'red');
    }
}

/**
 * Show market status
 */
function show_market_status() {
    print_colored("Current Market Status", 'yellow');
    print_colored("====================", 'yellow');
    
    $market_status = get_current_market_status_simple();
    
    print_colored("🕐 Current Time (ET):  " . $market_status['current_time'], 'white');
    print_colored("📅 Trading Day:        " . ($market_status['is_weekday'] ? "YES" : "NO (Weekend)"), 
                 $market_status['is_weekday'] ? 'green' : 'red');
    
    if ($market_status['is_market_hours']) {
        $session_color = $market_status['market_session'] === 'regular' ? 'green' : 'yellow';
        print_colored("🔔 Market Status:      " . strtoupper($market_status['market_session']) . " HOURS", $session_color);
        print_colored("📈 Data Collection:    SHOULD BE ACTIVE", 'green');
    } else {
        print_colored("🔒 Market Status:      CLOSED", 'red');
        print_colored("📈 Data Collection:    SHOULD BE PAUSED", 'red');
        print_colored("⏰ Next Open:         " . $market_status['next_open'], 'cyan');
    }
    
    echo PHP_EOL;
    print_colored("Market Hours (ET):", 'cyan');
    print_colored("  Pre-Market:   4:00 AM - 9:30 AM", 'white');
    print_colored("  Regular:      9:30 AM - 4:00 PM", 'white');
    print_colored("  Post-Market:  4:00 PM - 8:00 PM", 'white');
}

/**
 * Configure API settings
 */
function configure_api() {
    print_colored("API Configuration", 'yellow');
    print_colored("=================", 'yellow');
    
    $current_url = get_option('stock_scanner_api_url', '');
    if (!empty($current_url)) {
        print_colored("Current API URL: " . $current_url, 'white');
    } else {
        print_colored("No API URL configured", 'red');
    }
    
    echo PHP_EOL;
    print_colored("Please enter your Cloudflare tunnel URL:", 'cyan');
    print_colored("Example: https://your-tunnel.trycloudflare.com", 'light_gray');
    echo "URL: ";
    
    $handle = fopen("php://stdin", "r");
    $new_url = trim(fgets($handle));
    fclose($handle);
    
    if (!empty($new_url)) {
        // Validate URL format
        if (filter_var($new_url, FILTER_VALIDATE_URL)) {
            update_option('stock_scanner_api_url', rtrim($new_url, '/'));
            print_colored("✓ API URL saved successfully", 'green');
            
            // Test the new URL
            print_colored("Testing new API URL...", 'cyan');
            $test_response = wp_remote_get($new_url . '/api/health/', ['timeout' => 10]);
            
            if (!is_wp_error($test_response) && wp_remote_retrieve_response_code($test_response) === 200) {
                print_colored("✓ API is reachable", 'green');
            } else {
                print_colored("⚠️  API test failed - please check your URL", 'yellow');
            }
        } else {
            print_colored("✗ Invalid URL format", 'red');
        }
    } else {
        print_colored("No changes made", 'light_gray');
    }
}

/**
 * Helper function to get market status
 */
function get_current_market_status_simple() {
    $now = new DateTime('now', new DateTimeZone('America/New_York'));
    $current_hour = (int) $now->format('H');
    $current_day = (int) $now->format('w');
    
    $is_weekday = ($current_day >= 1 && $current_day <= 5);
    $is_market_hours = $is_weekday && ($current_hour >= 4 && $current_hour < 20);
    
    $market_session = 'closed';
    if ($is_market_hours) {
        if ($current_hour < 9 || ($current_hour == 9 && (int) $now->format('i') < 30)) {
            $market_session = 'pre-market';
        } elseif ($current_hour < 16) {
            $market_session = 'regular';
        } else {
            $market_session = 'post-market';
        }
    }
    
    // Calculate next open
    $next_open = clone $now;
    if ($current_day == 0) { // Sunday
        $next_open->modify('tomorrow');
    } elseif ($current_day == 6) { // Saturday
        $next_open->modify('+2 days');
    } elseif ($current_hour >= 20) {
        $next_open->modify('tomorrow');
        if ((int) $next_open->format('w') == 6) {
            $next_open->modify('+2 days');
        }
    }
    $next_open->setTime(4, 0, 0);
    
    return [
        'current_time' => $now->format('Y-m-d H:i:s T'),
        'is_weekday' => $is_weekday,
        'is_market_hours' => $is_market_hours,
        'market_session' => $market_session,
        'next_open' => $next_open->format('Y-m-d H:i:s T')
    ];
}

// Initialize scheduler instance
global $stock_scanner_scheduler;
if (!isset($stock_scanner_scheduler)) {
    $stock_scanner_scheduler = new StockScannerScheduler();
}

// Main execution
print_header();

if ($argc < 2) {
    show_help();
    exit(0);
}

$command = $argv[1];

switch ($command) {
    case 'start':
        if (start_scheduler()) {
            exit(0);
        } else {
            exit(1);
        }
        break;
        
    case 'stop':
        if (stop_scheduler()) {
            exit(0);
        } else {
            exit(1);
        }
        break;
        
    case 'restart':
        print_colored("Restarting scheduler...", 'purple');
        stop_scheduler();
        sleep(2);
        if (start_scheduler()) {
            exit(0);
        } else {
            exit(1);
        }
        break;
        
    case 'status':
        show_status();
        break;
        
    case 'test':
        test_api();
        break;
        
    case 'logs':
        show_logs();
        break;
        
    case 'syscheck':
        run_system_check();
        break;
        
    case 'market':
        show_market_status();
        break;
        
    case 'config':
        configure_api();
        break;
        
    default:
        print_colored("❌ Error: Unknown command '$command'", 'red');
        echo PHP_EOL;
        show_help();
        exit(1);
}
?>