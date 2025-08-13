<?php
/**
 * Template Name: Premium Plans
 * 
 * The template for displaying premium subscription plans
 */

get_header(); 
?>

<div class="premium-plans-container">
    <!-- Hero Section -->
    <div class="hero-section">
        <div class="container">
            <div class="hero-content">
                <h1 class="hero-title">Unlock Premium Features</h1>
                <p class="hero-subtitle">Choose the perfect plan to supercharge your trading and investment analysis</p>
                
                <!-- Billing Toggle -->
                <div class="billing-toggle">
                    <span class="toggle-label monthly active">Monthly</span>
                    <label class="toggle-switch">
                        <input type="checkbox" id="billingToggle">
                        <span class="slider"></span>
                    </label>
                    <span class="toggle-label yearly">Yearly <span class="save-badge">Save 20%</span></span>
                </div>
            </div>
        </div>
    </div>

    <!-- Pricing Cards -->
    <div class="pricing-section">
        <div class="container">
            <div class="pricing-grid">
                <!-- Free Plan -->
                <div class="pricing-card free-plan">
                    <div class="plan-header">
                        <h3 class="plan-name">Free Plan</h3>
                        <div class="plan-price">
                            <span class="currency">$</span>
                            <span class="amount">0</span>
                            <span class="period">/month</span>
                        </div>
                        <p class="plan-description">Perfect for getting started with basic market analysis</p>
                    </div>
                    
                    <div class="plan-features">
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Basic stock lookup</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Market overview dashboard</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Limited watchlist (5 stocks)</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Basic market news</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Community support</span>
                        </div>
                    </div>
                    
                    <div class="plan-action">
                        <?php if (!is_user_logged_in()): ?>
                            <a href="/signup/" class="btn btn-outline">Get Started Free</a>
                        <?php else: ?>
                            <a href="/dashboard/" class="btn btn-outline">Access Dashboard</a>
                        <?php endif; ?>
                    </div>
                </div>

                <!-- Pro Plan -->
                <div class="pricing-card pro-plan popular">
                    <div class="popular-badge">Most Popular</div>
                    <div class="plan-header">
                        <h3 class="plan-name">Pro Plan</h3>
                        <div class="plan-price">
                            <span class="currency">$</span>
                            <span class="amount monthly-price">29</span>
                            <span class="amount yearly-price" style="display: none;">23</span>
                            <span class="period monthly-period">/month</span>
                            <span class="period yearly-period" style="display: none;">/month</span>
                        </div>
                        <p class="plan-description">Advanced tools for serious traders and investors</p>
                    </div>
                    
                    <div class="plan-features">
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span><strong>Everything in Free</strong></span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Advanced stock screener</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Unlimited watchlists</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Portfolio analytics & tracking</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Real-time price alerts</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Personalized news feed</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Priority email support</span>
                        </div>
                    </div>
                    
                    <div class="plan-action">
                        <button class="btn btn-primary" onclick="selectPlan('pro')">
                            Choose Pro Plan
                        </button>
                    </div>
                </div>

                <!-- Enterprise Plan -->
                <div class="pricing-card enterprise-plan">
                    <div class="plan-header">
                        <h3 class="plan-name">Enterprise</h3>
                        <div class="plan-price">
                            <span class="currency">$</span>
                            <span class="amount monthly-price">99</span>
                            <span class="amount yearly-price" style="display: none;">79</span>
                            <span class="period monthly-period">/month</span>
                            <span class="period yearly-period" style="display: none;">/month</span>
                        </div>
                        <p class="plan-description">Professional-grade tools for institutional use</p>
                    </div>
                    
                    <div class="plan-features">
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span><strong>Everything in Pro</strong></span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>AI-powered market insights</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Advanced portfolio optimization</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Custom API access</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>White-label solutions</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>Dedicated account manager</span>
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check"></i>
                            <span>24/7 phone support</span>
                        </div>
                    </div>
                    
                    <div class="plan-action">
                        <button class="btn btn-primary" onclick="selectPlan('enterprise')">
                            Choose Enterprise
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Feature Comparison -->
    <div class="comparison-section">
        <div class="container">
            <h2 class="section-title">Feature Comparison</h2>
            <div class="comparison-table">
                <div class="table-header">
                    <div class="feature-col">Features</div>
                    <div class="plan-col">Free</div>
                    <div class="plan-col">Pro</div>
                    <div class="plan-col">Enterprise</div>
                </div>
                
                <div class="table-body">
                    <div class="feature-row">
                        <div class="feature-name">Stock Lookup & Basic Data</div>
                        <div class="feature-check"><i class="fas fa-check"></i></div>
                        <div class="feature-check"><i class="fas fa-check"></i></div>
                        <div class="feature-check"><i class="fas fa-check"></i></div>
                    </div>
                    
                    <div class="feature-row">
                        <div class="feature-name">Watchlist Limit</div>
                        <div class="feature-value">5 stocks</div>
                        <div class="feature-value">Unlimited</div>
                        <div class="feature-value">Unlimited</div>
                    </div>
                    
                    <div class="feature-row">
                        <div class="feature-name">Advanced Stock Screener</div>
                        <div class="feature-none"><i class="fas fa-times"></i></div>
                        <div class="feature-check"><i class="fas fa-check"></i></div>
                        <div class="feature-check"><i class="fas fa-check"></i></div>
                    </div>
                    
                    <div class="feature-row">
                        <div class="feature-name">Portfolio Analytics</div>
                        <div class="feature-none"><i class="fas fa-times"></i></div>
                        <div class="feature-check"><i class="fas fa-check"></i></div>
                        <div class="feature-check"><i class="fas fa-check"></i></div>
                    </div>
                    
                    <div class="feature-row">
                        <div class="feature-name">Real-time Alerts</div>
                        <div class="feature-none"><i class="fas fa-times"></i></div>
                        <div class="feature-check"><i class="fas fa-check"></i></div>
                        <div class="feature-check"><i class="fas fa-check"></i></div>
                    </div>
                    
                    <div class="feature-row">
                        <div class="feature-name">AI Market Insights</div>
                        <div class="feature-none"><i class="fas fa-times"></i></div>
                        <div class="feature-none"><i class="fas fa-times"></i></div>
                        <div class="feature-check"><i class="fas fa-check"></i></div>
                    </div>
                    
                    <div class="feature-row">
                        <div class="feature-name">API Access</div>
                        <div class="feature-none"><i class="fas fa-times"></i></div>
                        <div class="feature-none"><i class="fas fa-times"></i></div>
                        <div class="feature-check"><i class="fas fa-check"></i></div>
                    </div>
                    
                    <div class="feature-row">
                        <div class="feature-name">Support Level</div>
                        <div class="feature-value">Community</div>
                        <div class="feature-value">Email</div>
                        <div class="feature-value">24/7 Phone</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Testimonials -->
    <div class="testimonials-section">
        <div class="container">
            <h2 class="section-title">What Our Users Say</h2>
            <div class="testimonials-grid">
                <div class="testimonial-card">
                    <div class="testimonial-content">
                        <p>"Stock Scanner Pro has revolutionized my trading strategy. The advanced screener helps me find opportunities I would have missed otherwise."</p>
                    </div>
                    <div class="testimonial-author">
                        <div class="author-avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="author-info">
                            <h4>Sarah Johnson</h4>
                            <span>Day Trader</span>
                        </div>
                    </div>
                </div>
                
                <div class="testimonial-card">
                    <div class="testimonial-content">
                        <p>"The AI insights have been game-changing for our investment decisions. The Enterprise plan pays for itself with better portfolio performance."</p>
                    </div>
                    <div class="testimonial-author">
                        <div class="author-avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="author-info">
                            <h4>Michael Chen</h4>
                            <span>Investment Manager</span>
                        </div>
                    </div>
                </div>
                
                <div class="testimonial-card">
                    <div class="testimonial-content">
                        <p>"Clean interface, powerful features, and excellent support. Everything I need for professional stock analysis in one place."</p>
                    </div>
                    <div class="testimonial-author">
                        <div class="author-avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="author-info">
                            <h4>Emma Rodriguez</h4>
                            <span>Financial Advisor</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- FAQ Section -->
    <div class="faq-section">
        <div class="container">
            <h2 class="section-title">Frequently Asked Questions</h2>
            <div class="faq-grid">
                <div class="faq-item">
                    <button class="faq-question">
                        <span>Can I upgrade or downgrade my plan anytime?</span>
                        <i class="fas fa-chevron-down"></i>
                    </button>
                    <div class="faq-answer">
                        <p>Yes, you can upgrade or downgrade your plan at any time. Changes will be prorated and take effect immediately.</p>
                    </div>
                </div>
                
                <div class="faq-item">
                    <button class="faq-question">
                        <span>Is there a free trial for premium plans?</span>
                        <i class="fas fa-chevron-down"></i>
                    </button>
                    <div class="faq-answer">
                        <p>We offer a 14-day free trial for all premium plans. No credit card required to start your trial.</p>
                    </div>
                </div>
                
                <div class="faq-item">
                    <button class="faq-question">
                        <span>What payment methods do you accept?</span>
                        <i class="fas fa-chevron-down"></i>
                    </button>
                    <div class="faq-answer">
                        <p>We accept all major credit cards, PayPal, and bank transfers for Enterprise plans.</p>
                    </div>
                </div>
                
                <div class="faq-item">
                    <button class="faq-question">
                        <span>Can I cancel my subscription anytime?</span>
                        <i class="fas fa-chevron-down"></i>
                    </button>
                    <div class="faq-answer">
                        <p>Yes, you can cancel your subscription at any time. You'll continue to have access until the end of your billing period.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.premium-plans-container {
    background: #f8f9fa;
    min-height: 100vh;
}

/* Hero Section */
.hero-section {
    background: linear-gradient(135deg, #3685fb 0%, #2563eb 100%);
    color: white;
    padding: 4rem 0;
    text-align: center;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 700;
    margin: 0 0 1rem 0;
}

.hero-subtitle {
    font-size: 1.3rem;
    opacity: 0.9;
    margin: 0 0 3rem 0;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

/* Billing Toggle */
.billing-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin-top: 2rem;
}

.toggle-label {
    font-weight: 600;
    font-size: 1.1rem;
    opacity: 0.7;
    transition: opacity 0.2s;
}

.toggle-label.active {
    opacity: 1;
}

.toggle-switch {
    position: relative;
    display: inline-block;
    width: 60px;
    height: 34px;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255,255,255,0.3);
    transition: .4s;
    border-radius: 34px;
}

.slider:before {
    position: absolute;
    content: "";
    height: 26px;
    width: 26px;
    left: 4px;
    bottom: 4px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
}

input:checked + .slider {
    background-color: rgba(255,255,255,0.5);
}

input:checked + .slider:before {
    transform: translateX(26px);
}

.save-badge {
    background: #10b981;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-left: 0.5rem;
}

/* Pricing Section */
.pricing-section {
    padding: 4rem 0;
    margin-top: -2rem;
}

.pricing-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.pricing-card {
    background: white;
    border-radius: 20px;
    padding: 2.5rem;
    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    position: relative;
    transition: transform 0.3s, box-shadow 0.3s;
}

.pricing-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.pricing-card.popular {
    border: 3px solid #3685fb;
    transform: scale(1.05);
}

.popular-badge {
    position: absolute;
    top: -15px;
    left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, #3685fb 0%, #2563eb 100%);
    color: white;
    padding: 0.5rem 1.5rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9rem;
}

.plan-header {
    text-align: center;
    margin-bottom: 2rem;
}

.plan-name {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 1rem 0;
}

.plan-price {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: 0.25rem;
    margin-bottom: 1rem;
}

.currency {
    font-size: 1.5rem;
    font-weight: 600;
    color: #666;
}

.amount {
    font-size: 4rem;
    font-weight: 700;
    color: #3685fb;
    line-height: 1;
}

.period {
    font-size: 1.1rem;
    color: #666;
    margin-bottom: 0.5rem;
}

.plan-description {
    color: #666;
    margin: 0;
    line-height: 1.5;
}

.plan-features {
    margin-bottom: 2rem;
}

.feature-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 0;
    border-bottom: 1px solid #f0f0f0;
}

.feature-item:last-child {
    border-bottom: none;
}

.feature-item i {
    color: #10b981;
    font-size: 1.1rem;
    width: 16px;
}

.plan-action {
    margin-top: auto;
}

.btn {
    width: 100%;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-weight: 600;
    font-size: 1.1rem;
    cursor: pointer;
    border: none;
    transition: all 0.3s;
    text-decoration: none;
    display: inline-block;
    text-align: center;
    box-sizing: border-box;
}

.btn-primary {
    background: linear-gradient(135deg, #3685fb 0%, #2563eb 100%);
    color: white;
}

.btn-primary:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(54, 133, 251, 0.3);
}

.btn-outline {
    background: transparent;
    color: #3685fb;
    border: 2px solid #3685fb;
}

.btn-outline:hover {
    background: #3685fb;
    color: white;
}

/* Comparison Table */
.comparison-section {
    padding: 4rem 0;
    background: white;
}

.section-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 3rem 0;
}

.comparison-table {
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    overflow: hidden;
}

.table-header {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 1rem;
    padding: 1.5rem;
    background: #f8f9fa;
    font-weight: 700;
    color: #333;
}

.table-body {
    padding: 0;
}

.feature-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 1rem;
    padding: 1.5rem;
    border-bottom: 1px solid #f0f0f0;
    align-items: center;
}

.feature-row:last-child {
    border-bottom: none;
}

.feature-name {
    font-weight: 600;
    color: #333;
}

.feature-check {
    text-align: center;
    color: #10b981;
    font-size: 1.2rem;
}

.feature-none {
    text-align: center;
    color: #ef4444;
    font-size: 1.2rem;
}

.feature-value {
    text-align: center;
    color: #666;
    font-weight: 500;
}

/* Testimonials */
.testimonials-section {
    padding: 4rem 0;
    background: #f8f9fa;
}

.testimonials-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
}

.testimonial-card {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 10px 40px rgba(0,0,0,0.05);
}

.testimonial-content {
    margin-bottom: 1.5rem;
}

.testimonial-content p {
    font-style: italic;
    color: #666;
    line-height: 1.6;
    margin: 0;
}

.testimonial-author {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.author-avatar {
    width: 50px;
    height: 50px;
    background: #3685fb;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
}

.author-info h4 {
    margin: 0;
    font-weight: 600;
    color: #333;
}

.author-info span {
    color: #666;
    font-size: 0.9rem;
}

/* FAQ Section */
.faq-section {
    padding: 4rem 0;
    background: white;
}

.faq-grid {
    max-width: 800px;
    margin: 0 auto;
}

.faq-item {
    border-bottom: 1px solid #e1e5e9;
}

.faq-question {
    width: 100%;
    padding: 1.5rem 0;
    background: none;
    border: none;
    text-align: left;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1.1rem;
    font-weight: 600;
    color: #333;
}

.faq-question:hover {
    color: #3685fb;
}

.faq-question i {
    transition: transform 0.3s;
}

.faq-item.active .faq-question i {
    transform: rotate(180deg);
}

.faq-answer {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.faq-item.active .faq-answer {
    max-height: 200px;
}

.faq-answer p {
    padding: 0 0 1.5rem 0;
    margin: 0;
    color: #666;
    line-height: 1.6;
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 2.5rem;
    }
    
    .pricing-grid {
        grid-template-columns: 1fr;
    }
    
    .pricing-card.popular {
        transform: none;
    }
    
    .table-header,
    .feature-row {
        grid-template-columns: 1fr;
        text-align: center;
    }
    
    .feature-name {
        font-weight: 700;
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .testimonials-grid {
        grid-template-columns: 1fr;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializePricingPage();
});

function initializePricingPage() {
    // Billing toggle functionality
    const billingToggle = document.getElementById('billingToggle');
    const monthlyLabels = document.querySelectorAll('.toggle-label.monthly');
    const yearlyLabels = document.querySelectorAll('.toggle-label.yearly');
    const monthlyPrices = document.querySelectorAll('.monthly-price');
    const yearlyPrices = document.querySelectorAll('.yearly-price');
    const monthlyPeriods = document.querySelectorAll('.monthly-period');
    const yearlyPeriods = document.querySelectorAll('.yearly-period');
    
    billingToggle.addEventListener('change', function() {
        const isYearly = this.checked;
        
        // Update labels
        monthlyLabels.forEach(label => label.classList.toggle('active', !isYearly));
        yearlyLabels.forEach(label => label.classList.toggle('active', isYearly));
        
        // Update prices
        monthlyPrices.forEach(price => price.style.display = isYearly ? 'none' : 'inline');
        yearlyPrices.forEach(price => price.style.display = isYearly ? 'inline' : 'none');
        monthlyPeriods.forEach(period => period.style.display = isYearly ? 'none' : 'inline');
        yearlyPeriods.forEach(period => period.style.display = isYearly ? 'inline' : 'none');
    });
    
    // FAQ functionality
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        question.addEventListener('click', function() {
            const isActive = item.classList.contains('active');
            
            // Close all FAQ items
            faqItems.forEach(faq => faq.classList.remove('active'));
            
            // Open clicked item if it wasn't active
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });
}

function selectPlan(planType) {
    if (!<?php echo is_user_logged_in() ? 'true' : 'false'; ?>) {
        // Redirect to signup with plan parameter
        window.location.href = `/signup/?plan=${planType}`;
        return;
    }
    
    // Get billing type
    const isYearly = document.getElementById('billingToggle').checked;
    const billing = isYearly ? 'yearly' : 'monthly';
    
    // Redirect to PayPal checkout
    window.location.href = `/paypal-checkout/?plan=${planType}&billing=${billing}`;
}

// Add smooth scrolling to plan selection
function scrollToComparison() {
    document.querySelector('.comparison-section').scrollIntoView({
        behavior: 'smooth'
    });
}
</script>

<?php get_footer(); ?>