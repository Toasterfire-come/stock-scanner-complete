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

<style>
/* Hero Section */
.hero-section {
    background: linear-gradient(135deg, #2271b1 0%, #135e96 100%);
    color: white;
    padding: 80px 0;
    text-align: center;
}

.hero-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.hero-title {
    font-size: 3.5em;
    font-weight: 700;
    margin-bottom: 20px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.hero-subtitle {
    font-size: 1.4em;
    margin-bottom: 40px;
    opacity: 0.9;
}

.hero-actions {
    display: flex;
    gap: 20px;
    justify-content: center;
    flex-wrap: wrap;
}

/* Dashboard Section */
.dashboard-section {
    padding: 60px 0;
    background: #f8f9fa;
}

/* Features Section */
.features-section {
    padding: 80px 0;
    background: white;
}

.section-title {
    font-size: 2.5em;
    text-align: center;
    color: #2271b1;
    margin-bottom: 20px;
}

.section-subtitle {
    text-align: center;
    font-size: 1.2em;
    color: #666;
    margin-bottom: 50px;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 40px;
    max-width: 1200px;
    margin: 0 auto;
}

.feature-card {
    text-align: center;
    padding: 40px 30px;
    background: #f8f9fa;
    border-radius: 12px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.feature-icon {
    font-size: 3em;
    margin-bottom: 20px;
}

.feature-card h3 {
    color: #2271b1;
    margin-bottom: 15px;
    font-size: 1.4em;
}

.feature-card p {
    color: #666;
    line-height: 1.6;
}

/* Pricing Section */
.pricing-section {
    padding: 80px 0;
    background: #f8f9fa;
}

/* CTA Section */
.cta-section {
    padding: 80px 0;
    background: linear-gradient(135deg, #646970 0%, #50575e 100%);
    color: white;
    text-align: center;
}

.cta-content h2 {
    font-size: 2.5em;
    margin-bottom: 20px;
}

.cta-content p {
    font-size: 1.2em;
    margin-bottom: 40px;
    opacity: 0.9;
}

/* Buttons */
.btn {
    display: inline-block;
    padding: 15px 30px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
    font-size: 1em;
}

.btn-large {
    padding: 18px 40px;
    font-size: 1.1em;
}

.btn-primary {
    background: #2271b1;
    color: white;
}

.btn-primary:hover {
    background: #135e96;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(34, 113, 177, 0.3);
}

.btn-secondary {
    background: transparent;
    color: white;
    border: 2px solid white;
}

.btn-secondary:hover {
    background: white;
    color: #2271b1;
}

/* Container */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Responsive Design */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2.5em;
    }
    
    .hero-subtitle {
        font-size: 1.2em;
    }
    
    .hero-actions {
        flex-direction: column;
        align-items: center;
    }
    
    .features-grid {
        grid-template-columns: 1fr;
        gap: 30px;
    }
    
    .section-title {
        font-size: 2em;
    }
    
    .cta-content h2 {
        font-size: 2em;
    }
}

@media (max-width: 480px) {
    .hero-section {
        padding: 60px 0;
    }
    
    .hero-title {
        font-size: 2em;
    }
    
    .features-section,
    .pricing-section,
    .cta-section {
        padding: 60px 0;
    }
    
    .btn-large {
        padding: 15px 25px;
        font-size: 1em;
        width: 100%;
        max-width: 300px;
    }
}
</style>

<?php get_footer(); ?>