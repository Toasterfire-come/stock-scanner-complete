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
    
    // Process tracking
    private $stock_process_file;
    private $news_process_file;
    private $log_file;
    
    // Paths
    private $stock_script_path;
    private $news_script_path;
    
    public function __construct() {
        $this->stock_process_file = ABSPATH . 'wp-content/stock_process.pid';
        $this->news_process_file = ABSPATH . 'wp-content/news_process.pid';
        $this->log_file = ABSPATH . 'wp-content/scheduler.log';
        
        // Set script paths
        $this->stock_script_path = dirname(ABSPATH) . '/enhanced_stock_retrieval_working.py';
        $this->news_script_path = dirname(ABSPATH) . '/yahoo_news_test.py';
        
        // Register shutdown function to clean up processes
        register_shutdown_function([$this, 'cleanup']);
    }
    
    /**
     * Start the scheduler daemon
     */
    public function start() {
        $this->log("Stock Scanner Scheduler starting...");
        
        // Start both schedulers in parallel
        $this->schedule_stock_retrieval();
        $this->schedule_news_retrieval();
        
        $this->log("Both schedulers started successfully");
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
}

// Global scheduler instance
global $stock_scanner_scheduler;
$stock_scanner_scheduler = new StockScannerScheduler();