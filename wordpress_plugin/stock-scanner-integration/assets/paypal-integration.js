/**
 * PayPal Integration JavaScript
 * 
 * Handles PayPal payment buttons and checkout flow
 * 
 * @package StockScannerIntegration
 * @since 1.0.0
 */

(function($) {
    'use strict';
    
    class StockScannerPayPal {
        constructor() {
            this.init();
        }
        
        init() {
            this.loadPayPalSDK();
            this.bindEvents();
        }
        
        /**
         * Load PayPal SDK
         */
        loadPayPalSDK() {
            const script = document.createElement('script');
            script.src = 'https://www.paypal.com/sdk/js?client-id=' + paypalConfig.clientId + '&currency=USD';
            script.onload = () => {
                this.initPayPalButtons();
            };
            document.head.appendChild(script);
        }
        
        /**
         * Initialize PayPal buttons
         */
        initPayPalButtons() {
            if (typeof paypal !== 'undefined') {
                paypal.Buttons({
                    createOrder: (data, actions) => {
                        return this.createOrder(data, actions);
                    },
                    onApprove: (data, actions) => {
                        return this.onApprove(data, actions);
                    },
                    onError: (err) => {
                        this.handleError(err);
                    }
                }).render('#paypal-button-container');
            }
        }
        
        /**
         * Create PayPal order
         */
        createOrder(data, actions) {
            const plan = $('#membership-plan').val();
            const billingCycle = $('#billing-cycle').val();
            
            return new Promise((resolve, reject) => {
                $.ajax({
                    url: paypalConfig.ajaxUrl,
                    type: 'POST',
                    data: {
                        action: 'create_paypal_order',
                        plan: plan,
                        billing_cycle: billingCycle,
                        nonce: paypalConfig.nonce
                    },
                    success: (response) => {
                        if (response.success) {
                            resolve(response.data.order_id);
                        } else {
                            reject(new Error('Failed to create order'));
                        }
                    },
                    error: (xhr, status, error) => {
                        reject(new Error('AJAX error: ' + error));
                    }
                });
            });
        }
        
        /**
         * Handle PayPal approval
         */
        onApprove(data, actions) {
            return new Promise((resolve, reject) => {
                $.ajax({
                    url: paypalConfig.ajaxUrl,
                    type: 'POST',
                    data: {
                        action: 'capture_paypal_order',
                        order_id: data.orderID,
                        nonce: paypalConfig.nonce
                    },
                    success: (response) => {
                        if (response.success) {
                            this.showSuccessMessage('Payment completed successfully!');
                            setTimeout(() => {
                                window.location.href = paypalConfig.successUrl;
                            }, 2000);
                            resolve();
                        } else {
                            this.showErrorMessage('Payment failed. Please try again.');
                            reject(new Error('Payment failed'));
                        }
                    },
                    error: (xhr, status, error) => {
                        this.showErrorMessage('Payment error: ' + error);
                        reject(new Error('AJAX error: ' + error));
                    }
                });
            });
        }
        
        /**
         * Handle PayPal errors
         */
        handleError(err) {
            console.error('PayPal error:', err);
            this.showErrorMessage('PayPal error occurred. Please try again.');
        }
        
        /**
         * Show success message
         */
        showSuccessMessage(message) {
            this.showMessage(message, 'success');
        }
        
        /**
         * Show error message
         */
        showErrorMessage(message) {
            this.showMessage(message, 'error');
        }
        
        /**
         * Show message
         */
        showMessage(message, type) {
            const messageClass = type === 'success' ? 'alert-success' : 'alert-danger';
            const messageHtml = `
                <div class="alert ${messageClass} alert-dismissible fade show" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            
            $('#paypal-messages').html(messageHtml);
        }
        
        /**
         * Bind events
         */
        bindEvents() {
            // Plan selection
            $('.plan-selector').on('change', function() {
                const plan = $(this).val();
                const billingCycle = $('#billing-cycle').val();
                updatePlanDisplay(plan, billingCycle);
            });
            
            // Billing cycle selection
            $('.billing-cycle-selector').on('change', function() {
                const plan = $('#membership-plan').val();
                const billingCycle = $(this).val();
                updatePlanDisplay(plan, billingCycle);
            });
            
            // Manual payment form
            $('#manual-payment-form').on('submit', function(e) {
                e.preventDefault();
                processManualPayment();
            });
        }
    }
    
    /**
     * Update plan display
     */
    function updatePlanDisplay(plan, billingCycle) {
        const prices = {
            'bronze_monthly': 14.99,
            'bronze_annual': 143.88,
            'silver_monthly': 29.99,
            'silver_annual': 287.88,
            'gold_monthly': 59.99,
            'gold_annual': 575.88
        };
        
        const key = plan + '_' + billingCycle;
        const price = prices[key] || 0;
        
        $('#plan-price').text('$' + price.toFixed(2));
        $('#plan-name').text(plan.charAt(0).toUpperCase() + plan.slice(1) + ' ' + 
                           billingCycle.charAt(0).toUpperCase() + billingCycle.slice(1));
    }
    
    /**
     * Process manual payment
     */
    function processManualPayment() {
        const formData = $('#manual-payment-form').serialize();
        
        $.ajax({
            url: paypalConfig.ajaxUrl,
            type: 'POST',
            data: formData + '&action=create_paypal_order&nonce=' + paypalConfig.nonce,
            success: (response) => {
                if (response.success) {
                    window.location.href = response.data.approval_url;
                } else {
                    showMessage('Failed to create payment. Please try again.', 'error');
                }
            },
            error: (xhr, status, error) => {
                showMessage('Payment error: ' + error, 'error');
            }
        });
    }
    
    /**
     * Show message
     */
    function showMessage(message, type) {
        const messageClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const messageHtml = `
            <div class="alert ${messageClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        $('#payment-messages').html(messageHtml);
    }
    
    /**
     * Initialize when document is ready
     */
    $(document).ready(function() {
        if (typeof paypalConfig !== 'undefined') {
            new StockScannerPayPal();
        }
    });
    
})(jQuery);