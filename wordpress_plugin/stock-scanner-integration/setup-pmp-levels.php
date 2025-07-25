<?php
/**
 * Stock Scanner - Paid Memberships Pro Level Setup
 * 
 * This script sets up the membership levels for Stock Scanner with Stripe integration.
 * Run this after installing Paid Memberships Pro plugin.
 * 
 * Usage: Include this file or run the setup_stock_scanner_membership_levels() function
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Set up Stock Scanner membership levels in Paid Memberships Pro
 */
function setup_stock_scanner_membership_levels() {
    global $wpdb;
    
    // Check if PMPro is active
    if (!function_exists('pmpro_getLevel')) {
        wp_die('Paid Memberships Pro plugin must be installed and activated first.');
    }
    
    $levels = array(
        array(
            'id' => 1,
            'name' => 'Basic',
            'description' => 'Perfect for casual traders - 1,000 API calls per day',
            'confirmation' => 'Welcome to Stock Scanner Basic! You now have access to 1,000 API calls per day.',
            'initial_payment' => 15.00,
            'billing_amount' => 15.00,
            'cycle_number' => 1,
            'cycle_period' => 'Month',
            'billing_limit' => 0,
            'trial_amount' => 0.00,
            'trial_limit' => 0,
            'allow_signups' => 1
        ),
        array(
            'id' => 2,
            'name' => 'Pro',
            'description' => 'Ideal for active traders - 5,000 API calls per day with priority access',
            'confirmation' => 'Welcome to Stock Scanner Pro! You now have access to 5,000 API calls per day with priority access during system load.',
            'initial_payment' => 30.00,
            'billing_amount' => 30.00,
            'cycle_number' => 1,
            'cycle_period' => 'Month',
            'billing_limit' => 0,
            'trial_amount' => 0.00,
            'trial_limit' => 0,
            'allow_signups' => 1
        ),
        array(
            'id' => 3,
            'name' => 'Enterprise',
            'description' => 'For professional traders - 20,000 API calls per day with guaranteed access',
            'confirmation' => 'Welcome to Stock Scanner Enterprise! You now have access to 20,000 API calls per day with guaranteed access even during system emergencies.',
            'initial_payment' => 100.00,
            'billing_amount' => 100.00,
            'cycle_number' => 1,
            'cycle_period' => 'Month',
            'billing_limit' => 0,
            'trial_amount' => 0.00,
            'trial_limit' => 0,
            'allow_signups' => 1
        )
    );
    
    $table_name = $wpdb->prefix . 'pmpro_membership_levels';
    
    foreach ($levels as $level) {
        // Check if level already exists
        $existing = $wpdb->get_row($wpdb->prepare(
            "SELECT * FROM $table_name WHERE id = %d",
            $level['id']
        ));
        
        if ($existing) {
            // Update existing level
            $wpdb->update(
                $table_name,
                $level,
                array('id' => $level['id']),
                array('%d', '%s', '%s', '%s', '%f', '%f', '%d', '%s', '%d', '%f', '%d', '%d'),
                array('%d')
            );
            echo "Updated membership level: " . $level['name'] . "\n";
        } else {
            // Insert new level
            $wpdb->insert(
                $table_name,
                $level,
                array('%d', '%s', '%s', '%s', '%f', '%f', '%d', '%s', '%d', '%f', '%d', '%d')
            );
            echo "Created membership level: " . $level['name'] . "\n";
        }
    }
    
    // Set up level categories (optional)
    setup_level_categories();
    
    // Create custom fields for levels
    setup_custom_level_fields();
    
    echo "Stock Scanner membership levels setup completed!\n";
}

/**
 * Set up level categories for better organization
 */
function setup_level_categories() {
    // This is optional - PMPro doesn't have built-in categories
    // But we can add custom meta for organization
    
    $level_meta = array(
        1 => array(
            'api_calls_per_day' => 1000,
            'stock_searches_per_day' => 200,
            'news_articles_per_day' => 500,
            'concurrent_requests' => 3,
            'priority_level' => 2,
            'emergency_access' => false,
            'support_level' => 'email'
        ),
        2 => array(
            'api_calls_per_day' => 5000,
            'stock_searches_per_day' => 1000,
            'news_articles_per_day' => 2500,
            'concurrent_requests' => 7,
            'priority_level' => 3,
            'emergency_access' => false,
            'support_level' => 'priority_email'
        ),
        3 => array(
            'api_calls_per_day' => 20000,
            'stock_searches_per_day' => 5000,
            'news_articles_per_day' => 10000,
            'concurrent_requests' => 15,
            'priority_level' => 4,
            'emergency_access' => true,
            'support_level' => 'phone_and_email'
        )
    );
    
    foreach ($level_meta as $level_id => $meta) {
        foreach ($meta as $key => $value) {
            update_option("pmpro_level_{$level_id}_{$key}", $value);
        }
    }
}

/**
 * Set up custom fields for membership levels
 */
function setup_custom_level_fields() {
    // Add custom checkout fields if needed
    $custom_fields = array(
        'company_name' => array(
            'label' => 'Company Name (Optional)',
            'type' => 'text',
            'required' => false,
            'levels' => array(2, 3) // Only for Pro and Enterprise
        ),
        'trading_experience' => array(
            'label' => 'Trading Experience',
            'type' => 'select',
            'options' => array(
                'beginner' => 'Beginner (0-1 years)',
                'intermediate' => 'Intermediate (2-5 years)',
                'advanced' => 'Advanced (5+ years)',
                'professional' => 'Professional Trader'
            ),
            'required' => false,
            'levels' => array(1, 2, 3)
        )
    );
    
    // Store custom fields configuration
    update_option('stock_scanner_custom_checkout_fields', $custom_fields);
}

/**
 * Configure Stripe settings for PMPro
 */
function configure_stripe_settings() {
    // These would typically be set in wp-admin, but we can provide defaults
    $stripe_settings = array(
        'gateway' => 'stripe',
        'stripe_publishablekey' => get_option('stock_scanner_stripe_publishable_key', ''),
        'stripe_secretkey' => get_option('stock_scanner_stripe_secret_key', ''),
        'stripe_webhook_secret' => get_option('stock_scanner_stripe_webhook_secret', ''),
        'currency' => 'USD',
        'tax_state' => '',
        'tax_rate' => 0,
        'accepted_credit_cards' => 'Visa,Mastercard,American Express,Discover'
    );
    
    foreach ($stripe_settings as $key => $value) {
        update_option("pmpro_{$key}", $value);
    }
    
    echo "Stripe settings configured. Please update your Stripe keys in wp-admin.\n";
}

/**
 * Set up checkout page content and styling
 */
function setup_checkout_page_content() {
    // Custom checkout page template content
    $checkout_content = '
    <div class="stock-scanner-checkout">
        <h2>Choose Your Stock Scanner Plan</h2>
        <div class="membership-benefits">
            <h3>What you get with Stock Scanner:</h3>
            <ul>
                <li>✅ Real-time NASDAQ stock data</li>
                <li>✅ AI-powered news sentiment analysis</li>
                <li>✅ Advanced stock screening tools</li>
                <li>✅ Portfolio tracking and alerts</li>
                <li>✅ Professional-grade analytics</li>
            </ul>
        </div>
        
        <div class="pricing-comparison">
            <table class="membership-comparison">
                <thead>
                    <tr>
                        <th>Feature</th>
                        <th>Basic ($15/mo)</th>
                        <th>Pro ($30/mo)</th>
                        <th>Enterprise ($100/mo)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>API Calls per Day</td>
                        <td>1,000</td>
                        <td>5,000</td>
                        <td>20,000</td>
                    </tr>
                    <tr>
                        <td>Stock Searches per Day</td>
                        <td>200</td>
                        <td>1,000</td>
                        <td>5,000</td>
                    </tr>
                    <tr>
                        <td>News Articles per Day</td>
                        <td>500</td>
                        <td>2,500</td>
                        <td>10,000</td>
                    </tr>
                    <tr>
                        <td>Concurrent Requests</td>
                        <td>3</td>
                        <td>7</td>
                        <td>15</td>
                    </tr>
                    <tr>
                        <td>Priority Access</td>
                        <td>❌</td>
                        <td>✅</td>
                        <td>✅ Guaranteed</td>
                    </tr>
                    <tr>
                        <td>Emergency Access</td>
                        <td>❌</td>
                        <td>❌</td>
                        <td>✅</td>
                    </tr>
                    <tr>
                        <td>Support</td>
                        <td>Email</td>
                        <td>Priority Email</td>
                        <td>Phone + Email</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="security-badges">
            <p><strong>🔒 Secure Payment:</strong> Your payment information is encrypted and secure. We use Stripe for payment processing.</p>
            <p><strong>💰 Money-Back Guarantee:</strong> 30-day money-back guarantee on all plans.</p>
            <p><strong>🔄 Cancel Anytime:</strong> No long-term contracts. Cancel or change your plan anytime.</p>
        </div>
    </div>';
    
    // Store checkout content for use in templates
    update_option('stock_scanner_checkout_content', $checkout_content);
}

/**
 * Add webhook endpoints for Stripe
 */
function setup_stripe_webhooks() {
    // Register webhook endpoint
    add_action('wp_ajax_nopriv_stock_scanner_stripe_webhook', 'handle_stripe_webhook');
    add_action('wp_ajax_stock_scanner_stripe_webhook', 'handle_stripe_webhook');
    
    // Rewrite rule for cleaner webhook URL
    add_rewrite_rule(
        '^stock-scanner/webhook/stripe/?$',
        'index.php?stock_scanner_stripe_webhook=1',
        'top'
    );
    
    add_filter('query_vars', function($vars) {
        $vars[] = 'stock_scanner_stripe_webhook';
        return $vars;
    });
    
    add_action('template_redirect', function() {
        if (get_query_var('stock_scanner_stripe_webhook')) {
            handle_stripe_webhook();
            exit;
        }
    });
    
    // Flush rewrite rules
    flush_rewrite_rules();
    
    echo "Stripe webhook endpoint configured: " . home_url('/stock-scanner/webhook/stripe/') . "\n";
}

/**
 * Handle Stripe webhook events
 */
function handle_stripe_webhook() {
    // Verify webhook signature
    $webhook_secret = get_option('stock_scanner_stripe_webhook_secret');
    if (!$webhook_secret) {
        http_response_code(400);
        exit('Webhook secret not configured');
    }
    
    $payload = @file_get_contents('php://input');
    $sig_header = $_SERVER['HTTP_STRIPE_SIGNATURE'] ?? '';
    
    try {
        // Verify webhook signature (simplified - use Stripe library in production)
        $event = json_decode($payload, true);
        
        // Handle different event types
        switch ($event['type']) {
            case 'customer.subscription.created':
                handle_subscription_created($event['data']['object']);
                break;
                
            case 'customer.subscription.updated':
                handle_subscription_updated($event['data']['object']);
                break;
                
            case 'customer.subscription.deleted':
                handle_subscription_cancelled($event['data']['object']);
                break;
                
            case 'invoice.payment_succeeded':
                handle_payment_succeeded($event['data']['object']);
                break;
                
            case 'invoice.payment_failed':
                handle_payment_failed($event['data']['object']);
                break;
        }
        
        http_response_code(200);
        echo 'OK';
        
    } catch (Exception $e) {
        error_log('Stripe webhook error: ' . $e->getMessage());
        http_response_code(400);
        exit('Webhook error');
    }
}

/**
 * Handle subscription created event
 */
function handle_subscription_created($subscription) {
    // Update user membership based on subscription
    $customer_id = $subscription['customer'];
    $user = get_users(array(
        'meta_key' => 'stripe_customer_id',
        'meta_value' => $customer_id,
        'number' => 1
    ));
    
    if (!empty($user)) {
        $user_id = $user[0]->ID;
        
        // Determine membership level based on subscription amount
        $amount = $subscription['items']['data'][0]['price']['unit_amount'] / 100;
        $level_id = get_level_id_by_amount($amount);
        
        if ($level_id) {
            // Update PMPro membership
            if (function_exists('pmpro_changeMembershipLevel')) {
                pmpro_changeMembershipLevel($level_id, $user_id);
            }
            
            // Update custom meta
            update_user_meta($user_id, 'stripe_subscription_id', $subscription['id']);
            update_user_meta($user_id, 'subscription_status', 'active');
        }
    }
}

/**
 * Handle subscription updated event
 */
function handle_subscription_updated($subscription) {
    // Similar to created, but handle plan changes
    handle_subscription_created($subscription);
}

/**
 * Handle subscription cancelled event
 */
function handle_subscription_cancelled($subscription) {
    $customer_id = $subscription['customer'];
    $user = get_users(array(
        'meta_key' => 'stripe_customer_id',
        'meta_value' => $customer_id,
        'number' => 1
    ));
    
    if (!empty($user)) {
        $user_id = $user[0]->ID;
        
        // Cancel PMPro membership
        if (function_exists('pmpro_changeMembershipLevel')) {
            pmpro_changeMembershipLevel(0, $user_id); // Level 0 = no membership
        }
        
        // Update meta
        update_user_meta($user_id, 'subscription_status', 'cancelled');
    }
}

/**
 * Handle successful payment
 */
function handle_payment_succeeded($invoice) {
    // Log successful payment, send confirmation email, etc.
    error_log('Payment succeeded for invoice: ' . $invoice['id']);
}

/**
 * Handle failed payment
 */
function handle_payment_failed($invoice) {
    // Handle failed payment - notify user, retry logic, etc.
    error_log('Payment failed for invoice: ' . $invoice['id']);
}

/**
 * Get membership level ID by payment amount
 */
function get_level_id_by_amount($amount) {
    $level_amounts = array(
        15 => 1,  // Basic
        30 => 2,  // Pro
        100 => 3  // Enterprise
    );
    
    return $level_amounts[$amount] ?? null;
}

/**
 * Main setup function - run this to set everything up
 */
function run_stock_scanner_pmp_setup() {
    echo "Setting up Stock Scanner Paid Memberships Pro integration...\n\n";
    
    setup_stock_scanner_membership_levels();
    configure_stripe_settings();
    setup_checkout_page_content();
    setup_stripe_webhooks();
    
    echo "\n✅ Setup completed!\n";
    echo "Next steps:\n";
    echo "1. Configure your Stripe keys in WordPress admin\n";
    echo "2. Test the checkout process\n";
    echo "3. Set up webhook URL in Stripe dashboard: " . home_url('/stock-scanner/webhook/stripe/') . "\n";
    echo "4. Configure tax settings if needed\n";
    echo "5. Customize checkout page styling\n";
}

// Uncomment the line below to run setup when this file is included
// run_stock_scanner_pmp_setup();

?>