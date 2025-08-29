<?php
/**
 * Template Name: Plans & Pricing
 * 
 * Pricing page with subscription plans and features comparison
 *
 * @package RetailTradeScanner
 */

get_header();

// Pricing plans data
$pricing_plans = array(
    'basic' => array(
        'name' => 'Basic',
        'tagline' => 'Perfect for individual traders',
        'price' => 29,
        'billing' => 'per month',
        'annual_price' => 290,
        'annual_discount' => 17,
        'popular' => false,
        'features' => array(
            'Real-time market data',
            'Basic stock screening',
            '5 active alerts',
            'Portfolio tracking',
            'Email support',
            'Mobile app access',
            'Basic charts & indicators',
            '10 watchlists'
        ),
        'limits' => array(
            'watchlists' => 10,
            'alerts' => 5,
            'screeners' => 3,
            'api_calls' => 1000
        ),
        'button_text' => 'Start Free Trial',
        'button_class' => 'btn-outline'
    ),
    'professional' => array(
        'name' => 'Professional',
        'tagline' => 'Advanced tools for serious traders',
        'price' => 79,
        'billing' => 'per month',
        'annual_price' => 790,
        'annual_discount' => 17,
        'popular' => true,
        'features' => array(
            'Everything in Basic',
            'Advanced screening filters',
            'Unlimited alerts',
            'Real-time news sentiment',
            'Technical analysis tools',
            'Portfolio analytics',
            'Priority support',
            'API access',
            'Custom indicators',
            'Unlimited watchlists',
            'Options data',
            'Backtesting tools'
        ),
        'limits' => array(
            'watchlists' => 'unlimited',
            'alerts' => 'unlimited',
            'screeners' => 'unlimited',
            'api_calls' => 10000
        ),
        'button_text' => 'Start Free Trial',
        'button_class' => 'btn-primary'
    ),
    'enterprise' => array(
        'name' => 'Enterprise',
        'tagline' => 'Institutional-grade platform',
        'price' => 299,
        'billing' => 'per month',
        'annual_price' => 2990,
        'annual_discount' => 17,
        'popular' => false,
        'features' => array(
            'Everything in Professional',
            'Multi-user accounts',
            'White-label solution',
            'Custom integrations',
            'Dedicated support',
            'On-premise deployment',
            'Advanced security',
            'Custom reporting',
            'Priority data feeds',
            'SLA guarantee',
            'Training sessions',
            'Custom development'
        ),
        'limits' => array(
            'users' => 'unlimited',
            'api_calls' => 'unlimited',
            'data_retention' => 'unlimited',
            'support' => '24/7 dedicated'
        ),
        'button_text' => 'Contact Sales',
        'button_class' => 'btn-secondary'
    )
);

$layout_args = array(
    'page_title' => __('Plans & Pricing', 'retail-trade-scanner'),
    'page_description' => __('Choose the perfect plan for your trading needs. Start with a 14-day free trial, no credit card required.', 'retail-trade-scanner'),
    'page_class' => 'pricing-page'
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<!-- Pricing Hero -->
<section class="pricing-hero">
    <div class="container">
        <div class="hero-content">
            <h1 class="hero-title animate-fade-up">
                <?php esc_html_e('Simple, Transparent Pricing', 'retail-trade-scanner'); ?>
            </h1>
            <p class="hero-description animate-fade-up">
                <?php esc_html_e('Choose the plan that fits your trading style. All plans include a 14-day free trial with full access to premium features.', 'retail-trade-scanner'); ?>
            </p>
            
            <!-- Billing Toggle -->
            <div class="billing-toggle animate-fade-up">
                <span class="toggle-label"><?php esc_html_e('Monthly', 'retail-trade-scanner'); ?></span>
                <label class="toggle-switch">
                    <input type="checkbox" id="billing-toggle">
                    <span class="toggle-slider"></span>
                </label>
                <span class="toggle-label">
                    <?php esc_html_e('Annual', 'retail-trade-scanner'); ?>
                    <span class="discount-badge"><?php esc_html_e('Save 17%', 'retail-trade-scanner'); ?></span>
                </span>
            </div>
        </div>
    </div>
</section>

<!-- Pricing Plans -->
<section class="pricing-plans">
    <div class="container">
        <div class="plans-grid">
            <?php foreach ($pricing_plans as $plan_key => $plan) : ?>
                <div class="pricing-card <?php echo $plan['popular'] ? 'popular' : ''; ?> animate-scale-in">
                    <?php if ($plan['popular']) : ?>
                        <div class="popular-badge">
                            <?php echo rts_get_icon('star', ['width' => '16', 'height' => '16']); ?>
                            <?php esc_html_e('Most Popular', 'retail-trade-scanner'); ?>
                        </div>
                    <?php endif; ?>
                    
                    <div class="plan-header">
                        <div class="plan-icon">
                            <?php
                            $icons = array(
                                'basic' => 'user',
                                'professional' => 'trending-up',
                                'enterprise' => 'building'
                            );
                            echo rts_get_icon($icons[$plan_key], ['width' => '32', 'height' => '32']);
                            ?>
                        </div>
                        
                        <h3 class="plan-name"><?php echo esc_html($plan['name']); ?></h3>
                        <p class="plan-tagline"><?php echo esc_html($plan['tagline']); ?></p>
                        
                        <div class="plan-pricing">
                            <div class="price-display">
                                <span class="currency">$</span>
                                <span class="price-amount monthly-price"><?php echo esc_html($plan['price']); ?></span>
                                <span class="price-amount annual-price hidden"><?php echo esc_html($plan['annual_price']); ?></span>
                                <span class="billing-period">
                                    <span class="monthly-billing"><?php echo esc_html($plan['billing']); ?></span>
                                    <span class="annual-billing hidden"><?php esc_html_e('per year', 'retail-trade-scanner'); ?></span>
                                </span>
                            </div>
                            
                            <div class="annual-savings hidden">
                                <span class="savings-text">
                                    <?php printf(esc_html__('Save $%d per year', 'retail-trade-scanner'), ($plan['price'] * 12) - $plan['annual_price']); ?>
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="plan-features">
                        <ul class="features-list">
                            <?php foreach ($plan['features'] as $feature) : ?>
                                <li class="feature-item">
                                    <?php echo rts_get_icon('check', ['width' => '16', 'height' => '16', 'class' => 'feature-check']); ?>
                                    <span><?php echo esc_html($feature); ?></span>
                                </li>
                            <?php endforeach; ?>
                        </ul>
                    </div>
                    
                    <div class="plan-limits">
                        <h4><?php esc_html_e('Plan Limits', 'retail-trade-scanner'); ?></h4>
                        <div class="limits-grid">
                            <?php foreach ($plan['limits'] as $limit_key => $limit_value) : ?>
                                <div class="limit-item">
                                    <span class="limit-label"><?php echo esc_html(ucfirst(str_replace('_', ' ', $limit_key))); ?></span>
                                    <span class="limit-value"><?php echo esc_html($limit_value); ?></span>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </div>
                    
                    <div class="plan-action">
                        <button class="btn <?php echo esc_attr($plan['button_class']); ?> btn-lg plan-button" 
                                data-plan="<?php echo esc_attr($plan_key); ?>">
                            <?php echo esc_html($plan['button_text']); ?>
                        </button>
                        
                        <p class="trial-note">
                            <?php if ($plan_key !== 'enterprise') : ?>
                                <?php esc_html_e('14-day free trial • No credit card required', 'retail-trade-scanner'); ?>
                            <?php else : ?>
                                <?php esc_html_e('Custom pricing • Contact for quote', 'retail-trade-scanner'); ?>
                            <?php endif; ?>
                        </p>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
</section>

<!-- Feature Comparison -->
<section class="feature-comparison">
    <div class="container">
        <div class="section-header">
            <h2 class="section-title"><?php esc_html_e('Feature Comparison', 'retail-trade-scanner'); ?></h2>
            <p class="section-description">
                <?php esc_html_e('Compare all features across our plans to find the perfect fit for your trading needs.', 'retail-trade-scanner'); ?>
            </p>
        </div>
        
        <div class="comparison-table-container">
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th class="feature-column"><?php esc_html_e('Features', 'retail-trade-scanner'); ?></th>
                        <th class="plan-column basic"><?php esc_html_e('Basic', 'retail-trade-scanner'); ?></th>
                        <th class="plan-column professional">
                            <?php esc_html_e('Professional', 'retail-trade-scanner'); ?>
                            <span class="popular-indicator"><?php esc_html_e('Popular', 'retail-trade-scanner'); ?></span>
                        </th>
                        <th class="plan-column enterprise"><?php esc_html_e('Enterprise', 'retail-trade-scanner'); ?></th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Core Features -->
                    <tr class="category-header">
                        <td colspan="4"><?php esc_html_e('Core Trading Features', 'retail-trade-scanner'); ?></td>
                    </tr>
                    <tr>
                        <td><?php esc_html_e('Real-time Market Data', 'retail-trade-scanner'); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                    </tr>
                    <tr>
                        <td><?php esc_html_e('Stock Screening', 'retail-trade-scanner'); ?></td>
                        <td><span class="feature-limit"><?php esc_html_e('Basic', 'retail-trade-scanner'); ?></span></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                    </tr>
                    <tr>
                        <td><?php esc_html_e('Portfolio Tracking', 'retail-trade-scanner'); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                    </tr>
                    <tr>
                        <td><?php esc_html_e('Price Alerts', 'retail-trade-scanner'); ?></td>
                        <td><span class="feature-limit"><?php esc_html_e('5 alerts', 'retail-trade-scanner'); ?></span></td>
                        <td><span class="feature-unlimited"><?php esc_html_e('Unlimited', 'retail-trade-scanner'); ?></span></td>
                        <td><span class="feature-unlimited"><?php esc_html_e('Unlimited', 'retail-trade-scanner'); ?></span></td>
                    </tr>
                    
                    <!-- Advanced Features -->
                    <tr class="category-header">
                        <td colspan="4"><?php esc_html_e('Advanced Analysis', 'retail-trade-scanner'); ?></td>
                    </tr>
                    <tr>
                        <td><?php esc_html_e('Technical Indicators', 'retail-trade-scanner'); ?></td>
                        <td><span class="feature-limit"><?php esc_html_e('Basic', 'retail-trade-scanner'); ?></span></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                    </tr>
                    <tr>
                        <td><?php esc_html_e('News Sentiment Analysis', 'retail-trade-scanner'); ?></td>
                        <td><?php echo rts_get_icon('x', ['width' => '20', 'height' => '20', 'class' => 'x-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                    </tr>
                    <tr>
                        <td><?php esc_html_e('Backtesting Tools', 'retail-trade-scanner'); ?></td>
                        <td><?php echo rts_get_icon('x', ['width' => '20', 'height' => '20', 'class' => 'x-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                    </tr>
                    <tr>
                        <td><?php esc_html_e('Options Data', 'retail-trade-scanner'); ?></td>
                        <td><?php echo rts_get_icon('x', ['width' => '20', 'height' => '20', 'class' => 'x-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                    </tr>
                    
                    <!-- Support & Integration -->
                    <tr class="category-header">
                        <td colspan="4"><?php esc_html_e('Support & Integration', 'retail-trade-scanner'); ?></td>
                    </tr>
                    <tr>
                        <td><?php esc_html_e('Customer Support', 'retail-trade-scanner'); ?></td>
                        <td><span class="feature-limit"><?php esc_html_e('Email', 'retail-trade-scanner'); ?></span></td>
                        <td><span class="feature-limit"><?php esc_html_e('Priority', 'retail-trade-scanner'); ?></span></td>
                        <td><span class="feature-unlimited"><?php esc_html_e('24/7 Dedicated', 'retail-trade-scanner'); ?></span></td>
                    </tr>
                    <tr>
                        <td><?php esc_html_e('API Access', 'retail-trade-scanner'); ?></td>
                        <td><?php echo rts_get_icon('x', ['width' => '20', 'height' => '20', 'class' => 'x-icon']); ?></td>
                        <td><span class="feature-limit"><?php esc_html_e('10K calls/month', 'retail-trade-scanner'); ?></span></td>
                        <td><span class="feature-unlimited"><?php esc_html_e('Unlimited', 'retail-trade-scanner'); ?></span></td>
                    </tr>
                    <tr>
                        <td><?php esc_html_e('Custom Integrations', 'retail-trade-scanner'); ?></td>
                        <td><?php echo rts_get_icon('x', ['width' => '20', 'height' => '20', 'class' => 'x-icon']); ?></td>
                        <td><?php echo rts_get_icon('x', ['width' => '20', 'height' => '20', 'class' => 'x-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                    </tr>
                    <tr>
                        <td><?php esc_html_e('White-label Solution', 'retail-trade-scanner'); ?></td>
                        <td><?php echo rts_get_icon('x', ['width' => '20', 'height' => '20', 'class' => 'x-icon']); ?></td>
                        <td><?php echo rts_get_icon('x', ['width' => '20', 'height' => '20', 'class' => 'x-icon']); ?></td>
                        <td><?php echo rts_get_icon('check', ['width' => '20', 'height' => '20', 'class' => 'check-icon']); ?></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</section>

<!-- FAQ Section -->
<section class="pricing-faq">
    <div class="container">
        <div class="section-header">
            <h2 class="section-title"><?php esc_html_e('Frequently Asked Questions', 'retail-trade-scanner'); ?></h2>
        </div>
        
        <div class="faq-grid">
            <div class="faq-column">
                <div class="faq-item">
                    <button class="faq-question">
                        <span><?php esc_html_e('Can I change plans at any time?', 'retail-trade-scanner'); ?></span>
                        <?php echo rts_get_icon('chevron-down', ['width' => '16', 'height' => '16']); ?>
                    </button>
                    <div class="faq-answer hidden">
                        <p><?php esc_html_e('Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately, and we\'ll prorate any billing differences.', 'retail-trade-scanner'); ?></p>
                    </div>
                </div>
                
                <div class="faq-item">
                    <button class="faq-question">
                        <span><?php esc_html_e('What payment methods do you accept?', 'retail-trade-scanner'); ?></span>
                        <?php echo rts_get_icon('chevron-down', ['width' => '16', 'height' => '16']); ?>
                    </button>
                    <div class="faq-answer hidden">
                        <p><?php esc_html_e('We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and ACH bank transfers for enterprise accounts.', 'retail-trade-scanner'); ?></p>
                    </div>
                </div>
                
                <div class="faq-item">
                    <button class="faq-question">
                        <span><?php esc_html_e('Is there a setup fee?', 'retail-trade-scanner'); ?></span>
                        <?php echo rts_get_icon('chevron-down', ['width' => '16', 'height' => '16']); ?>
                    </button>
                    <div class="faq-answer hidden">
                        <p><?php esc_html_e('No setup fees for Basic and Professional plans. Enterprise plans may include setup fees for custom integrations and training sessions.', 'retail-trade-scanner'); ?></p>
                    </div>
                </div>
            </div>
            
            <div class="faq-column">
                <div class="faq-item">
                    <button class="faq-question">
                        <span><?php esc_html_e('Can I cancel my subscription?', 'retail-trade-scanner'); ?></span>
                        <?php echo rts_get_icon('chevron-down', ['width' => '16', 'height' => '16']); ?>
                    </button>
                    <div class="faq-answer hidden">
                        <p><?php esc_html_e('Yes, you can cancel your subscription at any time. You\'ll continue to have access until the end of your current billing period.', 'retail-trade-scanner'); ?></p>
                    </div>
                </div>
                
                <div class="faq-item">
                    <button class="faq-question">
                        <span><?php esc_html_e('Do you offer refunds?', 'retail-trade-scanner'); ?></span>
                        <?php echo rts_get_icon('chevron-down', ['width' => '16', 'height' => '16']); ?>
                    </button>
                    <div class="faq-answer hidden">
                        <p><?php esc_html_e('We offer a 30-day money-back guarantee for all new subscriptions. If you\'re not satisfied, contact us for a full refund.', 'retail-trade-scanner'); ?></p>
                    </div>
                </div>
                
                <div class="faq-item">
                    <button class="faq-question">
                        <span><?php esc_html_e('Is my data secure?', 'retail-trade-scanner'); ?></span>
                        <?php echo rts_get_icon('chevron-down', ['width' => '16', 'height' => '16']); ?>
                    </button>
                    <div class="faq-answer hidden">
                        <p><?php esc_html_e('Absolutely. We use bank-level encryption, regular security audits, and comply with SOC 2 Type II standards to protect your data.', 'retail-trade-scanner'); ?></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- CTA Section -->
<section class="pricing-cta">
    <div class="container">
        <div class="cta-content">
            <h2 class="cta-title"><?php esc_html_e('Ready to Start Trading Smarter?', 'retail-trade-scanner'); ?></h2>
            <p class="cta-description">
                <?php esc_html_e('Join thousands of traders who use our platform to make better investment decisions. Start your free trial today.', 'retail-trade-scanner'); ?>
            </p>
            
            <div class="cta-actions">
                <button class="btn btn-primary btn-lg" data-plan="professional">
                    <?php esc_html_e('Start Free Trial', 'retail-trade-scanner'); ?>
                    <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
                </button>
                
                <a href="<?php echo esc_url(home_url('/contact/')); ?>" class="btn btn-outline btn-lg">
                    <?php esc_html_e('Contact Sales', 'retail-trade-scanner'); ?>
                </a>
            </div>
            
            <div class="cta-features">
                <div class="feature-item">
                    <?php echo rts_get_icon('check-circle', ['width' => '16', 'height' => '16']); ?>
                    <span><?php esc_html_e('14-day free trial', 'retail-trade-scanner'); ?></span>
                </div>
                <div class="feature-item">
                    <?php echo rts_get_icon('check-circle', ['width' => '16', 'height' => '16']); ?>
                    <span><?php esc_html_e('No credit card required', 'retail-trade-scanner'); ?></span>
                </div>
                <div class="feature-item">
                    <?php echo rts_get_icon('check-circle', ['width' => '16', 'height' => '16']); ?>
                    <span><?php esc_html_e('Cancel anytime', 'retail-trade-scanner'); ?></span>
                </div>
            </div>
        </div>
    </div>
</section>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initPricingPage();
});

function initPricingPage() {
    const billingToggle = document.getElementById('billing-toggle');
    const planButtons = document.querySelectorAll('.plan-button');
    
    // Billing toggle functionality
    if (billingToggle) {
        billingToggle.addEventListener('change', function() {
            toggleBillingDisplay(this.checked);
        });
    }
    
    // Plan button clicks
    planButtons.forEach(button => {
        button.addEventListener('click', function() {
            const plan = this.dataset.plan;
            const isAnnual = billingToggle?.checked || false;
            
            if (plan === 'enterprise') {
                window.location.href = '/contact/?inquiry=enterprise';
            } else {
                startTrial(plan, isAnnual);
            }
        });
    });
    
    // FAQ accordion
    document.querySelectorAll('.faq-question').forEach(question => {
        question.addEventListener('click', function() {
            const faqItem = this.parentElement;
            const answer = faqItem.querySelector('.faq-answer');
            const icon = this.querySelector('svg');
            
            // Close other FAQ items
            document.querySelectorAll('.faq-item').forEach(item => {
                if (item !== faqItem) {
                    item.querySelector('.faq-answer').classList.add('hidden');
                    item.querySelector('svg').style.transform = 'rotate(0deg)';
                }
            });
            
            // Toggle current item
            answer.classList.toggle('hidden');
            icon.style.transform = answer.classList.contains('hidden') ? 'rotate(0deg)' : 'rotate(180deg)';
        });
    });
    
    // Animate pricing cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '50px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animate-in');
                }, index * 200);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.pricing-card').forEach(card => {
        observer.observe(card);
    });
    
    function toggleBillingDisplay(isAnnual) {
        const monthlyElements = document.querySelectorAll('.monthly-price, .monthly-billing');
        const annualElements = document.querySelectorAll('.annual-price, .annual-billing, .annual-savings');
        
        if (isAnnual) {
            monthlyElements.forEach(el => el.classList.add('hidden'));
            annualElements.forEach(el => el.classList.remove('hidden'));
        } else {
            monthlyElements.forEach(el => el.classList.remove('hidden'));
            annualElements.forEach(el => el.classList.add('hidden'));
        }
        
        // Animate price changes
        document.querySelectorAll('.price-display').forEach(display => {
            display.classList.add('price-changing');
            setTimeout(() => {
                display.classList.remove('price-changing');
            }, 300);
        });
    }
    
    function startTrial(plan, isAnnual) {
        // Show loading state
        const button = document.querySelector(`[data-plan="${plan}"]`);
        const originalText = button.innerHTML;
        button.innerHTML = `
            <div class="loading-spinner"></div>
            ${RTS.translations?.starting || 'Starting Trial...'}
        `;
        button.disabled = true;
        
        // Simulate trial start process
        setTimeout(() => {
            // In a real implementation, this would redirect to signup
            RTS.showSuccess(`Starting your ${plan} trial! Redirecting to signup...`);
            
            setTimeout(() => {
                // Redirect to signup page with plan selected
                window.location.href = `/signup/?plan=${plan}&billing=${isAnnual ? 'annual' : 'monthly'}`;
            }, 1500);
        }, 2000);
    }
}
</script>

<style>
/* Pricing Page Styles */
.pricing-page {
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    min-height: 100vh;
}

.pricing-hero {
    padding: var(--spacing-4xl) 0;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(217, 70, 239, 0.05) 100%);
    text-align: center;
}

.hero-title {
    font-size: clamp(2.5rem, 2.2rem + 1.5vw, 3.5rem);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-xl);
}

.hero-description {
    font-size: var(--text-lg);
    color: var(--gray-600);
    line-height: 1.6;
    margin-bottom: var(--spacing-2xl);
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

/* Billing Toggle */
.billing-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-2xl);
}

.toggle-label {
    font-weight: 600;
    color: var(--gray-700);
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.discount-badge {
    padding: var(--spacing-xs) var(--spacing-sm);
    background: var(--success);
    color: white;
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: 700;
}

.toggle-switch {
    position: relative;
    width: 60px;
    height: 32px;
    cursor: pointer;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle-slider {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--gray-300);
    border-radius: 32px;
    transition: all var(--transition-normal) var(--easing-standard);
}

.toggle-slider:before {
    position: absolute;
    content: "";
    height: 24px;
    width: 24px;
    left: 4px;
    bottom: 4px;
    background: white;
    border-radius: 50%;
    transition: all var(--transition-normal) var(--easing-standard);
}

.toggle-switch input:checked + .toggle-slider {
    background: var(--primary-500);
}

.toggle-switch input:checked + .toggle-slider:before {
    transform: translateX(28px);
}

/* Pricing Plans */
.pricing-plans {
    padding: var(--spacing-4xl) 0;
}

.plans-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: var(--spacing-2xl);
    max-width: 1200px;
    margin: 0 auto;
}

.pricing-card {
    position: relative;
    background: var(--surface-raised);
    border: 2px solid var(--gray-200);
    border-radius: var(--radius-2xl);
    padding: var(--spacing-2xl);
    transition: all var(--transition-normal) var(--easing-standard);
    opacity: 0;
    transform: translateY(50px);
}

.pricing-card.animate-in {
    opacity: 1;
    transform: translateY(0);
}

.pricing-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-xl);
}

.pricing-card.popular {
    border-color: var(--primary-500);
    box-shadow: 0 0 0 1px var(--primary-500);
    transform: scale(1.05);
}

.popular-badge {
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--primary-500);
    color: white;
    padding: var(--spacing-xs) var(--spacing-lg);
    border-radius: var(--radius-full);
    font-size: var(--text-sm);
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
}

.plan-header {
    text-align: center;
    margin-bottom: var(--spacing-2xl);
}

.plan-icon {
    width: 80px;
    height: 80px;
    border-radius: var(--radius-2xl);
    background: var(--primary-100);
    color: var(--primary-600);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto var(--spacing-lg);
}

.plan-name {
    font-size: var(--text-2xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-sm);
}

.plan-tagline {
    color: var(--gray-600);
    margin: 0 0 var(--spacing-xl);
}

.plan-pricing {
    margin-bottom: var(--spacing-xl);
}

.price-display {
    display: flex;
    align-items: baseline;
    justify-content: center;
    gap: var(--spacing-xs);
    margin-bottom: var(--spacing-sm);
    transition: all var(--transition-normal) var(--easing-standard);
}

.price-display.price-changing {
    transform: scale(1.1);
}

.currency {
    font-size: var(--text-xl);
    font-weight: 600;
    color: var(--gray-700);
}

.price-amount {
    font-size: clamp(3rem, 2.5rem + 2vw, 4rem);
    font-weight: 700;
    color: var(--gray-900);
}

.billing-period {
    font-size: var(--text-base);
    color: var(--gray-600);
}

.annual-savings {
    text-align: center;
}

.savings-text {
    font-size: var(--text-sm);
    color: var(--success);
    font-weight: 600;
    padding: var(--spacing-xs) var(--spacing-md);
    background: var(--success-light);
    border-radius: var(--radius-full);
}

/* Plan Features */
.plan-features {
    margin-bottom: var(--spacing-2xl);
}

.features-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.feature-item {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-sm);
    font-size: var(--text-sm);
    line-height: 1.5;
}

.feature-check {
    color: var(--success);
    flex-shrink: 0;
    margin-top: 2px;
}

/* Plan Limits */
.plan-limits {
    margin-bottom: var(--spacing-2xl);
    padding-top: var(--spacing-lg);
    border-top: 1px solid var(--gray-200);
}

.plan-limits h4 {
    font-size: var(--text-sm);
    font-weight: 700;
    color: var(--gray-700);
    margin: 0 0 var(--spacing-lg);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.limits-grid {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.limit-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: var(--text-sm);
}

.limit-label {
    color: var(--gray-600);
}

.limit-value {
    font-weight: 600;
    color: var(--gray-900);
}

/* Plan Actions */
.plan-action {
    text-align: center;
}

.plan-button {
    width: 100%;
    margin-bottom: var(--spacing-md);
    min-height: 48px;
}

.trial-note {
    font-size: var(--text-xs);
    color: var(--gray-500);
    margin: 0;
}

/* Feature Comparison */
.feature-comparison {
    padding: var(--spacing-4xl) 0;
    background: var(--gray-50);
}

.section-header {
    text-align: center;
    margin-bottom: var(--spacing-2xl);
}

.section-title {
    font-size: var(--text-3xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-lg);
}

.section-description {
    font-size: var(--text-lg);
    color: var(--gray-600);
    max-width: 600px;
    margin: 0 auto;
}

.comparison-table-container {
    overflow-x: auto;
    border-radius: var(--radius-2xl);
    box-shadow: var(--shadow-lg);
    background: var(--surface);
}

.comparison-table {
    width: 100%;
    border-collapse: collapse;
    min-width: 800px;
}

.comparison-table th,
.comparison-table td {
    padding: var(--spacing-lg);
    text-align: center;
    border-bottom: 1px solid var(--gray-200);
}

.comparison-table th {
    background: var(--gray-100);
    font-weight: 700;
    color: var(--gray-900);
    position: sticky;
    top: 0;
    z-index: 10;
}

.feature-column {
    text-align: left !important;
    font-weight: 600;
    min-width: 250px;
}

.plan-column {
    min-width: 150px;
}

.plan-column.professional {
    background: var(--primary-50);
    position: relative;
}

.popular-indicator {
    display: block;
    font-size: var(--text-xs);
    color: var(--primary-600);
    font-weight: 600;
    text-transform: uppercase;
    margin-top: var(--spacing-xs);
}

.category-header td {
    background: var(--gray-100);
    font-weight: 700;
    color: var(--gray-900);
    text-align: left;
    padding: var(--spacing-md) var(--spacing-lg);
}

.check-icon {
    color: var(--success);
}

.x-icon {
    color: var(--gray-400);
}

.feature-limit {
    font-size: var(--text-sm);
    color: var(--gray-600);
    padding: var(--spacing-xs) var(--spacing-sm);
    background: var(--gray-100);
    border-radius: var(--radius-sm);
}

.feature-unlimited {
    font-size: var(--text-sm);
    color: var(--success);
    font-weight: 600;
}

/* FAQ Section */
.pricing-faq {
    padding: var(--spacing-4xl) 0;
}

.faq-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: var(--spacing-2xl);
    margin-top: var(--spacing-2xl);
}

.faq-item {
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-xl);
    overflow: hidden;
    background: var(--surface);
}

.faq-question {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-xl);
    background: none;
    border: none;
    font-size: var(--text-base);
    font-weight: 600;
    color: var(--gray-900);
    cursor: pointer;
    text-align: left;
    transition: all var(--transition-fast) var(--easing-standard);
}

.faq-question:hover {
    background: var(--gray-50);
}

.faq-question svg {
    transition: transform var(--transition-fast) var(--easing-standard);
    color: var(--gray-500);
    flex-shrink: 0;
}

.faq-answer {
    padding: 0 var(--spacing-xl) var(--spacing-xl);
    border-top: 1px solid var(--gray-100);
}

.faq-answer p {
    margin: 0;
    color: var(--gray-600);
    line-height: 1.6;
}

/* CTA Section */
.pricing-cta {
    padding: var(--spacing-4xl) 0;
    background: linear-gradient(135deg, var(--primary-500) 0%, var(--secondary-500) 100%);
    color: white;
    text-align: center;
}

.cta-title {
    font-size: var(--text-3xl);
    font-weight: 700;
    margin: 0 0 var(--spacing-lg);
}

.cta-description {
    font-size: var(--text-lg);
    margin: 0 0 var(--spacing-2xl);
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
    opacity: 0.9;
}

.cta-actions {
    display: flex;
    gap: var(--spacing-lg);
    justify-content: center;
    margin-bottom: var(--spacing-xl);
}

.cta-features {
    display: flex;
    gap: var(--spacing-xl);
    justify-content: center;
    flex-wrap: wrap;
}

.cta-features .feature-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--text-sm);
    opacity: 0.9;
}

/* Loading Spinner */
.loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    display: inline-block;
    margin-right: var(--spacing-xs);
}

/* Responsive Design */
@media (max-width: 1024px) {
    .plans-grid {
        grid-template-columns: 1fr;
        gap: var(--spacing-xl);
    }
    
    .pricing-card.popular {
        transform: none;
    }
    
    .billing-toggle {
        flex-direction: column;
        gap: var(--spacing-md);
    }
    
    .faq-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 640px) {
    .hero-title {
        font-size: 2rem;
    }
    
    .pricing-hero {
        padding: var(--spacing-2xl) 0;
    }
    
    .pricing-plans,
    .feature-comparison,
    .pricing-faq,
    .pricing-cta {
        padding: var(--spacing-2xl) 0;
    }
    
    .plans-grid {
        grid-template-columns: 1fr;
        gap: var(--spacing-lg);
    }
    
    .pricing-card {
        padding: var(--spacing-xl);
    }
    
    .cta-actions {
        flex-direction: column;
        align-items: center;
    }
    
    .cta-features {
        flex-direction: column;
        align-items: center;
    }
    
    .comparison-table th,
    .comparison-table td {
        padding: var(--spacing-md);
    }
}

/* Dark Mode */
[data-theme="dark"] .pricing-page {
    background: var(--gray-900);
}

[data-theme="dark"] .hero-title,
[data-theme="dark"] .section-title,
[data-theme="dark"] .cta-title {
    color: var(--gray-100);
}

[data-theme="dark"] .hero-description,
[data-theme="dark"] .section-description {
    color: var(--gray-300);
}

[data-theme="dark"] .pricing-card {
    background: var(--gray-800);
    border-color: var(--gray-700);
}

[data-theme="dark"] .plan-icon {
    background: var(--gray-700);
    color: var(--primary-400);
}

[data-theme="dark"] .plan-name {
    color: var(--gray-100);
}

[data-theme="dark"] .price-amount {
    color: var(--gray-100);
}

[data-theme="dark"] .comparison-table th {
    background: var(--gray-800);
    color: var(--gray-200);
}

[data-theme="dark"] .comparison-table td {
    background: var(--gray-850);
    border-color: var(--gray-700);
}

[data-theme="dark"] .feature-comparison {
    background: var(--gray-850);
}

[data-theme="dark"] .faq-item {
    background: var(--gray-800);
    border-color: var(--gray-700);
}

[data-theme="dark"] .faq-question {
    color: var(--gray-200);
}

[data-theme="dark"] .faq-question:hover {
    background: var(--gray-750);
}
</style>

<?php get_footer(); ?>