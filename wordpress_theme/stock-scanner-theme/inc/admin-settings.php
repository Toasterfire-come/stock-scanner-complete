<?php
/**
 * Stock Scanner Admin Settings
 * Comprehensive settings management for WordPress admin
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class StockScannerAdminSettings {
    
    private $settings_group = 'stock_scanner_settings';
    private $page_slug = 'stock-scanner-settings';
    
    public function __construct() {
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_scripts'));
        add_action('wp_ajax_test_api_connection', array($this, 'test_api_connection'));
        add_action('wp_ajax_test_paypal_connection', array($this, 'test_paypal_connection'));
    }
    
    /**
     * Add admin menu pages
     */
    public function add_admin_menu() {
        // Main settings page
        add_menu_page(
            'Stock Scanner Settings',
            'Stock Scanner',
            'manage_options',
            $this->page_slug,
            array($this, 'settings_page'),
            'dashicons-chart-line',
            30
        );
        
        // Sub-menu pages
        add_submenu_page(
            $this->page_slug,
            'API Configuration',
            'API Settings',
            'manage_options',
            'stock-scanner-api',
            array($this, 'api_settings_page')
        );
        
        add_submenu_page(
            $this->page_slug,
            'Payment Settings',
            'Payment Settings',
            'manage_options',
            'stock-scanner-payments',
            array($this, 'payment_settings_page')
        );
        
        add_submenu_page(
            $this->page_slug,
            'Feature Settings',
            'Features',
            'manage_options',
            'stock-scanner-features',
            array($this, 'feature_settings_page')
        );
        
        add_submenu_page(
            $this->page_slug,
            'User Limits',
            'User Limits',
            'manage_options',
            'stock-scanner-limits',
            array($this, 'limits_settings_page')
        );
        
        add_submenu_page(
            $this->page_slug,
            'Advanced Settings',
            'Advanced',
            'manage_options',
            'stock-scanner-advanced',
            array($this, 'advanced_settings_page')
        );
    }
    
    /**
     * Register all settings
     */
    public function register_settings() {
        // General Settings
        register_setting($this->settings_group, 'stock_scanner_general_settings', array($this, 'sanitize_general_settings'));
        
        // API Settings
        register_setting($this->settings_group, 'stock_scanner_api_settings', array($this, 'sanitize_api_settings'));
        
        // Payment Settings
        register_setting($this->settings_group, 'stock_scanner_payment_settings', array($this, 'sanitize_payment_settings'));
        
        // Feature Settings
        register_setting($this->settings_group, 'stock_scanner_feature_settings', array($this, 'sanitize_feature_settings'));
        
        // User Limits
        register_setting($this->settings_group, 'stock_scanner_limit_settings', array($this, 'sanitize_limit_settings'));
        
        // Advanced Settings
        register_setting($this->settings_group, 'stock_scanner_advanced_settings', array($this, 'sanitize_advanced_settings'));
    }
    
    /**
     * Enqueue admin scripts and styles
     */
    public function enqueue_admin_scripts($hook) {
        if (strpos($hook, 'stock-scanner') === false) {
            return;
        }
        
        wp_enqueue_style('stock-scanner-admin', get_template_directory_uri() . '/assets/css/admin-styles.css', array(), '1.0.0');
        wp_enqueue_script('stock-scanner-admin', get_template_directory_uri() . '/assets/js/admin-scripts.js', array('jquery'), '1.0.0', true);
        
        wp_localize_script('stock-scanner-admin', 'stockScannerAdmin', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('stock_scanner_admin_nonce'),
            'strings' => array(
                'testing_connection' => __('Testing connection...', 'stock-scanner'),
                'connection_successful' => __('Connection successful!', 'stock-scanner'),
                'connection_failed' => __('Connection failed!', 'stock-scanner'),
                'settings_saved' => __('Settings saved successfully!', 'stock-scanner'),
            )
        ));
    }
    
    /**
     * Main settings page
     */
    public function settings_page() {
        $general_settings = get_option('stock_scanner_general_settings', array());
        ?>
        <div class="wrap stock-scanner-admin">
            <h1><?php esc_html_e('Stock Scanner Settings', 'stock-scanner'); ?></h1>
            
            <div class="nav-tab-wrapper">
                <a href="#general" class="nav-tab nav-tab-active"><?php esc_html_e('General', 'stock-scanner'); ?></a>
                <a href="#dashboard" class="nav-tab"><?php esc_html_e('Dashboard', 'stock-scanner'); ?></a>
                <a href="#notifications" class="nav-tab"><?php esc_html_e('Notifications', 'stock-scanner'); ?></a>
            </div>
            
            <form method="post" action="options.php">
                <?php settings_fields($this->settings_group); ?>
                
                <!-- General Tab -->
                <div id="general" class="tab-content active">
                    <h2><?php esc_html_e('General Settings', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Site Title', 'stock-scanner'); ?></th>
                            <td>
                                <input type="text" name="stock_scanner_general_settings[site_title]" 
                                       value="<?php echo esc_attr($general_settings['site_title'] ?? 'Stock Scanner Pro'); ?>" 
                                       class="regular-text" />
                                <p class="description"><?php esc_html_e('The main title displayed on your site.', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Site Description', 'stock-scanner'); ?></th>
                            <td>
                                <textarea name="stock_scanner_general_settings[site_description]" 
                                          class="large-text" rows="3"><?php echo esc_textarea($general_settings['site_description'] ?? 'Professional stock screening and portfolio management platform'); ?></textarea>
                                <p class="description"><?php esc_html_e('Brief description of your site.', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Default Currency', 'stock-scanner'); ?></th>
                            <td>
                                <select name="stock_scanner_general_settings[default_currency]">
                                    <option value="USD" <?php selected($general_settings['default_currency'] ?? 'USD', 'USD'); ?>>USD ($)</option>
                                    <option value="EUR" <?php selected($general_settings['default_currency'] ?? 'USD', 'EUR'); ?>>EUR (€)</option>
                                    <option value="GBP" <?php selected($general_settings['default_currency'] ?? 'USD', 'GBP'); ?>>GBP (£)</option>
                                    <option value="CAD" <?php selected($general_settings['default_currency'] ?? 'USD', 'CAD'); ?>>CAD (C$)</option>
                                </select>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Time Zone', 'stock-scanner'); ?></th>
                            <td>
                                <select name="stock_scanner_general_settings[timezone]">
                                    <option value="America/New_York" <?php selected($general_settings['timezone'] ?? 'America/New_York', 'America/New_York'); ?>>Eastern Time (ET)</option>
                                    <option value="America/Chicago" <?php selected($general_settings['timezone'] ?? 'America/New_York', 'America/Chicago'); ?>>Central Time (CT)</option>
                                    <option value="America/Denver" <?php selected($general_settings['timezone'] ?? 'America/New_York', 'America/Denver'); ?>>Mountain Time (MT)</option>
                                    <option value="America/Los_Angeles" <?php selected($general_settings['timezone'] ?? 'America/New_York', 'America/Los_Angeles'); ?>>Pacific Time (PT)</option>
                                    <option value="Europe/London" <?php selected($general_settings['timezone'] ?? 'America/New_York', 'Europe/London'); ?>>London (GMT)</option>
                                </select>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable User Registration', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_general_settings[enable_registration]" 
                                           value="1" <?php checked($general_settings['enable_registration'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Allow new users to register', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Default User Role', 'stock-scanner'); ?></th>
                            <td>
                                <select name="stock_scanner_general_settings[default_role]">
                                    <option value="free" <?php selected($general_settings['default_role'] ?? 'free', 'free'); ?>>Free User</option>
                                    <option value="bronze" <?php selected($general_settings['default_role'] ?? 'free', 'bronze'); ?>>Bronze Member</option>
                                    <option value="silver" <?php selected($general_settings['default_role'] ?? 'free', 'silver'); ?>>Silver Member</option>
                                    <option value="gold" <?php selected($general_settings['default_role'] ?? 'free', 'gold'); ?>>Gold Member</option>
                                </select>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <!-- Dashboard Tab -->
                <div id="dashboard" class="tab-content">
                    <h2><?php esc_html_e('Dashboard Settings', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Default Dashboard View', 'stock-scanner'); ?></th>
                            <td>
                                <select name="stock_scanner_general_settings[default_dashboard]">
                                    <option value="overview" <?php selected($general_settings['default_dashboard'] ?? 'overview', 'overview'); ?>>Overview</option>
                                    <option value="portfolios" <?php selected($general_settings['default_dashboard'] ?? 'overview', 'portfolios'); ?>>My Portfolios</option>
                                    <option value="watchlists" <?php selected($general_settings['default_dashboard'] ?? 'overview', 'watchlists'); ?>>Watchlists</option>
                                    <option value="news" <?php selected($general_settings['default_dashboard'] ?? 'overview', 'news'); ?>>News Feed</option>
                                </select>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Show Welcome Message', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_general_settings[show_welcome]" 
                                           value="1" <?php checked($general_settings['show_welcome'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Display welcome message for new users', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Auto-refresh Data', 'stock-scanner'); ?></th>
                            <td>
                                <select name="stock_scanner_general_settings[auto_refresh]">
                                    <option value="30" <?php selected($general_settings['auto_refresh'] ?? '30', '30'); ?>>30 seconds</option>
                                    <option value="60" <?php selected($general_settings['auto_refresh'] ?? '30', '60'); ?>>1 minute</option>
                                    <option value="300" <?php selected($general_settings['auto_refresh'] ?? '30', '300'); ?>>5 minutes</option>
                                    <option value="0" <?php selected($general_settings['auto_refresh'] ?? '30', '0'); ?>>Disabled</option>
                                </select>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <!-- Notifications Tab -->
                <div id="notifications" class="tab-content">
                    <h2><?php esc_html_e('Notification Settings', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Email Notifications', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_general_settings[email_notifications]" 
                                           value="1" <?php checked($general_settings['email_notifications'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Enable email notifications', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Admin Email', 'stock-scanner'); ?></th>
                            <td>
                                <input type="email" name="stock_scanner_general_settings[admin_email]" 
                                       value="<?php echo esc_attr($general_settings['admin_email'] ?? get_option('admin_email')); ?>" 
                                       class="regular-text" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Notification Types', 'stock-scanner'); ?></th>
                            <td>
                                <fieldset>
                                    <label>
                                        <input type="checkbox" name="stock_scanner_general_settings[notify_new_users]" 
                                               value="1" <?php checked($general_settings['notify_new_users'] ?? 1, 1); ?> />
                                        <?php esc_html_e('New user registrations', 'stock-scanner'); ?>
                                    </label><br>
                                    
                                    <label>
                                        <input type="checkbox" name="stock_scanner_general_settings[notify_upgrades]" 
                                               value="1" <?php checked($general_settings['notify_upgrades'] ?? 1, 1); ?> />
                                        <?php esc_html_e('Plan upgrades', 'stock-scanner'); ?>
                                    </label><br>
                                    
                                    <label>
                                        <input type="checkbox" name="stock_scanner_general_settings[notify_errors]" 
                                               value="1" <?php checked($general_settings['notify_errors'] ?? 1, 1); ?> />
                                        <?php esc_html_e('System errors', 'stock-scanner'); ?>
                                    </label>
                                </fieldset>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
    
    /**
     * API settings page
     */
    public function api_settings_page() {
        $api_settings = get_option('stock_scanner_api_settings', array());
        ?>
        <div class="wrap stock-scanner-admin">
            <h1><?php esc_html_e('API Configuration', 'stock-scanner'); ?></h1>
            
            <form method="post" action="options.php">
                <?php settings_fields($this->settings_group); ?>
                
                <div class="card">
                    <h2><?php esc_html_e('Django Backend Configuration', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Backend URL', 'stock-scanner'); ?></th>
                            <td>
                                <input type="url" name="stock_scanner_api_settings[backend_url]" 
                                       value="<?php echo esc_attr($api_settings['backend_url'] ?? 'https://your-django-backend.com'); ?>" 
                                       class="regular-text" required />
                                <p class="description"><?php esc_html_e('Full URL to your Django backend (e.g., https://api.yoursite.com)', 'stock-scanner'); ?></p>
                                <button type="button" class="button test-connection" data-type="django">
                                    <?php esc_html_e('Test Connection', 'stock-scanner'); ?>
                                </button>
                                <span class="connection-status"></span>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('API Key', 'stock-scanner'); ?></th>
                            <td>
                                <input type="password" name="stock_scanner_api_settings[api_key]" 
                                       value="<?php echo esc_attr($api_settings['api_key'] ?? ''); ?>" 
                                       class="regular-text" />
                                <p class="description"><?php esc_html_e('API key for backend authentication', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('API Version', 'stock-scanner'); ?></th>
                            <td>
                                <select name="stock_scanner_api_settings[api_version]">
                                    <option value="v1" <?php selected($api_settings['api_version'] ?? 'v1', 'v1'); ?>>v1</option>
                                    <option value="v2" <?php selected($api_settings['api_version'] ?? 'v1', 'v2'); ?>>v2</option>
                                </select>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Timeout (seconds)', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_api_settings[timeout]" 
                                       value="<?php echo esc_attr($api_settings['timeout'] ?? '30'); ?>" 
                                       min="5" max="120" />
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="card">
                    <h2><?php esc_html_e('Stock Data API', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Stock Data Provider', 'stock-scanner'); ?></th>
                            <td>
                                <select name="stock_scanner_api_settings[stock_provider]">
                                    <option value="alpha_vantage" <?php selected($api_settings['stock_provider'] ?? 'alpha_vantage', 'alpha_vantage'); ?>>Alpha Vantage</option>
                                    <option value="finnhub" <?php selected($api_settings['stock_provider'] ?? 'alpha_vantage', 'finnhub'); ?>>Finnhub</option>
                                    <option value="iex_cloud" <?php selected($api_settings['stock_provider'] ?? 'alpha_vantage', 'iex_cloud'); ?>>IEX Cloud</option>
                                    <option value="polygon" <?php selected($api_settings['stock_provider'] ?? 'alpha_vantage', 'polygon'); ?>>Polygon.io</option>
                                </select>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Stock API Key', 'stock-scanner'); ?></th>
                            <td>
                                <input type="password" name="stock_scanner_api_settings[stock_api_key]" 
                                       value="<?php echo esc_attr($api_settings['stock_api_key'] ?? ''); ?>" 
                                       class="regular-text" />
                                <p class="description"><?php esc_html_e('API key for stock data provider', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Real-time Data', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_api_settings[realtime_data]" 
                                           value="1" <?php checked($api_settings['realtime_data'] ?? 0, 1); ?> />
                                    <?php esc_html_e('Enable real-time stock data (premium required)', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="card">
                    <h2><?php esc_html_e('News API Configuration', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('News Provider', 'stock-scanner'); ?></th>
                            <td>
                                <select name="stock_scanner_api_settings[news_provider]">
                                    <option value="newsapi" <?php selected($api_settings['news_provider'] ?? 'newsapi', 'newsapi'); ?>>NewsAPI</option>
                                    <option value="alpha_vantage_news" <?php selected($api_settings['news_provider'] ?? 'newsapi', 'alpha_vantage_news'); ?>>Alpha Vantage News</option>
                                    <option value="finnhub_news" <?php selected($api_settings['news_provider'] ?? 'newsapi', 'finnhub_news'); ?>>Finnhub News</option>
                                </select>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('News API Key', 'stock-scanner'); ?></th>
                            <td>
                                <input type="password" name="stock_scanner_api_settings[news_api_key]" 
                                       value="<?php echo esc_attr($api_settings['news_api_key'] ?? ''); ?>" 
                                       class="regular-text" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('News Update Frequency', 'stock-scanner'); ?></th>
                            <td>
                                <select name="stock_scanner_api_settings[news_frequency]">
                                    <option value="15" <?php selected($api_settings['news_frequency'] ?? '60', '15'); ?>>15 minutes</option>
                                    <option value="30" <?php selected($api_settings['news_frequency'] ?? '60', '30'); ?>>30 minutes</option>
                                    <option value="60" <?php selected($api_settings['news_frequency'] ?? '60', '60'); ?>>1 hour</option>
                                    <option value="240" <?php selected($api_settings['news_frequency'] ?? '60', '240'); ?>>4 hours</option>
                                </select>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
    
    /**
     * Payment settings page
     */
    public function payment_settings_page() {
        $payment_settings = get_option('stock_scanner_payment_settings', array());
        ?>
        <div class="wrap stock-scanner-admin">
            <h1><?php esc_html_e('Payment Settings', 'stock-scanner'); ?></h1>
            
            <form method="post" action="options.php">
                <?php settings_fields($this->settings_group); ?>
                
                <div class="card">
                    <h2><?php esc_html_e('PayPal Configuration', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('PayPal Mode', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="radio" name="stock_scanner_payment_settings[paypal_mode]" 
                                           value="sandbox" <?php checked($payment_settings['paypal_mode'] ?? 'sandbox', 'sandbox'); ?> />
                                    <?php esc_html_e('Sandbox (Testing)', 'stock-scanner'); ?>
                                </label><br>
                                <label>
                                    <input type="radio" name="stock_scanner_payment_settings[paypal_mode]" 
                                           value="live" <?php checked($payment_settings['paypal_mode'] ?? 'sandbox', 'live'); ?> />
                                    <?php esc_html_e('Live (Production)', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('PayPal Client ID', 'stock-scanner'); ?></th>
                            <td>
                                <input type="text" name="stock_scanner_payment_settings[paypal_client_id]" 
                                       value="<?php echo esc_attr($payment_settings['paypal_client_id'] ?? ''); ?>" 
                                       class="regular-text" />
                                <p class="description"><?php esc_html_e('Your PayPal application client ID', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('PayPal Client Secret', 'stock-scanner'); ?></th>
                            <td>
                                <input type="password" name="stock_scanner_payment_settings[paypal_client_secret]" 
                                       value="<?php echo esc_attr($payment_settings['paypal_client_secret'] ?? ''); ?>" 
                                       class="regular-text" />
                                <p class="description"><?php esc_html_e('Your PayPal application client secret', 'stock-scanner'); ?></p>
                                <button type="button" class="button test-connection" data-type="paypal">
                                    <?php esc_html_e('Test PayPal Connection', 'stock-scanner'); ?>
                                </button>
                                <span class="connection-status"></span>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Webhook ID', 'stock-scanner'); ?></th>
                            <td>
                                <input type="text" name="stock_scanner_payment_settings[paypal_webhook_id]" 
                                       value="<?php echo esc_attr($payment_settings['paypal_webhook_id'] ?? ''); ?>" 
                                       class="regular-text" />
                                <p class="description"><?php esc_html_e('PayPal webhook ID for payment notifications', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="card">
                    <h2><?php esc_html_e('Subscription Plans', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Bronze Plan Price', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_payment_settings[bronze_price]" 
                                       value="<?php echo esc_attr($payment_settings['bronze_price'] ?? '9.99'); ?>" 
                                       step="0.01" min="0" />
                                <span><?php echo esc_html($general_settings['default_currency'] ?? 'USD'); ?></span>
                                <p class="description"><?php esc_html_e('Monthly price for Bronze membership', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Silver Plan Price', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_payment_settings[silver_price]" 
                                       value="<?php echo esc_attr($payment_settings['silver_price'] ?? '19.99'); ?>" 
                                       step="0.01" min="0" />
                                <span><?php echo esc_html($general_settings['default_currency'] ?? 'USD'); ?></span>
                                <p class="description"><?php esc_html_e('Monthly price for Silver membership', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Gold Plan Price', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_payment_settings[gold_price]" 
                                       value="<?php echo esc_attr($payment_settings['gold_price'] ?? '39.99'); ?>" 
                                       step="0.01" min="0" />
                                <span><?php echo esc_html($general_settings['default_currency'] ?? 'USD'); ?></span>
                                <p class="description"><?php esc_html_e('Monthly price for Gold membership', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Free Trial Period', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_payment_settings[trial_days]" 
                                       value="<?php echo esc_attr($payment_settings['trial_days'] ?? '7'); ?>" 
                                       min="0" max="90" />
                                <span><?php esc_html_e('days', 'stock-scanner'); ?></span>
                                <p class="description"><?php esc_html_e('Number of free trial days for new users', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="card">
                    <h2><?php esc_html_e('Stripe Configuration (Alternative)', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable Stripe', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_payment_settings[enable_stripe]" 
                                           value="1" <?php checked($payment_settings['enable_stripe'] ?? 0, 1); ?> />
                                    <?php esc_html_e('Enable Stripe payments as alternative to PayPal', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Stripe Publishable Key', 'stock-scanner'); ?></th>
                            <td>
                                <input type="text" name="stock_scanner_payment_settings[stripe_publishable_key]" 
                                       value="<?php echo esc_attr($payment_settings['stripe_publishable_key'] ?? ''); ?>" 
                                       class="regular-text" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Stripe Secret Key', 'stock-scanner'); ?></th>
                            <td>
                                <input type="password" name="stock_scanner_payment_settings[stripe_secret_key]" 
                                       value="<?php echo esc_attr($payment_settings['stripe_secret_key'] ?? ''); ?>" 
                                       class="regular-text" />
                            </td>
                        </tr>
                    </table>
                </div>
                
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
    
    /**
     * Feature settings page
     */
    public function feature_settings_page() {
        $feature_settings = get_option('stock_scanner_feature_settings', array());
        ?>
        <div class="wrap stock-scanner-admin">
            <h1><?php esc_html_e('Feature Settings', 'stock-scanner'); ?></h1>
            
            <form method="post" action="options.php">
                <?php settings_fields($this->settings_group); ?>
                
                <div class="card">
                    <h2><?php esc_html_e('Portfolio Features', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable Portfolio Management', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_feature_settings[enable_portfolios]" 
                                           value="1" <?php checked($feature_settings['enable_portfolios'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Allow users to create and manage portfolios', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable Public Portfolios', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_feature_settings[enable_public_portfolios]" 
                                           value="1" <?php checked($feature_settings['enable_public_portfolios'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Allow users to make portfolios public', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable CSV Import/Export', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_feature_settings[enable_csv]" 
                                           value="1" <?php checked($feature_settings['enable_csv'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Allow portfolio CSV import/export', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable Performance Analytics', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_feature_settings[enable_analytics]" 
                                           value="1" <?php checked($feature_settings['enable_analytics'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Show detailed performance analytics', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="card">
                    <h2><?php esc_html_e('Watchlist Features', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable Enhanced Watchlists', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_feature_settings[enable_watchlists]" 
                                           value="1" <?php checked($feature_settings['enable_watchlists'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Allow users to create enhanced watchlists', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable Price Alerts', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_feature_settings[enable_price_alerts]" 
                                           value="1" <?php checked($feature_settings['enable_price_alerts'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Allow price alerts and notifications', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable Bulk Operations', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_feature_settings[enable_bulk_ops]" 
                                           value="1" <?php checked($feature_settings['enable_bulk_ops'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Allow bulk add/remove operations', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="card">
                    <h2><?php esc_html_e('News Features', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable Personalized News', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_feature_settings[enable_news]" 
                                           value="1" <?php checked($feature_settings['enable_news'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Enable intelligent news curation', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable News Analytics', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_feature_settings[enable_news_analytics]" 
                                           value="1" <?php checked($feature_settings['enable_news_analytics'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Track reading behavior and preferences', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable Social Features', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_feature_settings[enable_social]" 
                                           value="1" <?php checked($feature_settings['enable_social'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Allow following other users and portfolios', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
    
    /**
     * User limits settings page
     */
    public function limits_settings_page() {
        $limit_settings = get_option('stock_scanner_limit_settings', array());
        ?>
        <div class="wrap stock-scanner-admin">
            <h1><?php esc_html_e('User Limits & Quotas', 'stock-scanner'); ?></h1>
            
            <form method="post" action="options.php">
                <?php settings_fields($this->settings_group); ?>
                
                <div class="card">
                    <h2><?php esc_html_e('Free Users', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Monthly API Calls', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[free_api_calls]" 
                                       value="<?php echo esc_attr($limit_settings['free_api_calls'] ?? '15'); ?>" 
                                       min="0" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Max Portfolios', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[free_portfolios]" 
                                       value="<?php echo esc_attr($limit_settings['free_portfolios'] ?? '1'); ?>" 
                                       min="0" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Max Watchlists', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[free_watchlists]" 
                                       value="<?php echo esc_attr($limit_settings['free_watchlists'] ?? '2'); ?>" 
                                       min="0" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Max Holdings per Portfolio', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[free_holdings]" 
                                       value="<?php echo esc_attr($limit_settings['free_holdings'] ?? '10'); ?>" 
                                       min="0" />
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="card">
                    <h2><?php esc_html_e('Bronze Members', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Monthly API Calls', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[bronze_api_calls]" 
                                       value="<?php echo esc_attr($limit_settings['bronze_api_calls'] ?? '1500'); ?>" 
                                       min="0" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Max Portfolios', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[bronze_portfolios]" 
                                       value="<?php echo esc_attr($limit_settings['bronze_portfolios'] ?? '5'); ?>" 
                                       min="0" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Max Watchlists', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[bronze_watchlists]" 
                                       value="<?php echo esc_attr($limit_settings['bronze_watchlists'] ?? '10'); ?>" 
                                       min="0" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Max Holdings per Portfolio', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[bronze_holdings]" 
                                       value="<?php echo esc_attr($limit_settings['bronze_holdings'] ?? '50'); ?>" 
                                       min="0" />
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="card">
                    <h2><?php esc_html_e('Silver Members', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Monthly API Calls', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[silver_api_calls]" 
                                       value="<?php echo esc_attr($limit_settings['silver_api_calls'] ?? '5000'); ?>" 
                                       min="0" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Max Portfolios', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[silver_portfolios]" 
                                       value="<?php echo esc_attr($limit_settings['silver_portfolios'] ?? '15'); ?>" 
                                       min="0" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Max Watchlists', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[silver_watchlists]" 
                                       value="<?php echo esc_attr($limit_settings['silver_watchlists'] ?? '25'); ?>" 
                                       min="0" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Max Holdings per Portfolio', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[silver_holdings]" 
                                       value="<?php echo esc_attr($limit_settings['silver_holdings'] ?? '100'); ?>" 
                                       min="0" />
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="card">
                    <h2><?php esc_html_e('Gold Members', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Monthly API Calls', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[gold_api_calls]" 
                                       value="<?php echo esc_attr($limit_settings['gold_api_calls'] ?? '-1'); ?>" 
                                       min="-1" />
                                <p class="description"><?php esc_html_e('Use -1 for unlimited', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Max Portfolios', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[gold_portfolios]" 
                                       value="<?php echo esc_attr($limit_settings['gold_portfolios'] ?? '-1'); ?>" 
                                       min="-1" />
                                <p class="description"><?php esc_html_e('Use -1 for unlimited', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Max Watchlists', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[gold_watchlists]" 
                                       value="<?php echo esc_attr($limit_settings['gold_watchlists'] ?? '-1'); ?>" 
                                       min="-1" />
                                <p class="description"><?php esc_html_e('Use -1 for unlimited', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Max Holdings per Portfolio', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_limit_settings[gold_holdings]" 
                                       value="<?php echo esc_attr($limit_settings['gold_holdings'] ?? '-1'); ?>" 
                                       min="-1" />
                                <p class="description"><?php esc_html_e('Use -1 for unlimited', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
    
    /**
     * Advanced settings page
     */
    public function advanced_settings_page() {
        $advanced_settings = get_option('stock_scanner_advanced_settings', array());
        ?>
        <div class="wrap stock-scanner-admin">
            <h1><?php esc_html_e('Advanced Settings', 'stock-scanner'); ?></h1>
            
            <form method="post" action="options.php">
                <?php settings_fields($this->settings_group); ?>
                
                <div class="card">
                    <h2><?php esc_html_e('Performance & Caching', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable Caching', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_advanced_settings[enable_caching]" 
                                           value="1" <?php checked($advanced_settings['enable_caching'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Cache API responses for better performance', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Cache Duration (minutes)', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_advanced_settings[cache_duration]" 
                                       value="<?php echo esc_attr($advanced_settings['cache_duration'] ?? '15'); ?>" 
                                       min="1" max="1440" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Database Optimization', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_advanced_settings[db_optimization]" 
                                           value="1" <?php checked($advanced_settings['db_optimization'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Enable database query optimization', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="card">
                    <h2><?php esc_html_e('Security Settings', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable Rate Limiting', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_advanced_settings[enable_rate_limiting]" 
                                           value="1" <?php checked($advanced_settings['enable_rate_limiting'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Limit API requests per user', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Rate Limit (requests/hour)', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_advanced_settings[rate_limit]" 
                                       value="<?php echo esc_attr($advanced_settings['rate_limit'] ?? '100'); ?>" 
                                       min="10" max="10000" />
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Enable Audit Logging', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_advanced_settings[enable_audit_log]" 
                                           value="1" <?php checked($advanced_settings['enable_audit_log'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Log user actions for security audit', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('IP Whitelist', 'stock-scanner'); ?></th>
                            <td>
                                <textarea name="stock_scanner_advanced_settings[ip_whitelist]" 
                                          class="large-text" rows="3" 
                                          placeholder="127.0.0.1&#10;192.168.1.0/24"><?php echo esc_textarea($advanced_settings['ip_whitelist'] ?? ''); ?></textarea>
                                <p class="description"><?php esc_html_e('One IP address or CIDR range per line. Leave empty to allow all IPs.', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="card">
                    <h2><?php esc_html_e('Debug & Logging', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Debug Mode', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_advanced_settings[debug_mode]" 
                                           value="1" <?php checked($advanced_settings['debug_mode'] ?? 0, 1); ?> />
                                    <?php esc_html_e('Enable debug mode (for development only)', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Log Level', 'stock-scanner'); ?></th>
                            <td>
                                <select name="stock_scanner_advanced_settings[log_level]">
                                    <option value="error" <?php selected($advanced_settings['log_level'] ?? 'error', 'error'); ?>>Error</option>
                                    <option value="warning" <?php selected($advanced_settings['log_level'] ?? 'error', 'warning'); ?>>Warning</option>
                                    <option value="info" <?php selected($advanced_settings['log_level'] ?? 'error', 'info'); ?>>Info</option>
                                    <option value="debug" <?php selected($advanced_settings['log_level'] ?? 'error', 'debug'); ?>>Debug</option>
                                </select>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Log Retention (days)', 'stock-scanner'); ?></th>
                            <td>
                                <input type="number" name="stock_scanner_advanced_settings[log_retention]" 
                                       value="<?php echo esc_attr($advanced_settings['log_retention'] ?? '30'); ?>" 
                                       min="1" max="365" />
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="card">
                    <h2><?php esc_html_e('System Maintenance', 'stock-scanner'); ?></h2>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php esc_html_e('Maintenance Mode', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_advanced_settings[maintenance_mode]" 
                                           value="1" <?php checked($advanced_settings['maintenance_mode'] ?? 0, 1); ?> />
                                    <?php esc_html_e('Enable maintenance mode', 'stock-scanner'); ?>
                                </label>
                                <p class="description"><?php esc_html_e('When enabled, only administrators can access the site', 'stock-scanner'); ?></p>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Maintenance Message', 'stock-scanner'); ?></th>
                            <td>
                                <textarea name="stock_scanner_advanced_settings[maintenance_message]" 
                                          class="large-text" rows="3"><?php echo esc_textarea($advanced_settings['maintenance_message'] ?? 'We are currently performing scheduled maintenance. Please check back soon.'); ?></textarea>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row"><?php esc_html_e('Auto-cleanup Old Data', 'stock-scanner'); ?></th>
                            <td>
                                <label>
                                    <input type="checkbox" name="stock_scanner_advanced_settings[auto_cleanup]" 
                                           value="1" <?php checked($advanced_settings['auto_cleanup'] ?? 1, 1); ?> />
                                    <?php esc_html_e('Automatically clean up old logs and temporary data', 'stock-scanner'); ?>
                                </label>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
    
    /**
     * Test API connection
     */
    public function test_api_connection() {
        check_ajax_referer('stock_scanner_admin_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die(__('Unauthorized', 'stock-scanner'));
        }
        
        $api_settings = get_option('stock_scanner_api_settings', array());
        $backend_url = $api_settings['backend_url'] ?? '';
        $api_key = $api_settings['api_key'] ?? '';
        
        if (empty($backend_url)) {
            wp_send_json_error(__('Backend URL not configured', 'stock-scanner'));
        }
        
        $response = wp_remote_get($backend_url . '/api/health/', array(
            'headers' => array(
                'Authorization' => 'Bearer ' . $api_key
            ),
            'timeout' => 10
        ));
        
        if (is_wp_error($response)) {
            wp_send_json_error($response->get_error_message());
        }
        
        $status_code = wp_remote_retrieve_response_code($response);
        
        if ($status_code === 200) {
            wp_send_json_success(__('Connection successful!', 'stock-scanner'));
        } else {
            wp_send_json_error(sprintf(__('Connection failed with status code: %d', 'stock-scanner'), $status_code));
        }
    }
    
    /**
     * Test PayPal connection
     */
    public function test_paypal_connection() {
        check_ajax_referer('stock_scanner_admin_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die(__('Unauthorized', 'stock-scanner'));
        }
        
        $payment_settings = get_option('stock_scanner_payment_settings', array());
        $client_id = $payment_settings['paypal_client_id'] ?? '';
        $client_secret = $payment_settings['paypal_client_secret'] ?? '';
        $mode = $payment_settings['paypal_mode'] ?? 'sandbox';
        
        if (empty($client_id) || empty($client_secret)) {
            wp_send_json_error(__('PayPal credentials not configured', 'stock-scanner'));
        }
        
        $api_url = $mode === 'live' 
            ? 'https://api.paypal.com/v1/oauth2/token'
            : 'https://api.sandbox.paypal.com/v1/oauth2/token';
        
        $response = wp_remote_post($api_url, array(
            'headers' => array(
                'Authorization' => 'Basic ' . base64_encode($client_id . ':' . $client_secret),
                'Content-Type' => 'application/x-www-form-urlencoded'
            ),
            'body' => 'grant_type=client_credentials',
            'timeout' => 10
        ));
        
        if (is_wp_error($response)) {
            wp_send_json_error($response->get_error_message());
        }
        
        $status_code = wp_remote_retrieve_response_code($response);
        
        if ($status_code === 200) {
            $body = json_decode(wp_remote_retrieve_body($response), true);
            if (isset($body['access_token'])) {
                wp_send_json_success(__('PayPal connection successful!', 'stock-scanner'));
            } else {
                wp_send_json_error(__('Invalid PayPal response', 'stock-scanner'));
            }
        } else {
            wp_send_json_error(sprintf(__('PayPal connection failed with status code: %d', 'stock-scanner'), $status_code));
        }
    }
    
    /**
     * Sanitize settings functions
     */
    public function sanitize_general_settings($input) {
        $sanitized = array();
        
        if (isset($input['site_title'])) {
            $sanitized['site_title'] = sanitize_text_field($input['site_title']);
        }
        
        if (isset($input['site_description'])) {
            $sanitized['site_description'] = sanitize_textarea_field($input['site_description']);
        }
        
        if (isset($input['default_currency'])) {
            $sanitized['default_currency'] = sanitize_text_field($input['default_currency']);
        }
        
        if (isset($input['timezone'])) {
            $sanitized['timezone'] = sanitize_text_field($input['timezone']);
        }
        
        $sanitized['enable_registration'] = isset($input['enable_registration']) ? 1 : 0;
        $sanitized['show_welcome'] = isset($input['show_welcome']) ? 1 : 0;
        $sanitized['email_notifications'] = isset($input['email_notifications']) ? 1 : 0;
        $sanitized['notify_new_users'] = isset($input['notify_new_users']) ? 1 : 0;
        $sanitized['notify_upgrades'] = isset($input['notify_upgrades']) ? 1 : 0;
        $sanitized['notify_errors'] = isset($input['notify_errors']) ? 1 : 0;
        
        if (isset($input['default_role'])) {
            $sanitized['default_role'] = sanitize_text_field($input['default_role']);
        }
        
        if (isset($input['default_dashboard'])) {
            $sanitized['default_dashboard'] = sanitize_text_field($input['default_dashboard']);
        }
        
        if (isset($input['auto_refresh'])) {
            $sanitized['auto_refresh'] = absint($input['auto_refresh']);
        }
        
        if (isset($input['admin_email'])) {
            $sanitized['admin_email'] = sanitize_email($input['admin_email']);
        }
        
        return $sanitized;
    }
    
    public function sanitize_api_settings($input) {
        $sanitized = array();
        
        if (isset($input['backend_url'])) {
            $sanitized['backend_url'] = esc_url_raw($input['backend_url']);
        }
        
        if (isset($input['api_key'])) {
            $sanitized['api_key'] = sanitize_text_field($input['api_key']);
        }
        
        if (isset($input['api_version'])) {
            $sanitized['api_version'] = sanitize_text_field($input['api_version']);
        }
        
        if (isset($input['timeout'])) {
            $sanitized['timeout'] = absint($input['timeout']);
        }
        
        if (isset($input['stock_provider'])) {
            $sanitized['stock_provider'] = sanitize_text_field($input['stock_provider']);
        }
        
        if (isset($input['stock_api_key'])) {
            $sanitized['stock_api_key'] = sanitize_text_field($input['stock_api_key']);
        }
        
        $sanitized['realtime_data'] = isset($input['realtime_data']) ? 1 : 0;
        
        if (isset($input['news_provider'])) {
            $sanitized['news_provider'] = sanitize_text_field($input['news_provider']);
        }
        
        if (isset($input['news_api_key'])) {
            $sanitized['news_api_key'] = sanitize_text_field($input['news_api_key']);
        }
        
        if (isset($input['news_frequency'])) {
            $sanitized['news_frequency'] = absint($input['news_frequency']);
        }
        
        return $sanitized;
    }
    
    public function sanitize_payment_settings($input) {
        $sanitized = array();
        
        if (isset($input['paypal_mode'])) {
            $sanitized['paypal_mode'] = sanitize_text_field($input['paypal_mode']);
        }
        
        if (isset($input['paypal_client_id'])) {
            $sanitized['paypal_client_id'] = sanitize_text_field($input['paypal_client_id']);
        }
        
        if (isset($input['paypal_client_secret'])) {
            $sanitized['paypal_client_secret'] = sanitize_text_field($input['paypal_client_secret']);
        }
        
        if (isset($input['paypal_webhook_id'])) {
            $sanitized['paypal_webhook_id'] = sanitize_text_field($input['paypal_webhook_id']);
        }
        
        if (isset($input['bronze_price'])) {
            $sanitized['bronze_price'] = floatval($input['bronze_price']);
        }
        
        if (isset($input['silver_price'])) {
            $sanitized['silver_price'] = floatval($input['silver_price']);
        }
        
        if (isset($input['gold_price'])) {
            $sanitized['gold_price'] = floatval($input['gold_price']);
        }
        
        if (isset($input['trial_days'])) {
            $sanitized['trial_days'] = absint($input['trial_days']);
        }
        
        $sanitized['enable_stripe'] = isset($input['enable_stripe']) ? 1 : 0;
        
        if (isset($input['stripe_publishable_key'])) {
            $sanitized['stripe_publishable_key'] = sanitize_text_field($input['stripe_publishable_key']);
        }
        
        if (isset($input['stripe_secret_key'])) {
            $sanitized['stripe_secret_key'] = sanitize_text_field($input['stripe_secret_key']);
        }
        
        return $sanitized;
    }
    
    public function sanitize_feature_settings($input) {
        $sanitized = array();
        
        $sanitized['enable_portfolios'] = isset($input['enable_portfolios']) ? 1 : 0;
        $sanitized['enable_public_portfolios'] = isset($input['enable_public_portfolios']) ? 1 : 0;
        $sanitized['enable_csv'] = isset($input['enable_csv']) ? 1 : 0;
        $sanitized['enable_analytics'] = isset($input['enable_analytics']) ? 1 : 0;
        $sanitized['enable_watchlists'] = isset($input['enable_watchlists']) ? 1 : 0;
        $sanitized['enable_price_alerts'] = isset($input['enable_price_alerts']) ? 1 : 0;
        $sanitized['enable_bulk_ops'] = isset($input['enable_bulk_ops']) ? 1 : 0;
        $sanitized['enable_news'] = isset($input['enable_news']) ? 1 : 0;
        $sanitized['enable_news_analytics'] = isset($input['enable_news_analytics']) ? 1 : 0;
        $sanitized['enable_social'] = isset($input['enable_social']) ? 1 : 0;
        
        return $sanitized;
    }
    
    public function sanitize_limit_settings($input) {
        $sanitized = array();
        
        $fields = [
            'free_api_calls', 'free_portfolios', 'free_watchlists', 'free_holdings',
            'bronze_api_calls', 'bronze_portfolios', 'bronze_watchlists', 'bronze_holdings',
            'silver_api_calls', 'silver_portfolios', 'silver_watchlists', 'silver_holdings',
            'gold_api_calls', 'gold_portfolios', 'gold_watchlists', 'gold_holdings'
        ];
        
        foreach ($fields as $field) {
            if (isset($input[$field])) {
                $sanitized[$field] = intval($input[$field]);
            }
        }
        
        return $sanitized;
    }
    
    public function sanitize_advanced_settings($input) {
        $sanitized = array();
        
        $sanitized['enable_caching'] = isset($input['enable_caching']) ? 1 : 0;
        $sanitized['db_optimization'] = isset($input['db_optimization']) ? 1 : 0;
        $sanitized['enable_rate_limiting'] = isset($input['enable_rate_limiting']) ? 1 : 0;
        $sanitized['enable_audit_log'] = isset($input['enable_audit_log']) ? 1 : 0;
        $sanitized['debug_mode'] = isset($input['debug_mode']) ? 1 : 0;
        $sanitized['maintenance_mode'] = isset($input['maintenance_mode']) ? 1 : 0;
        $sanitized['auto_cleanup'] = isset($input['auto_cleanup']) ? 1 : 0;
        
        if (isset($input['cache_duration'])) {
            $sanitized['cache_duration'] = absint($input['cache_duration']);
        }
        
        if (isset($input['rate_limit'])) {
            $sanitized['rate_limit'] = absint($input['rate_limit']);
        }
        
        if (isset($input['log_level'])) {
            $sanitized['log_level'] = sanitize_text_field($input['log_level']);
        }
        
        if (isset($input['log_retention'])) {
            $sanitized['log_retention'] = absint($input['log_retention']);
        }
        
        if (isset($input['ip_whitelist'])) {
            $sanitized['ip_whitelist'] = sanitize_textarea_field($input['ip_whitelist']);
        }
        
        if (isset($input['maintenance_message'])) {
            $sanitized['maintenance_message'] = sanitize_textarea_field($input['maintenance_message']);
        }
        
        return $sanitized;
    }
}

// Initialize the admin settings
new StockScannerAdminSettings();