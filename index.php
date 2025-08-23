<?php
/**
 * Stock Scanner Theme Main Template v3.0.0
 * ULTRA-MODERN ENHANCED HOMEPAGE
 * Premium design with glassmorphism, advanced animations, and professional UI components
 */

get_header(); ?>

<div class="stock-scanner-homepage enhanced-layout">
    
    <!-- Premium Hero Section with Advanced Effects -->
    <section class="hero-section gradient-hero animate-fade-in" itemscope itemtype="https://schema.org/WebPageElement">
        <div class="container">
            <div class="hero-content scroll-reveal">
                <h1 class="hero-title text-gradient animate-scale-in">
                    <?php _e('Professional Stock Scanner', 'stock-scanner'); ?>
                </h1>
                <p class="hero-subtitle animate-fade-in">
                    <?php _e('Advanced stock analysis tools for informed investment decisions. Real-time data, powerful screening, and comprehensive portfolio tracking with enterprise-grade features.', 'stock-scanner'); ?>
                </p>
                
                <?php if (is_user_logged_in()): ?>
                    <div class="hero-actions animate-slide-up">
                        <a href="/dashboard/" class="btn btn-secondary btn-lg glass shadow-glass">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                                <rect x="3" y="3" width="7" height="7"></rect>
                                <rect x="14" y="3" width="7" height="7"></rect>
                                <rect x="14" y="14" width="7" height="7"></rect>
                                <rect x="3" y="14" width="7" height="7"></rect>
                            </svg>
                            <?php _e('Go to Dashboard', 'stock-scanner'); ?>
                        </a>
                        <a href="/stock-screener/" class="btn btn-outline btn-lg glass">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                                <circle cx="11" cy="11" r="8"></circle>
                                <path d="M21 21l-4.35-4.35"></path>
                            </svg>
                            <?php _e('Start Scanning', 'stock-scanner'); ?>
                        </a>
                    </div>
                <?php else: ?>
                    <div class="hero-actions animate-slide-up">
                        <a href="<?php echo wp_registration_url(); ?>" class="btn btn-secondary btn-lg glass shadow-glass">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                                <star class="star-icon">⭐</star>
                                <polygon points="12,2 15.09,8.26 22,9 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9 8.91,8.26"></polygon>
                            </svg>
                            <?php _e('Start 7‑Day Trial for $1', 'stock-scanner'); ?>
                        </a>
                        <a href="<?php echo wp_login_url(); ?>" class="btn btn-outline btn-lg glass">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                                <polyline points="10,17 15,12 10,7"></polyline>
                                <line x1="15" y1="12" x2="3" y2="12"></line>
                            </svg>
                            <?php _e('Login', 'stock-scanner'); ?>
                        </a>
                    </div>
                <?php endif; ?>
                
                <!-- Enhanced Trust Indicators -->
                <div class="hero-trust-indicators animate-fade-in">
                    <div class="trust-item glass">
                        <span class="trust-icon">✅</span>
                        <span><?php _e('Professional Platform', 'stock-scanner'); ?></span>
                    </div>
                    <div class="trust-item glass">
                        <span class="trust-icon">🛡️</span>
                        <span><?php _e('Bank-Level Security', 'stock-scanner'); ?></span>
                    </div>
                    <div class="trust-item glass">
                        <span class="trust-icon">⚡</span>
                        <span><?php _e('Real-time Data', 'stock-scanner'); ?></span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Enhanced Dashboard for Logged-in Users -->
    <?php if (is_user_logged_in()): ?>
        <section class="dashboard-section glass-section animate-fade-in">
            <div class="container">
                <div class="section-intro scroll-reveal">
                    <h2 class="section-title text-gradient"><?php _e('Your Dashboard', 'stock-scanner'); ?></h2>
                    <p class="section-subtitle"><?php _e('Real-time overview of your portfolio and market activity', 'stock-scanner'); ?></p>
                </div>
                <?php echo do_shortcode('[stock_scanner_dashboard]'); ?>
            </div>
        </section>
    <?php endif; ?>

    <!-- Premium Features Section with Advanced Cards -->
    <section class="features-section glass-section">
        <div class="container">
            <div class="section-intro scroll-reveal">
                <h2 class="section-title text-gradient"><?php _e('Powerful Features', 'stock-scanner'); ?></h2>
                <p class="section-subtitle"><?php _e('Enterprise-grade tools designed for professional traders and investors', 'stock-scanner'); ?></p>
            </div>
            
            <div class="features-grid">
                <div class="feature-card glass-card scroll-reveal">
                    <div class="feature-icon gradient-primary">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
                        </svg>
                    </div>
                    <h3><?php _e('Real-time Data', 'stock-scanner'); ?></h3>
                    <p><?php _e('Get live stock quotes and market data updated in real-time with sub-second latency for informed trading decisions.', 'stock-scanner'); ?></p>
                    <div class="feature-stats glass">
                        <span class="stat-item">
                            <strong>< 100ms</strong> Latency
                        </span>
                        <span class="stat-item">
                            <strong>99.9%</strong> Uptime
                        </span>
                    </div>
                </div>
                
                <div class="feature-card glass-card scroll-reveal">
                    <div class="feature-icon gradient-primary">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"></circle>
                            <path d="M21 21l-4.35-4.35"></path>
                        </svg>
                    </div>
                    <h3><?php _e('Advanced Scanning', 'stock-scanner'); ?></h3>
                    <p><?php _e('Use powerful filters and technical indicators to find stocks that match your specific criteria with AI-powered insights.', 'stock-scanner'); ?></p>
                    <div class="feature-stats glass">
                        <span class="stat-item">
                            <strong>50+</strong> Indicators
                        </span>
                        <span class="stat-item">
                            <strong>AI</strong> Powered
                        </span>
                    </div>
                </div>
                
                <div class="feature-card glass-card scroll-reveal">
                    <div class="feature-icon gradient-primary">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="12" y1="1" x2="12" y2="23"></line>
                            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                        </svg>
                    </div>
                    <h3><?php _e('Portfolio Tracking', 'stock-scanner'); ?></h3>
                    <p><?php _e('Monitor your investments with comprehensive portfolio analysis, performance tracking, and risk management tools.', 'stock-scanner'); ?></p>
                    <div class="feature-stats glass">
                        <span class="stat-item">
                            <strong>360°</strong> Analysis
                        </span>
                        <span class="stat-item">
                            <strong>Risk</strong> Metrics
                        </span>
                    </div>
                </div>
                
                <div class="feature-card glass-card scroll-reveal">
                    <div class="feature-icon gradient-primary">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                            <line x1="8" y1="21" x2="16" y2="21"></line>
                            <line x1="12" y1="17" x2="12" y2="21"></line>
                        </svg>
                    </div>
                    <h3><?php _e('Lightning Fast', 'stock-scanner'); ?></h3>
                    <p><?php _e('Experience blazing-fast performance with our optimized platform, advanced caching, and global CDN infrastructure.', 'stock-scanner'); ?></p>
                    <div class="feature-stats glass">
                        <span class="stat-item">
                            <strong>< 2s</strong> Load Time
                        </span>
                        <span class="stat-item">
                            <strong>Global</strong> CDN
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Enhanced Statistics Section -->
    <section class="stats-section gradient-hero">
        <div class="container">
            <div class="section-intro scroll-reveal">
                <h2 class="section-title"><?php _e('Join Our Growing Community', 'stock-scanner'); ?></h2>
                <p class="section-subtitle"><?php _e('Professional traders and investors trust our platform worldwide', 'stock-scanner'); ?></p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-item glass-card scroll-reveal">
                    <div class="stat-number">Professional</div>
                    <div class="stat-label"><?php _e('Trading Platform', 'stock-scanner'); ?></div>
                    <div class="stat-growth">Enterprise grade</div>
                </div>
                <div class="stat-item glass-card scroll-reveal">
                    <div class="stat-number">Real-time</div>
                    <div class="stat-label"><?php _e('Market Data', 'stock-scanner'); ?></div>
                    <div class="stat-growth">Live updates</div>
                </div>
                <div class="stat-item glass-card scroll-reveal">
                    <div class="stat-number">24/7</div>
                    <div class="stat-label"><?php _e('Support', 'stock-scanner'); ?></div>
                    <div class="stat-growth">Expert team</div>
                </div>
                <div class="stat-item glass-card scroll-reveal">
                    <div class="stat-number">Secure</div>
                    <div class="stat-label"><?php _e('Platform', 'stock-scanner'); ?></div>
                    <div class="stat-growth">Bank-level security</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Premium Trial Promo Section -->
    <section class="trial-promo-section glass-section">
        <div class="container">
            <div class="trial-promo glass-card shadow-glass scroll-reveal">
                <div class="promo-content">
                    <div class="promo-badge glass gradient-primary">
                        <span class="badge-icon">🎯</span>
                        <span><?php _e('Limited Time Offer', 'stock-scanner'); ?></span>
                    </div>
                    <h2 class="section-title text-gradient"><?php _e('Try Premium for 7 Days — Only $1', 'stock-scanner'); ?></h2>
                    <p class="promo-description">
                        <?php _e('Full access to all Premium features including real‑time data, advanced screening, and portfolio tools. Cancel anytime with one click.', 'stock-scanner'); ?>
                    </p>
                    
                    <div class="promo-features">
                        <div class="promo-feature glass">
                            <span class="feature-check">✅</span>
                            <span><?php _e('Unlimited real-time quotes', 'stock-scanner'); ?></span>
                        </div>
                        <div class="promo-feature glass">
                            <span class="feature-check">✅</span>
                            <span><?php _e('Advanced screening tools', 'stock-scanner'); ?></span>
                        </div>
                        <div class="promo-feature glass">
                            <span class="feature-check">✅</span>
                            <span><?php _e('Portfolio analytics', 'stock-scanner'); ?></span>
                        </div>
                        <div class="promo-feature glass">
                            <span class="feature-check">✅</span>
                            <span><?php _e('Premium research reports', 'stock-scanner'); ?></span>
                        </div>
                    </div>
                    
                    <div class="cta-buttons">
                        <?php if (!is_user_logged_in()): ?>
                            <a href="<?php echo wp_registration_url(); ?>" class="btn btn-primary btn-lg gradient-primary shadow-glass">
                                <span class="btn-text"><?php _e('Start 7‑Day Trial for $1', 'stock-scanner'); ?></span>
                                <span class="btn-subtext"><?php _e('Then $29/month', 'stock-scanner'); ?></span>
                            </a>
                            <a href="/compare-plans/" class="btn btn-outline btn-lg glass">
                                <?php _e('Compare All Plans', 'stock-scanner'); ?>
                            </a>
                        <?php else: ?>
                            <a href="/premium-plans/" class="btn btn-primary btn-lg gradient-primary shadow-glass">
                                <span class="btn-text"><?php _e('Upgrade for $1 Trial', 'stock-scanner'); ?></span>
                                <span class="btn-subtext"><?php _e('7 days to explore', 'stock-scanner'); ?></span>
                            </a>
                            <a href="/compare-plans/" class="btn btn-outline btn-lg glass">
                                <?php _e('View All Features', 'stock-scanner'); ?>
                            </a>
                        <?php endif; ?>
                    </div>
                    
                    <p class="trial-terms">
                        <?php _e('$1 covers 7 days of Premium access. Standard pricing applies unless cancelled. No hidden fees.', 'stock-scanner'); ?>
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- Enhanced Pricing Section -->
    <section class="pricing-section glass-section">
        <div class="container">
            <div class="section-intro scroll-reveal">
                <h2 class="section-title text-gradient"><?php _e('Choose Your Plan', 'stock-scanner'); ?></h2>
                <p class="section-subtitle"><?php _e('Flexible pricing options designed to grow with your trading needs', 'stock-scanner'); ?></p>
            </div>
            
            <!-- Enhanced Pricing Toggle -->
            <div class="pricing-toggle glass-card">
                <span class="toggle-label"><?php _e('Monthly', 'stock-scanner'); ?></span>
                <button class="toggle-switch" data-pricing-toggle>
                    <span class="toggle-slider"></span>
                </button>
                <span class="toggle-label">
                    <?php _e('Annual', 'stock-scanner'); ?> 
                    <span class="savings-badge gradient-primary"><?php _e('Save 20%', 'stock-scanner'); ?></span>
                </span>
            </div>
            
            <?php echo do_shortcode('[stock_scanner_pricing show_trial="true" highlight_plan="premium"]'); ?>
        </div>
    </section>

    <!-- Premium Testimonials Section -->
    <section class="testimonials-section gradient-hero">
        <div class="container">
            <div class="section-intro scroll-reveal">
                <h2 class="section-title"><?php _e('What Our Users Say', 'stock-scanner'); ?></h2>
                <p class="section-subtitle"><?php _e('Professional trading platform built for serious investors', 'stock-scanner'); ?></p>
            </div>
            
            <div class="testimonials-grid">
                <div class="testimonial-card glass-card scroll-reveal">
                    <div class="testimonial-rating">
                        <span class="stars">⭐⭐⭐⭐⭐</span>
                        <span class="rating-text">5.0</span>
                    </div>
                    <blockquote class="testimonial-quote">
                        "<?php _e('Professional-grade stock analysis platform with comprehensive features for serious traders and investors.', 'stock-scanner'); ?>"
                    </blockquote>
                    <div class="testimonial-author">
                        <div class="author-avatar glass">
                            <span>PT</span>
                        </div>
                        <div class="author-info">
                            <cite class="author-name"><?php _e('Professional Trader', 'stock-scanner'); ?></cite>
                            <span class="author-role"><?php _e('Investment Professional', 'stock-scanner'); ?></span>
                        </div>
                    </div>
                </div>
                
                <div class="testimonial-card glass-card scroll-reveal">
                    <div class="testimonial-rating">
                        <span class="stars">⭐⭐⭐⭐⭐</span>
                        <span class="rating-text">5.0</span>
                    </div>
                    <blockquote class="testimonial-quote">
                        "<?php _e('Advanced portfolio tracking and analysis tools provide detailed insights for investment decision making.', 'stock-scanner'); ?>"
                    </blockquote>
                    <div class="testimonial-author">
                        <div class="author-avatar glass">
                            <span>IA</span>
                        </div>
                        <div class="author-info">
                            <cite class="author-name"><?php _e('Investment Advisor', 'stock-scanner'); ?></cite>
                            <span class="author-role"><?php _e('Financial Services', 'stock-scanner'); ?></span>
                        </div>
                    </div>
                </div>
                
                <div class="testimonial-card glass-card scroll-reveal">
                    <div class="testimonial-rating">
                        <span class="stars">⭐⭐⭐⭐⭐</span>
                        <span class="rating-text">5.0</span>
                    </div>
                    <blockquote class="testimonial-quote">
                        "<?php _e('Enterprise-grade platform with excellent performance, intuitive interface, and professional support team.', 'stock-scanner'); ?>"
                    </blockquote>
                    <div class="testimonial-author">
                        <div class="author-avatar glass">
                            <span>PM</span>
                        </div>
                        <div class="author-info">
                            <cite class="author-name"><?php _e('Portfolio Manager', 'stock-scanner'); ?></cite>
                            <span class="author-role"><?php _e('Asset Management', 'stock-scanner'); ?></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Enhanced CTA Section -->
    <section class="cta-section gradient-hero">
        <div class="container">
            <div class="cta-content glass-card shadow-glass scroll-reveal">
                <div class="cta-icon gradient-primary">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
                    </svg>
                </div>
                <h2 class="cta-title"><?php _e('Ready to Start Professional Trading?', 'stock-scanner'); ?></h2>
                <p class="cta-description"><?php _e('Join thousands of successful traders who trust our platform for their investment decisions. Start your journey today.', 'stock-scanner'); ?></p>
                
                <div class="cta-actions">
                    <?php if (!is_user_logged_in()): ?>
                        <a href="<?php echo wp_registration_url(); ?>" class="btn btn-primary btn-lg gradient-primary shadow-glass">
                            <span class="btn-icon">🚀</span>
                            <span class="btn-text"><?php _e('Start 7‑Day Trial for $1', 'stock-scanner'); ?></span>
                        </a>
                        <a href="/demo/" class="btn btn-outline btn-lg glass">
                            <span class="btn-icon">▶️</span>
                            <span class="btn-text"><?php _e('Watch Demo', 'stock-scanner'); ?></span>
                        </a>
                    <?php else: ?>
                        <a href="/premium-plans/" class="btn btn-primary btn-lg gradient-primary shadow-glass">
                            <span class="btn-icon">⭐</span>
                            <span class="btn-text"><?php _e('Upgrade Your Plan', 'stock-scanner'); ?></span>
                        </a>
                        <a href="/dashboard/" class="btn btn-outline btn-lg glass">
                            <span class="btn-icon">📊</span>
                            <span class="btn-text"><?php _e('Go to Dashboard', 'stock-scanner'); ?></span>
                        </a>
                    <?php endif; ?>
                </div>
                
                <div class="cta-guarantee glass">
                    <span class="guarantee-icon">🛡️</span>
                    <span class="guarantee-text"><?php _e('30-day money-back guarantee • Cancel anytime', 'stock-scanner'); ?></span>
                </div>
            </div>
        </div>
    </section>

</div>

<!-- Add custom JavaScript for enhanced interactions -->
<script>
// Enhanced page-specific interactions
document.addEventListener('DOMContentLoaded', function() {
    // Enhanced testimonial carousel (if needed)
    const testimonials = document.querySelectorAll('.testimonial-card');
    testimonials.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.2}s`;
    });
    
    // Pricing toggle functionality
    const pricingToggle = document.querySelector('[data-pricing-toggle]');
    if (pricingToggle) {
        pricingToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            // Add pricing toggle logic here
            console.log('Pricing toggle clicked - implement annual/monthly switch');
        });
    }
});
</script>

<?php get_footer(); ?>