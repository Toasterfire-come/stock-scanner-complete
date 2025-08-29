<?php
/**
 * The front page template
 *
 * @package RetailTradeScanner
 */

get_header();
?>

<!-- Hero Section -->
<section class="hero-section">
    <div class="container">
        <div class="hero-content text-center animate-fade-up">
            <h1 class="hero-title">
                <?php esc_html_e('Advanced Stock Analysis', 'retail-trade-scanner'); ?>
                <span class="text-primary"><?php esc_html_e('Made Simple', 'retail-trade-scanner'); ?></span>
            </h1>
            <p class="hero-description">
                <?php esc_html_e('Scan, screen, and track the market with professional-grade tools. Get real-time insights and make informed trading decisions.', 'retail-trade-scanner'); ?>
            </p>
            <div class="hero-actions flex items-center justify-center gap-lg">
                <?php if (!is_user_logged_in()) : ?>
                    <a href="<?php echo esc_url(wp_registration_url()); ?>" class="btn btn-primary btn-lg btn-magnetic">
                        <?php esc_html_e('Get Started Free', 'retail-trade-scanner'); ?>
                        <?php echo rts_get_icon('arrow-right', ['width' => '20', 'height' => '20']); ?>
                    </a>
                    <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="btn btn-glass btn-lg">
                        <?php echo rts_get_icon('scanner', ['width' => '20', 'height' => '20']); ?>
                        <?php esc_html_e('Try Scanner', 'retail-trade-scanner'); ?>
                    </a>
                <?php else : ?>
                    <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="btn btn-primary btn-lg btn-magnetic">
                        <?php echo rts_get_icon('dashboard', ['width' => '20', 'height' => '20']); ?>
                        <?php esc_html_e('Go to Dashboard', 'retail-trade-scanner'); ?>
                    </a>
                    <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="btn btn-glass btn-lg">
                        <?php echo rts_get_icon('scanner', ['width' => '20', 'height' => '20']); ?>
                        <?php esc_html_e('Stock Scanner', 'retail-trade-scanner'); ?>
                    </a>
                <?php endif; ?>
            </div>
        </div>
        
        <!-- Hero Visual - Stock Widget Demo -->
        <div class="hero-visual animate-scale-in">
            <div class="demo-dashboard glass-card">
                <div class="demo-header">
                    <div class="demo-nav">
                        <div class="demo-nav-item active">Dashboard</div>
                        <div class="demo-nav-item">Scanner</div>
                        <div class="demo-nav-item">Portfolio</div>
                    </div>
                </div>
                <div class="demo-content bento-grid">
                    <div class="demo-widget bento-item-large glass-card">
                        <h3>Market Overview</h3>
                        <div class="demo-chart skeleton" style="height: 120px;"></div>
                    </div>
                    <div class="demo-widget bento-item-medium glass-card">
                        <h4>Top Movers</h4>
                        <div class="demo-list">
                            <div class="demo-stock">
                                <span>AAPL</span>
                                <span class="text-success">+2.34%</span>
                            </div>
                            <div class="demo-stock">
                                <span>TSLA</span>
                                <span class="text-danger">-1.28%</span>
                            </div>
                            <div class="demo-stock">
                                <span>NVDA</span>
                                <span class="text-success">+3.67%</span>
                            </div>
                        </div>
                    </div>
                    <div class="demo-widget bento-item-small glass-card">
                        <h4>Portfolio</h4>
                        <div class="demo-value">$124,567</div>
                        <div class="demo-change text-success">+5.23%</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Features Section -->
<section class="features-section">
    <div class="container">
        <div class="section-header text-center animate-fade-up">
            <h2 class="section-title"><?php esc_html_e('Powerful Trading Tools', 'retail-trade-scanner'); ?></h2>
            <p class="section-description">
                <?php esc_html_e('Everything you need to analyze markets, track performance, and make informed decisions.', 'retail-trade-scanner'); ?>
            </p>
        </div>

        <div class="features-grid grid grid-3 gap-xl">
            <div class="feature-card glass-card animate-scale-in">
                <div class="feature-icon">
                    <?php echo rts_get_icon('scanner', ['width' => '48', 'height' => '48']); ?>
                </div>
                <h3 class="feature-title"><?php esc_html_e('Real-Time Scanner', 'retail-trade-scanner'); ?></h3>
                <p class="feature-description">
                    <?php esc_html_e('Scan thousands of stocks in real-time with advanced filtering and screening capabilities.', 'retail-trade-scanner'); ?>
                </p>
                <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="feature-link">
                    <?php esc_html_e('Try Scanner', 'retail-trade-scanner'); ?>
                    <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
                </a>
            </div>

            <div class="feature-card glass-card animate-scale-in">
                <div class="feature-icon">
                    <?php echo rts_get_icon('portfolio', ['width' => '48', 'height' => '48']); ?>
                </div>
                <h3 class="feature-title"><?php esc_html_e('Portfolio Tracking', 'retail-trade-scanner'); ?></h3>
                <p class="feature-description">
                    <?php esc_html_e('Track your investments with detailed performance analytics and risk management tools.', 'retail-trade-scanner'); ?>
                </p>
                <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="feature-link">
                    <?php esc_html_e('View Portfolio', 'retail-trade-scanner'); ?>
                    <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
                </a>
            </div>

            <div class="feature-card glass-card animate-scale-in">
                <div class="feature-icon">
                    <?php echo rts_get_icon('alerts', ['width' => '48', 'height' => '48']); ?>
                </div>
                <h3 class="feature-title"><?php esc_html_e('Smart Alerts', 'retail-trade-scanner'); ?></h3>
                <p class="feature-description">
                    <?php esc_html_e('Never miss opportunities with intelligent price alerts and market notifications.', 'retail-trade-scanner'); ?>
                </p>
                <a href="<?php echo esc_url(home_url('/alerts/')); ?>" class="feature-link">
                    <?php esc_html_e('Set Alerts', 'retail-trade-scanner'); ?>
                    <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
                </a>
            </div>

            <div class="feature-card glass-card animate-scale-in">
                <div class="feature-icon">
                    <?php echo rts_get_icon('news', ['width' => '48', 'height' => '48']); ?>
                </div>
                <h3 class="feature-title"><?php esc_html_e('Market News', 'retail-trade-scanner'); ?></h3>
                <p class="feature-description">
                    <?php esc_html_e('Stay informed with curated financial news and market-moving events.', 'retail-trade-scanner'); ?>
                </p>
                <a href="<?php echo esc_url(home_url('/news/')); ?>" class="feature-link">
                    <?php esc_html_e('Read News', 'retail-trade-scanner'); ?>
                    <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
                </a>
            </div>

            <div class="feature-card glass-card animate-scale-in">
                <div class="feature-icon">
                    <?php echo rts_get_icon('watchlist', ['width' => '48', 'height' => '48']); ?>
                </div>
                <h3 class="feature-title"><?php esc_html_e('Watchlists', 'retail-trade-scanner'); ?></h3>
                <p class="feature-description">
                    <?php esc_html_e('Organize and monitor your favorite stocks with customizable watchlists.', 'retail-trade-scanner'); ?>
                </p>
                <a href="<?php echo esc_url(home_url('/watchlists/')); ?>" class="feature-link">
                    <?php esc_html_e('Create Lists', 'retail-trade-scanner'); ?>
                    <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
                </a>
            </div>

            <div class="feature-card glass-card animate-scale-in">
                <div class="feature-icon">
                    <?php echo rts_get_icon('finder', ['width' => '48', 'height' => '48']); ?>
                </div>
                <h3 class="feature-title"><?php esc_html_e('Stock Finder', 'retail-trade-scanner'); ?></h3>
                <p class="feature-description">
                    <?php esc_html_e('Discover investment opportunities with AI-powered stock recommendations.', 'retail-trade-scanner'); ?>
                </p>
                <a href="<?php echo esc_url(home_url('/finder/')); ?>" class="feature-link">
                    <?php esc_html_e('Find Stocks', 'retail-trade-scanner'); ?>
                    <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
                </a>
            </div>
        </div>
    </div>
</section>

<!-- Statistics Section -->
<section class="stats-section bg-primary text-white">
    <div class="container">
        <div class="stats-grid grid grid-4 gap-xl text-center">
            <div class="stat-item animate-fade-up">
                <div class="stat-number">50,000+</div>
                <div class="stat-label"><?php esc_html_e('Active Users', 'retail-trade-scanner'); ?></div>
            </div>
            <div class="stat-item animate-fade-up">
                <div class="stat-number">10M+</div>
                <div class="stat-label"><?php esc_html_e('Stocks Scanned', 'retail-trade-scanner'); ?></div>
            </div>
            <div class="stat-item animate-fade-up">
                <div class="stat-number">99.9%</div>
                <div class="stat-label"><?php esc_html_e('Uptime', 'retail-trade-scanner'); ?></div>
            </div>
            <div class="stat-item animate-fade-up">
                <div class="stat-number">24/7</div>
                <div class="stat-label"><?php esc_html_e('Market Coverage', 'retail-trade-scanner'); ?></div>
            </div>
        </div>
    </div>
</section>

<!-- CTA Section -->
<section class="cta-section">
    <div class="container">
        <div class="cta-content glass-card text-center">
            <h2 class="cta-title">
                <?php esc_html_e('Ready to Start Trading Smarter?', 'retail-trade-scanner'); ?>
            </h2>
            <p class="cta-description">
                <?php esc_html_e('Join thousands of traders who trust our platform for their market analysis and trading decisions.', 'retail-trade-scanner'); ?>
            </p>
            <div class="cta-actions">
                <?php if (!is_user_logged_in()) : ?>
                    <a href="<?php echo esc_url(wp_registration_url()); ?>" class="btn btn-primary btn-lg btn-magnetic">
                        <?php esc_html_e('Get Started Free', 'retail-trade-scanner'); ?>
                    </a>
                    <a href="<?php echo esc_url(home_url('/plans/')); ?>" class="btn btn-outline btn-lg">
                        <?php esc_html_e('View Plans', 'retail-trade-scanner'); ?>
                    </a>
                <?php else : ?>
                    <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="btn btn-primary btn-lg btn-magnetic">
                        <?php esc_html_e('Go to Dashboard', 'retail-trade-scanner'); ?>
                    </a>
                <?php endif; ?>
            </div>
        </div>
    </div>
</section>

<?php
get_footer();