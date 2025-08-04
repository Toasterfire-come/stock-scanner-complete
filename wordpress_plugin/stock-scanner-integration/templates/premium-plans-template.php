<?php
/**
 * Stock Scanner Professional - Premium Plans Template
 * Optimized for SEO and customer conversion
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

get_header(); ?>

<div class="stock-scanner-pro">
    <!-- Professional Navigation -->
    <nav class="stock-scanner-nav">
        <div class="stock-scanner-nav-container">
            <div class="nav-logo">
                <h2 style="margin: 0; color: var(--wp-primary);">
                    <span class="dashicons dashicons-chart-line" style="font-size: 24px; margin-right: 8px;"></span>
                    Stock Scanner Pro
                </h2>
            </div>
            
            <ul class="stock-scanner-nav-menu">
                <li class="stock-scanner-nav-item">
                    <a href="/stock-scanner-dashboard/" class="stock-scanner-nav-link">
                        <span class="dashicons dashicons-dashboard"></span>
                        Dashboard
                    </a>
                </li>
                <li class="stock-scanner-nav-item">
                    <a href="/stock-scanner/" class="stock-scanner-nav-link">
                        <span class="dashicons dashicons-search"></span>
                        Scanner
                    </a>
                </li>
                <li class="stock-scanner-nav-item">
                    <a href="/watchlists/" class="stock-scanner-nav-link">
                        <span class="dashicons dashicons-visibility"></span>
                        Watchlists
                    </a>
                </li>
                <li class="stock-scanner-nav-item">
                    <a href="/market-overview/" class="stock-scanner-nav-link">
                        <span class="dashicons dashicons-chart-area"></span>
                        Market
                    </a>
                </li>
                <li class="stock-scanner-nav-item">
                    <a href="/analytics/" class="stock-scanner-nav-link">
                        <span class="dashicons dashicons-analytics"></span>
                        Analytics
                    </a>
                </li>
                <li class="stock-scanner-nav-item">
                    <a href="/premium-plans/" class="stock-scanner-nav-link active">
                        <span class="dashicons dashicons-star-filled"></span>
                        Premium
                    </a>
                </li>
            </ul>
        </div>
    </nav>
    
    <!-- Main Content -->
    <div class="stock-scanner-page-content">
        <div class="stock-scanner-container">
            <!-- SEO-Optimized Content -->
            <?php
            if (class_exists('StockScannerSEO')) {
                $seo_optimizer = new StockScannerSEO();
                echo $seo_optimizer->get_optimized_content('premium-plans');
            } else {
                echo '<h1>Premium Stock Scanner Plans - Professional Trading Made Simple</h1>';
            }
            ?>
            
            <!-- Hero Section -->
            <div class="premium-hero" style="text-align: center; margin: 3rem 0; padding: 2rem; background: linear-gradient(135deg, var(--wp-primary) 0%, var(--wp-primary-hover) 100%); color: white; border-radius: 12px;">
                <h2 style="color: white; margin-bottom: 1rem; font-size: 2.5rem;">Unlock Professional Trading Power</h2>
                <p style="font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9;">Join thousands of successful traders using our premium stock analysis tools</p>
                <div class="hero-stats" style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                    <div class="stat-item">
                        <div style="font-size: 2rem; font-weight: bold;">8,000+</div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">Stocks Tracked</div>
                    </div>
                    <div class="stat-item">
                        <div style="font-size: 2rem; font-weight: bold;">50+</div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">Technical Indicators</div>
                    </div>
                    <div class="stat-item">
                        <div style="font-size: 2rem; font-weight: bold;">24/7</div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">Market Monitoring</div>
                    </div>
                    <div class="stat-item">
                        <div style="font-size: 2rem; font-weight: bold;">99.9%</div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">Uptime</div>
                    </div>
                </div>
            </div>
            
            <!-- Pricing Plans -->
            <div class="pricing-section">
                <h2 style="text-align: center; margin: 3rem 0 2rem; font-size: 2.2rem;">Choose Your Trading Plan</h2>
                
                <div class="pricing-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 2rem 0;">
                    
                    <!-- Free Plan -->
                    <div class="pricing-card" style="background: white; border: 2px solid var(--wp-border); border-radius: 12px; padding: 2rem; position: relative;">
                        <div class="plan-header" style="text-align: center; margin-bottom: 1.5rem;">
                            <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Free Starter</h3>
                            <div class="price" style="font-size: 2.5rem; font-weight: bold; color: var(--wp-primary);">$0<span style="font-size: 1rem; color: var(--wp-text-secondary);">/month</span></div>
                            <p style="color: var(--wp-text-secondary); margin: 0.5rem 0;">Perfect for beginners</p>
                        </div>
                        
                        <ul class="plan-features" style="list-style: none; padding: 0; margin: 1.5rem 0;">
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> 10 stock scans per day</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Basic technical indicators</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> 3 watchlists (25 stocks each)</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Email support</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Mobile responsive</li>
                            <li style="padding: 0.5rem 0; color: var(--wp-text-secondary);"><span class="dashicons dashicons-no" style="color: var(--wp-error);"></span> Real-time data (delayed 15 min)</li>
                        </ul>
                        
                        <button class="plan-button" style="width: 100%; padding: 1rem; background: var(--wp-border); color: var(--wp-text-primary); border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">Get Started Free</button>
                    </div>
                    
                    <!-- Bronze Plan -->
                    <div class="pricing-card" style="background: white; border: 2px solid var(--wp-primary); border-radius: 12px; padding: 2rem; position: relative; transform: scale(1.05);">
                        <div class="popular-badge" style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: var(--wp-primary); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">MOST POPULAR</div>
                        
                        <div class="plan-header" style="text-align: center; margin-bottom: 1.5rem;">
                            <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Bronze Trader</h3>
                            <div class="price" style="font-size: 2.5rem; font-weight: bold; color: var(--wp-primary);">$9.99<span style="font-size: 1rem; color: var(--wp-text-secondary);">/month</span></div>
                            <p style="color: var(--wp-text-secondary); margin: 0.5rem 0;">For active traders</p>
                        </div>
                        
                        <ul class="plan-features" style="list-style: none; padding: 0; margin: 1.5rem 0;">
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Unlimited stock scans</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Real-time market data</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> 25+ technical indicators</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Unlimited watchlists</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Email & SMS alerts</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Priority support</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Advanced charting</li>
                        </ul>
                        
                        <button class="plan-button" style="width: 100%; padding: 1rem; background: var(--wp-primary); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">Start 7-Day Free Trial</button>
                    </div>
                    
                    <!-- Silver Plan -->
                    <div class="pricing-card" style="background: white; border: 2px solid var(--wp-border); border-radius: 12px; padding: 2rem; position: relative;">
                        <div class="plan-header" style="text-align: center; margin-bottom: 1.5rem;">
                            <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Silver Pro</h3>
                            <div class="price" style="font-size: 2.5rem; font-weight: bold; color: var(--wp-primary);">$19.99<span style="font-size: 1rem; color: var(--wp-text-secondary);">/month</span></div>
                            <p style="color: var(--wp-text-secondary); margin: 0.5rem 0;">For professional traders</p>
                        </div>
                        
                        <ul class="plan-features" style="list-style: none; padding: 0; margin: 1.5rem 0;">
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Everything in Bronze</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> 50+ advanced indicators</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> AI-powered insights</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Custom scan formulas</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Options data & analysis</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Portfolio tracking</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> API access</li>
                        </ul>
                        
                        <button class="plan-button" style="width: 100%; padding: 1rem; background: var(--wp-primary); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">Start 7-Day Free Trial</button>
                    </div>
                    
                    <!-- Gold Plan -->
                    <div class="pricing-card" style="background: white; border: 2px solid #FFD700; border-radius: 12px; padding: 2rem; position: relative;">
                        <div class="enterprise-badge" style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: #FFD700; color: #000; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">ENTERPRISE</div>
                        
                        <div class="plan-header" style="text-align: center; margin-bottom: 1.5rem;">
                            <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Gold Elite</h3>
                            <div class="price" style="font-size: 2.5rem; font-weight: bold; color: #FFD700;">$49.99<span style="font-size: 1rem; color: var(--wp-text-secondary);">/month</span></div>
                            <p style="color: var(--wp-text-secondary); margin: 0.5rem 0;">For institutional traders</p>
                        </div>
                        
                        <ul class="plan-features" style="list-style: none; padding: 0; margin: 1.5rem 0;">
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Everything in Silver</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Level 2 market data</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Institutional analytics</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Backtesting engine</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Multi-account support</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> White-label options</li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--wp-border-light);"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span> Dedicated account manager</li>
                        </ul>
                        
                        <button class="plan-button" style="width: 100%; padding: 1rem; background: #FFD700; color: #000; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">Contact Sales</button>
                    </div>
                </div>
            </div>
            
            <!-- Features Comparison -->
            <div class="features-comparison" style="margin: 4rem 0;">
                <h2 style="text-align: center; margin-bottom: 2rem;">Complete Feature Comparison</h2>
                
                <div class="comparison-table" style="overflow-x: auto; margin: 2rem 0;">
                    <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <thead>
                            <tr style="background: var(--wp-primary); color: white;">
                                <th style="padding: 1rem; text-align: left;">Feature</th>
                                <th style="padding: 1rem; text-align: center;">Free</th>
                                <th style="padding: 1rem; text-align: center;">Bronze</th>
                                <th style="padding: 1rem; text-align: center;">Silver</th>
                                <th style="padding: 1rem; text-align: center;">Gold</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom: 1px solid var(--wp-border-light);">
                                <td style="padding: 1rem; font-weight: 600;">Daily Stock Scans</td>
                                <td style="padding: 1rem; text-align: center;">10</td>
                                <td style="padding: 1rem; text-align: center;">Unlimited</td>
                                <td style="padding: 1rem; text-align: center;">Unlimited</td>
                                <td style="padding: 1rem; text-align: center;">Unlimited</td>
                            </tr>
                            <tr style="border-bottom: 1px solid var(--wp-border-light);">
                                <td style="padding: 1rem; font-weight: 600;">Real-Time Data</td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-no" style="color: var(--wp-error);"></span></td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span></td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span></td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span></td>
                            </tr>
                            <tr style="border-bottom: 1px solid var(--wp-border-light);">
                                <td style="padding: 1rem; font-weight: 600;">Technical Indicators</td>
                                <td style="padding: 1rem; text-align: center;">10</td>
                                <td style="padding: 1rem; text-align: center;">25+</td>
                                <td style="padding: 1rem; text-align: center;">50+</td>
                                <td style="padding: 1rem; text-align: center;">100+</td>
                            </tr>
                            <tr style="border-bottom: 1px solid var(--wp-border-light);">
                                <td style="padding: 1rem; font-weight: 600;">AI-Powered Insights</td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-no" style="color: var(--wp-error);"></span></td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-no" style="color: var(--wp-error);"></span></td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span></td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span></td>
                            </tr>
                            <tr style="border-bottom: 1px solid var(--wp-border-light);">
                                <td style="padding: 1rem; font-weight: 600;">API Access</td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-no" style="color: var(--wp-error);"></span></td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-no" style="color: var(--wp-error);"></span></td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span></td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span></td>
                            </tr>
                            <tr>
                                <td style="padding: 1rem; font-weight: 600;">Level 2 Data</td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-no" style="color: var(--wp-error);"></span></td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-no" style="color: var(--wp-error);"></span></td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-no" style="color: var(--wp-error);"></span></td>
                                <td style="padding: 1rem; text-align: center;"><span class="dashicons dashicons-yes" style="color: var(--wp-success);"></span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Trust Indicators -->
            <div class="trust-section" style="background: var(--wp-surface); padding: 3rem; border-radius: 12px; margin: 4rem 0; text-align: center;">
                <h2 style="margin-bottom: 2rem;">Trusted by Traders Worldwide</h2>
                
                <div class="trust-indicators" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; margin: 2rem 0;">
                    <div class="trust-item">
                        <div style="font-size: 2.5rem; color: var(--wp-primary); margin-bottom: 0.5rem;">🔒</div>
                        <h4>Bank-Level Security</h4>
                        <p style="color: var(--wp-text-secondary);">256-bit SSL encryption</p>
                    </div>
                    <div class="trust-item">
                        <div style="font-size: 2.5rem; color: var(--wp-primary); margin-bottom: 0.5rem;">⚡</div>
                        <h4>99.9% Uptime</h4>
                        <p style="color: var(--wp-text-secondary);">Reliable 24/7 access</p>
                    </div>
                    <div class="trust-item">
                        <div style="font-size: 2.5rem; color: var(--wp-primary); margin-bottom: 0.5rem;">📞</div>
                        <h4>24/7 Support</h4>
                        <p style="color: var(--wp-text-secondary);">Expert help when you need it</p>
                    </div>
                    <div class="trust-item">
                        <div style="font-size: 2.5rem; color: var(--wp-primary); margin-bottom: 0.5rem;">💰</div>
                        <h4>30-Day Guarantee</h4>
                        <p style="color: var(--wp-text-secondary);">Money back if not satisfied</p>
                    </div>
                </div>
                
                <!-- Customer Reviews -->
                <div class="reviews-section" style="margin: 3rem 0;">
                    <h3>What Our Customers Say</h3>
                    <div class="reviews-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 2rem 0;">
                        <div class="review-card" style="background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid var(--wp-border);">
                            <div class="review-stars" style="color: #FFD700; margin-bottom: 1rem;">★★★★★</div>
                            <p style="font-style: italic; margin-bottom: 1rem;">"The AI insights have completely transformed my trading strategy. I've increased my win rate by 40% since upgrading to Silver."</p>
                            <div style="font-weight: 600;">- Sarah M., Day Trader</div>
                        </div>
                        <div class="review-card" style="background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid var(--wp-border);">
                            <div class="review-stars" style="color: #FFD700; margin-bottom: 1rem;">★★★★★</div>
                            <p style="font-style: italic; margin-bottom: 1rem;">"Best stock scanner I've ever used. The real-time data and custom alerts saved me from several losing trades."</p>
                            <div style="font-weight: 600;">- Michael C., Swing Trader</div>
                        </div>
                        <div class="review-card" style="background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid var(--wp-border);">
                            <div class="review-stars" style="color: #FFD700; margin-bottom: 1rem;">★★★★★</div>
                            <p style="font-style: italic; margin-bottom: 1rem;">"The Gold plan's institutional features give me the same tools as hedge funds. Absolutely worth the investment."</p>
                            <div style="font-weight: 600;">- Jennifer L., Portfolio Manager</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Call to Action -->
            <div class="cta-section" style="background: linear-gradient(135deg, var(--wp-primary) 0%, var(--wp-primary-hover) 100%); color: white; padding: 3rem; border-radius: 12px; text-align: center; margin: 4rem 0;">
                <h2 style="color: white; margin-bottom: 1rem;">Ready to Start Your Trading Journey?</h2>
                <p style="font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9;">Join thousands of successful traders using our platform. Start with a free trial today!</p>
                <button style="background: white; color: var(--wp-primary); padding: 1rem 2rem; border: none; border-radius: 8px; font-size: 1.1rem; font-weight: 600; cursor: pointer; margin-right: 1rem;">Start Free Trial</button>
                <button style="background: transparent; color: white; padding: 1rem 2rem; border: 2px solid white; border-radius: 8px; font-size: 1.1rem; font-weight: 600; cursor: pointer;">View Demo</button>
            </div>
        </div>
    </div>
</div>

<?php get_footer(); ?>