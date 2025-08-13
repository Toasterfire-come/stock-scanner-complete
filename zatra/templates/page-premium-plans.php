<?php
/**
 * Template Name: Stock Scanner Pro - Premium Plans
 * 
 * Professional pricing page with Zatra theme styling
 */

get_header(); ?>

<main id="main" class="wp-block-group alignfull is-layout-constrained wp-block-group-is-layout-constrained" style="margin-top:0">
    
    <div class="wp-block-group__inner-container">
        <div class="container">
            <div class="premium-plans-page">
                
                <!-- Plans Header -->
                <div class="plans-header">
                    <h1 class="wp-block-heading has-text-align-center has-huge-font-size">Choose Your Plan</h1>
                    <p class="has-text-align-center has-medium-font-size">Unlock powerful features and get the data you need to make informed investment decisions</p>
                    
                    <div class="billing-toggle">
                        <span class="toggle-label">Monthly</span>
                        <label class="switch">
                            <input type="checkbox" id="billing-toggle">
                            <span class="slider"></span>
                        </label>
                        <span class="toggle-label">Yearly <span class="discount-badge">Save 10%</span></span>
                    </div>
                </div>

                <!-- Pricing Table -->
                <div class="pricing-table">
                    <?php 
                    $user_tier = get_user_tier();
                    $plans = array(
                        'free' => array(
                            'name' => 'Free',
                            'price_monthly' => 0,
                            'price_yearly' => 0,
                            'description' => 'Perfect for getting started',
                            'features' => array(
                                '15 API calls per month',
                                '3 watchlist items',
                                'Basic charts',
                                'Delayed market data',
                                'Email support'
                            ),
                            'unavailable' => array(
                                'Real-time data',
                                'Advanced charts',
                                'Data export'
                            )
                        ),
                        'basic' => array(
                            'name' => 'Basic',
                            'price_monthly' => 24.99,
                            'price_yearly' => 22.49,
                            'description' => 'Great for active traders',
                            'featured' => true,
                            'features' => array(
                                '1,500 API calls per month',
                                '25 watchlist items',
                                'Real-time market data',
                                'Advanced charts & indicators',
                                'Data export (CSV, Excel)',
                                'Price alerts',
                                'Priority email support'
                            ),
                            'unavailable' => array(
                                'API access'
                            )
                        ),
                        'pro' => array(
                            'name' => 'Pro',
                            'price_monthly' => 49.99,
                            'price_yearly' => 44.99,
                            'description' => 'For professional investors',
                            'features' => array(
                                '5,000 API calls per month',
                                '100 watchlist items',
                                'Everything in Basic',
                                'Full API access',
                                'Custom alerts & notifications',
                                'Advanced analytics',
                                'Portfolio optimization tools',
                                'Phone & chat support'
                            )
                        ),
                        'enterprise' => array(
                            'name' => 'Enterprise',
                            'price_monthly' => 79.99,
                            'price_yearly' => 71.99,
                            'description' => 'For institutions & power users',
                            'features' => array(
                                'Unlimited API calls',
                                'Unlimited watchlist items',
                                'Everything in Pro',
                                'White-label solutions',
                                'Custom integrations',
                                'Dedicated account manager',
                                'SLA guarantee',
                                '24/7 priority support'
                            )
                        )
                    );
                    
                    foreach ($plans as $tier => $plan):
                        $is_current = ($user_tier === $tier);
                        $is_featured = isset($plan['featured']) && $plan['featured'];
                    ?>
                        <!-- <?php echo ucfirst($tier); ?> Plan -->
                        <div class="pricing-card <?php echo $is_featured ? 'featured' : ''; ?> <?php echo $is_current ? 'current-plan' : ''; ?>">
                            <?php if ($is_featured): ?>
                                <div class="plan-badge">Most Popular</div>
                            <?php endif; ?>
                            
                            <div class="plan-header">
                                <h3><?php echo $plan['name']; ?></h3>
                                <div class="price">
                                    <span class="amount monthly-price">$<?php echo number_format($plan['price_monthly'], 2); ?></span>
                                    <?php if ($plan['price_yearly'] > 0): ?>
                                        <span class="amount yearly-price" style="display: none;">$<?php echo number_format($plan['price_yearly'], 2); ?></span>
                                    <?php endif; ?>
                                    <span class="period">/month</span>
                                </div>
                                <p class="plan-description"><?php echo $plan['description']; ?></p>
                            </div>
                            
                            <ul class="features-list">
                                <?php foreach ($plan['features'] as $feature): ?>
                                    <li><i class="fas fa-check"></i> <?php echo $feature; ?></li>
                                <?php endforeach; ?>
                                
                                <?php if (isset($plan['unavailable'])): ?>
                                    <?php foreach ($plan['unavailable'] as $feature): ?>
                                        <li class="unavailable"><i class="fas fa-times"></i> <?php echo $feature; ?></li>
                                    <?php endforeach; ?>
                                <?php endif; ?>
                            </ul>
                            
                            <div class="plan-action">
                                <?php if ($is_current): ?>
                                    <button class="btn btn-outline" disabled>Current Plan</button>
                                <?php elseif ($tier === 'free'): ?>
                                    <?php if ($user_tier !== 'free'): ?>
                                        <button class="btn btn-outline" disabled>Downgrade Available</button>
                                    <?php endif; ?>
                                <?php else: ?>
                                    <?php if (in_array($user_tier, ['free']) || ($tier === 'basic' && $user_tier === 'free') || ($tier === 'pro' && in_array($user_tier, ['free', 'basic'])) || ($tier === 'enterprise')): ?>
                                        <button class="btn btn-primary upgrade-btn" data-plan="<?php echo $tier; ?>">Upgrade Now</button>
                                    <?php else: ?>
                                        <button class="btn btn-secondary downgrade-btn" data-plan="<?php echo $tier; ?>">Downgrade</button>
                                    <?php endif; ?>
                                <?php endif; ?>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>

                <!-- Features Comparison -->
                <div class="features-comparison">
                    <h2 class="wp-block-heading has-text-align-center has-large-font-size">Feature Comparison</h2>
                    <div class="comparison-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>Feature</th>
                                    <th>Free</th>
                                    <th>Basic</th>
                                    <th>Pro</th>
                                    <th>Enterprise</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>API Calls per Month</td>
                                    <td>15</td>
                                    <td>1,500</td>
                                    <td>5,000</td>
                                    <td>Unlimited</td>
                                </tr>
                                <tr>
                                    <td>Watchlist Items</td>
                                    <td>3</td>
                                    <td>25</td>
                                    <td>100</td>
                                    <td>Unlimited</td>
                                </tr>
                                <tr>
                                    <td>Real-time Data</td>
                                    <td><i class="fas fa-times text-red"></i></td>
                                    <td><i class="fas fa-check text-green"></i></td>
                                    <td><i class="fas fa-check text-green"></i></td>
                                    <td><i class="fas fa-check text-green"></i></td>
                                </tr>
                                <tr>
                                    <td>Advanced Charts</td>
                                    <td><i class="fas fa-times text-red"></i></td>
                                    <td><i class="fas fa-check text-green"></i></td>
                                    <td><i class="fas fa-check text-green"></i></td>
                                    <td><i class="fas fa-check text-green"></i></td>
                                </tr>
                                <tr>
                                    <td>Data Export</td>
                                    <td><i class="fas fa-times text-red"></i></td>
                                    <td><i class="fas fa-check text-green"></i></td>
                                    <td><i class="fas fa-check text-green"></i></td>
                                    <td><i class="fas fa-check text-green"></i></td>
                                </tr>
                                <tr>
                                    <td>API Access</td>
                                    <td><i class="fas fa-times text-red"></i></td>
                                    <td><i class="fas fa-times text-red"></i></td>
                                    <td><i class="fas fa-check text-green"></i></td>
                                    <td><i class="fas fa-check text-green"></i></td>
                                </tr>
                                <tr>
                                    <td>Custom Alerts</td>
                                    <td><i class="fas fa-times text-red"></i></td>
                                    <td>Basic</td>
                                    <td>Advanced</td>
                                    <td>Advanced</td>
                                </tr>
                                <tr>
                                    <td>Support</td>
                                    <td>Email</td>
                                    <td>Priority Email</td>
                                    <td>Phone & Chat</td>
                                    <td>24/7 Dedicated</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- FAQ Section -->
                <div class="faq-section">
                    <h2 class="wp-block-heading has-text-align-center has-large-font-size">Frequently Asked Questions</h2>
                    <div class="faq-grid">
                        <div class="faq-item">
                            <h4>Can I change my plan anytime?</h4>
                            <p>Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and billing is prorated.</p>
                        </div>
                        <div class="faq-item">
                            <h4>What payment methods do you accept?</h4>
                            <p>We accept all major credit cards and PayPal. All payments are processed securely through PayPal.</p>
                        </div>
                        <div class="faq-item">
                            <h4>Is there a free trial?</h4>
                            <p>Yes! Our Free plan gives you 15 API calls per month to try our service. No credit card required.</p>
                        </div>
                        <div class="faq-item">
                            <h4>What happens if I exceed my API limit?</h4>
                            <p>If you exceed your monthly limit, API calls will be temporarily restricted until your next billing cycle or you upgrade your plan.</p>
                        </div>
                        <div class="faq-item">
                            <h4>Do you offer annual discounts?</h4>
                            <p>Yes! Save 10% when you choose annual billing. The discount is automatically applied when you toggle to yearly pricing.</p>
                        </div>
                        <div class="faq-item">
                            <h4>Can I cancel my subscription?</h4>
                            <p>Absolutely. You can cancel your subscription at any time from your account settings. You'll retain access until the end of your billing period.</p>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>

</main>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const billingToggle = document.getElementById('billing-toggle');
    const monthlyPrices = document.querySelectorAll('.monthly-price');
    const yearlyPrices = document.querySelectorAll('.yearly-price');

    billingToggle.addEventListener('change', function() {
        if (this.checked) {
            // Show yearly prices
            monthlyPrices.forEach(price => price.style.display = 'none');
            yearlyPrices.forEach(price => price.style.display = 'inline');
        } else {
            // Show monthly prices
            monthlyPrices.forEach(price => price.style.display = 'inline');
            yearlyPrices.forEach(price => price.style.display = 'none');
        }
    });

    // Handle upgrade buttons
    document.querySelectorAll('.upgrade-btn, .downgrade-btn').forEach(button => {
        button.addEventListener('click', function() {
            const plan = this.dataset.plan;
            const isYearly = billingToggle.checked;
            
            // Redirect to PayPal checkout
            const checkoutUrl = `/paypal-checkout/?plan=${plan}&billing=${isYearly ? 'yearly' : 'monthly'}`;
            window.location.href = checkoutUrl;
        });
    });

    // Add animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.pricing-card, .faq-item').forEach(el => {
        observer.observe(el);
    });
});
</script>

<?php get_footer(); ?>