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
                        <div class="demo-nav-item active" data-demo-tab="dashboard">
                            <?php echo rts_get_icon('dashboard', ['width' => '16', 'height' => '16']); ?>
                            Dashboard
                        </div>
                        <div class="demo-nav-item" data-demo-tab="scanner">
                            <?php echo rts_get_icon('scanner', ['width' => '16', 'height' => '16']); ?>
                            Scanner
                        </div>
                        <div class="demo-nav-item" data-demo-tab="portfolio">
                            <?php echo rts_get_icon('portfolio', ['width' => '16', 'height' => '16']); ?>
                            Portfolio
                        </div>
                    </div>
                    <div class="demo-status">
                        <span class="status-indicator status-online">Live</span>
                    </div>
                </div>
                
                <!-- Dashboard Demo -->
                <div class="demo-content demo-dashboard-view active" id="demo-dashboard">
                    <div class="demo-kpis">
                        <div class="demo-kpi">
                            <div class="demo-kpi-label">Portfolio</div>
                            <div class="demo-kpi-value">$124,567</div>
                            <div class="demo-kpi-change text-success">+5.23%</div>
                        </div>
                        <div class="demo-kpi">
                            <div class="demo-kpi-label">P&L Today</div>
                            <div class="demo-kpi-value">+$2,341</div>
                            <div class="demo-kpi-change text-success">+1.92%</div>
                        </div>
                        <div class="demo-kpi">
                            <div class="demo-kpi-label">Active</div>
                            <div class="demo-kpi-value">23</div>
                            <div class="demo-kpi-change text-muted">positions</div>
                        </div>
                    </div>
                    <div class="demo-chart-area">
                        <canvas id="demo-chart" width="400" height="150"></canvas>
                    </div>
                </div>
                
                <!-- Scanner Demo -->
                <div class="demo-content demo-scanner-view" id="demo-scanner">
                    <div class="demo-filters">
                        <div class="demo-filter-chip active">Price: $10-$100</div>
                        <div class="demo-filter-chip active">Volume: >1M</div>
                        <div class="demo-filter-chip">+5% Today</div>
                    </div>
                    <div class="demo-results">
                        <div class="demo-stock-row">
                            <span class="stock-symbol">NVDA</span>
                            <span class="stock-price">$234.56</span>
                            <span class="stock-change text-success">+8.45%</span>
                        </div>
                        <div class="demo-stock-row">
                            <span class="stock-symbol">AMD</span>
                            <span class="stock-price">$156.78</span>
                            <span class="stock-change text-success">+6.23%</span>
                        </div>
                        <div class="demo-stock-row">
                            <span class="stock-symbol">TSLA</span>
                            <span class="stock-price">$234.56</span>
                            <span class="stock-change text-success">+5.67%</span>
                        </div>
                    </div>
                </div>
                
                <!-- Portfolio Demo -->
                <div class="demo-content demo-portfolio-view" id="demo-portfolio">
                    <div class="demo-holdings">
                        <div class="demo-holding">
                            <div class="holding-info">
                                <span class="holding-symbol">AAPL</span>
                                <span class="holding-shares">150 shares</span>
                            </div>
                            <div class="holding-value">
                                <span class="holding-price">$26,250</span>
                                <span class="holding-change text-success">+$1,125</span>
                            </div>
                        </div>
                        <div class="demo-holding">
                            <div class="holding-info">
                                <span class="holding-symbol">MSFT</span>
                                <span class="holding-shares">80 shares</span>
                            </div>
                            <div class="holding-value">
                                <span class="holding-price">$28,800</span>
                                <span class="holding-change text-success">+$960</span>
                            </div>
                        </div>
                        <div class="demo-holding">
                            <div class="holding-info">
                                <span class="holding-symbol">GOOGL</span>
                                <span class="holding-shares">45 shares</span>
                            </div>
                            <div class="holding-value">
                                <span class="holding-price">$22,500</span>
                                <span class="holding-change text-danger">-$450</span>
                            </div>
                        </div>
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