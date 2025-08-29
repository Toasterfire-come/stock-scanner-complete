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

<!-- Demo Interaction JavaScript -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    initHeroDemo();
    initAnimatedCounters();
    initIntersectionObserver();
});

function initHeroDemo() {
    const demoTabs = document.querySelectorAll('.demo-nav-item');
    const demoViews = document.querySelectorAll('.demo-content');
    
    demoTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.dataset.demoTab;
            
            // Update active tab
            demoTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Update active view
            demoViews.forEach(view => {
                view.classList.remove('active');
                if (view.id === `demo-${targetTab}`) {
                    view.classList.add('active');
                }
            });
            
            // Animate chart if dashboard is selected
            if (targetTab === 'dashboard') {
                setTimeout(() => {
                    drawDemoChart();
                }, 300);
            }
        });
    });
    
    // Initialize chart
    setTimeout(() => {
        drawDemoChart();
    }, 1000);
    
    // Auto-rotate demo tabs
    let currentTab = 0;
    const totalTabs = demoTabs.length;
    
    setInterval(() => {
        currentTab = (currentTab + 1) % totalTabs;
        demoTabs[currentTab].click();
    }, 4000);
}

function drawDemoChart() {
    const canvas = document.getElementById('demo-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Generate sample data
    const dataPoints = 20;
    const data = [];
    let value = 100;
    
    for (let i = 0; i < dataPoints; i++) {
        value += (Math.random() - 0.4) * 10;
        value = Math.max(80, Math.min(120, value));
        data.push(value);
    }
    
    // Draw gradient background
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.2)');
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.05)');
    
    // Draw line
    ctx.beginPath();
    ctx.moveTo(0, height);
    
    for (let i = 0; i < data.length; i++) {
        const x = (i / (data.length - 1)) * width;
        const y = height - ((data[i] - 80) / 40) * height;
        
        if (i === 0) {
            ctx.lineTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    
    ctx.lineTo(width, height);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();
    
    // Draw line
    ctx.beginPath();
    for (let i = 0; i < data.length; i++) {
        const x = (i / (data.length - 1)) * width;
        const y = height - ((data[i] - 80) / 40) * height;
        
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 3;
    ctx.stroke();
}

function initAnimatedCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    counters.forEach(counter => {
        const target = counter.textContent;
        const isPercent = target.includes('%');
        const isPlus = target.includes('+');
        let numericValue = parseFloat(target.replace(/[^\d.]/g, ''));
        
        if (target.includes('M+')) {
            numericValue = parseFloat(target.replace('M+', ''));
        } else if (target.includes('K+')) {
            numericValue = parseFloat(target.replace('K+', ''));
        }
        
        let current = 0;
        const increment = numericValue / 50; // 50 frames
        
        const timer = setInterval(() => {
            current += increment;
            
            if (current >= numericValue) {
                current = numericValue;
                clearInterval(timer);
            }
            
            let displayValue = Math.floor(current);
            
            if (target.includes('M+')) {
                displayValue = Math.floor(current) + 'M+';
            } else if (target.includes('K+')) {
                displayValue = Math.floor(current) + 'K+';
            } else if (isPercent) {
                displayValue = Math.floor(current) + '%';
            } else if (target.includes('/')) {
                displayValue = target; // Don't animate text like "24/7"
                clearInterval(timer);
                return;
            }
            
            counter.textContent = displayValue;
        }, 50);
    });
}

function initIntersectionObserver() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '50px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                
                // Start counter animation for stats
                if (entry.target.classList.contains('stats-section')) {
                    setTimeout(() => {
                        initAnimatedCounters();
                    }, 500);
                }
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe animated elements
    document.querySelectorAll('.animate-fade-up, .animate-scale-in, .stats-section').forEach(el => {
        observer.observe(el);
    });
}
</script>

<!-- Demo Styles -->
<style>
.hero-visual {
    margin-top: 4rem;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

.demo-dashboard {
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 1rem;
    box-shadow: 0 20px 25px rgba(0, 0, 0, 0.1);
}

.demo-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.demo-nav {
    display: flex;
    gap: 0.5rem;
}

.demo-nav-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: 1px solid transparent;
    border-radius: 0.5rem;
    background: rgba(0, 0, 0, 0.05);
    font-size: 0.875rem;
    font-weight: 600;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.3s ease;
}

.demo-nav-item.active {
    background: #3b82f6;
    color: white;
    box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
}

.demo-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.demo-content {
    display: none;
    min-height: 200px;
}

.demo-content.active {
    display: block;
    animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Dashboard Demo */
.demo-kpis {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.demo-kpi {
    text-align: center;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 0.75rem;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.demo-kpi-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.demo-kpi-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 0.25rem;
}

.demo-kpi-change {
    font-size: 0.875rem;
    font-weight: 600;
}

.demo-chart-area {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 0.75rem;
    padding: 1rem;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

/* Scanner Demo */
.demo-filters {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

.demo-filter-chip {
    padding: 0.5rem 0.75rem;
    background: rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.3s ease;
}

.demo-filter-chip.active {
    background: #3b82f6;
    color: white;
    border-color: #3b82f6;
}

.demo-results {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 0.75rem;
    padding: 1rem;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.demo-stock-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.demo-stock-row:last-child {
    border-bottom: none;
}

.stock-symbol {
    font-weight: 700;
    color: #111827;
}

.stock-price {
    font-weight: 600;
    color: #374151;
}

.stock-change {
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 0.375rem;
    font-size: 0.875rem;
}

/* Portfolio Demo */
.demo-holdings {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 0.75rem;
    padding: 1rem;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.demo-holding {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.demo-holding:last-child {
    border-bottom: none;
}

.holding-info {
    display: flex;
    flex-direction: column;
}

.holding-symbol {
    font-weight: 700;
    color: #111827;
    margin-bottom: 0.25rem;
}

.holding-shares {
    font-size: 0.875rem;
    color: #6b7280;
}

.holding-value {
    text-align: right;
    display: flex;
    flex-direction: column;
}

.holding-price {
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.25rem;
}

.holding-change {
    font-size: 0.875rem;
    font-weight: 600;
}

/* Responsive */
@media (max-width: 768px) {
    .demo-kpis {
        grid-template-columns: 1fr;
    }
    
    .demo-nav {
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .demo-nav-item {
        justify-content: center;
    }
    
    .demo-header {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }
}
</style>

<?php
get_footer();