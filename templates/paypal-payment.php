<?php
/**
 * PayPal Payment Template
 * 
 * Template for PayPal payment processing
 * 
 * @package StockScannerIntegration
 * @since 1.0.0
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}
?>

<div class="paypal-payment-container">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h3 class="mb-0">
                            <i class="fab fa-paypal"></i> PayPal Checkout
                        </h3>
                    </div>
                    <div class="card-body">
                        
                        <!-- Plan Selection -->
                        <div class="row mb-4">
                            <div class="col-md-6">
                                <label for="membership-plan" class="form-label">Select Plan</label>
                                                                    <select id="membership-plan" class="form-select plan-selector">
                                        <option value="bronze">Bronze Plan</option>
                                        <option value="silver">Silver Plan</option>
                                        <option value="gold">Gold Plan</option>
                                    </select>
                            </div>
                            <div class="col-md-6">
                                <label for="billing-cycle" class="form-label">Billing Cycle</label>
                                <select id="billing-cycle" class="form-select billing-cycle-selector">
                                    <option value="monthly">Monthly</option>
                                    <option value="annual">Annual (Save 20%)</option>
                                </select>
                            </div>
                        </div>
                        
                        <!-- Plan Details -->
                        <div class="plan-details mb-4">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h5 class="card-title">
                                        <span id="plan-name">Bronze Monthly</span>
                                    </h5>
                                    <div class="price-display">
                                        <span class="h3 text-primary">$<span id="plan-price">14.99</span></span>
                                        <span class="text-muted" id="billing-period">/month</span>
                                    </div>
                                    <div class="plan-features mt-3">
                                        <ul class="list-unstyled">
                                            <li><i class="fas fa-check text-success"></i> Real-time stock data</li>
                                            <li><i class="fas fa-check text-success"></i> Advanced scanning tools</li>
                                            <li><i class="fas fa-check text-success"></i> Email alerts</li>
                                            <li><i class="fas fa-check text-success"></i> Priority support</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- PayPal Messages -->
                        <div id="paypal-messages"></div>
                        
                        <!-- PayPal Button Container -->
                        <div class="paypal-button-container mb-4">
                            <div id="paypal-button-container"></div>
                        </div>
                        
                        <!-- Alternative Payment Methods -->
                        <div class="alternative-payment">
                            <div class="text-center">
                                <p class="text-muted">Or use alternative payment methods:</p>
                                <div class="btn-group" role="group">
                                    <button type="button" class="btn btn-outline-primary" onclick="showManualPayment()">
                                        <i class="fas fa-credit-card"></i> Credit Card
                                    </button>
                                    <button type="button" class="btn btn-outline-success" onclick="showBankTransfer()">
                                        <i class="fas fa-university"></i> Bank Transfer
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Manual Payment Form (Hidden by default) -->
                        <div id="manual-payment-form" style="display: none;">
                            <div class="card">
                                <div class="card-header">
                                    <h5>Manual Payment</h5>
                                </div>
                                <div class="card-body">
                                    <form id="payment-form">
                                        <div class="row">
                                            <div class="col-md-6">
                                                <div class="mb-3">
                                                    <label for="card-name" class="form-label">Cardholder Name</label>
                                                    <input type="text" class="form-control" id="card-name" required>
                                                </div>
                                            </div>
                                            <div class="col-md-6">
                                                <div class="mb-3">
                                                    <label for="card-number" class="form-label">Card Number</label>
                                                    <input type="text" class="form-control" id="card-number" required>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-4">
                                                <div class="mb-3">
                                                    <label for="card-expiry" class="form-label">Expiry Date</label>
                                                    <input type="text" class="form-control" id="card-expiry" placeholder="MM/YY" required>
                                                </div>
                                            </div>
                                            <div class="col-md-4">
                                                <div class="mb-3">
                                                    <label for="card-cvv" class="form-label">CVV</label>
                                                    <input type="text" class="form-control" id="card-cvv" required>
                                                </div>
                                            </div>
                                            <div class="col-md-4">
                                                <div class="mb-3">
                                                    <label for="card-zip" class="form-label">ZIP Code</label>
                                                    <input type="text" class="form-control" id="card-zip" required>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="text-center">
                                            <button type="submit" class="btn btn-primary">
                                                <i class="fas fa-lock"></i> Secure Payment
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Payment Messages -->
                        <div id="payment-messages"></div>
                        
                        <!-- Security Notice -->
                        <div class="security-notice mt-4">
                            <div class="alert alert-info">
                                <i class="fas fa-shield-alt"></i>
                                <strong>Secure Payment:</strong> All payments are processed securely through PayPal. 
                                Your financial information is never stored on our servers.
                            </div>
                        </div>
                        
                        <!-- Terms and Conditions -->
                        <div class="terms-notice mt-3">
                            <small class="text-muted">
                                By completing your purchase, you agree to our 
                                <a href="/terms-of-service/" target="_blank">Terms of Service</a> and 
                                <a href="/privacy-policy/" target="_blank">Privacy Policy</a>.
                            </small>
                        </div>
                        
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.paypal-payment-container {
    padding: 2rem 0;
}

.plan-details .card {
    border: 2px solid #e9ecef;
    transition: border-color 0.3s ease;
}

.plan-details .card:hover {
    border-color: #007cba;
}

.price-display {
    text-align: center;
    margin: 1rem 0;
}

.plan-features ul li {
    margin-bottom: 0.5rem;
}

.plan-features ul li i {
    margin-right: 0.5rem;
}

.paypal-button-container {
    text-align: center;
    padding: 1rem;
    border: 1px solid #e9ecef;
    border-radius: 0.375rem;
    background-color: #f8f9fa;
}

.alternative-payment {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #e9ecef;
}

.security-notice .alert {
    border-left: 4px solid #007cba;
}

.terms-notice {
    text-align: center;
}

.terms-notice a {
    color: #007cba;
    text-decoration: none;
}

.terms-notice a:hover {
    text-decoration: underline;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .paypal-payment-container {
        padding: 1rem 0;
    }
    
    .btn-group {
        flex-direction: column;
    }
    
    .btn-group .btn {
        margin-bottom: 0.5rem;
    }
}
</style>

<script>
// Plan pricing data
const planPrices = {
    'bronze_monthly': 14.99,
    'bronze_annual': 143.88,
    'silver_monthly': 29.99,
    'silver_annual': 287.88,
    'gold_monthly': 59.99,
    'gold_annual': 575.88
};

// Update plan display when selections change
function updatePlanDisplay() {
    const plan = document.getElementById('membership-plan').value;
    const billingCycle = document.getElementById('billing-cycle').value;
    const key = plan + '_' + billingCycle;
    const price = planPrices[key] || 0;
    
    document.getElementById('plan-price').textContent = price.toFixed(2);
    document.getElementById('plan-name').textContent = 
        plan.charAt(0).toUpperCase() + plan.slice(1) + ' ' + 
        billingCycle.charAt(0).toUpperCase() + billingCycle.slice(1);
    
    document.getElementById('billing-period').textContent = 
        billingCycle === 'annual' ? '/year' : '/month';
}

// Show manual payment form
function showManualPayment() {
    document.getElementById('manual-payment-form').style.display = 'block';
    document.querySelector('.paypal-button-container').style.display = 'none';
}

// Show bank transfer info
function showBankTransfer() {
    alert('For bank transfer payments, please contact our support team at support@stockscanner.com');
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Update plan display on change
    document.getElementById('membership-plan').addEventListener('change', updatePlanDisplay);
    document.getElementById('billing-cycle').addEventListener('change', updatePlanDisplay);
    
    // Initialize plan display
    updatePlanDisplay();
});
</script>