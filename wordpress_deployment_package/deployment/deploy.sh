#!/bin/bash

# =============================================================================
# WordPress Deployment Script - Retail Trade Scan Net
# =============================================================================
# 
# This script automates the deployment of the stock scanner frontend to WordPress
# with SEO optimization and Django backend integration.
#
# Usage: ./deploy.sh [options]
# Options:
#   --theme-only    Deploy only the theme
#   --plugin-only   Deploy only the plugin
#   --full          Full deployment (default)
#   --staging       Deploy to staging environment
#   --production    Deploy to production environment
#   --help          Show this help message
#
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_DIR="$(dirname "$SCRIPT_DIR")"
THEME_NAME="retail-trade-scan-net"
PLUGIN_NAME="stock-scanner-integration"

# Default values
DEPLOY_MODE="full"
ENVIRONMENT="staging"
WP_PATH=""
DJANGO_API_URL=""
DJANGO_API_KEY=""

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "${BLUE}"
    echo "=================================="
    echo " WordPress Deployment Script"
    echo " Retail Trade Scan Net"
    echo "=================================="
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

show_help() {
    echo "WordPress Deployment Script - Retail Trade Scan Net"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --theme-only     Deploy only the WordPress theme"
    echo "  --plugin-only    Deploy only the integration plugin"
    echo "  --full          Deploy both theme and plugin (default)"
    echo "  --staging       Deploy to staging environment (default)"
    echo "  --production    Deploy to production environment"
    echo "  --wp-path PATH  Specify WordPress installation path"
    echo "  --django-url URL Set Django API URL"
    echo "  --api-key KEY   Set Django API key"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --full --production --wp-path /var/www/html"
    echo "  $0 --theme-only --staging"
    echo "  $0 --django-url https://api.retailtradescan.net"
    echo ""
}

check_dependencies() {
    print_info "Checking dependencies..."
    
    local missing_deps=()
    
    # Check for required commands
    command -v zip >/dev/null 2>&1 || missing_deps+=("zip")
    command -v curl >/dev/null 2>&1 || missing_deps+=("curl")
    command -v wp >/dev/null 2>&1 || print_warning "WP-CLI not found - manual upload will be required"
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_success "All dependencies found"
}

check_wordpress_path() {
    if [ -n "$WP_PATH" ]; then
        if [ ! -f "$WP_PATH/wp-config.php" ]; then
            print_error "WordPress not found at $WP_PATH"
            exit 1
        fi
        print_success "WordPress found at $WP_PATH"
    else
        print_warning "WordPress path not specified - manual installation required"
    fi
}

create_theme_package() {
    print_info "Creating theme package..."
    
    local theme_dir="$PACKAGE_DIR/theme"
    local temp_dir="/tmp/$THEME_NAME"
    local zip_file="$PACKAGE_DIR/$THEME_NAME.zip"
    
    # Clean up any existing temp directory
    rm -rf "$temp_dir"
    mkdir -p "$temp_dir"
    
    # Copy theme files
    cp -r "$theme_dir"/* "$temp_dir/"
    
    # Create assets directories if they don't exist
    mkdir -p "$temp_dir/assets/js"
    mkdir -p "$temp_dir/assets/css"
    mkdir -p "$temp_dir/assets/images"
    
    # Create basic JavaScript files if they don't exist
    if [ ! -f "$temp_dir/assets/js/stock-integration.js" ]; then
        cat > "$temp_dir/assets/js/stock-integration.js" << 'EOF'
// Stock Integration JavaScript
jQuery(document).ready(function($) {
    // Real-time stock price updates
    function updateStockPrices() {
        $('.stock-ticker[data-ticker]').each(function() {
            var ticker = $(this).data('ticker');
            var element = $(this);
            
            $.ajax({
                url: stockAjax.ajaxurl,
                type: 'POST',
                data: {
                    action: 'get_stock_data',
                    ticker: ticker,
                    nonce: stockAjax.nonce
                },
                success: function(response) {
                    if (response.success) {
                        var data = response.data;
                        var changeClass = data.change >= 0 ? 'positive' : 'negative';
                        element.removeClass('positive negative').addClass(changeClass);
                        element.text(ticker + ': $' + data.price.toFixed(2));
                    }
                }
            });
        });
    }
    
    // Update stock prices every 5 minutes
    setInterval(updateStockPrices, 5 * 60 * 1000);
    
    // Initial update
    updateStockPrices();
});
EOF
    fi
    
    if [ ! -f "$temp_dir/assets/js/navigation.js" ]; then
        cat > "$temp_dir/assets/js/navigation.js" << 'EOF'
// Mobile Navigation
document.addEventListener('DOMContentLoaded', function() {
    var toggle = document.querySelector('.mobile-menu-toggle');
    var nav = document.querySelector('.main-navigation');
    
    if (toggle && nav) {
        toggle.addEventListener('click', function() {
            nav.classList.toggle('active');
        });
    }
});
EOF
    fi
    
    # Create critical CSS file if it doesn't exist
    if [ ! -f "$temp_dir/assets/css/critical.css" ]; then
        cat > "$temp_dir/assets/css/critical.css" << 'EOF'
/* Critical CSS - Above the fold styles */
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;margin:0;background:#f4f4f9}
.site-header{background:#1f2937;color:white;padding:1rem 0;position:sticky;top:0;z-index:1000}
.header-container{max-width:1200px;margin:0 auto;padding:0 2rem;display:flex;justify-content:space-between;align-items:center}
.site-logo{font-size:1.5rem;font-weight:bold;color:white;text-decoration:none}
.main-navigation{display:flex;list-style:none;margin:0;padding:0}
.main-navigation li{margin-left:2rem}
.main-navigation a{color:white;text-decoration:none;font-weight:500}
EOF
    fi
    
    # Create zip package
    cd "$(dirname "$temp_dir")"
    zip -r "$zip_file" "$(basename "$temp_dir")" >/dev/null
    
    # Clean up temp directory
    rm -rf "$temp_dir"
    
    print_success "Theme package created: $zip_file"
}

create_plugin_package() {
    print_info "Creating plugin package..."
    
    local plugin_dir="$PACKAGE_DIR/plugins/$PLUGIN_NAME"
    local temp_dir="/tmp/$PLUGIN_NAME"
    local zip_file="$PACKAGE_DIR/$PLUGIN_NAME.zip"
    
    # Clean up any existing temp directory
    rm -rf "$temp_dir"
    mkdir -p "$temp_dir"
    
    # Create plugin structure if it doesn't exist
    if [ ! -d "$plugin_dir" ]; then
        mkdir -p "$plugin_dir"
        
        # Create main plugin file
        cat > "$plugin_dir/$PLUGIN_NAME.php" << 'EOF'
<?php
/**
 * Plugin Name: Stock Scanner Integration
 * Description: Integrates Django stock scanner backend with WordPress frontend for real-time stock data display.
 * Version: 1.0.0
 * Author: Retail Trade Scan Net
 * Text Domain: stock-scanner-integration
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Plugin constants
define('STOCK_SCANNER_VERSION', '1.0.0');
define('STOCK_SCANNER_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('STOCK_SCANNER_PLUGIN_URL', plugin_dir_url(__FILE__));

// Main plugin class
class StockScannerIntegration {
    
    public function __construct() {
        add_action('init', [$this, 'init']);
        add_action('wp_enqueue_scripts', [$this, 'enqueue_scripts']);
        add_action('widgets_init', [$this, 'register_widgets']);
    }
    
    public function init() {
        // Initialize plugin
        load_plugin_textdomain('stock-scanner-integration', false, dirname(plugin_basename(__FILE__)) . '/languages');
    }
    
    public function enqueue_scripts() {
        wp_enqueue_script(
            'stock-scanner-integration',
            STOCK_SCANNER_PLUGIN_URL . 'assets/js/stock-integration.js',
            ['jquery'],
            STOCK_SCANNER_VERSION,
            true
        );
        
        wp_localize_script('stock-scanner-integration', 'stockScanner', [
            'ajaxurl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('stock_scanner_nonce'),
        ]);
    }
    
    public function register_widgets() {
        // Register stock widgets
        require_once STOCK_SCANNER_PLUGIN_DIR . 'includes/widgets/stock-price-widget.php';
        register_widget('Stock_Price_Widget');
    }
}

// Initialize plugin
new StockScannerIntegration();

// Stock Price Widget
class Stock_Price_Widget extends WP_Widget {
    
    public function __construct() {
        parent::__construct(
            'stock_price_widget',
            __('Stock Price Widget', 'stock-scanner-integration'),
            ['description' => __('Display real-time stock prices', 'stock-scanner-integration')]
        );
    }
    
    public function widget($args, $instance) {
        echo $args['before_widget'];
        
        if (!empty($instance['title'])) {
            echo $args['before_title'] . apply_filters('widget_title', $instance['title']) . $args['after_title'];
        }
        
        $tickers = explode(',', $instance['tickers'] ?? '');
        foreach ($tickers as $ticker) {
            $ticker = trim($ticker);
            if (!empty($ticker)) {
                echo do_shortcode('[stock_price ticker="' . esc_attr($ticker) . '"]');
            }
        }
        
        echo $args['after_widget'];
    }
    
    public function form($instance) {
        $title = !empty($instance['title']) ? $instance['title'] : __('Stock Prices', 'stock-scanner-integration');
        $tickers = !empty($instance['tickers']) ? $instance['tickers'] : '';
        ?>
        <p>
            <label for="<?php echo esc_attr($this->get_field_id('title')); ?>"><?php _e('Title:', 'stock-scanner-integration'); ?></label>
            <input class="widefat" id="<?php echo esc_attr($this->get_field_id('title')); ?>" name="<?php echo esc_attr($this->get_field_name('title')); ?>" type="text" value="<?php echo esc_attr($title); ?>">
        </p>
        <p>
            <label for="<?php echo esc_attr($this->get_field_id('tickers')); ?>"><?php _e('Stock Tickers (comma-separated):', 'stock-scanner-integration'); ?></label>
            <input class="widefat" id="<?php echo esc_attr($this->get_field_id('tickers')); ?>" name="<?php echo esc_attr($this->get_field_name('tickers')); ?>" type="text" value="<?php echo esc_attr($tickers); ?>">
        </p>
        <?php
    }
    
    public function update($new_instance, $old_instance) {
        $instance = [];
        $instance['title'] = (!empty($new_instance['title'])) ? sanitize_text_field($new_instance['title']) : '';
        $instance['tickers'] = (!empty($new_instance['tickers'])) ? sanitize_text_field($new_instance['tickers']) : '';
        return $instance;
    }
}
EOF
        
        # Create plugin assets directory
        mkdir -p "$plugin_dir/assets/js"
        
        # Create plugin JavaScript
        cat > "$plugin_dir/assets/js/stock-integration.js" << 'EOF'
// Stock Scanner Integration Plugin JavaScript
jQuery(document).ready(function($) {
    // Plugin-specific functionality
    console.log('Stock Scanner Integration Plugin loaded');
});
EOF
    fi
    
    # Copy plugin files
    cp -r "$plugin_dir"/* "$temp_dir/"
    
    # Create zip package
    cd "$(dirname "$temp_dir")"
    zip -r "$zip_file" "$(basename "$temp_dir")" >/dev/null
    
    # Clean up temp directory
    rm -rf "$temp_dir"
    
    print_success "Plugin package created: $zip_file"
}

deploy_theme() {
    print_info "Deploying theme..."
    
    if [ -n "$WP_PATH" ] && command -v wp >/dev/null 2>&1; then
        # Deploy using WP-CLI
        cd "$WP_PATH"
        
        # Install theme
        wp theme install "$PACKAGE_DIR/$THEME_NAME.zip" --activate --allow-root
        
        print_success "Theme deployed and activated via WP-CLI"
    else
        print_warning "Manual theme installation required:"
        print_info "1. Upload $PACKAGE_DIR/$THEME_NAME.zip to WordPress admin"
        print_info "2. Go to Appearance > Themes > Add New > Upload Theme"
        print_info "3. Upload the zip file and activate the theme"
    fi
}

deploy_plugin() {
    print_info "Deploying plugin..."
    
    if [ -n "$WP_PATH" ] && command -v wp >/dev/null 2>&1; then
        # Deploy using WP-CLI
        cd "$WP_PATH"
        
        # Install plugin
        wp plugin install "$PACKAGE_DIR/$PLUGIN_NAME.zip" --activate --allow-root
        
        print_success "Plugin deployed and activated via WP-CLI"
    else
        print_warning "Manual plugin installation required:"
        print_info "1. Upload $PACKAGE_DIR/$PLUGIN_NAME.zip to WordPress admin"
        print_info "2. Go to Plugins > Add New > Upload Plugin"
        print_info "3. Upload the zip file and activate the plugin"
    fi
}

configure_wordpress() {
    print_info "Configuring WordPress settings..."
    
    if [ -n "$WP_PATH" ] && command -v wp >/dev/null 2>&1; then
        cd "$WP_PATH"
        
        # Set Django API configuration
        if [ -n "$DJANGO_API_URL" ]; then
            wp config set DJANGO_API_URL "$DJANGO_API_URL" --allow-root
            print_success "Django API URL configured"
        fi
        
        if [ -n "$DJANGO_API_KEY" ]; then
            wp config set DJANGO_API_KEY "$DJANGO_API_KEY" --allow-root
            print_success "Django API key configured"
        fi
        
        # Enable pretty permalinks
        wp rewrite structure '/%postname%/' --allow-root
        wp rewrite flush --allow-root
        
        # Install recommended plugins
        wp plugin install wordpress-seo --activate --allow-root || print_warning "Failed to install Yoast SEO"
        wp plugin install w3-total-cache --activate --allow-root || print_warning "Failed to install W3 Total Cache"
        
        print_success "WordPress configuration completed"
    else
        print_warning "Manual WordPress configuration required:"
        print_info "1. Add the following to wp-config.php:"
        
        if [ -n "$DJANGO_API_URL" ]; then
            print_info "   define('DJANGO_API_URL', '$DJANGO_API_URL');"
        fi
        
        if [ -n "$DJANGO_API_KEY" ]; then
            print_info "   define('DJANGO_API_KEY', '$DJANGO_API_KEY');"
        fi
        
        print_info "2. Set permalinks to 'Post name' in Settings > Permalinks"
        print_info "3. Install recommended plugins: Yoast SEO, W3 Total Cache"
    fi
}

run_seo_optimization() {
    print_info "Running SEO optimization..."
    
    if [ -n "$WP_PATH" ] && command -v wp >/dev/null 2>&1; then
        cd "$WP_PATH"
        
        # Generate sitemap
        wp rewrite flush --allow-root
        
        # Set basic SEO settings
        wp option update blogdescription "Professional stock analysis, trading insights, and market research platform" --allow-root
        
        print_success "SEO optimization completed"
    else
        print_info "Manual SEO optimization:"
        print_info "1. Set site tagline to describe your stock analysis platform"
        print_info "2. Configure Yoast SEO plugin settings"
        print_info "3. Generate and submit sitemap to search engines"
    fi
}

cleanup() {
    print_info "Cleaning up temporary files..."
    
    # Remove zip files
    rm -f "$PACKAGE_DIR/$THEME_NAME.zip"
    rm -f "$PACKAGE_DIR/$PLUGIN_NAME.zip"
    
    print_success "Cleanup completed"
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    print_header
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --theme-only)
                DEPLOY_MODE="theme"
                shift
                ;;
            --plugin-only)
                DEPLOY_MODE="plugin"
                shift
                ;;
            --full)
                DEPLOY_MODE="full"
                shift
                ;;
            --staging)
                ENVIRONMENT="staging"
                shift
                ;;
            --production)
                ENVIRONMENT="production"
                shift
                ;;
            --wp-path)
                WP_PATH="$2"
                shift 2
                ;;
            --django-url)
                DJANGO_API_URL="$2"
                shift 2
                ;;
            --api-key)
                DJANGO_API_KEY="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_info "Deployment mode: $DEPLOY_MODE"
    print_info "Environment: $ENVIRONMENT"
    
    # Run pre-deployment checks
    check_dependencies
    check_wordpress_path
    
    # Create packages
    if [ "$DEPLOY_MODE" = "full" ] || [ "$DEPLOY_MODE" = "theme" ]; then
        create_theme_package
    fi
    
    if [ "$DEPLOY_MODE" = "full" ] || [ "$DEPLOY_MODE" = "plugin" ]; then
        create_plugin_package
    fi
    
    # Deploy packages
    if [ "$DEPLOY_MODE" = "full" ] || [ "$DEPLOY_MODE" = "theme" ]; then
        deploy_theme
    fi
    
    if [ "$DEPLOY_MODE" = "full" ] || [ "$DEPLOY_MODE" = "plugin" ]; then
        deploy_plugin
    fi
    
    # Configure WordPress
    if [ "$DEPLOY_MODE" = "full" ]; then
        configure_wordpress
        run_seo_optimization
    fi
    
    # Cleanup
    cleanup
    
    print_success "Deployment completed successfully!"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        print_warning "Production deployment completed. Please:"
        print_info "1. Test all functionality thoroughly"
        print_info "2. Monitor performance and error logs"
        print_info "3. Set up backups and monitoring"
        print_info "4. Configure caching and CDN"
    fi
    
    print_info "Your WordPress site is now integrated with your Django stock scanner backend!"
    print_info "Visit your site to see the new stock-focused design and functionality."
}

# Run main function
main "$@"