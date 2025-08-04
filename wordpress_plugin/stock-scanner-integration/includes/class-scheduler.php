<?php
/**
 * Stock Scanner Professional - Intelligent Scheduler
 * Version: 3.0.0
 * 
 * Manages timed execution of stock retrieval and news scripts with:
 * - Fixed 3-minute intervals regardless of execution time
 * - Intelligent delay calculation (180 seconds - execution time)
 * - Error handling and logging
 * - Process monitoring and recovery
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class StockScannerScheduler {
    
    // Configuration
    private $stock_interval = 180; // 3 minutes in seconds
    private $news_interval = 180;  // 3 minutes in seconds
    private $max_execution_time = 150; // Maximum allowed execution time
    private $min_delay = 10; // Minimum delay between runs
    
    // Market hours configuration
    private $market_open_hour = 4;   // 4:00 AM ET (pre-market)
    private $market_close_hour = 20; // 8:00 PM ET (post-market)
    private $system_check_interval = 300; // 5 minutes for system checks
    
    // Process tracking
    private $stock_process_file;
    private $news_process_file;
    private $master_process_file;
    private $log_file;
    private $status_file;
    
    // Paths
    private $stock_script_path;
    private $news_script_path;
    private $server_start_script;
    private $django_project_path;
    
    public function __construct() {
        $this->stock_process_file = ABSPATH . 'wp-content/stock_process.pid';
        $this->news_process_file = ABSPATH . 'wp-content/news_process.pid';
        $this->master_process_file = ABSPATH . 'wp-content/master_scheduler.pid';
        $this->log_file = ABSPATH . 'wp-content/scheduler.log';
        $this->status_file = ABSPATH . 'wp-content/scheduler_status.json';
        
        // Set script paths
        $this->stock_script_path = dirname(ABSPATH) . '/enhanced_stock_retrieval_working.py';
        $this->news_script_path = dirname(ABSPATH) . '/yahoo_news_test.py';
        $this->server_start_script = dirname(ABSPATH) . '/run_production.sh';
        $this->django_project_path = dirname(ABSPATH) . '/stockscanner_django';
        
        // Register shutdown function to clean up processes
        register_shutdown_function([$this, 'cleanup']);
    }
    
    /**
     * Start the master scheduler daemon with market hours awareness
     */
    public function start() {
        $this->log("Stock Scanner Master Scheduler starting...");
        
        // Start master scheduler process
        $pid = pcntl_fork();
        
        if ($pid == -1) {
            $this->log("ERROR: Could not fork master scheduler process");
            return false;
        } elseif ($pid == 0) {
            // Child process - run master scheduler
            $this->run_master_scheduler();
            exit(0);
        } else {
            // Parent process - save PID
            file_put_contents($this->master_process_file, $pid);
            $this->log("Master scheduler started with PID: $pid");
            return $pid;
        }
    }
    
    /**
     * Run master scheduler that manages market hours and system startup
     */
    private function run_master_scheduler() {
        $this->log("Master scheduler loop started - managing market hours and systems");
        
        while (true) {
            try {
                $current_status = $this->get_current_market_status();
                
                if ($current_status['is_market_hours']) {
                    // Market is open - ensure systems are running
                    if (!$this->are_systems_running()) {
                        $this->log("Market is open but systems are down - starting up...");
                        $this->startup_systems();
                    }
                    
                    // Ensure schedulers are running
                    if (!$this->are_schedulers_running()) {
                        $this->log("Starting data collection schedulers...");
                        $this->start_data_schedulers();
                    }
                    
                } else {
                    // Market is closed - stop data collection but keep master running
                    if ($this->are_schedulers_running()) {
                        $this->log("Market closed - stopping data collection schedulers");
                        $this->stop_data_schedulers();
                    }
                    
                    // If we're close to market open, prepare systems
                    if ($current_status['minutes_to_open'] <= 30 && $current_status['minutes_to_open'] > 0) {
                        $this->log("Market opens in {$current_status['minutes_to_open']} minutes - preparing systems");
                        $this->prepare_for_market_open();
                    }
                }
                
                // Perform system health checks
                $this->perform_system_checks();
                
                // Update status file
                $this->update_status_file($current_status);
                
                // Sleep for system check interval
                sleep($this->system_check_interval);
                
            } catch (Exception $e) {
                $this->log("ERROR in master scheduler: " . $e->getMessage());
                sleep(60); // Wait 1 minute before retrying
            }
        }
    }
    
    /**
     * Schedule stock retrieval with 3-minute intervals
     */
    private function schedule_stock_retrieval() {
        // Fork process for stock retrieval
        $pid = pcntl_fork();
        
        if ($pid == -1) {
            $this->log("ERROR: Could not fork stock retrieval process");
            return false;
        } elseif ($pid == 0) {
            // Child process - run stock scheduler
            $this->run_stock_scheduler();
            exit(0);
        } else {
            // Parent process - save PID
            file_put_contents($this->stock_process_file, $pid);
            $this->log("Stock retrieval scheduler started with PID: $pid");
            return $pid;
        }
    }
    
    /**
     * Schedule news retrieval with 3-minute intervals
     */
    private function schedule_news_retrieval() {
        // Fork process for news retrieval
        $pid = pcntl_fork();
        
        if ($pid == -1) {
            $this->log("ERROR: Could not fork news retrieval process");
            return false;
        } elseif ($pid == 0) {
            // Child process - run news scheduler
            $this->run_news_scheduler();
            exit(0);
        } else {
            // Parent process - save PID
            file_put_contents($this->news_process_file, $pid);
            $this->log("News retrieval scheduler started with PID: $pid");
            return $pid;
        }
    }
    
    /**
     * Run stock retrieval scheduler loop
     */
    private function run_stock_scheduler() {
        $this->log("Stock scheduler loop started");
        
        while (true) {
            $start_time = microtime(true);
            
            try {
                $this->log("Starting stock retrieval...");
                $this->execute_stock_script();
                
                $execution_time = microtime(true) - $start_time;
                $delay = $this->calculate_delay($execution_time, $this->stock_interval);
                
                $this->log(sprintf(
                    "Stock retrieval completed in %.2f seconds. Next run in %d seconds.",
                    $execution_time,
                    $delay
                ));
                
                // Sleep for calculated delay
                sleep($delay);
                
            } catch (Exception $e) {
                $this->log("ERROR in stock scheduler: " . $e->getMessage());
                
                // Sleep for minimum delay on error
                sleep($this->min_delay);
            }
        }
    }
    
    /**
     * Run news retrieval scheduler loop
     */
    private function run_news_scheduler() {
        $this->log("News scheduler loop started");
        
        while (true) {
            $start_time = microtime(true);
            
            try {
                $this->log("Starting news retrieval...");
                $this->execute_news_script();
                
                $execution_time = microtime(true) - $start_time;
                $delay = $this->calculate_delay($execution_time, $this->news_interval);
                
                $this->log(sprintf(
                    "News retrieval completed in %.2f seconds. Next run in %d seconds.",
                    $execution_time,
                    $delay
                ));
                
                // Sleep for calculated delay
                sleep($delay);
                
            } catch (Exception $e) {
                $this->log("ERROR in news scheduler: " . $e->getMessage());
                
                // Sleep for minimum delay on error
                sleep($this->min_delay);
            }
        }
    }
    
    /**
     * Execute stock retrieval script
     */
    private function execute_stock_script() {
        if (!file_exists($this->stock_script_path)) {
            throw new Exception("Stock script not found: " . $this->stock_script_path);
        }
        
        $command = "python3 " . escapeshellarg($this->stock_script_path) . " 2>&1";
        $output = [];
        $return_code = 0;
        
        exec($command, $output, $return_code);
        
        if ($return_code !== 0) {
            $error_output = implode("\n", $output);
            throw new Exception("Stock script failed with code $return_code: $error_output");
        }
        
        $this->log("Stock script executed successfully");
        return $output;
    }
    
    /**
     * Execute news retrieval script
     */
    private function execute_news_script() {
        if (!file_exists($this->news_script_path)) {
            throw new Exception("News script not found: " . $this->news_script_path);
        }
        
        $command = "python3 " . escapeshellarg($this->news_script_path) . " 2>&1";
        $output = [];
        $return_code = 0;
        
        exec($command, $output, $return_code);
        
        if ($return_code !== 0) {
            $error_output = implode("\n", $output);
            throw new Exception("News script failed with code $return_code: $error_output");
        }
        
        $this->log("News script executed successfully");
        return $output;
    }
    
    /**
     * Calculate delay to maintain fixed interval
     * 
     * @param float $execution_time Time taken to execute script
     * @param int $target_interval Target interval in seconds (180 for 3 minutes)
     * @return int Delay in seconds
     */
    private function calculate_delay($execution_time, $target_interval) {
        $execution_seconds = (int) ceil($execution_time);
        $delay = $target_interval - $execution_seconds;
        
        // Ensure minimum delay
        if ($delay < $this->min_delay) {
            $delay = $this->min_delay;
            $this->log("WARNING: Execution time ($execution_seconds s) too close to interval ($target_interval s). Using minimum delay.");
        }
        
        // Warn if execution time exceeds safe threshold
        if ($execution_seconds > $this->max_execution_time) {
            $this->log("WARNING: Execution time ($execution_seconds s) exceeds safe threshold ({$this->max_execution_time} s)");
        }
        
        return $delay;
    }
    
    /**
     * Stop all scheduler processes
     */
    public function stop() {
        $this->log("Stopping Stock Scanner Scheduler...");
        
        // Stop stock process
        if (file_exists($this->stock_process_file)) {
            $stock_pid = (int) file_get_contents($this->stock_process_file);
            if ($stock_pid > 0) {
                posix_kill($stock_pid, SIGTERM);
                $this->log("Terminated stock process PID: $stock_pid");
            }
            unlink($this->stock_process_file);
        }
        
        // Stop news process
        if (file_exists($this->news_process_file)) {
            $news_pid = (int) file_get_contents($this->news_process_file);
            if ($news_pid > 0) {
                posix_kill($news_pid, SIGTERM);
                $this->log("Terminated news process PID: $news_pid");
            }
            unlink($this->news_process_file);
        }
        
        $this->log("Scheduler stopped successfully");
    }
    
    /**
     * Check if scheduler is running
     */
    public function is_running() {
        $stock_running = false;
        $news_running = false;
        
        // Check stock process
        if (file_exists($this->stock_process_file)) {
            $stock_pid = (int) file_get_contents($this->stock_process_file);
            $stock_running = $stock_pid > 0 && posix_kill($stock_pid, 0);
        }
        
        // Check news process
        if (file_exists($this->news_process_file)) {
            $news_pid = (int) file_get_contents($this->news_process_file);
            $news_running = $news_pid > 0 && posix_kill($news_pid, 0);
        }
        
        return [
            'stock' => $stock_running,
            'news' => $news_running,
            'both' => $stock_running && $news_running
        ];
    }
    
    /**
     * Get scheduler status
     */
    public function get_status() {
        $running = $this->is_running();
        $log_content = $this->get_recent_logs(50);
        
        return [
            'running' => $running,
            'stock_interval' => $this->stock_interval,
            'news_interval' => $this->news_interval,
            'recent_logs' => $log_content,
            'log_file' => $this->log_file
        ];
    }
    
    /**
     * Get recent log entries
     */
    private function get_recent_logs($lines = 50) {
        if (!file_exists($this->log_file)) {
            return [];
        }
        
        $log_lines = file($this->log_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        return array_slice($log_lines, -$lines);
    }
    
    /**
     * Restart scheduler
     */
    public function restart() {
        $this->log("Restarting scheduler...");
        $this->stop();
        sleep(2); // Give processes time to stop
        $this->start();
    }
    
    /**
     * Log message with timestamp
     */
    private function log($message) {
        $timestamp = date('Y-m-d H:i:s');
        $log_entry = "[$timestamp] $message" . PHP_EOL;
        
        file_put_contents($this->log_file, $log_entry, FILE_APPEND | LOCK_EX);
        
        // Also log to WordPress if available
        if (function_exists('error_log')) {
            error_log("Stock Scanner Scheduler: $message");
        }
    }
    
    /**
     * Cleanup function called on shutdown
     */
    public function cleanup() {
        // Clean up any zombie processes
        if (function_exists('pcntl_wait')) {
            pcntl_wait($status, WNOHANG);
        }
    }
    
    /**
     * Manual execution for testing
     */
    public function test_execution() {
        $results = [];
        
        try {
            $start_time = microtime(true);
            $this->execute_stock_script();
            $stock_time = microtime(true) - $start_time;
            
            $results['stock'] = [
                'success' => true,
                'execution_time' => $stock_time,
                'delay_needed' => $this->calculate_delay($stock_time, $this->stock_interval)
            ];
            
        } catch (Exception $e) {
            $results['stock'] = [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
        
        try {
            $start_time = microtime(true);
            $this->execute_news_script();
            $news_time = microtime(true) - $start_time;
            
            $results['news'] = [
                'success' => true,
                'execution_time' => $news_time,
                'delay_needed' => $this->calculate_delay($news_time, $this->news_interval)
            ];
            
        } catch (Exception $e) {
            $results['news'] = [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
        
        return $results;
    }
    
    /**
     * Get current market status with detailed information
     */
    private function get_current_market_status() {
        $now = new Date();
        $eastern_time = new DateTime($now->format('Y-m-d H:i:s'), new DateTimeZone('America/New_York'));
        
        $current_hour = (int) $eastern_time->format('H');
        $current_day = (int) $eastern_time->format('w'); // 0 = Sunday, 6 = Saturday
        
        // Check if it's a weekday
        $is_weekday = ($current_day >= 1 && $current_day <= 5);
        
        // Check if within market hours (4 AM - 8 PM ET)
        $is_market_hours = $is_weekday && 
                          ($current_hour >= $this->market_open_hour && 
                           $current_hour < $this->market_close_hour);
        
        // Calculate minutes to next market open
        $minutes_to_open = $this->calculate_minutes_to_market_open($eastern_time);
        
        // Determine market session
        $market_session = 'closed';
        if ($is_market_hours) {
            if ($current_hour < 9 || ($current_hour == 9 && (int) $eastern_time->format('i') < 30)) {
                $market_session = 'pre-market';
            } elseif ($current_hour < 16) {
                $market_session = 'regular';
            } else {
                $market_session = 'post-market';
            }
        }
        
        return [
            'current_time' => $eastern_time->format('Y-m-d H:i:s T'),
            'is_weekday' => $is_weekday,
            'is_market_hours' => $is_market_hours,
            'market_session' => $market_session,
            'current_hour' => $current_hour,
            'minutes_to_open' => $minutes_to_open,
            'next_open_time' => $this->get_next_market_open_time($eastern_time)
        ];
    }
    
    /**
     * Calculate minutes until next market open
     */
    private function calculate_minutes_to_market_open($current_time) {
        $next_open = clone $current_time;
        $current_day = (int) $current_time->format('w');
        $current_hour = (int) $current_time->format('H');
        
        // If it's weekend, move to Monday
        if ($current_day == 0) { // Sunday
            $next_open->modify('tomorrow');
        } elseif ($current_day == 6) { // Saturday
            $next_open->modify('+2 days');
        } elseif ($current_hour >= $this->market_close_hour) {
            // After market close, move to next day
            $next_open->modify('tomorrow');
            if ((int) $next_open->format('w') == 6) { // If next day is Saturday
                $next_open->modify('+2 days'); // Move to Monday
            }
        }
        
        // Set to market open time (4:00 AM)
        $next_open->setTime($this->market_open_hour, 0, 0);
        
        $diff = $next_open->getTimestamp() - $current_time->getTimestamp();
        return max(0, (int) ($diff / 60)); // Convert to minutes
    }
    
    /**
     * Get next market open time as formatted string
     */
    private function get_next_market_open_time($current_time) {
        $minutes = $this->calculate_minutes_to_market_open($current_time);
        $next_open_timestamp = $current_time->getTimestamp() + ($minutes * 60);
        
        return date('Y-m-d H:i:s T', $next_open_timestamp);
    }
    
    /**
     * Check if all required systems are running
     */
    private function are_systems_running() {
        $checks = [
            'django_server' => $this->is_django_server_running(),
            'database' => $this->is_database_accessible(),
            'api_endpoint' => $this->is_api_endpoint_responsive()
        ];
        
        return array_reduce($checks, function($carry, $check) {
            return $carry && $check;
        }, true);
    }
    
    /**
     * Check if data collection schedulers are running
     */
    private function are_schedulers_running() {
        $running = $this->is_running();
        return $running['stock'] && $running['news'];
    }
    
    /**
     * Start all required systems
     */
    private function startup_systems() {
        $this->log("Starting up all required systems...");
        
        try {
            // Start Django server
            $this->start_django_server();
            
            // Wait for server to start
            sleep(10);
            
            // Verify systems are running
            if ($this->are_systems_running()) {
                $this->log("✓ All systems started successfully");
            } else {
                $this->log("⚠ Some systems may not have started properly");
            }
            
        } catch (Exception $e) {
            $this->log("ERROR starting systems: " . $e->getMessage());
        }
    }
    
    /**
     * Start data collection schedulers
     */
    private function start_data_schedulers() {
        $this->schedule_stock_retrieval();
        $this->schedule_news_retrieval();
        $this->log("Data collection schedulers started");
    }
    
    /**
     * Stop data collection schedulers
     */
    private function stop_data_schedulers() {
        // Stop stock process
        if (file_exists($this->stock_process_file)) {
            $stock_pid = (int) file_get_contents($this->stock_process_file);
            if ($stock_pid > 0) {
                posix_kill($stock_pid, SIGTERM);
                $this->log("Stopped stock process PID: $stock_pid");
            }
            unlink($this->stock_process_file);
        }
        
        // Stop news process
        if (file_exists($this->news_process_file)) {
            $news_pid = (int) file_get_contents($this->news_process_file);
            if ($news_pid > 0) {
                posix_kill($news_pid, SIGTERM);
                $this->log("Stopped news process PID: $news_pid");
            }
            unlink($this->news_process_file);
        }
        
        $this->log("Data collection schedulers stopped");
    }
    
    /**
     * Prepare systems for market open
     */
    private function prepare_for_market_open() {
        $this->log("Preparing systems for market open...");
        
        // Pre-start Django server if not running
        if (!$this->is_django_server_running()) {
            $this->start_django_server();
        }
        
        // Run system checks
        $this->perform_comprehensive_system_check();
        
        // Clear any stale cache files
        $this->clear_stale_caches();
        
        $this->log("Market open preparation completed");
    }
    
    /**
     * Perform regular system health checks
     */
    private function perform_system_checks() {
        $checks = [
            'disk_space' => $this->check_disk_space(),
            'memory_usage' => $this->check_memory_usage(),
            'log_file_size' => $this->check_log_file_size(),
            'process_health' => $this->check_process_health()
        ];
        
        foreach ($checks as $check_name => $result) {
            if (!$result['status']) {
                $this->log("WARNING: {$check_name} check failed: {$result['message']}");
            }
        }
    }
    
    /**
     * Perform comprehensive system check
     */
    private function perform_comprehensive_system_check() {
        $this->log("Running comprehensive system check...");
        
        $checks = [
            'Django Server' => $this->is_django_server_running(),
            'Database' => $this->is_database_accessible(),
            'API Endpoint' => $this->is_api_endpoint_responsive(),
            'Stock Script' => file_exists($this->stock_script_path),
            'News Script' => file_exists($this->news_script_path),
            'Python3' => $this->is_python3_available(),
            'Required Packages' => $this->check_python_packages()
        ];
        
        foreach ($checks as $component => $status) {
            if ($status) {
                $this->log("✓ {$component}: OK");
            } else {
                $this->log("✗ {$component}: FAILED");
            }
        }
    }
    
    /**
     * Start Django server
     */
    private function start_django_server() {
        if (!file_exists($this->server_start_script)) {
            throw new Exception("Server start script not found: " . $this->server_start_script);
        }
        
        $this->log("Starting Django server...");
        
        // Make script executable
        chmod($this->server_start_script, 0755);
        
        // Start server in background
        $command = "cd " . escapeshellarg(dirname($this->server_start_script)) . " && " . 
                  escapeshellarg($this->server_start_script) . " > /dev/null 2>&1 &";
        
        exec($command);
        
        $this->log("Django server start command executed");
    }
    
    /**
     * Check if Django server is running
     */
    private function is_django_server_running() {
        // Check if Django process is running on expected port
        $command = "netstat -tlnp 2>/dev/null | grep ':8000 ' | wc -l";
        $output = shell_exec($command);
        
        return (int) trim($output) > 0;
    }
    
    /**
     * Check if database is accessible
     */
    private function is_database_accessible() {
        try {
            global $wpdb;
            $result = $wpdb->get_var("SELECT 1");
            return $result == 1;
        } catch (Exception $e) {
            return false;
        }
    }
    
    /**
     * Check if API endpoint is responsive
     */
    private function is_api_endpoint_responsive() {
        $api_url = "http://localhost:8000/api/health/";
        
        $context = stream_context_create([
            'http' => [
                'timeout' => 5,
                'method' => 'GET'
            ]
        ]);
        
        $response = @file_get_contents($api_url, false, $context);
        return $response !== false;
    }
    
    /**
     * Check if Python3 is available
     */
    private function is_python3_available() {
        $output = shell_exec('python3 --version 2>&1');
        return strpos($output, 'Python 3') !== false;
    }
    
    /**
     * Check required Python packages
     */
    private function check_python_packages() {
        $required_packages = ['requests', 'pandas', 'numpy', 'django'];
        
        foreach ($required_packages as $package) {
            $command = "python3 -c 'import {$package}' 2>&1";
            $output = shell_exec($command);
            
            if (!empty($output)) {
                return false; // Package import failed
            }
        }
        
        return true;
    }
    
    /**
     * Check disk space
     */
    private function check_disk_space() {
        $free_bytes = disk_free_space(ABSPATH);
        $total_bytes = disk_total_space(ABSPATH);
        $used_percent = (($total_bytes - $free_bytes) / $total_bytes) * 100;
        
        if ($used_percent > 90) {
            return [
                'status' => false,
                'message' => "Disk usage is {$used_percent}% - critically high"
            ];
        } elseif ($used_percent > 80) {
            return [
                'status' => true,
                'message' => "Disk usage is {$used_percent}% - warning level"
            ];
        }
        
        return [
            'status' => true,
            'message' => "Disk usage is {$used_percent}% - normal"
        ];
    }
    
    /**
     * Check memory usage
     */
    private function check_memory_usage() {
        $memory_usage = memory_get_usage(true);
        $memory_limit = ini_get('memory_limit');
        
        if ($memory_limit == '-1') {
            return ['status' => true, 'message' => 'No memory limit set'];
        }
        
        $limit_bytes = $this->convert_to_bytes($memory_limit);
        $usage_percent = ($memory_usage / $limit_bytes) * 100;
        
        if ($usage_percent > 90) {
            return [
                'status' => false,
                'message' => "Memory usage is {$usage_percent}% - critically high"
            ];
        }
        
        return [
            'status' => true,
            'message' => "Memory usage is {$usage_percent}% - normal"
        ];
    }
    
    /**
     * Check log file size
     */
    private function check_log_file_size() {
        if (!file_exists($this->log_file)) {
            return ['status' => true, 'message' => 'Log file does not exist yet'];
        }
        
        $size_bytes = filesize($this->log_file);
        $size_mb = $size_bytes / (1024 * 1024);
        
        if ($size_mb > 100) {
            // Rotate log file
            $backup_file = $this->log_file . '.backup.' . date('Y-m-d-H-i-s');
            rename($this->log_file, $backup_file);
            
            return [
                'status' => true,
                'message' => "Log file rotated (was {$size_mb}MB)"
            ];
        }
        
        return [
            'status' => true,
            'message' => "Log file size: {$size_mb}MB - normal"
        ];
    }
    
    /**
     * Check process health
     */
    private function check_process_health() {
        // Check for zombie processes
        $zombie_count = (int) shell_exec("ps aux | awk '\$8 ~ /^Z/ { count++ } END { print count+0 }'");
        
        if ($zombie_count > 5) {
            return [
                'status' => false,
                'message' => "Too many zombie processes: {$zombie_count}"
            ];
        }
        
        return [
            'status' => true,
            'message' => "Process health normal"
        ];
    }
    
    /**
     * Clear stale cache files
     */
    private function clear_stale_caches() {
        $cache_dirs = [
            ABSPATH . 'wp-content/cache/',
            '/tmp/stock_scanner_cache/'
        ];
        
        foreach ($cache_dirs as $cache_dir) {
            if (is_dir($cache_dir)) {
                $command = "find " . escapeshellarg($cache_dir) . " -type f -mtime +1 -delete 2>/dev/null";
                shell_exec($command);
                $this->log("Cleared stale cache files from: {$cache_dir}");
            }
        }
    }
    
    /**
     * Update status file with current information
     */
    private function update_status_file($market_status) {
        $status_data = [
            'last_update' => date('Y-m-d H:i:s'),
            'market_status' => $market_status,
            'schedulers_running' => $this->are_schedulers_running(),
            'systems_running' => $this->are_systems_running(),
            'master_scheduler_pid' => file_exists($this->master_process_file) ? 
                                    (int) file_get_contents($this->master_process_file) : null
        ];
        
        file_put_contents($this->status_file, json_encode($status_data, JSON_PRETTY_PRINT));
    }
    
    /**
     * Convert memory limit string to bytes
     */
    private function convert_to_bytes($size_str) {
        $size_str = trim($size_str);
        $unit = strtolower(substr($size_str, -1));
        $size = (int) substr($size_str, 0, -1);
        
        switch ($unit) {
            case 'g': return $size * 1024 * 1024 * 1024;
            case 'm': return $size * 1024 * 1024;
            case 'k': return $size * 1024;
            default: return (int) $size_str;
        }
    }
}

// Global scheduler instance
global $stock_scanner_scheduler;
$stock_scanner_scheduler = new StockScannerScheduler();