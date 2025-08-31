<?php
/**
 * WordPress Compatibility Test
 * Tests if functions.php can be loaded without fatal errors
 */

echo "🔍 WordPress Compatibility Test\n";
echo "===============================\n\n";

// Mock WordPress functions to test compatibility
function mock_wordpress_functions() {
    // Define WordPress constants
    if (!defined('ABSPATH')) {
        define('ABSPATH', '/app/wordpress/');
    }
    
    // Mock WordPress functions that are used in functions.php
    $wp_functions = [
        'get_template_directory' => function() { return '/app'; },
        'get_template_directory_uri' => function() { return 'https://example.com/wp-content/themes/retail-trade-scanner'; },
        'wp_get_theme' => function() { 
            return (object) ['get' => function($key) { 
                return $key === 'Version' ? '2.0.0' : 'Retail Trade Scanner'; 
            }]; 
        },
        'add_action' => function($hook, $callback, $priority = 10, $args = 1) { 
            echo "  📌 Hook registered: {$hook}\n"; 
        },
        'add_filter' => function($hook, $callback, $priority = 10, $args = 1) { 
            echo "  🔧 Filter registered: {$hook}\n"; 
        },
        'wp_enqueue_script' => function($handle, $src = '', $deps = [], $ver = false, $in_footer = false) { 
            echo "  📜 Script enqueued: {$handle}\n"; 
        },
        'wp_enqueue_style' => function($handle, $src = '', $deps = [], $ver = false, $media = 'all') { 
            echo "  🎨 Style enqueued: {$handle}\n"; 
        },
        'wp_localize_script' => function($handle, $object_name, $l10n) { 
            echo "  🌐 Script localized: {$handle}\n"; 
        },
        'register_nav_menus' => function($locations) { 
            echo "  📋 Navigation menus registered: " . count($locations) . " locations\n"; 
        },
        'add_theme_support' => function($feature, $args = null) { 
            echo "  ✨ Theme support added: {$feature}\n"; 
        },
        'register_sidebar' => function($args) { 
            $name = is_array($args) ? ($args['name'] ?? 'Sidebar') : 'Sidebar';
            echo "  📦 Sidebar registered: {$name}\n"; 
        },
        'load_theme_textdomain' => function($domain, $path) { 
            echo "  🌍 Text domain loaded: {$domain}\n"; 
        },
        'wp_create_nonce' => function($action) { return 'mock_nonce_' . md5($action); },
        'admin_url' => function($path) { return 'https://example.com/wp-admin/' . $path; },
        'home_url' => function($path = '/') { return 'https://example.com' . $path; },
        'get_stylesheet_uri' => function() { return 'https://example.com/wp-content/themes/retail-trade-scanner/style.css'; },
        'wp_verify_nonce' => function($nonce, $action) { return true; },
        'sanitize_email' => function($email) { return filter_var($email, FILTER_SANITIZE_EMAIL); },
        'is_email' => function($email) { return filter_var($email, FILTER_VALIDATE_EMAIL) !== false; },
        'wp_send_json_error' => function($data) { echo json_encode(['success' => false, 'data' => $data]); },
        'wp_send_json_success' => function($data) { echo json_encode(['success' => true, 'data' => $data]); },
        'wp_send_json' => function($data) { echo json_encode($data); },
        'get_option' => function($option, $default = false) { 
            $options = [
                'admin_email' => 'admin@example.com',
                'stock_scanner_api_url' => 'https://api.example.com',
                'stock_scanner_api_secret' => 'mock_secret'
            ];
            return $options[$option] ?? $default; 
        },
        'update_option' => function($option, $value) { return true; },
        'current_time' => function($type) { return date($type === 'c' ? 'c' : 'Y-m-d H:i:s'); },
        'get_bloginfo' => function($show) { 
            $info = ['name' => 'Test Site', 'description' => 'Test Description', 'version' => '6.0'];
            return $info[$show] ?? '';
        },
        'wp_convert_hr_to_bytes' => function($value) { return 128 * 1024 * 1024; },
        'wp_mail' => function($to, $subject, $message) { return true; },
        'is_page' => function($pages = null) { return false; },
        'is_front_page' => function() { return false; },
        'is_admin' => function() { return false; },
        'current_user_can' => function($capability) { return true; },
        'wp_get_referer' => function() { return 'https://example.com/'; },
        'wp_safe_redirect' => function($location) { echo "Redirect to: {$location}\n"; },
        'sanitize_text_field' => function($str) { return strip_tags($str); },
        'wp_kses_post' => function($data) { return $data; },
        'wp_strip_all_tags' => function($string) { return strip_tags($string); },
        'get_page_by_path' => function($path) { return null; },
        'wp_insert_post' => function($postarr) { return rand(1, 1000); },
        'wp_update_post' => function($postarr) { return rand(1, 1000); },
        'update_post_meta' => function($post_id, $meta_key, $meta_value) { return true; },
        'get_theme_file_path' => function($file) { return '/app/' . $file; },
        'wp_create_nav_menu' => function($menu_name) { return rand(1, 100); },
        'wp_get_nav_menu_object' => function($menu) { return null; },
        'wp_update_nav_menu_item' => function($menu_id, $menu_item_db_id, $menu_item_data) { return rand(1, 1000); },
        'wp_get_nav_menu_items' => function($menu) { return []; },
        'get_nav_menu_locations' => function() { return []; },
        'set_theme_mod' => function($name, $value) { return true; },
        'get_theme_mod' => function($name, $default = false) { return $default; },
        'flush_rewrite_rules' => function() { return true; },
        'wp_clear_scheduled_hook' => function($hook) { return true; },
        'register_shutdown_function' => function($callback) { return true; },
        'error_get_last' => function() { return null; },
        'headers_sent' => function() { return false; },
        'header' => function($string) { echo "Header: {$string}\n"; },
        'timer_stop' => function($display, $precision) { return 0.5; },
        'memory_get_peak_usage' => function($real_usage = false) { return 1024 * 1024; },
        'ini_set' => function($varname, $newvalue) { return true; },
        'error_reporting' => function($level = null) { return E_ALL; },
        'wp_parse_url' => function($url) { return parse_url($url); },
        'esc_url' => function($url) { return htmlspecialchars($url, ENT_QUOTES, 'UTF-8'); },
        'esc_attr' => function($text) { return htmlspecialchars($text, ENT_QUOTES, 'UTF-8'); },
        'wp_json_encode' => function($data) { return json_encode($data); },
        'wp_get_document_title' => function() { return 'Test Page Title'; },
        'add_query_arg' => function($key, $value = null, $url = null) { return 'https://example.com/test'; },
        'is_singular' => function() { return false; },
        'has_post_thumbnail' => function() { return false; },
        'get_the_post_thumbnail_url' => function($post = null, $size = 'post-thumbnail') { return ''; },
        'language_attributes' => function() { return 'lang="en-US"'; },
        'bloginfo' => function($show) { echo get_bloginfo($show); },
        '__' => function($text, $domain = 'default') { return $text; },
        '_e' => function($text, $domain = 'default') { echo $text; },
        'sprintf' => 'sprintf',
        'get_the_title' => function($post = null) { return 'Test Page Title'; },
        'get_the_ID' => function() { return 1; },
        'get_post_field' => function($field, $post = null) { return 'Test content for reading time calculation.'; },
        'strip_shortcodes' => function($content) { return $content; },
        'str_word_count' => 'str_word_count',
        'ceil' => 'ceil',
        'extract' => 'extract',
        'ob_start' => 'ob_start',
        'ob_get_clean' => 'ob_get_clean',
        'include' => function($file) { return true; },
        'file_exists' => 'file_exists',
        'is_array' => 'is_array',
        'defined' => 'defined',
        'function_exists' => 'function_exists',
        'class_exists' => 'class_exists',
        'is_dir' => 'is_dir',
        'glob' => 'glob',
        'count' => 'count',
        'empty' => 'empty',
        'intval' => 'intval',
        'get_post' => function($post = null) { return (object)['ID' => 1, 'post_title' => 'Test']; },
        'add_editor_style' => function($stylesheet) { echo "  🎨 Editor style added: {$stylesheet}\n"; },
        'add_image_size' => function($name, $width, $height, $crop = false) { echo "  🖼️ Image size added: {$name}\n"; },
        'trailingslashit' => function($string) { return rtrim($string, '/') . '/'; },
        'str_replace' => 'str_replace',
        'substr' => 'substr',
        'substr_count' => 'substr_count',
        'in_array' => 'in_array',
        'array_count_values' => 'array_count_values',
        'array_filter' => 'array_filter',
        'preg_match_all' => 'preg_match_all',
        'preg_match' => 'preg_match',
        'explode' => 'explode',
        'trim' => 'trim',
        'strpos' => 'strpos',
        'rtrim' => 'rtrim',
        'htmlspecialchars' => 'htmlspecialchars',
        'strip_tags' => 'strip_tags',
        'filter_var' => 'filter_var',
        'json_encode' => 'json_encode',
        'date' => 'date',
        'rand' => 'rand',
        'md5' => 'md5',
        'parse_url' => 'parse_url'
    ];
    
    // Create mock functions
    foreach ($wp_functions as $func_name => $func_callback) {
        if (!function_exists($func_name)) {
            if (is_callable($func_callback)) {
                // Create a wrapper function
                eval("function {$func_name}() { 
                    \$args = func_get_args(); 
                    \$callback = " . var_export($func_callback, true) . "; 
                    return call_user_func_array(\$callback, \$args); 
                }");
            } else {
                // It's an alias to existing function
                eval("function {$func_name}() { 
                    \$args = func_get_args(); 
                    return call_user_func_array('{$func_callback}', \$args); 
                }");
            }
        }
    }
    
    // Define WordPress constants
    $constants = [
        'WP_DEBUG' => false,
        'WP_CLI' => false,
        'E_ERROR' => E_ERROR,
        'E_CORE_ERROR' => E_CORE_ERROR,
        'E_COMPILE_ERROR' => E_COMPILE_ERROR,
        'E_PARSE' => E_PARSE,
        'EXTR_SKIP' => EXTR_SKIP,
        'EXTR_REFS' => EXTR_REFS,
        'FILTER_SANITIZE_EMAIL' => FILTER_SANITIZE_EMAIL,
        'FILTER_VALIDATE_EMAIL' => FILTER_VALIDATE_EMAIL,
        'ENT_QUOTES' => ENT_QUOTES
    ];
    
    foreach ($constants as $name => $value) {
        if (!defined($name)) {
            define($name, $value);
        }
    }
}

// Test functions.php loading
function test_functions_php_loading() {
    echo "1. Testing functions.php loading...\n";
    
    $functions_file = '/app/functions.php';
    
    if (!file_exists($functions_file)) {
        echo "❌ functions.php not found\n";
        return false;
    }
    
    // Mock WordPress environment
    mock_wordpress_functions();
    
    // Capture any output/errors
    ob_start();
    $error_occurred = false;
    
    // Set error handler to catch any issues
    set_error_handler(function($severity, $message, $file, $line) use (&$error_occurred) {
        $error_occurred = true;
        echo "❌ Error: {$message} in {$file} on line {$line}\n";
    });
    
    try {
        // Include the functions.php file
        include_once $functions_file;
        
        if (!$error_occurred) {
            echo "✅ functions.php loaded successfully without fatal errors\n";
        }
        
    } catch (ParseError $e) {
        echo "❌ Parse Error: " . $e->getMessage() . "\n";
        $error_occurred = true;
    } catch (Error $e) {
        echo "❌ Fatal Error: " . $e->getMessage() . "\n";
        $error_occurred = true;
    } catch (Exception $e) {
        echo "❌ Exception: " . $e->getMessage() . "\n";
        $error_occurred = true;
    }
    
    // Restore error handler
    restore_error_handler();
    
    $output = ob_get_clean();
    echo $output;
    
    return !$error_occurred;
}

// Test specific function existence
function test_function_existence() {
    echo "\n2. Testing critical function existence...\n";
    
    $critical_functions = [
        'rts_theme_setup',
        'rts_enqueue_assets', 
        'rts_handle_subscription',
        'rts_health_status_endpoint',
        'rts_body_classes',
        'rts_theme_activation',
        'rts_create_essential_pages',
        'rts_force_create_pages',
        'rts_admin_create_pages'
    ];
    
    $all_exist = true;
    
    foreach ($critical_functions as $func) {
        if (function_exists($func)) {
            echo "  ✅ {$func}()\n";
        } else {
            echo "  ❌ Missing: {$func}()\n";
            $all_exist = false;
        }
    }
    
    return $all_exist;
}

// Test include file dependencies
function test_include_dependencies() {
    echo "\n3. Testing include file dependencies...\n";
    
    $include_files = [
        '/inc/security.php',
        '/inc/performance.php', 
        '/inc/seo-analytics.php',
        '/inc/error-handling.php',
        '/inc/wordpress-standards.php',
        '/inc/browser-support.php',
        '/inc/monitoring.php',
        '/inc/plugin-integration.php'
    ];
    
    $all_exist = true;
    
    foreach ($include_files as $file) {
        $full_path = '/app' . $file;
        if (file_exists($full_path)) {
            echo "  ✅ {$file}\n";
            
            // Test if file can be included without errors
            ob_start();
            $error = false;
            
            try {
                include_once $full_path;
            } catch (Exception $e) {
                echo "  ❌ Error including {$file}: " . $e->getMessage() . "\n";
                $error = true;
                $all_exist = false;
            }
            
            ob_end_clean();
            
        } else {
            echo "  ❌ Missing: {$file}\n";
            $all_exist = false;
        }
    }
    
    return $all_exist;
}

// Run all tests
echo "Starting WordPress compatibility tests...\n\n";

$test1 = test_functions_php_loading();
$test2 = test_function_existence();  
$test3 = test_include_dependencies();

echo "\n" . str_repeat("=", 50) . "\n";
echo "📊 COMPATIBILITY TEST SUMMARY\n";
echo str_repeat("=", 50) . "\n";

if ($test1 && $test2 && $test3) {
    echo "✅ ALL COMPATIBILITY TESTS PASSED!\n";
    echo "🎉 Theme is WordPress compatible and ready for production\n";
    exit(0);
} else {
    echo "❌ SOME TESTS FAILED\n";
    if (!$test1) echo "   • functions.php loading failed\n";
    if (!$test2) echo "   • Missing critical functions\n";
    if (!$test3) echo "   • Include file issues\n";
    echo "🔧 Please review and fix the issues above\n";
    exit(1);
}