<?php
/**
 * Stock Scanner Theme Main Template
 * Professional homepage for stock scanning platform
 */

get_header(); ?>

<div class="stock-scanner-homepage">
    <!-- Hero Section -->
    <section class="hero-section" style="background: linear-gradient(135deg, var(--color-primary) 0%, #1d4ed8 100%); color: white; padding: var(--space-10) 0; text-align: center;">
        <div class="container">
            <div class="hero-content" style="max-width: 800px; margin: 0 auto;">
                <h1 class="hero-title" style="font-size: 3rem; font-weight: 800; margin-bottom: var(--space-4); line-height: 1.2;">
                    📈 Professional Stock Scanner
                </h1>
                <p class="hero-subtitle" style="font-size: 1.25rem; margin-bottom: var(--space-6); opacity: 0.9; line-height: 1.6;">
                    Advanced stock analysis tools for informed investment decisions. Real-time data, powerful screening, and comprehensive portfolio tracking.
                </p>
                <?php if (is_user_logged_in()): ?>
                    <div class="hero-actions" style="display: flex; gap: var(--space-4); justify-content: center; flex-wrap: wrap;">
                        <a href="/dashboard/" class="btn btn-secondary" style="background: white; color: var(--color-primary); border: 2px solid white; min-width: 180px;">🏠 Go to Dashboard</a>
                        <a href="/stock-screener/" class="btn btn-outline" style="border-color: white; color: white; min-width: 180px;">🔍 Start Scanning</a>
                    </div>
                <?php else: ?>
                    <div class="hero-actions" style="display: flex; gap: var(--space-4); justify-content: center; flex-wrap: wrap;">
                        <a href="<?php echo wp_registration_url(); ?>" class="btn btn-secondary" style="background: white; color: var(--color-primary); border: 2px solid white; min-width: 180px;">🚀 Start Free Trial</a>
                        <a href="<?php echo wp_login_url(); ?>" class="btn btn-outline" style="border-color: white; color: white; min-width: 180px;">🔑 Login</a>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </section>

    <!-- Dashboard for Logged-in Users -->
    <?php if (is_user_logged_in()): ?>
        <section class="dashboard-section" style="padding: var(--space-10) 0; background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);">
            <div class="container">
                <?php echo do_shortcode('[stock_scanner_dashboard]'); ?>
            </div>
        </section>
    <?php endif; ?>

    <!-- Features Section -->
    <section class="features-section" style="padding: var(--space-10) 0; background: <?php echo is_user_logged_in() ? 'white' : 'linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%)'; ?>;">
        <div class="container">
            <div style="text-align: center; margin-bottom: var(--space-8);">
                <h2 class="section-title" style="color: var(--color-text); font-size: 2.5rem; margin-bottom: var(--space-4);">⚡ Powerful Features</h2>
                <p style="color: var(--color-text-muted); font-size: 1.125rem; max-width: 600px; margin: 0 auto;">Everything you need to analyze stocks and make informed investment decisions</p>
            </div>
            <div class="features-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--space-6);">
                <div class="feature-card card p-6" style="text-align: center; transition: transform 0.2s ease, box-shadow 0.2s ease;">
                    <div class="feature-icon" style="font-size: 3rem; margin-bottom: var(--space-4); padding: var(--space-4); background: linear-gradient(135deg, var(--color-primary) 0%, #1d4ed8 100%); border-radius: 50%; color: white; display: inline-flex; align-items: center; justify-content: center; width: 80px; height: 80px;">📊</div>
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-3);">Real-time Data</h3>
                    <p style="color: var(--color-text-muted); line-height: 1.6;">Get live stock quotes and market data updated in real-time for informed trading decisions.</p>
                </div>
                <div class="feature-card card p-6" style="text-align: center; transition: transform 0.2s ease, box-shadow 0.2s ease;">
                    <div class="feature-icon" style="font-size: 3rem; margin-bottom: var(--space-4); padding: var(--space-4); background: linear-gradient(135deg, var(--color-primary) 0%, #1d4ed8 100%); border-radius: 50%; color: white; display: inline-flex; align-items: center; justify-content: center; width: 80px; height: 80px;">🔍</div>
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-3);">Advanced Scanning</h3>
                    <p style="color: var(--color-text-muted); line-height: 1.6;">Use powerful filters and technical indicators to find stocks that match your criteria.</p>
                </div>
                <div class="feature-card card p-6" style="text-align: center; transition: transform 0.2s ease, box-shadow 0.2s ease;">
                    <div class="feature-icon" style="font-size: 3rem; margin-bottom: var(--space-4); padding: var(--space-4); background: linear-gradient(135deg, var(--color-primary) 0%, #1d4ed8 100%); border-radius: 50%; color: white; display: inline-flex; align-items: center; justify-content: center; width: 80px; height: 80px;">📈</div>
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-3);">Portfolio Tracking</h3>
                    <p style="color: var(--color-text-muted); line-height: 1.6;">Monitor your investments with comprehensive portfolio analysis and performance tracking.</p>
                </div>
                <div class="feature-card card p-6" style="text-align: center; transition: transform 0.2s ease, box-shadow 0.2s ease;">
                    <div class="feature-icon" style="font-size: 3rem; margin-bottom: var(--space-4); padding: var(--space-4); background: linear-gradient(135deg, var(--color-primary) 0%, #1d4ed8 100%); border-radius: 50%; color: white; display: inline-flex; align-items: center; justify-content: center; width: 80px; height: 80px;">⚡</div>
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-3);">Lightning Fast</h3>
                    <p style="color: var(--color-text-muted); line-height: 1.6;">Experience blazing-fast performance with our optimized platform and API integration.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Statistics Section -->
    <section class="stats-section" style="padding: var(--space-10) 0; background: white;">
        <div class="container">
            <div style="text-align: center; margin-bottom: var(--space-8);">
                <h2 style="color: var(--color-text); font-size: 2.5rem; margin-bottom: var(--space-4);">📊 Trusted by Thousands</h2>
                <p style="color: var(--color-text-muted); font-size: 1.125rem;">Join the growing community of successful traders and investors</p>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--space-6); text-align: center;">
                <div class="stat-item">
                    <div style="font-size: 3rem; font-weight: 800; color: var(--color-primary); margin-bottom: var(--space-2);">15K+</div>
                    <div style="color: var(--color-text-muted); font-weight: 600;">Active Users</div>
                </div>
                <div class="stat-item">
                    <div style="font-size: 3rem; font-weight: 800; color: var(--color-primary); margin-bottom: var(--space-2);">2M+</div>
                    <div style="color: var(--color-text-muted); font-weight: 600;">Stocks Analyzed</div>
                </div>
                <div class="stat-item">
                    <div style="font-size: 3rem; font-weight: 800; color: var(--color-primary); margin-bottom: var(--space-2);">99.9%</div>
                    <div style="color: var(--color-text-muted); font-weight: 600;">Uptime SLA</div>
                </div>
                <div class="stat-item">
                    <div style="font-size: 3rem; font-weight: 800; color: var(--color-primary); margin-bottom: var(--space-2);">24/7</div>
                    <div style="color: var(--color-text-muted); font-weight: 600;">Support</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Pricing Section -->
    <section class="pricing-section" style="padding: var(--space-10) 0; background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);">
        <div class="container">
            <div style="text-align: center; margin-bottom: var(--space-8);">
                <h2 class="section-title" style="color: var(--color-text); font-size: 2.5rem; margin-bottom: var(--space-4);">💎 Choose Your Plan</h2>
                <p class="section-subtitle" style="color: var(--color-text-muted); font-size: 1.125rem;">Start free and upgrade as you grow</p>
            </div>
            <?php echo do_shortcode('[stock_scanner_pricing]'); ?>
        </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section" style="padding: var(--space-10) 0; background: linear-gradient(135deg, var(--color-primary) 0%, #1d4ed8 100%); color: white; text-align: center;">
        <div class="container">
            <div class="cta-content" style="max-width: 600px; margin: 0 auto;">
                <h2 style="font-size: 2.5rem; margin-bottom: var(--space-4); font-weight: 700;">🚀 Ready to Start Scanning?</h2>
                <p style="font-size: 1.125rem; margin-bottom: var(--space-6); opacity: 0.9; line-height: 1.6;">Join thousands of traders who trust our platform for their stock analysis needs.</p>
                <?php if (!is_user_logged_in()): ?>
                    <a href="<?php echo wp_registration_url(); ?>" class="btn btn-secondary" style="background: white; color: var(--color-primary); border: 2px solid white; font-size: 1.125rem; padding: var(--space-4) var(--space-6);">Get Started Free</a>
                <?php else: ?>
                    <a href="/premium-plans/" class="btn btn-secondary" style="background: white; color: var(--color-primary); border: 2px solid white; font-size: 1.125rem; padding: var(--space-4) var(--space-6);">Upgrade Your Plan</a>
                <?php endif; ?>
            </div>
        </div>
    </section>
</div>

<style>
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 2rem !important;
    }
    
    .hero-actions {
        flex-direction: column !important;
        align-items: center;
    }
    
    .hero-actions .btn {
        width: 100%;
        max-width: 300px;
    }
    
    .section-title {
        font-size: 2rem !important;
    }
}
</style>

<?php get_footer(); ?>