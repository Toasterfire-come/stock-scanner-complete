<?php
/**
 * Stock Scanner Theme Main Template
 * Professional homepage for stock scanning platform
 */

get_header(); ?>

<div class="stock-scanner-homepage">
    <!-- Hero Section -->
    <section class="hero-section">
        <div class="hero-container">
            <div class="hero-content">
                <h1 class="hero-title">Professional Stock Scanner</h1>
                <p class="hero-subtitle">Advanced stock analysis tools for informed investment decisions</p>
                <?php if (is_user_logged_in()): ?>
                    <div class="hero-actions">
                        <a href="/dashboard/" class="btn btn-primary btn-large">Go to Dashboard</a>
                        <a href="/stock-scanner/" class="btn btn-secondary btn-large">Start Scanning</a>
                    </div>
                <?php else: ?>
                    <div class="hero-actions">
                        <a href="<?php echo wp_registration_url(); ?>" class="btn btn-primary btn-large">Start Free Trial</a>
                        <a href="<?php echo wp_login_url(); ?>" class="btn btn-secondary btn-large">Login</a>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </section>

    <!-- Dashboard for Logged-in Users -->
    <?php if (is_user_logged_in()): ?>
        <section class="dashboard-section">
            <div class="container">
                <?php echo do_shortcode('[stock_scanner_dashboard]'); ?>
            </div>
        </section>
    <?php endif; ?>

    <!-- Features Section -->
    <section class="features-section">
        <div class="container">
            <h2 class="section-title">Powerful Features</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>Real-time Data</h3>
                    <p>Get live stock quotes and market data updated in real-time for informed trading decisions.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔍</div>
                    <h3>Advanced Scanning</h3>
                    <p>Use powerful filters and technical indicators to find stocks that match your criteria.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📈</div>
                    <h3>Portfolio Tracking</h3>
                    <p>Monitor your investments with comprehensive portfolio analysis and performance tracking.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <h3>Lightning Fast</h3>
                    <p>Experience blazing-fast performance with our optimized platform and API integration.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Pricing Section -->
    <section class="pricing-section">
        <div class="container">
            <h2 class="section-title">Choose Your Plan</h2>
            <p class="section-subtitle">Start free and upgrade as you grow</p>
            <?php echo do_shortcode('[stock_scanner_pricing]'); ?>
        </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
        <div class="container">
            <div class="cta-content">
                <h2>Ready to Start Scanning?</h2>
                <p>Join thousands of traders who trust our platform for their stock analysis needs.</p>
                <?php if (!is_user_logged_in()): ?>
                    <a href="<?php echo wp_registration_url(); ?>" class="btn btn-primary btn-large">Get Started Free</a>
                <?php else: ?>
                    <a href="/premium-plans/" class="btn btn-primary btn-large">Upgrade Your Plan</a>
                <?php endif; ?>
            </div>
        </div>
    </section>
</div>


<?php get_footer(); ?>