<?php
/*
Template Name: Compare Plans
Description: Side-by-side plan comparison with detailed feature matrix
*/

get_header(); ?>

<div class="container mx-auto p-6">
    <div class="page-header text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Compare Our Plans</h1>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">Choose the perfect plan for your stock analysis needs. All plans include our core features with varying limits and advanced capabilities.</p>
    </div>

    <!-- Plan Toggle -->
    <div class="flex justify-center mb-8">
        <div class="bg-gray-100 p-1 rounded-lg">
            <button id="monthly-toggle" class="px-6 py-2 rounded-md font-medium transition-all duration-200 bg-white text-gray-900 shadow-sm">Monthly</button>
            <button id="annual-toggle" class="px-6 py-2 rounded-md font-medium transition-all duration-200 text-gray-600 hover:text-gray-900">Annual <span class="text-green-600 text-sm">(Save 20%)</span></button>
        </div>
    </div>

    <!-- Plans Comparison Table -->
    <div class="card p-6 mb-8">
        <div class="overflow-x-auto">
            <table class="w-full comparison-table">
                <thead>
                    <tr>
                        <th class="feature-column">Features</th>
                        <th class="plan-column free-plan">
                            <div class="plan-header">
                                <h3 class="text-lg font-bold text-gray-900">Free</h3>
                                <div class="price-display">
                                    <span class="price">$0</span>
                                    <span class="period">/month</span>
                                </div>
                                <button class="btn btn-outline w-full mt-4" onclick="selectPlan('free')">Current Plan</button>
                            </div>
                        </th>
                        <th class="plan-column bronze-plan">
                            <div class="plan-header">
                                <h3 class="text-lg font-bold text-gray-900">Bronze</h3>
                                <div class="price-display">
                                    <span class="price monthly-price">$24.99</span>
                                    <span class="price annual-price" style="display: none;">$19.99</span>
                                    <span class="period">/month</span>
                                </div>
                                <p class="annual-savings" style="display: none;">$60 saved annually</p>
                                <button class="btn btn-primary w-full mt-4" onclick="selectPlan('bronze')">Upgrade to Bronze</button>
                            </div>
                        </th>
                        <th class="plan-column silver-plan popular">
                            <div class="popular-badge">Most Popular</div>
                            <div class="plan-header">
                                <h3 class="text-lg font-bold text-gray-900">Silver</h3>
                                <div class="price-display">
                                    <span class="price monthly-price">$39.99</span>
                                    <span class="price annual-price" style="display: none;">$31.99</span>
                                    <span class="period">/month</span>
                                </div>
                                <p class="annual-savings" style="display: none;">$96 saved annually</p>
                                <button class="btn btn-primary w-full mt-4" onclick="selectPlan('silver')">Upgrade to Silver</button>
                            </div>
                        </th>
                        <th class="plan-column gold-plan">
                            <div class="plan-header">
                                <h3 class="text-lg font-bold text-gray-900">Gold</h3>
                                <div class="price-display">
                                    <span class="price monthly-price">$89.99</span>
                                    <span class="price annual-price" style="display: none;">$71.99</span>
                                    <span class="period">/month</span>
                                </div>
                                <p class="annual-savings" style="display: none;">$216 saved annually</p>
                                <button class="btn btn-primary w-full mt-4" onclick="selectPlan('gold')">Upgrade to Gold</button>
                            </div>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <!-- API Access -->
                    <tr class="feature-category">
                        <td colspan="5" class="category-header">API Access & Data</td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Monthly API Calls</td>
                        <td class="feature-value">100</td>
                        <td class="feature-value">1,500</td>
                        <td class="feature-value">5,000</td>
                        <td class="feature-value">Unlimited</td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Real-time Data</td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value"><span class="feature-limited">15-min delay</span></td>
                        <td class="feature-value"><span class="feature-yes">✓</span></td>
                        <td class="feature-value"><span class="feature-yes">✓</span></td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Historical Data Access</td>
                        <td class="feature-value"><span class="feature-limited">1 year</span></td>
                        <td class="feature-value"><span class="feature-limited">3 years</span></td>
                        <td class="feature-value"><span class="feature-limited">5 years</span></td>
                        <td class="feature-value"><span class="feature-yes">Unlimited</span></td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">International Markets</td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value"><span class="feature-limited">US Only</span></td>
                        <td class="feature-value"><span class="feature-limited">US + Canada</span></td>
                        <td class="feature-value"><span class="feature-yes">Global</span></td>
                    </tr>

                    <!-- Portfolio & Watchlists -->
                    <tr class="feature-category">
                        <td colspan="5" class="category-header">Portfolio & Watchlists</td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Portfolios</td>
                        <td class="feature-value">1</td>
                        <td class="feature-value">5</td>
                        <td class="feature-value">Unlimited</td>
                        <td class="feature-value">Unlimited</td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Stocks per Watchlist</td>
                        <td class="feature-value">10</td>
                        <td class="feature-value">50</td>
                        <td class="feature-value">200</td>
                        <td class="feature-value">Unlimited</td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Portfolio Tracking</td>
                        <td class="feature-value"><span class="feature-limited">Basic</span></td>
                        <td class="feature-value"><span class="feature-yes">Advanced</span></td>
                        <td class="feature-value"><span class="feature-yes">Advanced</span></td>
                        <td class="feature-value"><span class="feature-yes">Professional</span></td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Performance Analytics</td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value"><span class="feature-limited">Basic</span></td>
                        <td class="feature-value"><span class="feature-yes">Advanced</span></td>
                        <td class="feature-value"><span class="feature-yes">Professional</span></td>
                    </tr>

                    <!-- Screening & Analysis -->
                    <tr class="feature-category">
                        <td colspan="5" class="category-header">Screening & Analysis</td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Stock Screener</td>
                        <td class="feature-value"><span class="feature-limited">Basic</span></td>
                        <td class="feature-value"><span class="feature-yes">Advanced</span></td>
                        <td class="feature-value"><span class="feature-yes">Advanced</span></td>
                        <td class="feature-value"><span class="feature-yes">Professional</span></td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Technical Indicators</td>
                        <td class="feature-value">5</td>
                        <td class="feature-value">25</td>
                        <td class="feature-value">50</td>
                        <td class="feature-value">100+</td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Custom Screeners</td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value">3</td>
                        <td class="feature-value">10</td>
                        <td class="feature-value">Unlimited</td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Backtesting</td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value"><span class="feature-limited">Basic</span></td>
                        <td class="feature-value"><span class="feature-yes">Advanced</span></td>
                    </tr>

                    <!-- Alerts & Notifications -->
                    <tr class="feature-category">
                        <td colspan="5" class="category-header">Alerts & Notifications</td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Price Alerts</td>
                        <td class="feature-value">5</td>
                        <td class="feature-value">25</td>
                        <td class="feature-value">100</td>
                        <td class="feature-value">Unlimited</td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Email Notifications</td>
                        <td class="feature-value"><span class="feature-yes">✓</span></td>
                        <td class="feature-value"><span class="feature-yes">✓</span></td>
                        <td class="feature-value"><span class="feature-yes">✓</span></td>
                        <td class="feature-value"><span class="feature-yes">✓</span></td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">SMS Notifications</td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value"><span class="feature-yes">✓</span></td>
                        <td class="feature-value"><span class="feature-yes">✓</span></td>
                        <td class="feature-value"><span class="feature-yes">✓</span></td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Push Notifications</td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value"><span class="feature-yes">✓</span></td>
                        <td class="feature-value"><span class="feature-yes">✓</span></td>
                    </tr>

                    <!-- Support & Features -->
                    <tr class="feature-category">
                        <td colspan="5" class="category-header">Support & Additional Features</td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Customer Support</td>
                        <td class="feature-value"><span class="feature-limited">Community</span></td>
                        <td class="feature-value"><span class="feature-limited">Email</span></td>
                        <td class="feature-value"><span class="feature-yes">Email + Chat</span></td>
                        <td class="feature-value"><span class="feature-yes">Priority Support</span></td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">API Access</td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value"><span class="feature-limited">REST API</span></td>
                        <td class="feature-value"><span class="feature-yes">REST + WebSocket</span></td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">Export Data</td>
                        <td class="feature-value"><span class="feature-limited">CSV</span></td>
                        <td class="feature-value"><span class="feature-limited">CSV</span></td>
                        <td class="feature-value"><span class="feature-yes">CSV + PDF</span></td>
                        <td class="feature-value"><span class="feature-yes">All Formats</span></td>
                    </tr>
                    <tr class="feature-row">
                        <td class="feature-name">White Label</td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value"><span class="feature-no">✗</span></td>
                        <td class="feature-value"><span class="feature-yes">✓</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- FAQ Section -->
    <div class="card p-6">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h2>
        <div class="space-y-4">
            <div class="faq-item">
                <button class="faq-question w-full text-left p-4 bg-gray-50 rounded-lg font-medium hover:bg-gray-100">
                    Can I switch plans at any time?
                    <span class="float-right">+</span>
                </button>
                <div class="faq-answer hidden p-4 text-gray-600">
                    Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately for upgrades, and at the end of your billing cycle for downgrades.
                </div>
            </div>
            <div class="faq-item">
                <button class="faq-question w-full text-left p-4 bg-gray-50 rounded-lg font-medium hover:bg-gray-100">
                    What happens if I exceed my API limits?
                    <span class="float-right">+</span>
                </button>
                <div class="faq-answer hidden p-4 text-gray-600">
                    If you reach your monthly API limit, we'll send you a notification. You can either upgrade your plan for immediate access or wait until your limits reset next month.
                </div>
            </div>
            <div class="faq-item">
                <button class="faq-question w-full text-left p-4 bg-gray-50 rounded-lg font-medium hover:bg-gray-100">
                    Do you offer refunds?
                    <span class="float-right">+</span>
                </button>
                <div class="faq-answer hidden p-4 text-gray-600">
                    Refunds are not guaranteed. Start with the trial and cancel anytime before renewal. Contact support with any questions.
                </div>
            </div>
        </div>
    </div>
</div>

<style>
/* Plan Comparison Specific Styles */
.comparison-table {
    border-collapse: separate;
    border-spacing: 0;
}

.feature-column {
    width: 30%;
    padding: var(--space-4);
    text-align: left;
    font-weight: 600;
    color: var(--color-text);
    border-bottom: 1px solid var(--color-border);
    background: var(--color-surface);
}

.plan-column {
    width: 17.5%;
    padding: var(--space-4);
    text-align: center;
    border-bottom: 1px solid var(--color-border);
    border-left: 1px solid var(--color-border);
    background: var(--color-surface);
    position: relative;
}

.plan-column.popular {
    border: 2px solid var(--color-primary);
    background: rgba(37, 99, 235, 0.02);
}

.popular-badge {
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--color-primary);
    color: var(--color-primary-contrast);
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-lg);
    font-size: 12px;
    font-weight: 600;
}

.plan-header {
    padding: var(--space-4) 0;
}

.price-display {
    margin: var(--space-3) 0;
}

.price {
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-primary);
}

.period {
    font-size: 0.9rem;
    color: var(--color-text-muted);
}

.annual-savings {
    font-size: 0.8rem;
    color: var(--color-success);
    font-weight: 500;
    margin-top: var(--space-1);
}

.category-header {
    background: var(--color-primary);
    color: var(--color-primary-contrast);
    font-weight: 600;
    padding: var(--space-3) var(--space-4);
    text-align: center;
}

.feature-row {
    border-bottom: 1px solid var(--color-border);
}

.feature-name {
    padding: var(--space-3) var(--space-4);
    font-weight: 500;
    background: var(--color-surface);
}

.feature-value {
    padding: var(--space-3) var(--space-4);
    text-align: center;
    background: var(--color-surface);
    border-left: 1px solid var(--color-border);
}

.feature-yes {
    color: var(--color-success);
    font-weight: 600;
}

.feature-no {
    color: var(--color-danger);
    font-weight: 600;
}

.feature-limited {
    color: var(--color-warning);
    font-weight: 500;
}

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-3) var(--space-4);
    font-weight: 500;
    border-radius: var(--radius-md);
    transition: all 0.2s ease;
    border: none;
    cursor: pointer;
    text-decoration: none;
}

.btn-primary {
    background: var(--color-primary);
    color: var(--color-primary-contrast);
}

.btn-primary:hover {
    background: #1d4ed8;
    transform: translateY(-1px);
}

.btn-outline {
    background: transparent;
    color: var(--color-text);
    border: 1px solid var(--color-border);
}

.btn-outline:hover {
    background: var(--color-border);
}

.faq-item {
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    overflow: hidden;
}

.faq-question {
    background: none;
    border: none;
    width: 100%;
}

.faq-answer {
    border-top: 1px solid var(--color-border);
    background: var(--color-surface);
}

@media (max-width: 768px) {
    .comparison-table {
        font-size: 0.875rem;
    }
    
    .plan-column {
        width: 15%;
        padding: var(--space-2);
    }
    
    .feature-column {
        width: 40%;
        padding: var(--space-2);
    }
    
    .price {
        font-size: 1.5rem;
    }
    
    .btn {
        padding: var(--space-2) var(--space-3);
        font-size: 0.8rem;
    }
}
</style>

<script>
// Plan Comparison JavaScript
class PlanComparison {
    constructor() {
        this.isAnnual = false;
        this.initializeToggles();
        this.initializeFAQ();
    }
    
    initializeToggles() {
        document.getElementById('monthly-toggle').addEventListener('click', () => this.toggleBilling(false));
        document.getElementById('annual-toggle').addEventListener('click', () => this.toggleBilling(true));
    }
    
    toggleBilling(isAnnual) {
        this.isAnnual = isAnnual;
        
        // Update toggle buttons
        const monthlyBtn = document.getElementById('monthly-toggle');
        const annualBtn = document.getElementById('annual-toggle');
        
        if (isAnnual) {
            monthlyBtn.className = 'px-6 py-2 rounded-md font-medium transition-all duration-200 text-gray-600 hover:text-gray-900';
            annualBtn.className = 'px-6 py-2 rounded-md font-medium transition-all duration-200 bg-white text-gray-900 shadow-sm';
        } else {
            monthlyBtn.className = 'px-6 py-2 rounded-md font-medium transition-all duration-200 bg-white text-gray-900 shadow-sm';
            annualBtn.className = 'px-6 py-2 rounded-md font-medium transition-all duration-200 text-gray-600 hover:text-gray-900';
        }
        
        // Update prices
        document.querySelectorAll('.monthly-price').forEach(el => {
            el.style.display = isAnnual ? 'none' : 'inline';
        });
        
        document.querySelectorAll('.annual-price').forEach(el => {
            el.style.display = isAnnual ? 'inline' : 'none';
        });
        
        document.querySelectorAll('.annual-savings').forEach(el => {
            el.style.display = isAnnual ? 'block' : 'none';
        });
    }
    
    initializeFAQ() {
        document.querySelectorAll('.faq-question').forEach(question => {
            question.addEventListener('click', () => {
                const answer = question.nextElementSibling;
                const isOpen = !answer.classList.contains('hidden');
                
                // Close all other FAQ items
                document.querySelectorAll('.faq-answer').forEach(a => a.classList.add('hidden'));
                document.querySelectorAll('.faq-question span').forEach(s => s.textContent = '+');
                
                if (!isOpen) {
                    answer.classList.remove('hidden');
                    question.querySelector('span').textContent = '−';
                }
            });
        });
    }
}

// Initialize plan comparison
const planComparison = new PlanComparison();

// Plan selection function
function selectPlan(plan) {
    console.log('Selected plan:', plan);
    
    if (plan === 'free') {
        alert('You are already on the Free plan!');
        return;
    }
    
    // Check if user is logged in
    <?php if (!is_user_logged_in()): ?>
        // Redirect to login/signup if not logged in
        const loginUrl = '<?php echo wp_login_url(); ?>';
        window.location.href = loginUrl + '&redirect_to=' + encodeURIComponent(window.location.href);
        return;
    <?php endif; ?>
    
    const billingType = planComparison.isAnnual ? 'annual' : 'monthly';
    const planName = plan.charAt(0).toUpperCase() + plan.slice(1);
    
    // Redirect to PayPal checkout page with plan parameters
    const checkoutUrl = `/paypal-checkout/?plan=${plan}&billing=${billingType}`;
    window.location.href = checkoutUrl;
}
</script>

<?php get_footer(); ?>