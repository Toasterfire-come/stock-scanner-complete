<?php
/**
 * WordPress Theme PHP Syntax Validation Test
 * Tests all theme PHP files for syntax errors and WordPress compatibility
 */

class WordPressThemeTester {
    private $theme_root;
    private $test_results = [];
    private $errors = [];
    private $warnings = [];
    
    public function __construct($theme_root = '/app') {
        $this->theme_root = $theme_root;
    }
    
    /**
     * Run comprehensive theme validation
     */
    public function runTests() {
        echo "🔍 WordPress Theme Validation Test\n";
        echo "==================================\n\n";
        
        // Test 1: PHP Syntax Validation
        echo "1. Testing PHP Syntax...\n";
        $this->testPHPSyntax();
        
        // Test 2: WordPress Function Dependencies
        echo "\n2. Testing WordPress Dependencies...\n";
        $this->testWordPressDependencies();
        
        // Test 3: File Structure Validation
        echo "\n3. Testing File Structure...\n";
        $this->testFileStructure();
        
        // Test 4: Functions.php Specific Tests
        echo "\n4. Testing functions.php...\n";
        $this->testFunctionsFile();
        
        // Test 5: Include Files Validation
        echo "\n5. Testing Include Files...\n";
        $this->testIncludeFiles();
        
        // Print Summary
        $this->printSummary();
        
        return empty($this->errors);
    }
    
    /**
     * Test PHP syntax for all theme files
     */
    private function testPHPSyntax() {
        $php_files = $this->getThemePhpFiles();
        
        foreach ($php_files as $file) {
            $result = $this->validatePhpSyntax($file);
            if ($result['valid']) {
                echo "  ✅ {$file}\n";
            } else {
                echo "  ❌ {$file}: {$result['error']}\n";
                $this->errors[] = "Syntax error in {$file}: {$result['error']}";
            }
        }
    }
    
    /**
     * Test WordPress function dependencies
     */
    private function testWordPressDependencies() {
        $functions_file = $this->theme_root . '/functions.php';
        
        if (!file_exists($functions_file)) {
            $this->errors[] = "functions.php not found";
            return;
        }
        
        $content = file_get_contents($functions_file);
        
        // Check for WordPress function calls
        $wp_functions = [
            'add_action', 'add_filter', 'wp_enqueue_script', 'wp_enqueue_style',
            'get_template_directory', 'get_template_directory_uri', 'wp_get_theme',
            'register_nav_menus', 'add_theme_support', 'register_sidebar'
        ];
        
        foreach ($wp_functions as $func) {
            if (strpos($content, $func) !== false) {
                echo "  ✅ Uses {$func}\n";
            }
        }
        
        // Check for potential issues
        $this->checkForCommonIssues($content);
    }
    
    /**
     * Test file structure
     */
    private function testFileStructure() {
        $required_files = [
            'functions.php' => 'Main theme functions file',
            'index.php' => 'Main template file',
            'style.css' => 'Main stylesheet',
            'templates/error-500.php' => 'Error template'
        ];
        
        foreach ($required_files as $file => $description) {
            $path = $this->theme_root . '/' . $file;
            if (file_exists($path)) {
                echo "  ✅ {$file} ({$description})\n";
            } else {
                echo "  ❌ Missing: {$file} ({$description})\n";
                $this->errors[] = "Missing required file: {$file}";
            }
        }
        
        // Check inc directory
        $inc_dir = $this->theme_root . '/inc';
        if (is_dir($inc_dir)) {
            echo "  ✅ /inc directory exists\n";
            $inc_files = glob($inc_dir . '/*.php');
            echo "  📁 Found " . count($inc_files) . " include files\n";
        } else {
            $this->warnings[] = "/inc directory not found";
        }
    }
    
    /**
     * Test functions.php specifically
     */
    private function testFunctionsFile() {
        $functions_file = $this->theme_root . '/functions.php';
        
        if (!file_exists($functions_file)) {
            $this->errors[] = "functions.php not found";
            return;
        }
        
        $content = file_get_contents($functions_file);
        
        // Check for duplicate function declarations
        $this->checkDuplicateFunctions($content);
        
        // Check for proper WordPress security
        if (strpos($content, "if (!defined('ABSPATH'))") !== false) {
            echo "  ✅ Has ABSPATH security check\n";
        } else {
            $this->warnings[] = "Missing ABSPATH security check in functions.php";
        }
        
        // Check for proper hook usage
        if (strpos($content, 'after_setup_theme') !== false) {
            echo "  ✅ Uses after_setup_theme hook\n";
        }
        
        if (strpos($content, 'wp_enqueue_scripts') !== false) {
            echo "  ✅ Uses wp_enqueue_scripts hook\n";
        }
        
        // Check for the specific fix mentioned in the review
        if (strpos($content, 'rts_create_essential_pages') !== false) {
            echo "  ✅ Contains rts_create_essential_pages function\n";
            
            // Count function declarations
            $func_count = substr_count($content, 'function rts_create_essential_pages');
            if ($func_count === 1) {
                echo "  ✅ Single function declaration (no duplicates)\n";
            } else {
                $this->errors[] = "Multiple declarations of rts_create_essential_pages function found: {$func_count}";
            }
        }
    }
    
    /**
     * Test include files
     */
    private function testIncludeFiles() {
        $functions_file = $this->theme_root . '/functions.php';
        
        if (!file_exists($functions_file)) {
            return;
        }
        
        $content = file_get_contents($functions_file);
        
        // Find require_once statements
        preg_match_all('/require_once\s+get_template_directory\(\)\s*\.\s*[\'"]([^\'"]+)[\'"]/', $content, $matches);
        
        foreach ($matches[1] as $include_path) {
            $full_path = $this->theme_root . $include_path;
            if (file_exists($full_path)) {
                echo "  ✅ {$include_path}\n";
                
                // Test syntax of include file
                $result = $this->validatePhpSyntax($full_path);
                if (!$result['valid']) {
                    $this->errors[] = "Syntax error in include {$include_path}: {$result['error']}";
                }
            } else {
                echo "  ❌ Missing include: {$include_path}\n";
                $this->errors[] = "Missing include file: {$include_path}";
            }
        }
    }
    
    /**
     * Get all PHP files in theme (excluding WordPress core)
     */
    private function getThemePhpFiles() {
        $files = [];
        $iterator = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($this->theme_root)
        );
        
        foreach ($iterator as $file) {
            if ($file->isFile() && 
                $file->getExtension() === 'php' && 
                strpos($file->getPathname(), '/wordpress/') === false &&
                strpos($file->getPathname(), '/node_modules/') === false) {
                $files[] = $file->getPathname();
            }
        }
        
        return $files;
    }
    
    /**
     * Validate PHP syntax of a file
     */
    private function validatePhpSyntax($file) {
        $output = [];
        $return_code = 0;
        
        exec("php -l " . escapeshellarg($file) . " 2>&1", $output, $return_code);
        
        return [
            'valid' => $return_code === 0,
            'error' => $return_code !== 0 ? implode("\n", $output) : null
        ];
    }
    
    /**
     * Check for duplicate function declarations
     */
    private function checkDuplicateFunctions($content) {
        // Remove comments to avoid false positives
        $content = preg_replace('/\/\*.*?\*\//s', '', $content);
        $content = preg_replace('/\/\/.*$/m', '', $content);
        
        preg_match_all('/function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/', $content, $matches);
        
        $functions = $matches[1];
        $function_counts = array_count_values($functions);
        
        foreach ($function_counts as $func_name => $count) {
            if ($count > 1) {
                echo "  ❌ Duplicate function: {$func_name} (declared {$count} times)\n";
                $this->errors[] = "Duplicate function declaration: {$func_name}";
            }
        }
        
        if (empty(array_filter($function_counts, function($count) { return $count > 1; }))) {
            echo "  ✅ No duplicate function declarations found\n";
        }
    }
    
    /**
     * Check for common WordPress issues
     */
    private function checkForCommonIssues($content) {
        // Check for direct PHP execution outside functions
        $lines = explode("\n", $content);
        $in_function = false;
        $brace_count = 0;
        
        foreach ($lines as $line_num => $line) {
            $line = trim($line);
            
            // Skip empty lines and comments
            if (empty($line) || strpos($line, '//') === 0 || strpos($line, '/*') === 0) {
                continue;
            }
            
            // Track function/class scope
            if (preg_match('/^(function|class)\s+/', $line)) {
                $in_function = true;
                $brace_count = 0;
            }
            
            $brace_count += substr_count($line, '{') - substr_count($line, '}');
            
            if ($in_function && $brace_count <= 0) {
                $in_function = false;
            }
            
            // Check for code execution outside functions (excluding WordPress hooks and basic setup)
            if (!$in_function && 
                !preg_match('/^(if|add_action|add_filter|require|include|define|\?>|<\?php)/', $line) &&
                !empty($line) &&
                strpos($line, '<?php') === false) {
                
                // This might be code executing outside functions
                $this->warnings[] = "Possible code execution outside function at line " . ($line_num + 1) . ": " . substr($line, 0, 50);
            }
        }
    }
    
    /**
     * Print test summary
     */
    private function printSummary() {
        echo "\n" . str_repeat("=", 50) . "\n";
        echo "📊 TEST SUMMARY\n";
        echo str_repeat("=", 50) . "\n";
        
        if (empty($this->errors)) {
            echo "✅ ALL TESTS PASSED!\n";
            echo "🎉 Theme is ready for production\n";
        } else {
            echo "❌ ERRORS FOUND: " . count($this->errors) . "\n";
            foreach ($this->errors as $error) {
                echo "   • {$error}\n";
            }
        }
        
        if (!empty($this->warnings)) {
            echo "\n⚠️  WARNINGS: " . count($this->warnings) . "\n";
            foreach ($this->warnings as $warning) {
                echo "   • {$warning}\n";
            }
        }
        
        echo "\n📈 STATISTICS:\n";
        echo "   • PHP files tested: " . count($this->getThemePhpFiles()) . "\n";
        echo "   • Errors: " . count($this->errors) . "\n";
        echo "   • Warnings: " . count($this->warnings) . "\n";
        
        if (empty($this->errors)) {
            echo "\n🚀 RESULT: THEME VALIDATION SUCCESSFUL\n";
        } else {
            echo "\n🔧 RESULT: FIXES REQUIRED BEFORE PRODUCTION\n";
        }
    }
}

// Run the tests
$tester = new WordPressThemeTester();
$success = $tester->runTests();

exit($success ? 0 : 1);