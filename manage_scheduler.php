<?php
/**
 * Stock Scanner Professional - Scheduler Management Script
 * Version: 3.0.0
 * 
 * Command-line script to manage the intelligent scheduler for:
 * - Stock retrieval script (every 3 minutes)
 * - News retrieval script (every 3 minutes)
 * 
 * Usage:
 * php manage_scheduler.php start    - Start both schedulers
 * php manage_scheduler.php stop     - Stop both schedulers
 * php manage_scheduler.php restart  - Restart both schedulers
 * php manage_scheduler.php status   - Check scheduler status
 * php manage_scheduler.php test     - Test script execution
 * php manage_scheduler.php logs     - Show recent logs
 */

// Set working directory to WordPress root
$wordpress_root = dirname(__FILE__);
chdir($wordpress_root);

// Load WordPress environment
require_once($wordpress_root . '/wp-config.php');
require_once($wordpress_root . '/wp-load.php');

// Load scheduler class
require_once($wordpress_root . '/wordpress_plugin/stock-scanner-integration/includes/class-scheduler.php');

// Colors for console output
class ConsoleColors {
    private $foreground_colors = [
        'black' => '0;30',   'dark_gray' => '1;30',
        'blue' => '0;34',    'light_blue' => '1;34',
        'green' => '0;32',   'light_green' => '1;32',
        'cyan' => '0;36',    'light_cyan' => '1;36',
        'red' => '0;31',     'light_red' => '1;31',
        'purple' => '0;35',  'light_purple' => '1;35',
        'brown' => '0;33',   'yellow' => '1;33',
        'light_gray' => '0;37', 'white' => '1;37'
    ];
    
    public function getColoredString($string, $foreground_color = null) {
        $colored_string = "";
        
        if (isset($this->foreground_colors[$foreground_color])) {
            $colored_string .= "\033[" . $this->foreground_colors[$foreground_color] . "m";
        }
        
        $colored_string .= $string . "\033[0m";
        return $colored_string;
    }
}

$colors = new ConsoleColors();

/**
 * Print colored output
 */
function print_colored($message, $color = 'white') {
    global $colors;
    echo $colors->getColoredString($message, $color) . PHP_EOL;
}

/**
 * Print header
 */
function print_header() {
    print_colored("=================================================================", 'cyan');
    print_colored("          Stock Scanner Professional - Scheduler Manager         ", 'yellow');
    print_colored("                     Version 3.0.0                             ", 'light_gray');
    print_colored("=================================================================", 'cyan');
    echo PHP_EOL;
}

/**
 * Print usage information
 */
function print_usage() {
    print_colored("Usage:", 'yellow');
    print_colored("  php manage_scheduler.php <command>", 'white');
    echo PHP_EOL;
    print_colored("Commands:", 'yellow');
    print_colored("  start     - Start master scheduler with market hours management", 'green');
    print_colored("  stop      - Stop all schedulers and processes", 'red');
    print_colored("  restart   - Restart master scheduler", 'purple');
    print_colored("  status    - Check current scheduler and system status", 'blue');
    print_colored("  test      - Test script execution (dry run)", 'cyan');
    print_colored("  logs      - Show recent scheduler logs", 'light_gray');
    print_colored("  syscheck  - Run comprehensive system check", 'yellow');
    print_colored("  market    - Show current market status", 'cyan');
    echo PHP_EOL;
}

/**
 * Format execution time
 */
function format_time($seconds) {
    if ($seconds < 60) {
        return sprintf("%.2f seconds", $seconds);
    } elseif ($seconds < 3600) {
        return sprintf("%.1f minutes", $seconds / 60);
    } else {
        return sprintf("%.1f hours", $seconds / 3600);
    }
}

/**
 * Start scheduler
 */
function start_scheduler() {
    global $stock_scanner_scheduler;
    
    print_colored("Starting Stock Scanner Scheduler...", 'yellow');
    
    // Check if already running
    $status = $stock_scanner_scheduler->is_running();
    if ($status['both']) {
        print_colored("✗ Scheduler is already running!", 'red');
        return false;
    }
    
    try {
        $stock_scanner_scheduler->start();
        
        // Wait a moment and check if it started
        sleep(2);
        $status = $stock_scanner_scheduler->is_running();
        
        if ($status['stock']) {
            print_colored("✓ Stock retrieval scheduler started", 'green');
        } else {
            print_colored("✗ Stock retrieval scheduler failed to start", 'red');
        }
        
        if ($status['news']) {
            print_colored("✓ News retrieval scheduler started", 'green');
        } else {
            print_colored("✗ News retrieval scheduler failed to start", 'red');
        }
        
        if ($status['both']) {
            print_colored("✓ Both schedulers are running successfully!", 'green');
            print_colored("📊 Stock script runs every 3 minutes with intelligent delay calculation", 'cyan');
            print_colored("📰 News script runs every 3 minutes with intelligent delay calculation", 'cyan');
        }
        
        return $status['both'];
        
    } catch (Exception $e) {
        print_colored("✗ Error starting scheduler: " . $e->getMessage(), 'red');
        return false;
    }
}

/**
 * Stop scheduler
 */
function stop_scheduler() {
    global $stock_scanner_scheduler;
    
    print_colored("Stopping Stock Scanner Scheduler...", 'yellow');
    
    try {
        $stock_scanner_scheduler->stop();
        
        // Wait a moment and verify it stopped
        sleep(2);
        $status = $stock_scanner_scheduler->is_running();
        
        if (!$status['stock'] && !$status['news']) {
            print_colored("✓ Scheduler stopped successfully", 'green');
            return true;
        } else {
            print_colored("⚠ Some processes may still be running", 'yellow');
            return false;
        }
        
    } catch (Exception $e) {
        print_colored("✗ Error stopping scheduler: " . $e->getMessage(), 'red');
        return false;
    }
}

/**
 * Show scheduler status
 */
function show_status() {
    global $stock_scanner_scheduler;
    
    print_colored("Stock Scanner Master Scheduler Status", 'yellow');
    print_colored("=====================================", 'yellow');
    
    $status = $stock_scanner_scheduler->get_status();
    $running = $status['running'];
    
    // Check if status file exists for enhanced information
    $status_file = ABSPATH . 'wp-content/scheduler_status.json';
    $enhanced_status = [];
    if (file_exists($status_file)) {
        $enhanced_status = json_decode(file_get_contents($status_file), true);
    }
    
    // Master Scheduler Status
    $master_running = file_exists(ABSPATH . 'wp-content/master_scheduler.pid');
    if ($master_running) {
        print_colored("🎯 Master Scheduler: RUNNING", 'green');
    } else {
        print_colored("🎯 Master Scheduler: STOPPED", 'red');
    }
    
    // Market Status
    if (!empty($enhanced_status['market_status'])) {
        $market = $enhanced_status['market_status'];
        echo PHP_EOL;
        print_colored("Market Information:", 'cyan');
        print_colored("  Current Time:       " . $market['current_time'], 'white');
        
        if ($market['is_market_hours']) {
            $session_color = $market['market_session'] === 'regular' ? 'green' : 'yellow';
            print_colored("  Market Status:      OPEN (" . strtoupper($market['market_session']) . ")", $session_color);
        } else {
            print_colored("  Market Status:      CLOSED", 'red');
            print_colored("  Next Open:          " . $market['next_open_time'], 'white');
            print_colored("  Minutes to Open:    " . $market['minutes_to_open'], 'white');
        }
    }
    
    echo PHP_EOL;
    
    // Data Collection Status
    print_colored("Data Collection:", 'cyan');
    if ($running['stock']) {
        print_colored("  📊 Stock Retrieval:  RUNNING", 'green');
    } else {
        print_colored("  📊 Stock Retrieval:  STOPPED", 'red');
    }
    
    if ($running['news']) {
        print_colored("  📰 News Retrieval:   RUNNING", 'green');
    } else {
        print_colored("  📰 News Retrieval:   STOPPED", 'red');
    }
    
    echo PHP_EOL;
    
    // System Status
    if (!empty($enhanced_status['systems_running'])) {
        print_colored("System Health:", 'cyan');
        if ($enhanced_status['systems_running']) {
            print_colored("  🟢 All Systems:      OPERATIONAL", 'green');
        } else {
            print_colored("  🔴 Systems:          ISSUES DETECTED", 'red');
        }
    }
    
    echo PHP_EOL;
    
    // Configuration
    print_colored("Configuration:", 'cyan');
    print_colored("  Stock Interval:     " . $status['stock_interval'] . " seconds (3 minutes)", 'white');
    print_colored("  News Interval:      " . $status['news_interval'] . " seconds (3 minutes)", 'white');
    print_colored("  Market Hours:       4:00 AM - 8:00 PM ET", 'white');
    print_colored("  Auto Management:    ENABLED", 'green');
    print_colored("  Log File:           " . $status['log_file'], 'white');
    
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
            } elseif (strpos($log_entry, 'Starting') !== false || strpos($log_entry, 'Preparing') !== false) {
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
 * Test script execution
 */
function test_execution() {
    global $stock_scanner_scheduler;
    
    print_colored("Testing Script Execution (Dry Run)", 'yellow');
    print_colored("===================================", 'yellow');
    
    print_colored("Running test execution of both scripts...", 'cyan');
    
    try {
        $results = $stock_scanner_scheduler->test_execution();
        
        // Stock script results
        print_colored("📊 Stock Retrieval Script:", 'cyan');
        if ($results['stock']['success']) {
            $exec_time = $results['stock']['execution_time'];
            $delay = $results['stock']['delay_needed'];
            
            print_colored("  ✓ Status:           SUCCESS", 'green');
            print_colored("  ⏱ Execution Time:   " . format_time($exec_time), 'white');
            print_colored("  ⏰ Delay Needed:     {$delay} seconds", 'white');
            print_colored("  📋 Total Cycle:     " . format_time($exec_time + $delay), 'white');
            
            if ($exec_time > 150) {
                print_colored("  ⚠ WARNING: Execution time exceeds safe threshold!", 'yellow');
            }
        } else {
            print_colored("  ✗ Status:           FAILED", 'red');
            print_colored("  ❌ Error:           " . $results['stock']['error'], 'red');
        }
        
        echo PHP_EOL;
        
        // News script results
        print_colored("📰 News Retrieval Script:", 'cyan');
        if ($results['news']['success']) {
            $exec_time = $results['news']['execution_time'];
            $delay = $results['news']['delay_needed'];
            
            print_colored("  ✓ Status:           SUCCESS", 'green');
            print_colored("  ⏱ Execution Time:   " . format_time($exec_time), 'white');
            print_colored("  ⏰ Delay Needed:     {$delay} seconds", 'white');
            print_colored("  📋 Total Cycle:     " . format_time($exec_time + $delay), 'white');
            
            if ($exec_time > 150) {
                print_colored("  ⚠ WARNING: Execution time exceeds safe threshold!", 'yellow');
            }
        } else {
            print_colored("  ✗ Status:           FAILED", 'red');
            print_colored("  ❌ Error:           " . $results['news']['error'], 'red');
        }
        
    } catch (Exception $e) {
        print_colored("✗ Test execution failed: " . $e->getMessage(), 'red');
    }
}

/**
 * Show recent logs
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
        } elseif (strpos($log_entry, 'completed') !== false) {
            print_colored($log_entry, 'green');
        } elseif (strpos($log_entry, 'Starting') !== false) {
            print_colored($log_entry, 'cyan');
        } else {
            print_colored($log_entry, 'white');
        }
    }
}

/**
 * Run comprehensive system check
 */
function run_system_check() {
    global $stock_scanner_scheduler;
    
    print_colored("Comprehensive System Check", 'yellow');
    print_colored("==========================", 'yellow');
    
    print_colored("Running system diagnostics...", 'cyan');
    echo PHP_EOL;
    
    try {
        $results = $stock_scanner_scheduler->test_execution();
        
        // Check if Django server is running
        $django_running = check_django_server();
        print_colored("🌐 Django Server:      " . ($django_running ? "RUNNING" : "STOPPED"), 
                     $django_running ? 'green' : 'red');
        
        // Check database connectivity
        $db_ok = check_database();
        print_colored("🗄️  Database:          " . ($db_ok ? "CONNECTED" : "ERROR"), 
                     $db_ok ? 'green' : 'red');
        
        // Check Python3 availability
        $python_ok = check_python3();
        print_colored("🐍 Python3:           " . ($python_ok ? "AVAILABLE" : "MISSING"), 
                     $python_ok ? 'green' : 'red');
        
        // Check disk space
        $disk_info = check_disk_space();
        print_colored("💾 Disk Space:        " . $disk_info['message'], 
                     $disk_info['status'] ? 'green' : 'red');
        
        // Check script files
        $stock_script = dirname(__FILE__) . '/enhanced_stock_retrieval_working.py';
        $news_script = dirname(__FILE__) . '/yahoo_news_test.py';
        
        print_colored("📊 Stock Script:      " . (file_exists($stock_script) ? "FOUND" : "MISSING"), 
                     file_exists($stock_script) ? 'green' : 'red');
        print_colored("📰 News Script:       " . (file_exists($news_script) ? "FOUND" : "MISSING"), 
                     file_exists($news_script) ? 'green' : 'red');
        
        echo PHP_EOL;
        
        // Market status
        show_market_status();
        
    } catch (Exception $e) {
        print_colored("✗ System check failed: " . $e->getMessage(), 'red');
    }
}

/**
 * Show current market status
 */
function show_market_status() {
    print_colored("Current Market Status", 'yellow');
    print_colored("====================", 'yellow');
    
    $now = new DateTime('now', new DateTimeZone('America/New_York'));
    $current_hour = (int) $now->format('H');
    $current_day = (int) $now->format('w'); // 0 = Sunday, 6 = Saturday
    $current_time = $now->format('Y-m-d H:i:s T');
    
    print_colored("🕐 Current Time (ET):  " . $current_time, 'white');
    
    // Check if it's a weekday
    $is_weekday = ($current_day >= 1 && $current_day <= 5);
    print_colored("📅 Trading Day:        " . ($is_weekday ? "YES" : "NO (Weekend)"), 
                 $is_weekday ? 'green' : 'red');
    
    // Check market hours
    $is_market_hours = $is_weekday && ($current_hour >= 4 && $current_hour < 20);
    
    if ($is_market_hours) {
        if ($current_hour < 9 || ($current_hour == 9 && (int) $now->format('i') < 30)) {
            print_colored("🌅 Market Status:      PRE-MARKET OPEN", 'yellow');
        } elseif ($current_hour < 16) {
            print_colored("🔔 Market Status:      REGULAR HOURS OPEN", 'green');
        } else {
            print_colored("🌆 Market Status:      POST-MARKET OPEN", 'yellow');
        }
        
        print_colored("📈 Data Collection:    ACTIVE", 'green');
    } else {
        print_colored("🔒 Market Status:      CLOSED", 'red');
        print_colored("📈 Data Collection:    PAUSED", 'red');
        
        // Calculate next open time
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
        
        print_colored("⏰ Next Open:         " . $next_open->format('Y-m-d H:i:s T'), 'cyan');
        
        $diff = $next_open->getTimestamp() - $now->getTimestamp();
        $hours_until = round($diff / 3600, 1);
        print_colored("⏳ Hours Until Open:  " . $hours_until . " hours", 'cyan');
    }
    
    echo PHP_EOL;
    print_colored("Market Hours (ET):", 'cyan');
    print_colored("  Pre-Market:   4:00 AM - 9:30 AM", 'white');
    print_colored("  Regular:      9:30 AM - 4:00 PM", 'white');
    print_colored("  Post-Market:  4:00 PM - 8:00 PM", 'white');
}

/**
 * Helper function to check Django server
 */
function check_django_server() {
    $command = "netstat -tlnp 2>/dev/null | grep ':8000 ' | wc -l";
    $output = shell_exec($command);
    return (int) trim($output) > 0;
}

/**
 * Helper function to check database
 */
function check_database() {
    try {
        global $wpdb;
        $result = $wpdb->get_var("SELECT 1");
        return $result == 1;
    } catch (Exception $e) {
        return false;
    }
}

/**
 * Helper function to check Python3
 */
function check_python3() {
    $output = shell_exec('python3 --version 2>&1');
    return strpos($output, 'Python 3') !== false;
}

/**
 * Helper function to check disk space
 */
function check_disk_space() {
    $free_bytes = disk_free_space(dirname(__FILE__));
    $total_bytes = disk_total_space(dirname(__FILE__));
    $used_percent = round((($total_bytes - $free_bytes) / $total_bytes) * 100, 1);
    
    if ($used_percent > 90) {
        return [
            'status' => false,
            'message' => "{$used_percent}% USED (CRITICAL)"
        ];
    } elseif ($used_percent > 80) {
        return [
            'status' => true,
            'message' => "{$used_percent}% USED (WARNING)"
        ];
    }
    
    return [
        'status' => true,
        'message' => "{$used_percent}% USED (NORMAL)"
    ];
}

// Main execution
print_header();

if ($argc < 2) {
    print_colored("❌ Error: No command specified", 'red');
    echo PHP_EOL;
    print_usage();
    exit(1);
}

$command = strtolower($argv[1]);

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
        print_colored("Restarting master scheduler...", 'purple');
        stop_scheduler();
        sleep(3);
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
        test_execution();
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
        
    default:
        print_colored("❌ Error: Unknown command '$command'", 'red');
        echo PHP_EOL;
        print_usage();
        exit(1);
}

exit(0);