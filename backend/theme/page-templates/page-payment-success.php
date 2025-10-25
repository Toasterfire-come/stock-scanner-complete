<?php
/**
 * Template Name: Payment Success
 * Displays payment confirmation and next steps
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

$user = wp_get_current_user();
$order_id = isset($_GET['order_id']) ? sanitize_text_field($_GET['order_id']) : '';

// Get user's current membership info
$membership_level = get_user_meta($user->ID, 'membership_level', true) ?: 1;
$membership_plan = get_user_meta($user->ID, 'membership_plan', true) ?: 'free';
$billing_cycle = get_user_meta($user->ID, 'billing_cycle', true) ?: 'monthly';

$plan_names = [
    'free' => 'Free',
    'bronze' => 'Bronze',
    'silver' => 'Silver', 
    'gold' => 'Gold'
];

get_header();
?>

<div class="payment-success-container">
    <div class="success-content">
        <div class="success-icon">
            <div class="checkmark-circle">
                <div class="checkmark"></div>
            </div>
        </div>
        
        <h1>Payment Successful!</h1>
        <p class="success-message">
            Thank you for upgrading to Stock Scanner Pro! Your payment has been processed successfully.
        </p>
        
        <?php if ($order_id): ?>
            <div class="order-details">
                <h2>Order Confirmation</h2>
                <div class="order-info">
                    <div class="info-row">
                        <span class="label">Order ID:</span>
                        <span class="value"><?php echo esc_html($order_id); ?></span>
                    </div>
                    <div class="info-row">
                        <span class="label">Plan:</span>
                        <span class="value"><?php echo esc_html($plan_names[$membership_plan]); ?></span>
                    </div>
                    <div class="info-row">
                        <span class="label">Billing:</span>
                        <span class="value"><?php echo ucfirst($billing_cycle); ?></span>
                    </div>
                    <div class="info-row">
                        <span class="label">Customer:</span>
                        <span class="value"><?php echo esc_html($user->display_name); ?></span>
                    </div>
                    <div class="info-row">
                        <span class="label">Email:</span>
                        <span class="value"><?php echo esc_html($user->user_email); ?></span>
                    </div>
                </div>
            </div>
        <?php endif; ?>
        
        <div class="next-steps">
            <h2>What's Next?</h2>
            <div class="steps-grid">
                <div class="step-item">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <h3>Access Your Dashboard</h3>
                        <p>Your upgraded features are now active. Visit your dashboard to start exploring.</p>
                        <a href="<?php echo home_url('/dashboard/'); ?>" class="btn btn-primary">Go to Dashboard</a>
                    </div>
                </div>
                
                <div class="step-item">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <h3>Explore Advanced Features</h3>
                        <p>Check out the stock screener with your new filters and enhanced capabilities.</p>
                        <a href="<?php echo home_url('/stock-screener/'); ?>" class="btn btn-outline">Stock Screener</a>
                    </div>
                </div>
                
                <div class="step-item">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <h3>Manage Your Account</h3>
                        <p>Update your preferences and view your subscription details.</p>
                        <a href="<?php echo home_url('/user-settings/'); ?>" class="btn btn-outline">Account Settings</a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="feature-highlights">
            <h2>Your New Features</h2>
            <div class="features-grid">
                <?php if ($membership_plan === 'bronze'): ?>
                    <div class="feature-card">
                        <div class="feature-icon"></div>
                        <h3>Advanced Screening</h3>
                        <p>Access 25+ technical indicators and advanced filters</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon"></div>
                        <h3>5 Portfolios</h3>
                        <p>Track multiple investment strategies simultaneously</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔔</div>
                        <h3>25 Price Alerts</h3>
                        <p>Get notified when stocks hit your target prices</p>
                    </div>
                <?php elseif ($membership_plan === 'silver'): ?>
                    <div class="feature-card">
                        <div class="feature-icon"></div>
                        <h3>Real-time Data</h3>
                        <p>Live market data with no delays</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon"></div>
                        <h3>Unlimited Portfolios</h3>
                        <p>Create as many portfolios as you need</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔔</div>
                        <h3>100 Price Alerts</h3>
                        <p>Advanced alerting system with SMS notifications</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔌</div>
                        <h3>REST API Access</h3>
                        <p>Integrate our data with your applications</p>
                    </div>
                <?php elseif ($membership_plan === 'gold'): ?>
                    <div class="feature-card">
                        <div class="feature-icon">🌍</div>
                        <h3>Global Markets</h3>
                        <p>Access international stock markets worldwide</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon"></div>
                        <h3>Priority Support</h3>
                        <p>Dedicated support team for immediate assistance</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔧</div>
                        <h3>White Label</h3>
                        <p>Custom branding options for professional use</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon"></div>
                        <h3>WebSocket API</h3>
                        <p>Real-time streaming data integration</p>
                    </div>
                <?php endif; ?>
            </div>
        </div>
        
        <div class="support-section">
            <h2>Need Help?</h2>
            <p>Our support team is here to help you get the most out of your new plan.</p>
            <div class="support-options">
                <a href="<?php echo home_url('/help-center/'); ?>" class="support-link">
                    <span class="support-icon">📚</span>
                    <span>Help Center</span>
                </a>
                <a href="<?php echo home_url('/contact/'); ?>" class="support-link">
                    <span class="support-icon">💬</span>
                    <span>Contact Support</span>
                </a>
                <a href="<?php echo home_url('/getting-started/'); ?>" class="support-link">
                    <span class="support-icon"></span>
                    <span>Getting Started Guide</span>
                </a>
            </div>
        </div>
        
        <div class="receipt-notice">
            <h3>📧 Receipt & Billing</h3>
            <p>A payment receipt has been sent to your email address. You can also view your billing history and manage your subscription in your account settings.</p>
            <a href="<?php echo home_url('/billing-history/'); ?>" class="btn btn-outline">View Billing History</a>
        </div>
    </div>
</div>

<style>
.payment-success-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 40px 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.success-content {
    text-align: center;
}

.success-icon {
    margin-bottom: 30px;
}

.checkmark-circle {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: linear-gradient(135deg, #27ae60, #2ecc71);
    margin: 0 auto;
    position: relative;
    animation: scaleIn 0.6s ease-in-out;
}

@keyframes scaleIn {
    0% { transform: scale(0); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

.checkmark {
    width: 30px;
    height: 15px;
    border-left: 4px solid white;
    border-bottom: 4px solid white;
    transform: rotate(-45deg);
    position: absolute;
    top: 50%;
    left: 50%;
    margin-top: -10px;
    margin-left: -15px;
    animation: drawCheck 0.3s ease-in-out 0.3s both;
}

@keyframes drawCheck {
    0% { width: 0; height: 0; }
    50% { width: 30px; height: 0; }
    100% { width: 30px; height: 15px; }
}

.success-content h1 {
    font-size: 2.5rem;
    color: #2c3e50;
    margin: 0 0 20px 0;
    font-weight: 600;
}

.success-message {
    font-size: 1.2rem;
    color: #7f8c8d;
    margin-bottom: 40px;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.order-details {
    background: white;
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 40px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
    text-align: left;
}

.order-details h2 {
    margin: 0 0 25px 0;
    color: #2c3e50;
    font-size: 1.5rem;
    text-align: center;
}

.order-info {
    display: grid;
    gap: 15px;
}

.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #ecf0f1;
}

.info-row:last-child {
    border-bottom: none;
}

.info-row .label {
    font-weight: 600;
    color: #7f8c8d;
}

.info-row .value {
    font-weight: 500;
    color: #2c3e50;
}

.next-steps {
    margin-bottom: 50px;
}

.next-steps h2 {
    margin: 0 0 30px 0;
    color: #2c3e50;
    font-size: 2rem;
}

.steps-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    margin-top: 30px;
}

.step-item {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
    text-align: left;
    position: relative;
}

.step-number {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.2rem;
    margin-bottom: 20px;
}

.step-content h3 {
    margin: 0 0 15px 0;
    color: #2c3e50;
    font-size: 1.3rem;
}

.step-content p {
    color: #7f8c8d;
    margin-bottom: 20px;
    line-height: 1.6;
}

.feature-highlights {
    margin-bottom: 50px;
}

.feature-highlights h2 {
    margin: 0 0 30px 0;
    color: #2c3e50;
    font-size: 2rem;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 25px;
    margin-top: 30px;
}

.feature-card {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
    text-align: center;
    transition: transform 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 15px;
}

.feature-card h3 {
    margin: 0 0 10px 0;
    color: #2c3e50;
    font-size: 1.2rem;
}

.feature-card p {
    color: #7f8c8d;
    margin: 0;
    line-height: 1.5;
}

.support-section {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 40px;
    margin-bottom: 40px;
}

.support-section h2 {
    margin: 0 0 15px 0;
    color: #2c3e50;
    font-size: 1.8rem;
}

.support-section p {
    color: #7f8c8d;
    margin-bottom: 25px;
    font-size: 1.1rem;
}

.support-options {
    display: flex;
    justify-content: center;
    gap: 30px;
    flex-wrap: wrap;
}

.support-link {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 20px;
    background: white;
    border-radius: 8px;
    text-decoration: none;
    color: #2c3e50;
    transition: all 0.3s ease;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.support-link:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 20px rgba(0,0,0,0.15);
    text-decoration: none;
    color: #3498db;
}

.support-icon {
    font-size: 1.8rem;
}

.receipt-notice {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
}

.receipt-notice h3 {
    margin: 0 0 15px 0;
    color: #2c3e50;
    font-size: 1.3rem;
}

.receipt-notice p {
    color: #7f8c8d;
    margin-bottom: 20px;
    line-height: 1.6;
}

.btn {
    display: inline-block;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
    font-size: 1rem;
}

.btn-primary {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
}

.btn-primary:hover {
    background: linear-gradient(135deg, #2980b9, #21618c);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
    text-decoration: none;
    color: white;
}

.btn-outline {
    background: transparent;
    color: #3498db;
    border: 2px solid #3498db;
}

.btn-outline:hover {
    background: #3498db;
    color: white;
    transform: translateY(-2px);
    text-decoration: none;
}

@media (max-width: 768px) {
    .payment-success-container {
        padding: 20px 10px;
    }
    
    .steps-grid, .features-grid {
        grid-template-columns: 1fr;
    }
    
    .support-options {
        flex-direction: column;
        gap: 15px;
    }
    
    .order-details, .step-item, .feature-card, .support-section, .receipt-notice {
        padding: 20px;
    }
    
    .success-content h1 {
        font-size: 2rem;
    }
    
    .next-steps h2, .feature-highlights h2 {
        font-size: 1.5rem;
    }
}
</style>

<?php get_footer(); ?>