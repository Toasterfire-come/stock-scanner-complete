<?php
/**
 * Stripe + Paid Membership Pro Configuration
 * Stock Scanner Membership Levels with Stripe Integration
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Configure Paid Membership Pro Membership Levels with Stripe
 * Run this in WordPress admin or via WP-CLI
 */
function setup_stock_scanner_membership_levels() {
    
    // Check if PMPro is active
    if (!function_exists('pmpro_getLevel')) {
        return new WP_Error('pmpro_required', 'Paid Membership Pro is required');
    }

    // Membership Level Configurations
    $membership_levels = array(
        array(
            'id' => 1,
            'name' => 'Basic Stock Access',
            'description' => 'Access to 1,500 stocks per month with real-time data, volume information, and basic charts.',
            'confirmation' => 'Welcome to Basic Stock Access! You now have access to 1,500 stock views per month.',
            'initial_payment' => 9.99,
            'billing_amount' => 9.99,
            'cycle_number' => 1,
            'cycle_period' => 'Month',
            'billing_limit' => 0, // 0 = unlimited billing cycles
            'trial_amount' => 0,
            'trial_limit' => 0,
            'allow_signups' => 1,
            'expiration_number' => 0,
            'expiration_period' => '',
            'stripe_price_id' => 'price_basic_monthly', // Set in Stripe Dashboard
        ),
        array(
            'id' => 2,
            'name' => 'Premium Stock Analysis',
            'description' => 'Access to 6,000 stocks per month with technical indicators, price alerts, advanced charts, and portfolio tracking.',
            'confirmation' => 'Welcome to Premium Stock Analysis! You now have access to advanced features and 6,000 stock views per month.',
            'initial_payment' => 29.99,
            'billing_amount' => 29.99,
            'cycle_number' => 1,
            'cycle_period' => 'Month',
            'billing_limit' => 0,
            'trial_amount' => 0,
            'trial_limit' => 0,
            'allow_signups' => 1,
            'expiration_number' => 0,
            'expiration_period' => '',
            'stripe_price_id' => 'price_premium_monthly',
        ),
        array(
            'id' => 3,
            'name' => 'Pro Trading Suite',
            'description' => 'Unlimited stock access with AI analysis, market predictions, insider data, API access, and white-label options.',
            'confirmation' => 'Welcome to Pro Trading Suite! You now have unlimited access to all features and data.',
            'initial_payment' => 99.99,
            'billing_amount' => 99.99,
            'cycle_number' => 1,
            'cycle_period' => 'Month',
            'billing_limit' => 0,
            'trial_amount' => 0,
            'trial_limit' => 0,
            'allow_signups' => 1,
            'expiration_number' => 0,
            'expiration_period' => '',
            'stripe_price_id' => 'price_pro_monthly',
        ),
    );

    // Create/Update membership levels
    foreach ($membership_levels as $level_data) {
        $level_id = $level_data['id'];
        
        // Check if level exists
        $existing_level = pmpro_getLevel($level_id);
        
        if ($existing_level) {
            // Update existing level
            $result = pmpro_save_membership_level($level_data);
        } else {
            // Create new level
            $result = pmpro_save_membership_level($level_data);
        }
        
        if ($result) {
            echo "✅ Created/Updated membership level: {$level_data['name']}\n";
        } else {
            echo "❌ Failed to create membership level: {$level_data['name']}\n";
        }
    }
    
    return true;
}

/**
 * Stripe Configuration Settings
 */
function configure_stripe_settings() {
    
    // Stripe API Keys (Set these in your wp-config.php for security)
    $stripe_settings = array(
        'publishable_key' => defined('STRIPE_PUBLISHABLE_KEY') ? STRIPE_PUBLISHABLE_KEY : '',
        'secret_key' => defined('STRIPE_SECRET_KEY') ? STRIPE_SECRET_KEY : '',
        'webhook_endpoint_secret' => defined('STRIPE_WEBHOOK_SECRET') ? STRIPE_WEBHOOK_SECRET : '',
        'currency' => 'USD',
        'statement_descriptor' => 'STOCK SCANNER',
        'capture_method' => 'automatic',
    );
    
    // Update PMPro Stripe settings
    update_option('pmpro_stripe_publishablekey', $stripe_settings['publishable_key']);
    update_option('pmpro_stripe_secretkey', $stripe_settings['secret_key']);
    update_option('pmpro_currency', $stripe_settings['currency']);
    update_option('pmpro_stripe_billing_descriptorsuffix', $stripe_settings['statement_descriptor']);
    
    // Set Stripe as the gateway
    update_option('pmpro_gateway', 'stripe');
    update_option('pmpro_gateway_environment', 'live'); // Change to 'sandbox' for testing
    
    echo "✅ Stripe settings configured\n";
    
    return $stripe_settings;
}

/**
 * Create Stripe Products and Prices
 * This should be run once to set up your Stripe products
 */
function create_stripe_products() {
    
    if (!defined('STRIPE_SECRET_KEY') || empty(STRIPE_SECRET_KEY)) {
        return new WP_Error('stripe_key_missing', 'Stripe secret key is required');
    }
    
    // Stripe API configuration
    \Stripe\Stripe::setApiKey(STRIPE_SECRET_KEY);
    
    $products = array(
        array(
            'name' => 'Basic Stock Access',
            'description' => 'Access to 1,500 stocks per month with real-time data',
            'price_id' => 'price_basic_monthly',
            'amount' => 999, // $9.99 in cents
            'interval' => 'month',
            'features' => array(
                '1,500 stock views per month',
                'Real-time price data',
                'Volume information',
                'Basic charts',
                'Email support'
            )
        ),
        array(
            'name' => 'Premium Stock Analysis',
            'description' => 'Advanced stock analysis with 6,000 monthly views',
            'price_id' => 'price_premium_monthly',
            'amount' => 2999, // $29.99 in cents
            'interval' => 'month',
            'features' => array(
                '6,000 stock views per month',
                'Technical indicators',
                'Price alerts',
                'Advanced charts',
                'Portfolio tracking',
                'Priority support'
            )
        ),
        array(
            'name' => 'Pro Trading Suite',
            'description' => 'Unlimited access with AI analysis and API',
            'price_id' => 'price_pro_monthly',
            'amount' => 9999, // $99.99 in cents
            'interval' => 'month',
            'features' => array(
                'Unlimited stock views',
                'AI market analysis',
                'Predictive algorithms',
                'Insider data access',
                'Full API access',
                'White-label options',
                'Dedicated support'
            )
        )
    );
    
    foreach ($products as $product_data) {
        try {
            // Create Stripe Product
            $product = \Stripe\Product::create([
                'name' => $product_data['name'],
                'description' => $product_data['description'],
                'metadata' => [
                    'features' => implode(', ', $product_data['features']),
                    'wordpress_integration' => 'stock_scanner_pmp'
                ]
            ]);
            
            // Create Stripe Price
            $price = \Stripe\Price::create([
                'product' => $product->id,
                'unit_amount' => $product_data['amount'],
                'currency' => 'usd',
                'recurring' => [
                    'interval' => $product_data['interval']
                ],
                'lookup_key' => $product_data['price_id'],
                'metadata' => [
                    'pmp_level' => $product_data['price_id']
                ]
            ]);
            
            echo "✅ Created Stripe product: {$product_data['name']} (Price ID: {$price->id})\n";
            
            // Store the actual Stripe Price ID for PMPro
            update_option("stripe_price_id_{$product_data['price_id']}", $price->id);
            
        } catch (\Stripe\Exception\ApiErrorException $e) {
            echo "❌ Stripe error for {$product_data['name']}: " . $e->getMessage() . "\n";
        }
    }
    
    return true;
}

/**
 * Setup Stripe Webhooks
 */
function setup_stripe_webhooks() {
    
    if (!defined('STRIPE_SECRET_KEY') || empty(STRIPE_SECRET_KEY)) {
        return new WP_Error('stripe_key_missing', 'Stripe secret key is required');
    }
    
    \Stripe\Stripe::setApiKey(STRIPE_SECRET_KEY);
    
    // Your WordPress site URL
    $webhook_url = home_url('/wp-json/pmpro/v1/stripe-webhook/');
    
    try {
        $webhook = \Stripe\WebhookEndpoint::create([
            'url' => $webhook_url,
            'enabled_events' => [
                'customer.subscription.created',
                'customer.subscription.updated',
                'customer.subscription.deleted',
                'invoice.payment_succeeded',
                'invoice.payment_failed',
                'customer.created',
                'customer.updated',
                'payment_method.attached'
            ],
            'description' => 'Stock Scanner PMP Integration Webhook'
        ]);
        
        // Store webhook secret
        update_option('pmpro_stripe_webhook_secret', $webhook->secret);
        
        echo "✅ Stripe webhook created: {$webhook->url}\n";
        echo "🔑 Webhook secret: {$webhook->secret}\n";
        
        return $webhook;
        
    } catch (\Stripe\Exception\ApiErrorException $e) {
        echo "❌ Webhook creation error: " . $e->getMessage() . "\n";
        return false;
    }
}

/**
 * Custom checkout fields for stock scanner
 */
function add_stock_scanner_checkout_fields() {
    
    // Add custom fields to PMPro checkout
    add_action('pmpro_checkout_after_billing_fields', function() {
        ?>
        <div class="pmpro_checkout-field">
            <label for="trading_experience">Trading Experience</label>
            <select id="trading_experience" name="trading_experience" class="input">
                <option value="">Select your experience level</option>
                <option value="beginner">Beginner (0-1 years)</option>
                <option value="intermediate">Intermediate (2-5 years)</option>
                <option value="advanced">Advanced (5+ years)</option>
                <option value="professional">Professional Trader</option>
            </select>
        </div>
        
        <div class="pmpro_checkout-field">
            <label for="interested_sectors">Interested Sectors (optional)</label>
            <input type="text" id="interested_sectors" name="interested_sectors" class="input" 
                   placeholder="e.g., Technology, Healthcare, Finance" />
        </div>
        
        <div class="pmpro_checkout-field">
            <label for="referral_source">How did you hear about us?</label>
            <select id="referral_source" name="referral_source" class="input">
                <option value="">Select source</option>
                <option value="google">Google Search</option>
                <option value="social_media">Social Media</option>
                <option value="friend_referral">Friend Referral</option>
                <option value="financial_blog">Financial Blog/Website</option>
                <option value="advertisement">Advertisement</option>
                <option value="other">Other</option>
            </select>
        </div>
        <?php
    });
    
    // Save custom fields
    add_action('pmpro_after_checkout', function($user_id, $order) {
        if (!empty($_POST['trading_experience'])) {
            update_user_meta($user_id, 'trading_experience', sanitize_text_field($_POST['trading_experience']));
        }
        if (!empty($_POST['interested_sectors'])) {
            update_user_meta($user_id, 'interested_sectors', sanitize_text_field($_POST['interested_sectors']));
        }
        if (!empty($_POST['referral_source'])) {
            update_user_meta($user_id, 'referral_source', sanitize_text_field($_POST['referral_source']));
        }
    }, 10, 2);
}

/**
 * Initialize everything
 */
function initialize_stripe_pmp_integration() {
    
    // Add custom checkout fields
    add_stock_scanner_checkout_fields();
    
    // Hook to run setup when plugin is activated
    register_activation_hook(__FILE__, function() {
        setup_stock_scanner_membership_levels();
        configure_stripe_settings();
        
        // Only create Stripe products if API key is available
        if (defined('STRIPE_SECRET_KEY') && !empty(STRIPE_SECRET_KEY)) {
            create_stripe_products();
            setup_stripe_webhooks();
        }
    });
    
    echo "🚀 Stripe + PMP integration initialized\n";
}

// Auto-initialize if this file is included
if (function_exists('add_action')) {
    add_action('init', 'initialize_stripe_pmp_integration');
}

/**
 * WP-CLI Commands for easy setup
 */
if (defined('WP_CLI') && WP_CLI) {
    
    WP_CLI::add_command('stock-scanner setup-memberships', function() {
        WP_CLI::log('Setting up membership levels...');
        setup_stock_scanner_membership_levels();
        WP_CLI::success('Membership levels configured!');
    });
    
    WP_CLI::add_command('stock-scanner setup-stripe', function() {
        WP_CLI::log('Configuring Stripe settings...');
        configure_stripe_settings();
        WP_CLI::success('Stripe settings configured!');
    });
    
    WP_CLI::add_command('stock-scanner create-products', function() {
        WP_CLI::log('Creating Stripe products...');
        $result = create_stripe_products();
        if (is_wp_error($result)) {
            WP_CLI::error($result->get_error_message());
        } else {
            WP_CLI::success('Stripe products created!');
        }
    });
    
    WP_CLI::add_command('stock-scanner setup-webhooks', function() {
        WP_CLI::log('Setting up Stripe webhooks...');
        $result = setup_stripe_webhooks();
        if ($result) {
            WP_CLI::success('Webhooks configured!');
        } else {
            WP_CLI::error('Failed to setup webhooks');
        }
    });
}

?>

<!-- 
Add this to your wp-config.php file:

// Stripe Configuration
define('STRIPE_PUBLISHABLE_KEY', 'pk_live_your_publishable_key_here');
define('STRIPE_SECRET_KEY', 'sk_live_your_secret_key_here');
define('STRIPE_WEBHOOK_SECRET', 'whsec_your_webhook_secret_here');

// For testing, use:
// define('STRIPE_PUBLISHABLE_KEY', 'pk_test_your_test_publishable_key_here');
// define('STRIPE_SECRET_KEY', 'sk_test_your_test_secret_key_here');
-->