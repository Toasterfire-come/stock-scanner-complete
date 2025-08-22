<?php
/**
 * Template Name: PayPal Checkout
 * PayPal checkout page with integrated PayPal buttons
 */

// Security check
if (!defined('ABSPATH')) {
    exit;
}

// Redirect if user is not logged in
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

// Get plan parameters from URL
$selected_plan = isset($_GET['plan']) ? sanitize_text_field($_GET['plan']) : 'bronze';
$billing_cycle = isset($_GET['billing']) ? sanitize_text_field($_GET['billing']) : 'monthly';

// Validate plan
$valid_plans = ['bronze', 'silver', 'gold'];
if (!in_array($selected_plan, $valid_plans)) {
    $selected_plan = 'bronze';
}

// Validate billing cycle
$valid_cycles = ['monthly', 'annual'];
if (!in_array($billing_cycle, $valid_cycles)) {
    $billing_cycle = 'monthly';
}

// Plan configurations
$plans = [
    'bronze' => [
        'name' => 'Bronze',
        'monthly' => 24.99,
        'annual' => 249.99,
        'features' => [
            '1,500 Monthly API Calls',
            '5 Portfolios',
            '50 Stocks per Watchlist',
            '25 Price Alerts',
            'Email Support',
            '15-min Delayed Data'
        ]
    ],
    'silver' => [
        'name' => 'Silver',
        'monthly' => 39.99,
        'annual' => 399.99,
        'features' => [
            '5,000 Monthly API Calls',
            'Unlimited Portfolios',
            '200 Stocks per Watchlist',
            '100 Price Alerts',
            'Real-time Data',
            'Email + Chat Support',
            'REST API Access'
        ]
    ],
    'gold' => [
        'name' => 'Gold',
        'monthly' => 89.99,
        'annual' => 899.99,
        'features' => [
            'Unlimited API Calls',
            'Unlimited Everything',
            'Priority Support',
            'Real-time Data',
            'Global Markets',
            'REST + WebSocket API',
            'White Label Option'
        ]
    ]
];

$current_plan = $plans[$selected_plan];
$price = $current_plan[$billing_cycle];
$annual_savings = $billing_cycle === 'annual' ? ($current_plan['monthly'] * 12 - $current_plan['annual']) : 0;

// Get PayPal settings
$paypal_mode = get_option('paypal_mode', 'sandbox');
$paypal_client_id = get_option('paypal_client_id', '');

get_header();
?>

<div class="paypal-checkout-container">
    <div class="checkout-header">
        <h1>Complete Your Upgrade</h1>
        <p>Secure payment processing with PayPal</p>
    </div>

    <div class="checkout-content">
        <div class="plan-summary">
            <h2>Order Summary</h2>
            
            <div class="selected-plan">
                <div class="plan-badge <?php echo $selected_plan; ?>">
                    <?php echo $current_plan['name']; ?> Plan
                </div>
                
                <div class="plan-details">
                    <div class="billing-info">
                        <span class="price">$<?php echo number_format($price, 2); ?></span>
                        <span class="period">/<?php echo $billing_cycle === 'annual' ? 'year' : 'month'; ?></span>
                    </div>
                    
                    <?php if ($annual_savings > 0): ?>
                        <div class="savings-badge">
                            Save $<?php echo number_format($annual_savings, 2); ?> annually!
                        </div>
                    <?php endif; ?>
                </div>
            </div>
            
            <div class="plan-features">
                <h3>What's Included:</h3>
                <ul>
                    <?php foreach ($current_plan['features'] as $feature): ?>
                        <li><span class="check-icon">✓</span> <?php echo esc_html($feature); ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>
            
            <div class="billing-toggle">
                <h3>Billing Cycle:</h3>
                <div class="toggle-group">
                    <button class="toggle-btn <?php echo $billing_cycle === 'monthly' ? 'active' : ''; ?>" 
                            onclick="changeBilling('monthly')">
                        Monthly
                    </button>
                    <button class="toggle-btn <?php echo $billing_cycle === 'annual' ? 'active' : ''; ?>" 
                            onclick="changeBilling('annual')">
                        Annual <span class="save-badge">Save 17%</span>
                    </button>
                </div>
            </div>
        </div>
        
        <div class="payment-section">
            <h2>Payment Method</h2>
            
            <div class="payment-options">
                <div class="payment-option active">
                    <div class="option-header">
                        <input type="radio" name="payment_method" value="paypal" checked>
                        <label>PayPal</label>
                        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjI2IiB2aWV3Qm94PSIwIDAgMTAwIDI2IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxwYXRoIGQ9Ik04LjM2IDUuODFIMTMuNjFDMTYuMDcgNS44MSAxNy45IDYuNTcgMTcuOSA5LjAzQzE3LjkgMTEuODMgMTYuMTMgMTMuMzIgMTMuNSAxMy4zMkgxMS40OUwxMC41NiAxOC40M0g4LjM2TDEwLjM2IDkuNzFIMTMuMDdDMTQuMTEgOS43MSAxNC43NyAxMC4xNSAxNC43NyAxMC45QzE0Ljc3IDExLjkxIDEzLjg5IDEyLjQ0IDEyLjU2IDEyLjQ0SDEwLjk2TDEwLjM2IDkuNzFIMTMuMDdaTTIxLjQzIDUuODFIMjMuNjNMMjEuNjMgMTQuNTFIMTkuNDNMMjEuNDMgNS44MVpNMjcuNDMgMTQuNTFIMjUuMjNMMjcuMjMgNS44MUgyOS40M0wyNy40MyAxNC41MVoiIGZpbGw9IiMwMDNGNzEiLz48L3N2Zz4=" alt="PayPal" class="payment-logo">
                    </div>
                    <p class="payment-description">
                        Pay securely with your PayPal account or credit card
                    </p>
                </div>
            </div>
            
            <!-- PayPal Button Container -->
            <div id="paypal-button-container"></div>
            
            <!-- Loading State -->
            <div id="loading-state" style="display: none;">
                <div class="loading-spinner"></div>
                <p>Setting up secure payment...</p>
            </div>
            
            <!-- Error State -->
            <div id="error-state" style="display: none;" class="error-message">
                <h3>Payment Setup Error</h3>
                <p id="error-text"></p>
                <button onclick="retryPaymentSetup()" class="btn btn-primary">Try Again</button>
            </div>
        </div>
    </div>
    
    <div class="security-badges">
        <div class="security-item">
            <span class="security-icon">🔒</span>
            <span>SSL Encrypted</span>
        </div>
        <div class="security-item">
            <span class="security-icon">🛡️</span>
            <span>PayPal Protected</span>
        </div>
        <div class="security-item">
            <span class="security-icon">💳</span>
            <span>30-Day Guarantee</span>
        </div>
    </div>
</div>

<style>
.paypal-checkout-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.checkout-header {
    text-align: center;
    margin-bottom: 40px;
}

.checkout-header h1 {
    font-size: 2.5rem;
    color: #2c3e50;
    margin: 0 0 10px 0;
}

.checkout-header p {
    color: #7f8c8d;
    font-size: 1.1rem;
}

.checkout-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    margin-bottom: 40px;
}

.plan-summary, .payment-section {
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
}

.plan-summary h2, .payment-section h2 {
    margin: 0 0 25px 0;
    color: #2c3e50;
    font-size: 1.5rem;
}

.selected-plan {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 25px;
    border-left: 4px solid #3498db;
}

.plan-badge {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 15px;
}

.plan-badge.bronze { color: #cd7f32; }
.plan-badge.silver { color: #c0c0c0; }
.plan-badge.gold { color: #ffd700; }

.plan-details {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.billing-info .price {
    font-size: 2rem;
    font-weight: bold;
    color: #2c3e50;
}

.billing-info .period {
    color: #7f8c8d;
    font-size: 1.1rem;
}

.savings-badge {
    background: #27ae60;
    color: white;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: bold;
}

/* plan-features styles moved to main style.css to avoid conflicts */

.check-icon {
    color: #27ae60;
    font-weight: bold;
    margin-right: 10px;
}

.billing-toggle {
    margin-top: 25px;
    border-top: 1px solid #ecf0f1;
    padding-top: 20px;
}

.billing-toggle h3 {
    margin: 0 0 15px 0;
    color: #2c3e50;
}

.toggle-group {
    display: flex;
    gap: 10px;
}

.toggle-btn {
    flex: 1;
    padding: 12px 20px;
    border: 2px solid #e1e5e9;
    background: white;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
    position: relative;
}

.toggle-btn.active {
    border-color: #3498db;
    background: #3498db;
    color: white;
}

.toggle-btn:hover:not(.active) {
    border-color: #bdc3c7;
}

.save-badge {
    background: #e74c3c;
    color: white;
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 0.8rem;
    margin-left: 5px;
}

.payment-options {
    margin-bottom: 30px;
}

.payment-option {
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.payment-option.active {
    border-color: #3498db;
    background: rgba(52, 152, 219, 0.05);
}

.option-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 10px;
}

.option-header label {
    font-weight: 600;
    font-size: 1.1rem;
    color: #2c3e50;
    cursor: pointer;
}

.payment-logo {
    height: 30px;
    margin-left: auto;
}

.payment-description {
    color: #7f8c8d;
    margin: 0;
    margin-left: 35px;
}

#paypal-button-container {
    margin-top: 20px;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

#loading-state {
    text-align: center;
    padding: 40px;
    color: #7f8c8d;
}

.error-message {
    background: #fff5f5;
    border: 1px solid #feb2b2;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
}

.error-message h3 {
    color: #e53e3e;
    margin: 0 0 10px 0;
}

.error-message p {
    color: #744d4d;
    margin: 0 0 20px 0;
}

.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-block;
}

.btn-primary {
    background: #3498db;
    color: white;
}

.btn-primary:hover {
    background: #2980b9;
    transform: translateY(-2px);
}

.security-badges {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-top: 40px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

.security-item {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #2c3e50;
    font-weight: 500;
}

.security-icon {
    font-size: 1.2rem;
}

@media (max-width: 768px) {
    .checkout-content {
        grid-template-columns: 1fr;
        gap: 20px;
    }
    
    .plan-summary, .payment-section {
        padding: 20px;
    }
    
    .security-badges {
        flex-direction: column;
        gap: 15px;
        text-align: center;
    }
    
    .toggle-group {
        flex-direction: column;
    }
}
</style>

<script src="https://www.paypal.com/sdk/js?client-id=<?php echo esc_attr($paypal_client_id); ?>&currency=USD&intent=capture"></script>

<script>
let currentPlan = '<?php echo esc_js($selected_plan); ?>';
let currentBilling = '<?php echo esc_js($billing_cycle); ?>';

function changeBilling(cycle) {
    const url = new URL(window.location);
    url.searchParams.set('billing', cycle);
    window.location.href = url.toString();
}

function showLoading() {
    document.getElementById('paypal-button-container').style.display = 'none';
    document.getElementById('loading-state').style.display = 'block';
    document.getElementById('error-state').style.display = 'none';
}

function showError(message) {
    document.getElementById('paypal-button-container').style.display = 'none';
    document.getElementById('loading-state').style.display = 'none';
    document.getElementById('error-state').style.display = 'block';
    document.getElementById('error-text').textContent = message;
}

function retryPaymentSetup() {
    document.getElementById('error-state').style.display = 'none';
    initPayPalButtons();
}

function initPayPalButtons() {
    showLoading();
    
    paypal.Buttons({
        createOrder: function(data, actions) {
            return fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'action': 'create_paypal_order',
                    'plan': currentPlan,
                    'billing_cycle': currentBilling,
                    'nonce': '<?php echo wp_create_nonce('paypal_nonce'); ?>'
                })
            }).then(function(res) {
                return res.json();
            }).then(function(data) {
                if (data.success) {
                    return data.data.order_id;
                } else {
                    throw new Error(data.data || 'Failed to create order');
                }
            });
        },
        
        onApprove: function(data, actions) {
            return fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'action': 'capture_paypal_order',
                    'order_id': data.orderID,
                    'nonce': '<?php echo wp_create_nonce('paypal_nonce'); ?>'
                })
            }).then(function(res) {
                return res.json();
            }).then(function(data) {
                if (data.success) {
                    window.location.href = '<?php echo home_url('/payment-success/'); ?>?order_id=' + data.orderID;
                } else {
                    throw new Error(data.data || 'Payment capture failed');
                }
            });
        },
        
        onError: function(err) {
            console.error('PayPal Error:', err);
            showError('Payment processing error. Please try again.');
        },
        
        onCancel: function(data) {
            window.location.href = '<?php echo home_url('/payment-cancelled/'); ?>';
        }
        
    }).render('#paypal-button-container').then(function() {
        // Hide loading, show buttons
        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('paypal-button-container').style.display = 'block';
    }).catch(function(err) {
        console.error('PayPal Setup Error:', err);
        showError('Failed to load PayPal. Please check your connection and try again.');
    });
}

// Initialize PayPal buttons when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (typeof paypal !== 'undefined') {
        initPayPalButtons();
    } else {
        showError('PayPal SDK failed to load. Please refresh the page.');
    }
});
</script>

<?php get_footer(); ?>