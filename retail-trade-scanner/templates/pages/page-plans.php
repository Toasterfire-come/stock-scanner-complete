<?php
/**
 * Template Name: Plans
 * 
 * Pricing tiers and subscription management
 *
 * @package RetailTradeScanner
 */

get_header();

// Sample pricing plans
$pricing_plans = array(
    'free' => array(
        'name' => 'Free Tier',
        'price' => '$0',
        'period' => 'forever',
        'description' => 'Perfect for getting started with basic market data',
        'features' => array(
            'Basic stock quotes (15-min delay)',
            'Limited watchlist (10 stocks)',
            'Basic charts and indicators',
            'Daily market summary',
            'Community forum access'
        ),
        'limitations' => array(
            'Limited to 50 searches per day',
            'No real-time data',
            'Basic support only'
        ),
        'current' => false,
        'popular' => false
    ),
    'pro' => array(
        'name' => 'Pro Trader',
        'price' => '$49.99',
        'period' => 'month',
        'description' => 'Advanced tools for serious traders and investors',
        'features' => array(
            'Real-time market data',
            'Unlimited watchlists',
            'Advanced charting tools',
            'Custom alerts and notifications',
            'Portfolio tracking and analysis',
            'Sector performance analysis',
            'Technical indicators library',
            'Email support'
        ),
        'limitations' => array(),
        'current' => true,
        'popular' => true
    ),
    'enterprise' => array(
        'name' => 'Enterprise',
        'price' => '$199.99',
        'period' => 'month',
        'description' => 'Comprehensive solution for professional traders',
        'features' => array(
            'Everything in Pro Trader',
            'API access for custom integrations',
            'Advanced screening tools',
            'Institutional-grade data feeds',
            'Priority customer support',
            'Custom reporting and analytics',
            'Multi-user team access',
            'Dedicated account manager'
        ),
        'limitations' => array(),
        'current' => false,
        'popular' => false
    )
);

$layout_args = array(
    'page_title' => __('Pricing Plans', 'retail-trade-scanner'),
    'page_description' => __('Choose the perfect plan for your trading and investment needs', 'retail-trade-scanner'),
    'page_class' => 'plans-page',
    'breadcrumbs' => false
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<div class="plans-content">
    
    <!-- Pricing Header -->
    <div class="pricing-header text-center mb-2xl">
        <h1 class="pricing-title"><?php esc_html_e('Simple, Transparent Pricing', 'retail-trade-scanner'); ?></h1>
        <p class="pricing-subtitle"><?php esc_html_e('Choose the plan that fits your trading style and investment goals', 'retail-trade-scanner'); ?></p>
        
        <!-- Billing Toggle -->
        <div class="billing-toggle">
            <span class="toggle-label"><?php esc_html_e('Monthly', 'retail-trade-scanner'); ?></span>
            <label class="toggle-switch">
                <input type="checkbox" id="billing-period">
                <span class="toggle-slider"></span>
            </label>
            <span class="toggle-label">
                <?php esc_html_e('Yearly', 'retail-trade-scanner'); ?>
                <span class="discount-badge"><?php esc_html_e('Save 20%', 'retail-trade-scanner'); ?></span>
            </span>
        </div>
    </div>
    
    <!-- Pricing Cards -->
    <div class="pricing-grid">
        <?php foreach ($pricing_plans as $plan_id => $plan) : ?>
            <div class="pricing-card <?php echo $plan['popular'] ? 'popular' : ''; ?> <?php echo $plan['current'] ? 'current-plan' : ''; ?>" data-plan="<?php echo esc_attr($plan_id); ?>">
                
                <?php if ($plan['popular']) : ?>
                    <div class="popular-badge">
                        <?php esc_html_e('Most Popular', 'retail-trade-scanner'); ?>
                    </div>
                <?php endif; ?>
                
                <?php if ($plan['current']) : ?>
                    <div class="current-badge">
                        <?php esc_html_e('Current Plan', 'retail-trade-scanner'); ?>
                    </div>
                <?php endif; ?>
                
                <div class="card-header">
                    <h3 class="plan-name"><?php echo esc_html($plan['name']); ?></h3>
                    <div class="plan-pricing">
                        <span class="plan-price monthly-price"><?php echo esc_html($plan['price']); ?></span>
                        <?php if ($plan_id !== 'free') : ?>
                            <span class="plan-price yearly-price hidden">
                                <?php 
                                $yearly_price = '$' . number_format(floatval(str_replace('$', '', $plan['price'])) * 12 * 0.8, 2);
                                echo esc_html($yearly_price);
                                ?>
                            </span>
                        <?php endif; ?>
                        <span class="plan-period">
                            <span class="monthly-period">/<?php echo esc_html($plan['period']); ?></span>
                            <?php if ($plan_id !== 'free') : ?>
                                <span class="yearly-period hidden">/year</span>
                            <?php endif; ?>
                        </span>
                    </div>
                    <p class="plan-description"><?php echo esc_html($plan['description']); ?></p>
                </div>
                
                <div class="card-body">
                    <div class="features-section">
                        <h4 class="features-title"><?php esc_html_e('Features included:', 'retail-trade-scanner'); ?></h4>
                        <ul class="features-list">
                            <?php foreach ($plan['features'] as $feature) : ?>
                                <li class="feature-item">
                                    <?php echo rts_get_icon('check', ['width' => '16', 'height' => '16', 'class' => 'feature-icon']); ?>
                                    <span><?php echo esc_html($feature); ?></span>
                                </li>
                            <?php endforeach; ?>
                        </ul>
                    </div>
                    
                    <?php if (!empty($plan['limitations'])) : ?>
                        <div class="limitations-section">
                            <h4 class="limitations-title"><?php esc_html_e('Limitations:', 'retail-trade-scanner'); ?></h4>
                            <ul class="limitations-list">
                                <?php foreach ($plan['limitations'] as $limitation) : ?>
                                    <li class="limitation-item">
                                        <?php echo rts_get_icon('x', ['width' => '16', 'height' => '16', 'class' => 'limitation-icon']); ?>
                                        <span><?php echo esc_html($limitation); ?></span>
                                    </li>
                                <?php endforeach; ?>
                            </ul>
                        </div>
                    <?php endif; ?>
                </div>
                
                <div class="card-footer">
                    <?php if ($plan['current']) : ?>
                        <button class="btn btn-outline btn-block manage-plan" data-plan="<?php echo esc_attr($plan_id); ?>">
                            <?php esc_html_e('Manage Plan', 'retail-trade-scanner'); ?>
                        </button>
                    <?php elseif ($plan_id === 'free') : ?>
                        <button class="btn btn-ghost btn-block downgrade-plan" data-plan="<?php echo esc_attr($plan_id); ?>">
                            <?php esc_html_e('Downgrade to Free', 'retail-trade-scanner'); ?>
                        </button>
                    <?php else : ?>
                        <button class="btn btn-primary btn-block upgrade-plan" data-plan="<?php echo esc_attr($plan_id); ?>">
                            <?php esc_html_e('Upgrade Now', 'retail-trade-scanner'); ?>
                        </button>
                    <?php endif; ?>
                    
                    <?php if ($plan_id !== 'free') : ?>
                        <div class="plan-benefits">
                            <small><?php esc_html_e('✓ 14-day free trial', 'retail-trade-scanner'); ?></small>
                            <small><?php esc_html_e('✓ Cancel anytime', 'retail-trade-scanner'); ?></small>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        <?php endforeach; ?>
    </div>
    
    <!-- Feature Comparison -->
    <div class="feature-comparison mt-3xl">
        <div class="section-header text-center mb-xl">
            <h2><?php esc_html_e('Compare All Features', 'retail-trade-scanner'); ?></h2>
            <p><?php esc_html_e('See exactly what\'s included in each plan', 'retail-trade-scanner'); ?></p>
        </div>
        
        <div class="comparison-table-container card">
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th class="feature-column"><?php esc_html_e('Feature', 'retail-trade-scanner'); ?></th>
                        <th class="plan-column"><?php esc_html_e('Free', 'retail-trade-scanner'); ?></th>
                        <th class="plan-column popular"><?php esc_html_e('Pro Trader', 'retail-trade-scanner'); ?></th>
                        <th class="plan-column"><?php esc_html_e('Enterprise', 'retail-trade-scanner'); ?></th>
                    </tr>
                </thead>
                <tbody>
                    <?php
                    $comparison_features = array(
                        'Real-time Data' => array('free' => false, 'pro' => true, 'enterprise' => true),
                        'Watchlists' => array('free' => '10 stocks', 'pro' => 'Unlimited', 'enterprise' => 'Unlimited'),
                        'Advanced Charts' => array('free' => false, 'pro' => true, 'enterprise' => true),
                        'Custom Alerts' => array('free' => false, 'pro' => true, 'enterprise' => true),
                        'Portfolio Tracking' => array('free' => false, 'pro' => true, 'enterprise' => true),
                        'API Access' => array('free' => false, 'pro' => false, 'enterprise' => true),
                        'Support Level' => array('free' => 'Community', 'pro' => 'Email', 'enterprise' => 'Priority')
                    );
                    
                    foreach ($comparison_features as $feature_name => $plans) : ?>
                        <tr>
                            <td class="feature-name"><?php echo esc_html($feature_name); ?></td>
                            <?php foreach (array('free', 'pro', 'enterprise') as $plan_key) : ?>
                                <td class="feature-value">
                                    <?php if (is_bool($plans[$plan_key])) : ?>
                                        <?php if ($plans[$plan_key]) : ?>
                                            <?php echo rts_get_icon('check', ['width' => '16', 'height' => '16', 'class' => 'text-success']); ?>
                                        <?php else : ?>
                                            <?php echo rts_get_icon('x', ['width' => '16', 'height' => '16', 'class' => 'text-muted']); ?>
                                        <?php endif; ?>
                                    <?php else : ?>
                                        <?php echo esc_html($plans[$plan_key]); ?>
                                    <?php endif; ?>
                                </td>
                            <?php endforeach; ?>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- FAQ Section -->
    <div class="faq-section mt-3xl">
        <div class="section-header text-center mb-xl">
            <h2><?php esc_html_e('Frequently Asked Questions', 'retail-trade-scanner'); ?></h2>
        </div>
        
        <div class="faq-grid">
            <div class="faq-item card">
                <div class="faq-question">
                    <h3><?php esc_html_e('Can I change plans anytime?', 'retail-trade-scanner'); ?></h3>
                </div>
                <div class="faq-answer">
                    <p><?php esc_html_e('Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately and we\'ll prorate any billing differences.', 'retail-trade-scanner'); ?></p>
                </div>
            </div>
            
            <div class="faq-item card">
                <div class="faq-question">
                    <h3><?php esc_html_e('Is there a free trial?', 'retail-trade-scanner'); ?></h3>
                </div>
                <div class="faq-answer">
                    <p><?php esc_html_e('Yes! All paid plans come with a 14-day free trial. No credit card required to start your trial.', 'retail-trade-scanner'); ?></p>
                </div>
            </div>
            
            <div class="faq-item card">
                <div class="faq-question">
                    <h3><?php esc_html_e('What payment methods do you accept?', 'retail-trade-scanner'); ?></h3>
                </div>
                <div class="faq-answer">
                    <p><?php esc_html_e('We accept all major credit cards, PayPal, and bank transfers for annual plans.', 'retail-trade-scanner'); ?></p>
                </div>
            </div>
            
            <div class="faq-item card">
                <div class="faq-question">
                    <h3><?php esc_html_e('Do you offer refunds?', 'retail-trade-scanner'); ?></h3>
                </div>
                <div class="faq-answer">
                    <p><?php esc_html_e('Yes, we offer a 30-day money-back guarantee for all paid plans. If you\'re not satisfied, we\'ll refund your payment in full.', 'retail-trade-scanner'); ?></p>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initPlansPage();
});

function initPlansPage() {
    // Billing period toggle
    const billingToggle = document.getElementById('billing-period');
    if (billingToggle) {
        billingToggle.addEventListener('change', function() {
            toggleBillingPeriod(this.checked);
        });
    }
    
    // Plan selection buttons
    document.querySelectorAll('.upgrade-plan').forEach(btn => {
        btn.addEventListener('click', function() {
            const plan = this.dataset.plan;
            upgradeToPlan(plan);
        });
    });
    
    document.querySelectorAll('.downgrade-plan').forEach(btn => {
        btn.addEventListener('click', function() {
            const plan = this.dataset.plan;
            downgradeToPlan(plan);
        });
    });
    
    document.querySelectorAll('.manage-plan').forEach(btn => {
        btn.addEventListener('click', function() {
            const plan = this.dataset.plan;
            managePlan(plan);
        });
    });
    
    function toggleBillingPeriod(isYearly) {
        const monthlyElements = document.querySelectorAll('.monthly-price, .monthly-period');
        const yearlyElements = document.querySelectorAll('.yearly-price, .yearly-period');
        
        monthlyElements.forEach(el => {
            el.classList.toggle('hidden', isYearly);
        });
        
        yearlyElements.forEach(el => {
            el.classList.toggle('hidden', !isYearly);
        });
        
        // Update button text for yearly discount
        if (isYearly) {
            document.querySelectorAll('.upgrade-plan').forEach(btn => {
                if (btn.textContent.includes('Upgrade Now')) {
                    btn.innerHTML = btn.innerHTML.replace('Upgrade Now', 'Start Free Trial (20% Off)');
                }
            });
        } else {
            document.querySelectorAll('.upgrade-plan').forEach(btn => {
                if (btn.textContent.includes('Start Free Trial')) {
                    btn.innerHTML = btn.innerHTML.replace('Start Free Trial (20% Off)', 'Upgrade Now');
                }
            });
        }
        
        console.log('Billing period changed to:', isYearly ? 'yearly' : 'monthly');
    }
    
    function upgradeToPlan(plan) {
        console.log('Upgrading to plan:', plan);
        
        const btn = document.querySelector(`[data-plan="${plan}"].upgrade-plan`);
        btn.disabled = true;
        btn.textContent = 'Processing...';
        
        // Simulate upgrade process
        setTimeout(() => {
            btn.disabled = false;
            btn.textContent = 'Upgrade Now';
            
            RTS.showSuccess(`Successfully upgraded to ${plan} plan!`);
            
            // Update UI to show new current plan
            document.querySelectorAll('.pricing-card').forEach(card => {
                card.classList.remove('current-plan');
                const badge = card.querySelector('.current-badge');
                if (badge) badge.remove();
            });
            
            const newCurrentCard = document.querySelector(`[data-plan="${plan}"]`);
            newCurrentCard.classList.add('current-plan');
            
            const currentBadge = document.createElement('div');
            currentBadge.className = 'current-badge';
            currentBadge.textContent = 'Current Plan';
            newCurrentCard.appendChild(currentBadge);
            
        }, 2000);
    }
    
    function downgradeToPlan(plan) {
        if (confirm('Are you sure you want to downgrade to the free plan? You will lose access to premium features.')) {
            console.log('Downgrading to plan:', plan);
            
            const btn = document.querySelector(`[data-plan="${plan}"].downgrade-plan`);
            btn.disabled = true;
            btn.textContent = 'Processing...';
            
            setTimeout(() => {
                btn.disabled = false;
                btn.textContent = 'Downgrade to Free';
                RTS.showInfo('Downgraded to free plan. Premium features will remain active until the end of your billing period.');
            }, 2000);
        }
    }
    
    function managePlan(plan) {
        console.log('Managing plan:', plan);
        RTS.showInfo('Plan management options would open here');
    }
}
</script>

<style>
/* Plans Page Styles */
.plans-content {
    margin-bottom: var(--spacing-3xl);
}

.pricing-header {
    max-width: 600px;
    margin: 0 auto var(--spacing-3xl);
}

.pricing-title {
    font-size: var(--text-4xl);
    font-weight: 800;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-md);
    line-height: 1.2;
}

.pricing-subtitle {
    font-size: var(--text-xl);
    color: var(--gray-600);
    margin: 0 0 var(--spacing-2xl);
    line-height: 1.5;
}

.billing-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-md);
}

.toggle-label {
    font-size: var(--text-base);
    font-weight: 600;
    color: var(--gray-700);
}

.discount-badge {
    background: var(--success);
    color: white;
    font-size: var(--text-xs);
    padding: 2px var(--spacing-xs);
    border-radius: var(--radius-sm);
    margin-left: var(--spacing-xs);
}

.toggle-switch {
    position: relative;
    width: 60px;
    height: 30px;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: var(--gray-300);
    transition: var(--transition-normal);
    border-radius: 30px;
}

.toggle-slider:before {
    position: absolute;
    content: "";
    height: 26px;
    width: 26px;
    left: 2px;
    bottom: 2px;
    background-color: white;
    transition: var(--transition-normal);
    border-radius: 50%;
}

input:checked + .toggle-slider {
    background-color: var(--primary-500);
}

input:checked + .toggle-slider:before {
    transform: translateX(30px);
}

.pricing-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: var(--spacing-2xl);
    margin-bottom: var(--spacing-3xl);
}

.pricing-card {
    position: relative;
    background: var(--surface-raised);
    border: 2px solid var(--gray-200);
    border-radius: var(--radius-2xl);
    overflow: hidden;
    transition: all var(--transition-normal) var(--easing-standard);
}

.pricing-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-2xl);
}

.pricing-card.popular {
    border-color: var(--primary-500);
    box-shadow: 0 0 0 4px rgba(var(--primary-500), 0.1);
}

.pricing-card.current-plan {
    border-color: var(--success);
    background: linear-gradient(135deg, var(--success-light) 0%, var(--surface-raised) 20%);
}

.popular-badge,
.current-badge {
    position: absolute;
    top: var(--spacing-lg);
    right: var(--spacing-lg);
    background: var(--primary-500);
    color: white;
    font-size: var(--text-xs);
    font-weight: 700;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-full);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.current-badge {
    background: var(--success);
}

.pricing-card .card-header {
    padding: var(--spacing-2xl) var(--spacing-xl) var(--spacing-xl);
    text-align: center;
}

.plan-name {
    font-size: var(--text-2xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-md);
}

.plan-pricing {
    margin-bottom: var(--spacing-lg);
}

.plan-price {
    font-size: var(--text-4xl);
    font-weight: 800;
    color: var(--gray-900);
}

.plan-period {
    font-size: var(--text-lg);
    color: var(--gray-600);
}

.plan-description {
    font-size: var(--text-base);
    color: var(--gray-600);
    line-height: 1.6;
    margin: 0;
}

.pricing-card .card-body {
    padding: 0 var(--spacing-xl) var(--spacing-xl);
}

.features-section,
.limitations-section {
    margin-bottom: var(--spacing-xl);
}

.features-title,
.limitations-title {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--gray-700);
    margin: 0 0 var(--spacing-md);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.features-list,
.limitations-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.feature-item,
.limitation-item {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
    font-size: var(--text-sm);
    line-height: 1.5;
}

.feature-icon {
    color: var(--success);
    flex-shrink: 0;
    margin-top: 2px;
}

.limitation-icon {
    color: var(--danger);
    flex-shrink: 0;
    margin-top: 2px;
}

.pricing-card .card-footer {
    padding: var(--spacing-xl);
    border-top: 1px solid var(--gray-200);
}

.plan-benefits {
    margin-top: var(--spacing-md);
    text-align: center;
}

.plan-benefits small {
    display: block;
    color: var(--gray-600);
    font-size: var(--text-xs);
    margin-bottom: var(--spacing-xs);
}

.feature-comparison {
    max-width: 1000px;
    margin: 0 auto;
}

.comparison-table-container {
    overflow-x: auto;
}

.comparison-table {
    width: 100%;
    border-collapse: collapse;
}

.comparison-table th,
.comparison-table td {
    padding: var(--spacing-md) var(--spacing-lg);
    text-align: center;
    border-bottom: 1px solid var(--gray-200);
}

.comparison-table th {
    background: var(--gray-50);
    font-weight: 600;
    color: var(--gray-700);
}

.feature-column {
    text-align: left !important;
    min-width: 200px;
}

.plan-column.popular {
    background: rgba(var(--primary-500), 0.05);
    position: relative;
}

.feature-name {
    font-weight: 600;
    color: var(--gray-900);
}

.feature-value {
    color: var(--gray-600);
}

.faq-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: var(--spacing-xl);
    max-width: 1000px;
    margin: 0 auto;
}

.faq-item {
    padding: var(--spacing-xl);
}

.faq-question h3 {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-md);
}

.faq-answer p {
    color: var(--gray-600);
    line-height: 1.6;
    margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
    .pricing-title {
        font-size: var(--text-3xl);
    }
    
    .pricing-grid {
        grid-template-columns: 1fr;
        gap: var(--spacing-xl);
    }
    
    .billing-toggle {
        flex-direction: column;
        gap: var(--spacing-sm);
    }
    
    .popular-badge,
    .current-badge {
        position: static;
        align-self: center;
        margin-bottom: var(--spacing-md);
    }
    
    .comparison-table {
        font-size: var(--text-sm);
    }
    
    .comparison-table th,
    .comparison-table td {
        padding: var(--spacing-sm);
    }
    
    .faq-grid {
        grid-template-columns: 1fr;
    }
}

/* Dark Mode */
[data-theme="dark"] .pricing-title {
    color: var(--gray-100);
}

[data-theme="dark"] .pricing-subtitle {
    color: var(--gray-300);
}

[data-theme="dark"] .toggle-label {
    color: var(--gray-300);
}

[data-theme="dark"] .plan-name,
[data-theme="dark"] .plan-price,
[data-theme="dark"] .feature-name {
    color: var(--gray-100);
}

[data-theme="dark"] .plan-description,
[data-theme="dark"] .plan-period,
[data-theme="dark"] .feature-value,
[data-theme="dark"] .faq-answer p {
    color: var(--gray-400);
}

[data-theme="dark"] .comparison-table th {
    background: var(--gray-800);
    color: var(--gray-300);
}

[data-theme="dark"] .comparison-table td {
    border-color: var(--gray-700);
}

[data-theme="dark"] .faq-question h3 {
    color: var(--gray-200);
}
</style>

<?php get_footer(); ?>