<?php
/**
 * Template Name: Stock Scanner Pro - Homepage
 * 
 * Professional homepage with Zatra theme styling
 */

get_header(); ?>

<main id="main" class="wp-block-group alignfull is-layout-constrained wp-block-group-is-layout-constrained" style="margin-top:0">
    
    <!-- Hero Section -->
    <section class="wp-block-group alignfull hero-section has-custom-color-1-background-color has-background is-layout-constrained wp-block-group-is-layout-constrained">
        <div class="wp-block-group__inner-container">
            <div class="container">
                <div class="hero-content">
                    <h1 class="wp-block-heading has-text-align-center has-white-color has-text-color has-huge-font-size">
                        Professional Stock Analysis Made Simple
                    </h1>
                    <p class="hero-subtitle has-text-align-center">
                        Get real-time stock data, advanced charts, and powerful screening tools to make informed investment decisions.
                    </p>
                    
                    <?php if (!is_user_logged_in()): ?>
                        <div class="hero-cta wp-block-buttons is-layout-flex wp-block-buttons-is-layout-flex">
                            <div class="wp-block-button">
                                <a class="wp-block-button__link btn btn-primary btn-large" href="/signup/">Start Free Trial</a>
                            </div>
                            <div class="wp-block-button is-style-outline">
                                <a class="wp-block-button__link btn btn-secondary btn-large" href="/premium-plans/">View Plans</a>
                            </div>
                        </div>
                    <?php else: ?>
                        <div class="hero-cta wp-block-buttons is-layout-flex wp-block-buttons-is-layout-flex">
                            <div class="wp-block-button">
                                <a class="wp-block-button__link btn btn-primary btn-large" href="/dashboard/">Go to Dashboard</a>
                            </div>
                            <?php if (get_user_tier() === 'free'): ?>
                                <div class="wp-block-button is-style-outline">
                                    <a class="wp-block-button__link btn btn-secondary btn-large" href="/premium-plans/">Upgrade Now</a>
                                </div>
                            <?php endif; ?>
                        </div>
                    <?php endif; ?>
                </div>
                
                <div class="hero-stats">
                    <div class="stat-item">
                        <span class="stat-number">10,000+</span>
                        <span class="stat-label">Stocks Tracked</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">Real-time</span>
                        <span class="stat-label">Market Data</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">24/7</span>
                        <span class="stat-label">Support</span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="wp-block-group alignfull features-section has-custom-color-4-background-color has-background is-layout-constrained wp-block-group-is-layout-constrained">
        <div class="wp-block-group__inner-container">
            <div class="container">
                <h2 class="wp-block-heading has-text-align-center has-large-font-size">Powerful Features for Every Investor</h2>
                
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="home-icon-wrap home-icon-wrap-1">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <h3>Advanced Charts</h3>
                        <p>Interactive charts with technical indicators, candlestick patterns, and volume analysis.</p>
                        <?php if (get_user_tier() === 'free'): ?>
                            <span class="feature-badge">Premium</span>
                        <?php endif; ?>
                    </div>
                    
                    <div class="feature-card">
                        <div class="home-icon-wrap home-icon-wrap-2">
                            <i class="fas fa-search"></i>
                        </div>
                        <h3>Stock Screener</h3>
                        <p>Filter stocks by price, volume, market cap, P/E ratio, and dozens of other criteria.</p>
                    </div>
                    
                    <div class="feature-card">
                        <div class="home-icon-wrap home-icon-wrap-3">
                            <i class="fas fa-chart-area"></i>
                        </div>
                        <h3>Real-time Data</h3>
                        <p>Live market data with instant updates and price alerts for your watchlist.</p>
                        <?php if (get_user_tier() === 'free'): ?>
                            <span class="feature-badge">Premium</span>
                        <?php endif; ?>
                    </div>
                    
                    <div class="feature-card">
                        <div class="home-icon-wrap home-icon-wrap-1">
                            <i class="fas fa-briefcase"></i>
                        </div>
                        <h3>Portfolio Tracking</h3>
                        <p>Track your investments with performance analytics and profit/loss calculations.</p>
                    </div>
                    
                    <div class="feature-card">
                        <div class="home-icon-wrap home-icon-wrap-2">
                            <i class="fas fa-newspaper"></i>
                        </div>
                        <h3>Market News</h3>
                        <p>Stay informed with personalized news feeds and market analysis.</p>
                    </div>
                    
                    <div class="feature-card">
                        <div class="home-icon-wrap home-icon-wrap-3">
                            <i class="fas fa-bolt"></i>
                        </div>
                        <h3>Fast & Reliable</h3>
                        <p>Lightning-fast data delivery with 99.9% uptime guarantee.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Pricing Preview -->
    <section class="wp-block-group alignfull pricing-preview is-layout-constrained wp-block-group-is-layout-constrained">
        <div class="wp-block-group__inner-container">
            <div class="container">
                <h2 class="wp-block-heading has-text-align-center has-large-font-size">Choose Your Plan</h2>
                
                <div class="pricing-cards">
                    <?php 
                    $user_tier = get_user_tier();
                    $pricing_plans = array(
                        'free' => array('name' => 'Free', 'price' => '$0', 'calls' => '15', 'watchlist' => '3', 'features' => array('Basic charts', 'Delayed data')),
                        'basic' => array('name' => 'Basic', 'price' => '$24.99', 'calls' => '1,500', 'watchlist' => '25', 'features' => array('Real-time data', 'Advanced charts', 'Data export')),
                        'pro' => array('name' => 'Pro', 'price' => '$49.99', 'calls' => '5,000', 'watchlist' => '100', 'features' => array('API access', 'Custom alerts', 'Priority support')),
                        'enterprise' => array('name' => 'Enterprise', 'price' => '$79.99', 'calls' => 'Unlimited', 'watchlist' => 'Unlimited', 'features' => array('White-label', 'Dedicated support', 'SLA guarantee'))
                    );
                    
                    foreach ($pricing_plans as $tier => $plan): 
                        $is_current = ($user_tier === $tier);
                        $is_featured = ($tier === 'basic');
                    ?>
                        <div class="pricing-card <?php echo $is_featured ? 'featured' : ''; ?> <?php echo $is_current ? 'current' : ''; ?>">
                            <?php if ($is_featured): ?>
                                <div class="plan-badge">Most Popular</div>
                            <?php endif; ?>
                            
                            <div class="plan-header">
                                <h3><?php echo $plan['name']; ?></h3>
                                <div class="price">
                                    <span class="amount"><?php echo $plan['price']; ?></span>
                                    <span class="period">/month</span>
                                </div>
                            </div>
                            
                            <ul class="features-list">
                                <li><i class="fas fa-check"></i> <?php echo $plan['calls']; ?> API calls/month</li>
                                <li><i class="fas fa-check"></i> <?php echo $plan['watchlist']; ?> watchlist items</li>
                                <?php foreach ($plan['features'] as $feature): ?>
                                    <li><i class="fas fa-check"></i> <?php echo $feature; ?></li>
                                <?php endforeach; ?>
                            </ul>
                            
                            <div class="plan-action">
                                <?php if ($is_current): ?>
                                    <button class="btn btn-outline" disabled>Current Plan</button>
                                <?php elseif ($tier === 'free'): ?>
                                    <span class="text-secondary">Always Free</span>
                                <?php else: ?>
                                    <a href="/premium-plans/" class="btn btn-primary">Upgrade Now</a>
                                <?php endif; ?>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
                
                <div class="pricing-cta wp-block-buttons is-layout-flex wp-block-buttons-is-layout-flex">
                    <div class="wp-block-button">
                        <a href="/premium-plans/" class="wp-block-button__link btn btn-large">View All Plans</a>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Testimonials -->
    <section class="wp-block-group alignfull testimonials-section has-custom-color-4-background-color has-background is-layout-constrained wp-block-group-is-layout-constrained">
        <div class="wp-block-group__inner-container">
            <div class="container">
                <h2 class="wp-block-heading has-text-align-center has-large-font-size">What Our Users Say</h2>
                
                <div class="testimonials-grid">
                    <div class="testimonial-card">
                        <div class="testimonial-content">
                            <p>"The real-time data and advanced charts have completely transformed my trading strategy. Highly recommended!"</p>
                        </div>
                        <div class="testimonial-author">
                            <strong>Sarah Johnson</strong>
                            <span>Day Trader</span>
                        </div>
                    </div>
                    
                    <div class="testimonial-card">
                        <div class="testimonial-content">
                            <p>"Best stock screening tool I've used. The filtering options are incredibly detailed and accurate."</p>
                        </div>
                        <div class="testimonial-author">
                            <strong>Michael Chen</strong>
                            <span>Investment Advisor</span>
                        </div>
                    </div>
                    
                    <div class="testimonial-card">
                        <div class="testimonial-content">
                            <p>"The portfolio tracking feature helps me stay on top of all my investments. Great value for money."</p>
                        </div>
                        <div class="testimonial-author">
                            <strong>Emily Rodriguez</strong>
                            <span>Retail Investor</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

</main>

<script>
// Add interactive elements with Zatra theme compatibility
document.addEventListener('DOMContentLoaded', function() {
    // Animate stats on scroll
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.stat-item, .feature-card, .testimonial-card').forEach(el => {
        observer.observe(el);
    });
});
</script>

<?php get_footer(); ?>