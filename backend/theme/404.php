<?php
/**
 * 404 Error Page Template
 * Template for displaying 404 "page not found" errors
 */

get_header(); ?>

<div class="error-404-wrapper">
    <div class="container">
        <div class="error-404-content">
            <div class="error-404-visual">
                <div class="error-code">404</div>
                <div class="error-icon">📊</div>
                <div class="error-chart">
                    <div class="chart-bars">
                        <div class="bar bar-1"></div>
                        <div class="bar bar-2"></div>
                        <div class="bar bar-3"></div>
                        <div class="bar bar-4"></div>
                        <div class="bar bar-5"></div>
                    </div>
                </div>
            </div>
            
            <div class="error-404-text">
                <h1 class="error-title">Page Not Found</h1>
                <p class="error-description">
                    Oops! The page you're looking for seems to have moved or doesn't exist. 
                    Just like a stock that's delisted, this page is no longer available at this location.
                </p>
                
                <div class="error-suggestions">
                    <h2>What can you do?</h2>
                    <ul class="suggestion-list">
                        <li>Check the URL for typing errors</li>
                        <li>Use the search function to find what you're looking for</li>
                        <li>Browse our popular pages below</li>
                        <li>Return to the homepage and start fresh</li>
                    </ul>
                </div>
            </div>
            
            <div class="error-actions">
                <div class="search-section">
                    <h3>Search our site:</h3>
                    <form role="search" method="get" class="error-search-form" action="<?php echo esc_url(home_url('/')); ?>">
                        <input type="search" class="search-field" placeholder="Search for stocks, tools, or help..." name="s" />
                        <button type="submit" class="search-submit">
                            🔍 Search
                        </button>
                    </form>
                </div>
                
                <div class="quick-links">
                    <h3>Popular Pages:</h3>
                    <div class="links-grid">
                        <a href="<?php echo home_url(); ?>" class="quick-link home-link">
                            <span class="link-icon">🏠</span>
                            <span class="link-text">
                                <strong>Homepage</strong>
                                <small>Start here</small>
                            </span>
                        </a>
                        
                        <a href="<?php echo home_url('/stock-screener/'); ?>" class="quick-link">
                            <span class="link-icon">🔍</span>
                            <span class="link-text">
                                <strong>Stock Screener</strong>
                                <small>Find stocks</small>
                            </span>
                        </a>
                        
                        <a href="<?php echo home_url('/market-overview/'); ?>" class="quick-link">
                            <span class="link-icon">📈</span>
                            <span class="link-text">
                                <strong>Market Overview</strong>
                                <small>Market data</small>
                            </span>
                        </a>
                        
                        <a href="<?php echo home_url('/portfolio/'); ?>" class="quick-link">
                            <span class="link-icon">💼</span>
                            <span class="link-text">
                                <strong>Portfolio</strong>
                                <small>Track investments</small>
                            </span>
                        </a>
                        
                        <a href="<?php echo home_url('/watchlist/'); ?>" class="quick-link">
                            <span class="link-icon">👁️</span>
                            <span class="link-text">
                                <strong>Watchlist</strong>
                                <small>Monitor stocks</small>
                            </span>
                        </a>
                        
                        <a href="<?php echo home_url('/premium-plans/'); ?>" class="quick-link">
                            <span class="link-icon">⭐</span>
                            <span class="link-text">
                                <strong>Premium Plans</strong>
                                <small>Upgrade features</small>
                            </span>
                        </a>
                        
                        <a href="<?php echo home_url('/contact/'); ?>" class="quick-link">
                            <span class="link-icon">📞</span>
                            <span class="link-text">
                                <strong>Contact Support</strong>
                                <small>Get help</small>
                            </span>
                        </a>
                        
                        <a href="<?php echo home_url('/faq/'); ?>" class="quick-link">
                            <span class="link-icon">❓</span>
                            <span class="link-text">
                                <strong>FAQ</strong>
                                <small>Common questions</small>
                            </span>
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="error-footer">
                <p>If you believe this is an error or need assistance, please <a href="<?php echo home_url('/contact/'); ?>">contact our support team</a>.</p>
            </div>
        </div>
    </div>
</div>

<style>
.error-404-wrapper {
    padding: 2rem 0;
    background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
    min-height: 80vh;
    display: flex;
    align-items: center;
}

.error-404-content {
    text-align: center;
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
}

.error-404-visual {
    position: relative;
    margin-bottom: 3rem;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.error-code {
    font-size: 8rem;
    font-weight: 900;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin-bottom: 1rem;
    text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.error-icon {
    font-size: 4rem;
    margin-bottom: 2rem;
    opacity: 0.7;
}

.error-chart {
    margin-bottom: 2rem;
}

.chart-bars {
    display: flex;
    align-items: end;
    gap: 0.5rem;
    height: 60px;
    justify-content: center;
}

.bar {
    width: 12px;
    background: var(--primary-gradient);
    border-radius: 2px 2px 0 0;
    animation: chartPulse 2s infinite;
    opacity: 0.7;
}

.bar-1 { height: 30%; animation-delay: 0s; }
.bar-2 { height: 60%; animation-delay: 0.2s; }
.bar-3 { height: 45%; animation-delay: 0.4s; }
.bar-4 { height: 80%; animation-delay: 0.6s; }
.bar-5 { height: 35%; animation-delay: 0.8s; }

@keyframes chartPulse {
    0%, 100% { opacity: 0.7; transform: scaleY(1); }
    50% { opacity: 1; transform: scaleY(1.1); }
}

.error-404-text {
    margin-bottom: 3rem;
}

.error-title {
    font-size: 3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1rem;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.error-description {
    font-size: 1.25rem;
    color: var(--text-secondary);
    line-height: 1.6;
    max-width: 600px;
    margin: 0 auto 2rem;
}

.error-suggestions {
    background: var(--bg-primary);
    padding: 2rem;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    margin-bottom: 2rem;
    border: 1px solid var(--border-color);
}

.error-suggestions h2 {
    color: var(--text-primary);
    margin-bottom: 1rem;
    font-size: 1.5rem;
}

.suggestion-list {
    list-style: none;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
    text-align: left;
}

.suggestion-list li {
    padding: 1rem;
    background: var(--bg-secondary);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    position: relative;
    padding-left: 3rem;
}

.suggestion-list li::before {
    content: '→';
    position: absolute;
    left: 1rem;
    color: var(--primary-color);
    font-weight: bold;
}

.error-actions {
    display: grid;
    grid-template-columns: 1fr;
    gap: 3rem;
    margin-bottom: 3rem;
}

.search-section {
    background: var(--bg-primary);
    padding: 2rem;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
}

.search-section h3 {
    color: var(--text-primary);
    margin-bottom: 1rem;
    font-size: 1.25rem;
}

.error-search-form {
    display: flex;
    max-width: 500px;
    margin: 0 auto;
    gap: 0;
    background: var(--bg-secondary);
    border-radius: var(--radius-lg);
    padding: 0.5rem;
    border: 1px solid var(--border-color);
}

.search-field {
    flex: 1;
    padding: 1rem 1.5rem;
    border: none;
    background: transparent;
    color: var(--text-primary);
    font-size: 1rem;
    outline: none;
}

.search-field::placeholder {
    color: var(--text-secondary);
}

.search-submit {
    padding: 1rem 1.5rem;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    font-weight: 600;
    transition: all var(--transition-normal);
    white-space: nowrap;
}

.search-submit:hover {
    background: var(--primary-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

.quick-links h3 {
    color: var(--text-primary);
    margin-bottom: 1.5rem;
    font-size: 1.25rem;
}

.links-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
}

.quick-link {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    text-decoration: none;
    transition: all var(--transition-normal);
    box-shadow: var(--shadow-sm);
}

.quick-link:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-3px);
    border-color: var(--primary-color);
}

.quick-link.home-link {
    border-color: var(--primary-color);
    background: rgba(var(--primary-color-rgb), 0.05);
}

.link-icon {
    font-size: 2rem;
    flex-shrink: 0;
}

.link-text {
    text-align: left;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.link-text strong {
    color: var(--text-primary);
    font-size: 1rem;
    font-weight: 600;
}

.link-text small {
    color: var(--text-secondary);
    font-size: 0.875rem;
}

.error-footer {
    padding-top: 2rem;
    border-top: 1px solid var(--border-color);
    color: var(--text-secondary);
}

.error-footer a {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 600;
}

.error-footer a:hover {
    text-decoration: underline;
}

@media (max-width: 768px) {
    .error-code {
        font-size: 6rem;
    }
    
    .error-title {
        font-size: 2rem;
    }
    
    .error-description {
        font-size: 1rem;
    }
    
    .error-search-form {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .links-grid {
        grid-template-columns: 1fr;
    }
    
    .suggestion-list {
        grid-template-columns: 1fr;
    }
    
    .error-404-content {
        padding: 1rem;
    }
    
    .error-suggestions,
    .search-section {
        padding: 1.5rem;
    }
}

@media (max-width: 480px) {
    .error-code {
        font-size: 4rem;
    }
    
    .error-title {
        font-size: 1.5rem;
    }
    
    .chart-bars {
        height: 40px;
    }
    
    .bar {
        width: 8px;
    }
}
</style>

<?php get_footer(); ?>