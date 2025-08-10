<?php
/**
 * Template Name: Payment Cancelled
 * Displays when user cancels payment
 */

// Security check
if (!defined('ABSPATH')) {
    exit;
}

get_header();
?>

<div class="payment-cancelled-container">
    <div class="cancelled-content">
        <div class="cancelled-icon">
            <div class="cancel-circle">
                <div class="cancel-x">✕</div>
            </div>
        </div>
        
        <h1>Payment Cancelled</h1>
        <p class="cancelled-message">
            Your payment has been cancelled. No charges have been made to your account.
        </p>
        
        <div class="reason-section">
            <h2>What happened?</h2>
            <div class="reason-grid">
                <div class="reason-item">
                    <div class="reason-icon">🔄</div>
                    <h3>Payment Cancelled</h3>
                    <p>You chose to cancel the payment process before completion.</p>
                </div>
                <div class="reason-item">
                    <div class="reason-icon">💳</div>
                    <h3>No Charges Made</h3>
                    <p>Your payment method has not been charged and no transaction occurred.</p>
                </div>
                <div class="reason-item">
                    <div class="reason-icon">🔒</div>
                    <h3>Account Unchanged</h3>
                    <p>Your current membership plan and benefits remain the same.</p>
                </div>
            </div>
        </div>
        
        <div class="retry-section">
            <h2>Want to try again?</h2>
            <p>You can always upgrade your plan later or try a different payment method.</p>
            
            <div class="action-buttons">
                <a href="<?php echo home_url('/compare-plans/'); ?>" class="btn btn-primary">
                    <span class="btn-icon">📊</span>
                    View Plans Again
                </a>
                <a href="<?php echo home_url('/dashboard/'); ?>" class="btn btn-outline">
                    <span class="btn-icon">🏠</span>
                    Go to Dashboard
                </a>
            </div>
        </div>
        
        <div class="help-section">
            <h2>Need Help?</h2>
            <p>If you encountered any issues during checkout, our support team is here to help.</p>
            
            <div class="help-options">
                <a href="<?php echo home_url('/contact/'); ?>" class="help-link">
                    <span class="help-icon">💬</span>
                    <div class="help-content">
                        <strong>Contact Support</strong>
                        <span>Get help with payment issues</span>
                    </div>
                </a>
                <a href="<?php echo home_url('/faq/'); ?>" class="help-link">
                    <span class="help-icon">❓</span>
                    <div class="help-content">
                        <strong>FAQ</strong>
                        <span>Common payment questions</span>
                    </div>
                </a>
                <a href="<?php echo home_url('/help-center/'); ?>" class="help-link">
                    <span class="help-icon">📚</span>
                    <div class="help-content">
                        <strong>Help Center</strong>
                        <span>Browse all help topics</span>
                    </div>
                </a>
            </div>
        </div>
        
        <div class="alternative-section">
            <h2>Alternative Options</h2>
            <div class="alternatives-grid">
                <div class="alternative-card">
                    <div class="alternative-icon">🆓</div>
                    <h3>Continue with Free Plan</h3>
                    <p>Keep using Stock Scanner with our free features while you decide.</p>
                    <ul>
                        <li>100 Monthly API Calls</li>
                        <li>1 Portfolio</li>
                        <li>10 Stocks per Watchlist</li>
                        <li>5 Price Alerts</li>
                    </ul>
                    <a href="<?php echo home_url('/dashboard/'); ?>" class="btn btn-outline btn-small">Continue Free</a>
                </div>
                
                <div class="alternative-card">
                    <div class="alternative-icon">📧</div>
                    <h3>Get Notified of Deals</h3>
                    <p>Stay informed about special promotions and discounts on our plans.</p>
                    <form class="newsletter-form" action="<?php echo admin_url('admin-ajax.php'); ?>" method="post">
                        <input type="hidden" name="action" value="subscribe_newsletter">
                        <input type="hidden" name="nonce" value="<?php echo wp_create_nonce('newsletter_nonce'); ?>">
                        <input type="email" name="email" placeholder="Your email address" required 
                               value="<?php echo is_user_logged_in() ? wp_get_current_user()->user_email : ''; ?>">
                        <button type="submit" class="btn btn-primary btn-small">Subscribe</button>
                    </form>
                </div>
                
                <div class="alternative-card">
                    <div class="alternative-icon">⏰</div>
                    <h3>Set a Reminder</h3>
                    <p>We can remind you to upgrade later when you're ready.</p>
                    <div class="reminder-options">
                        <button class="reminder-btn" onclick="setReminder(7)">
                            <span>Remind me in 1 week</span>
                        </button>
                        <button class="reminder-btn" onclick="setReminder(30)">
                            <span>Remind me in 1 month</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="feedback-section">
            <h2>Help Us Improve</h2>
            <p>Was there something that prevented you from completing your purchase? Your feedback helps us improve.</p>
            
            <form class="feedback-form" action="<?php echo admin_url('admin-ajax.php'); ?>" method="post">
                <input type="hidden" name="action" value="submit_cancellation_feedback">
                <input type="hidden" name="nonce" value="<?php echo wp_create_nonce('feedback_nonce'); ?>">
                
                <div class="feedback-options">
                    <label class="feedback-option">
                        <input type="radio" name="reason" value="too_expensive">
                        <span>Too expensive</span>
                    </label>
                    <label class="feedback-option">
                        <input type="radio" name="reason" value="payment_issues">
                        <span>Payment method issues</span>
                    </label>
                    <label class="feedback-option">
                        <input type="radio" name="reason" value="need_more_time">
                        <span>Need more time to decide</span>
                    </label>
                    <label class="feedback-option">
                        <input type="radio" name="reason" value="not_ready">
                        <span>Not ready to upgrade yet</span>
                    </label>
                    <label class="feedback-option">
                        <input type="radio" name="reason" value="other">
                        <span>Other reason</span>
                    </label>
                </div>
                
                <textarea name="comments" placeholder="Additional comments (optional)" rows="3"></textarea>
                
                <button type="submit" class="btn btn-outline">Submit Feedback</button>
            </form>
        </div>
    </div>
</div>

<style>
.payment-cancelled-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.cancelled-content {
    text-align: center;
}

.cancelled-icon {
    margin-bottom: 30px;
}

.cancel-circle {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: linear-gradient(135deg, #e74c3c, #c0392b);
    margin: 0 auto;
    position: relative;
    animation: scaleIn 0.6s ease-in-out;
    display: flex;
    align-items: center;
    justify-content: center;
}

@keyframes scaleIn {
    0% { transform: scale(0); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

.cancel-x {
    color: white;
    font-size: 2.5rem;
    font-weight: bold;
    line-height: 1;
}

.cancelled-content h1 {
    font-size: 2.5rem;
    color: #2c3e50;
    margin: 0 0 20px 0;
    font-weight: 600;
}

.cancelled-message {
    font-size: 1.2rem;
    color: #7f8c8d;
    margin-bottom: 50px;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.reason-section {
    margin-bottom: 50px;
}

.reason-section h2 {
    margin: 0 0 30px 0;
    color: #2c3e50;
    font-size: 2rem;
}

.reason-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 30px;
    margin-top: 30px;
}

.reason-item {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
}

.reason-icon {
    font-size: 2.5rem;
    margin-bottom: 20px;
}

.reason-item h3 {
    margin: 0 0 15px 0;
    color: #2c3e50;
    font-size: 1.3rem;
}

.reason-item p {
    color: #7f8c8d;
    margin: 0;
    line-height: 1.6;
}

.retry-section {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 40px;
    margin-bottom: 50px;
}

.retry-section h2 {
    margin: 0 0 15px 0;
    color: #2c3e50;
    font-size: 1.8rem;
}

.retry-section p {
    color: #7f8c8d;
    margin-bottom: 30px;
    font-size: 1.1rem;
}

.action-buttons {
    display: flex;
    justify-content: center;
    gap: 20px;
    flex-wrap: wrap;
}

.help-section {
    margin-bottom: 50px;
}

.help-section h2 {
    margin: 0 0 15px 0;
    color: #2c3e50;
    font-size: 1.8rem;
}

.help-section p {
    color: #7f8c8d;
    margin-bottom: 30px;
    font-size: 1.1rem;
}

.help-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

.help-link {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 20px;
    background: white;
    border-radius: 8px;
    text-decoration: none;
    color: #2c3e50;
    transition: all 0.3s ease;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
}

.help-link:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 20px rgba(0,0,0,0.15);
    text-decoration: none;
    color: #3498db;
}

.help-icon {
    font-size: 1.8rem;
    flex-shrink: 0;
}

.help-content {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.help-content strong {
    font-weight: 600;
    font-size: 1.1rem;
}

.help-content span {
    font-size: 0.9rem;
    color: #7f8c8d;
}

.alternative-section {
    margin-bottom: 50px;
}

.alternative-section h2 {
    margin: 0 0 30px 0;
    color: #2c3e50;
    font-size: 1.8rem;
}

.alternatives-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
}

.alternative-card {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
    text-align: left;
}

.alternative-icon {
    font-size: 2.5rem;
    margin-bottom: 20px;
}

.alternative-card h3 {
    margin: 0 0 15px 0;
    color: #2c3e50;
    font-size: 1.3rem;
}

.alternative-card p {
    color: #7f8c8d;
    margin-bottom: 20px;
    line-height: 1.6;
}

.alternative-card ul {
    list-style: none;
    padding: 0;
    margin: 0 0 25px 0;
}

.alternative-card li {
    padding: 5px 0;
    color: #7f8c8d;
    font-size: 0.9rem;
}

.alternative-card li:before {
    content: "✓ ";
    color: #27ae60;
    font-weight: bold;
    margin-right: 8px;
}

.newsletter-form {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.newsletter-form input[type="email"] {
    flex: 1;
    min-width: 200px;
    padding: 10px;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    font-size: 0.9rem;
}

.reminder-options {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.reminder-btn {
    background: white;
    border: 2px solid #e1e5e9;
    border-radius: 6px;
    padding: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;
}

.reminder-btn:hover {
    border-color: #3498db;
    background: #f8f9fa;
}

.feedback-section {
    background: white;
    border-radius: 12px;
    padding: 40px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    border: 1px solid #e1e5e9;
    text-align: left;
}

.feedback-section h2 {
    margin: 0 0 15px 0;
    color: #2c3e50;
    font-size: 1.5rem;
    text-align: center;
}

.feedback-section p {
    color: #7f8c8d;
    margin-bottom: 25px;
    text-align: center;
}

.feedback-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 25px;
}

.feedback-option {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    padding: 10px;
    border-radius: 6px;
    transition: background 0.3s ease;
}

.feedback-option:hover {
    background: #f8f9fa;
}

.feedback-option input[type="radio"] {
    margin: 0;
}

.feedback-form textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    margin-bottom: 20px;
    resize: vertical;
    font-family: inherit;
}

.btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
    font-size: 1rem;
}

.btn-small {
    padding: 8px 16px;
    font-size: 0.9rem;
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

.btn-icon {
    font-size: 1.1rem;
}

@media (max-width: 768px) {
    .payment-cancelled-container {
        padding: 20px 10px;
    }
    
    .reason-grid, .alternatives-grid, .help-options {
        grid-template-columns: 1fr;
    }
    
    .action-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .action-buttons .btn {
        width: 100%;
        max-width: 300px;
    }
    
    .newsletter-form {
        flex-direction: column;
    }
    
    .newsletter-form input[type="email"] {
        min-width: auto;
    }
    
    .feedback-options {
        grid-template-columns: 1fr;
    }
    
    .cancelled-content h1 {
        font-size: 2rem;
    }
    
    .reason-section h2, .retry-section h2, .help-section h2, .alternative-section h2 {
        font-size: 1.5rem;
    }
}
</style>

<script>
function setReminder(days) {
    const data = new FormData();
    data.append('action', 'set_upgrade_reminder');
    data.append('days', days);
    data.append('nonce', '<?php echo wp_create_nonce('reminder_nonce'); ?>');
    
    fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
        method: 'POST',
        body: data
    }).then(response => response.json())
    .then(result => {
        if (result.success) {
            alert(`Reminder set! We'll email you in ${days} days.`);
        } else {
            alert('Error setting reminder. Please try again.');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Error setting reminder. Please try again.');
    });
}

// Handle newsletter form
document.querySelector('.newsletter-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const button = this.querySelector('button[type="submit"]');
    const originalText = button.textContent;
    
    button.textContent = 'Subscribing...';
    button.disabled = true;
    
    fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Successfully subscribed to notifications!');
            this.reset();
        } else {
            alert(result.data || 'Error subscribing. Please try again.');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Error subscribing. Please try again.');
    }).finally(() => {
        button.textContent = originalText;
        button.disabled = false;
    });
});

// Handle feedback form
document.querySelector('.feedback-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const button = this.querySelector('button[type="submit"]');
    const originalText = button.textContent;
    
    button.textContent = 'Submitting...';
    button.disabled = true;
    
    fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Thank you for your feedback!');
            this.reset();
        } else {
            alert('Error submitting feedback. Please try again.');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert('Error submitting feedback. Please try again.');
    }).finally(() => {
        button.textContent = originalText;
        button.disabled = false;
    });
});
</script>

<?php get_footer(); ?>