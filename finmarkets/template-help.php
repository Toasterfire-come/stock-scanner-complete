<?php /* Template Name: Help Center */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<div class="help-center-page glass-section">
    <div class="container">
        <div class="page-header section-intro">
            <h1>📖 Help Center</h1>
            <p class="page-description">Comprehensive guides and documentation to help you get the most out of Stock Scanner</p>
        </div>

        <div class="card glass-card p-6 mb-6">
            <div class="help-search" style="max-width: 600px; margin: 0 auto; text-align: center;">
                <h2 style="color: var(--color-text); margin-bottom: var(--space-4);">How can we help you?</h2>
                <div class="search-container" style="position: relative;">
                    <input type="text" id="help-search" placeholder="Search documentation, guides, and tutorials..." style="width: 100%; padding-left: 3rem;" class="input">
                    <span style="position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: var(--color-text-muted); font-size: 1.2rem;"></span>
                </div>
            </div>
        </div>

        <div class="help-categories features-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: var(--space-6); margin-bottom: var(--space-8);">
            <div class="help-category card glass-card p-6">
                <div class="category-header" style="text-align: center; margin-bottom: var(--space-5);">
                    <div style="font-size: 3rem; margin-bottom: var(--space-3);"></div>
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-2);">Getting Started</h3>
                    <p style="color: var(--color-text-muted);">Set up your account and learn the basics</p>
                </div>
                <div class="help-links" style="display: grid; gap: var(--space-2);">
                    <a href="/getting-started/" class="help-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius); transition: background-color 0.2s; text-decoration: none; color: var(--color-primary);"><span>📝</span><span>Account Setup Guide</span></a>
                    <a href="/first-screening/" class="help-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius); transition: background-color 0.2s; text-decoration: none; color: var(--color-primary);"><span></span><span>Your First Stock Screen</span></a>
                    <a href="/dashboard-tour/" class="help-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius); transition: background-color 0.2s; text-decoration: none; color: var(--color-primary);"><span>🏠</span><span>Dashboard Overview</span></a>
                </div>
            </div>

            <div class="help-category card glass-card p-6">
                <div class="category-header" style="text-align: center; margin-bottom: var(--space-5);">
                    <div style="font-size: 3rem; margin-bottom: var(--space-3);">🔧</div>
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-2);">Features Guide</h3>
                    <p style="color: var(--color-text-muted);">Master all the powerful tools available</p>
                </div>
                <div class="help-links" style="display: grid; gap: var(--space-2);">
                    <a href="/screener-guide/" class="help-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius); transition: background-color 0.2s; text-decoration: none; color: var(--color-primary);"><span></span><span>Advanced Screener</span></a>
                    <a href="/watchlist-guide/" class="help-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius); transition: background-color 0.2s; text-decoration: none; color: var(--color-primary);"><span>👁️</span><span>Watchlist Management</span></a>
                    <a href="/portfolio-guide/" class="help-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius); transition: background-color 0.2s; text-decoration: none; color: var(--color-primary);"><span></span><span>Portfolio Tracking</span></a>
                </div>
            </div>

            <div class="help-category card glass-card p-6">
                <div class="category-header" style="text-align: center; margin-bottom: var(--space-5);">
                    <div style="font-size: 3rem; margin-bottom: var(--space-3);">💳</div>
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-2);">Account & Billing</h3>
                    <p style="color: var(--color-text-muted);">Manage your subscription and settings</p>
                </div>
                <div class="help-links" style="display: grid; gap: var(--space-2);">
                    <a href="/account-settings/" class="help-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius); transition: background-color 0.2s; text-decoration: none; color: var(--color-primary);"><span>⚙️</span><span>Account Settings</span></a>
                    <a href="/billing-help/" class="help-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius); transition: background-color 0.2s; text-decoration: none; color: var(--color-primary);"><span></span><span>Billing & Payments</span></a>
                    <a href="/upgrade-guide/" class="help-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius); transition: background-color 0.2s; text-decoration: none; color: var(--color-primary);"><span>⬆️</span><span>Upgrade Your Plan</span></a>
                </div>
            </div>

            <div class="help-category card glass-card p-6">
                <div class="category-header" style="text-align: center; margin-bottom: var(--space-5);">
                    <div style="font-size: 3rem; margin-bottom: var(--space-3);">🛠️</div>
                    <h3 style="color: var(--color-text); margin-bottom: var(--space-2);">Troubleshooting</h3>
                    <p style="color: var(--color-text-muted);">Fix common issues and errors</p>
                </div>
                <div class="help-links" style="display: grid; gap: var(--space-2);">
                    <a href="/login-issues/" class="help-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius); transition: background-color 0.2s; text-decoration: none; color: var(--color-primary);"><span>🔑</span><span>Login Problems</span></a>
                    <a href="/data-issues/" class="help-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius); transition: background-color 0.2s; text-decoration: none; color: var(--color-primary);"><span>📡</span><span>Data Loading Issues</span></a>
                    <a href="/browser-support/" class="help-link" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius); transition: background-color 0.2s; text-decoration: none; color: var(--color-primary);"><span>🌐</span><span>Browser Compatibility</span></a>
                </div>
            </div>
        </div>

        <div class="card glass-card p-6 mb-6">
            <h2 style="color: var(--color-text); margin-bottom: var(--space-5); text-align: center;">📌 Popular Articles</h2>
            <div class="popular-articles" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: var(--space-4);">
                <article class="popular-article" style="padding: var(--space-4); border: 1px solid var(--color-border); border-radius: var(--radius); transition: box-shadow 0.2s ease;">
                    <h3 style="color: var(--color-primary); margin-bottom: var(--space-2);">How to Screen for Growth Stocks</h3>
                    <p style="color: var(--color-text-muted); line-height: 1.6; margin-bottom: var(--space-3);">Learn the key metrics and filters to identify high-growth potential stocks using our screener.</p>
                    <a href="/growth-screening-guide/" style="color: var(--color-primary); font-weight: 600; text-decoration: none;">Read More →</a>
                </article>
                <article class="popular-article" style="padding: var(--space-4); border: 1px solid var(--color-border); border-radius: var(--radius); transition: box-shadow 0.2s ease;">
                    <h3 style="color: var(--color-primary); margin-bottom: var(--space-2);">Building Your First Watchlist</h3>
                    <p style="color: var(--color-text-muted); line-height: 1.6; margin-bottom: var(--space-3);">Step-by-step guide to creating and managing an effective stock watchlist.</p>
                    <a href="/watchlist-tutorial/" style="color: var(--color-primary); font-weight: 600; text-decoration: none;">Read More →</a>
                </article>
                <article class="popular-article" style="padding: var(--space-4); border: 1px solid var(--color-border); border-radius: var(--radius); transition: box-shadow 0.2s ease;">
                    <h3 style="color: var(--color-primary); margin-bottom: var(--space-2);">Understanding Market Data</h3>
                    <p style="color: var(--color-text-muted); line-height: 1.6; margin-bottom: var(--space-3);">Learn how to interpret the various market data points and indicators we provide.</p>
                    <a href="/market-data-guide/" style="color: var(--color-primary); font-weight: 600; text-decoration: none;">Read More →</a>
                </article>
            </div>
        </div>

        <div class="card glass-card p-6" style="text-align: center;">
            <h2 style="color: var(--color-text); margin-bottom: var(--space-4);">Still Need Help?</h2>
            <p style="color: var(--color-text-muted); margin-bottom: var(--space-5);">Can't find what you're looking for? Our support team is ready to assist you.</p>
            <div style="display: flex; gap: var(--space-3); justify-content: center; flex-wrap: wrap;">
                <a href="/contact/" class="btn btn-primary">Contact Support</a>
                <a href="/faq/" class="btn btn-outline">View FAQ</a>
            </div>
        </div>
    </div>
</div>
<?php get_footer(); ?>