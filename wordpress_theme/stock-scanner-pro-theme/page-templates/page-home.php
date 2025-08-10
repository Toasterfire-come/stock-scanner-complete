<?php
/**
 * Template Name: Home (Marketing)
 * Description: Marketing-focused homepage to convert visitors into customers
 */

get_header(); ?>

<div class="home-page">
    <div class="container">
        <div class="page-header">
            <h1>📈 Retail Trade Scanner</h1>
            <p class="page-description">Find, track, and analyze stocks with professional-grade tools built for traders and investors</p>
        </div>

        <!-- Hero CTA -->
        <div class="card p-6 mb-6">
            <div class="hero-content" style="display: grid; gap: var(--space-5); text-align: center;">
                <div style="display: grid; gap: var(--space-3);">
                    <h2 style="margin: 0; color: var(--color-text); font-size: 2rem;">Powerful Stock Screening and Insights</h2>
                    <p class="muted" style="margin: 0; font-size: 1.125rem;">High-contrast, fast, and accurate. Start free and upgrade anytime.</p>
                </div>
                <div class="hero-buttons" style="display: flex; gap: var(--space-3); justify-content: center; flex-wrap: wrap;">
                    <a class="btn btn-primary" href="/stock-screener/">🔍 Start Screening</a>
                    <a class="btn btn-secondary" href="/signup/">🚀 Create Free Account</a>
                    <a class="btn btn-outline" href="/premium-plans/">💎 View Plans</a>
                </div>
            </div>
        </div>

        <!-- Feature Grid -->
        <div class="features-section mb-6">
            <h2 style="text-align: center; margin-bottom: var(--space-6); color: var(--color-text);">Essential Trading Tools</h2>
            <div class="features-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--space-5);">
                <div class="card p-5">
                    <div class="feature-icon" style="font-size: 2.5rem; margin-bottom: var(--space-3);">🔍</div>
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-3);">Advanced Screener</h3>
                    <p class="muted" style="margin-bottom: var(--space-4);">Filter by market cap, price, volume, performance, and technicals to quickly find opportunities.</p>
                    <a class="btn btn-outline" href="/stock-screener/">Explore Screener</a>
                </div>
                
                <div class="card p-5">
                    <div class="feature-icon" style="font-size: 2.5rem; margin-bottom: var(--space-3);">👁️</div>
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-3);">Smart Watchlist</h3>
                    <p class="muted" style="margin-bottom: var(--space-4);">Build a personalized watchlist and get quick suggestions to start, with alerts and notes.</p>
                    <a class="btn btn-outline" href="/watchlist/">Open Watchlist</a>
                </div>
                
                <div class="card p-5">
                    <div class="feature-icon" style="font-size: 2.5rem; margin-bottom: var(--space-3);">📊</div>
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-3);">Portfolio Tracking</h3>
                    <p class="muted" style="margin-bottom: var(--space-4);">Track holdings and ROI with real-time performance summaries and CSV import.</p>
                    <a class="btn btn-outline" href="/portfolio/">Go to Portfolios</a>
                </div>
                
                <div class="card p-5">
                    <div class="feature-icon" style="font-size: 2.5rem; margin-bottom: var(--space-3);">📰</div>
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-3);">Personalized News</h3>
                    <p class="muted" style="margin-bottom: var(--space-4);">See tailored news for your holdings and interests with smart filtering and analytics.</p>
                    <a class="btn btn-outline" href="/personalized-news/">See News</a>
                </div>
            </div>
        </div>

        <!-- Social Proof / Stats -->
        <div class="card p-6 mb-6">
            <h3 style="color: var(--color-text); margin-bottom: var(--space-4); text-align: center;">Why Traders Choose Retail Trade Scanner</h3>
            <div class="benefits-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--space-4);">
                <div class="benefit-item" style="display: flex; align-items: center; gap: var(--space-3);">
                    <span style="font-size: 1.5rem;">✨</span>
                    <span style="color: var(--color-text-muted);">High-contrast, accessible UI for long trading sessions</span>
                </div>
                <div class="benefit-item" style="display: flex; align-items: center; gap: var(--space-3);">
                    <span style="font-size: 1.5rem;">⚡</span>
                    <span style="color: var(--color-text-muted);">Fast screening with professional filters</span>
                </div>
                <div class="benefit-item" style="display: flex; align-items: center; gap: var(--space-3);">
                    <span style="font-size: 1.5rem;">📈</span>
                    <span style="color: var(--color-text-muted);">Unified dashboard with usage stats and limits</span>
                </div>
                <div class="benefit-item" style="display: flex; align-items: center; gap: var(--space-3);">
                    <span style="font-size: 1.5rem;">📋</span>
                    <span style="color: var(--color-text-muted);">Easy watchlists and portfolio import</span>
                </div>
            </div>
        </div>

        <!-- Statistics Section -->
        <div class="card p-6 mb-6">
            <h3 style="color: var(--color-text); margin-bottom: var(--space-5); text-align: center;">Platform Statistics</h3>
            <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: var(--space-4); text-align: center;">
                <div class="stat-item">
                    <div style="font-size: 2rem; font-weight: 700; color: var(--color-primary); margin-bottom: var(--space-2);">10K+</div>
                    <div style="color: var(--color-text-muted); font-size: 0.875rem;">Active Users</div>
                </div>
                <div class="stat-item">
                    <div style="font-size: 2rem; font-weight: 700; color: var(--color-primary); margin-bottom: var(--space-2);">500K+</div>
                    <div style="color: var(--color-text-muted); font-size: 0.875rem;">Stocks Screened</div>
                </div>
                <div class="stat-item">
                    <div style="font-size: 2rem; font-weight: 700; color: var(--color-primary); margin-bottom: var(--space-2);">99.9%</div>
                    <div style="color: var(--color-text-muted); font-size: 0.875rem;">Uptime</div>
                </div>
                <div class="stat-item">
                    <div style="font-size: 2rem; font-weight: 700; color: var(--color-primary); margin-bottom: var(--space-2);">24/7</div>
                    <div style="color: var(--color-text-muted); font-size: 0.875rem;">Market Data</div>
                </div>
            </div>
        </div>

        <!-- Secondary CTA -->
        <div class="card p-6">
            <div class="cta-content" style="display: flex; align-items: center; justify-content: space-between; gap: var(--space-4); flex-wrap: wrap;">
                <div>
                    <h3 style="margin: 0; color: var(--color-text);">Get started for free</h3>
                    <p class="muted" style="margin: 0;">Upgrade anytime for more features and higher limits</p>
                </div>
                <div class="cta-buttons" style="display: flex; gap: var(--space-3); flex-wrap: wrap;">
                    <a class="btn btn-primary" href="/signup/">Create Account</a>
                    <a class="btn btn-outline" href="/premium-plans/">Compare Plans</a>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
/* Home page specific styles */
.home-page {
    padding: var(--space-10) 0;
    background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);
    min-height: 100vh;
}

.feature-icon {
    display: inline-block;
    padding: var(--space-3);
    background: linear-gradient(135deg, var(--color-primary) 0%, #1d4ed8 100%);
    border-radius: 50%;
    color: white;
    text-align: center;
    width: 80px;
    height: 80px;
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
}

.hero-buttons .btn {
    min-width: 160px;
}

@media (max-width: 768px) {
    .cta-content {
        flex-direction: column;
        text-align: center;
    }
    
    .hero-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .hero-buttons .btn {
        width: 100%;
        max-width: 300px;
    }
}
</style>

<?php get_footer(); ?>