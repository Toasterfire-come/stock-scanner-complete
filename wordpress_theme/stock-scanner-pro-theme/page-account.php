<?php
/**
 * Template Name: My Account
 */

if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header(); ?>

<div class="account-page">
    <div class="container account-grid">
        <aside class="account-sidebar card">
            <h3 class="account-sidebar-title">Account</h3>
            <ul class="account-nav">
                <li><a href="/account/">Overview</a></li>
                <li><a href="/watchlist/">Watchlists</a></li>
                <li><a href="/premium-plans/">Upgrade</a></li>
                <li><a href="<?php echo esc_url(wp_logout_url(home_url('/'))); ?>">Sign out</a></li>
            </ul>
        </aside>
        <main class="account-content">
            <div class="card account-card">
                <h2>Your Membership</h2>
                <?php echo do_shortcode('[stock_scanner_dashboard show_notifications="false" show_security_status="true"]'); ?>
            </div>
            <div class="card account-card">
                <h3>Usage & Limits</h3>
                <?php echo do_shortcode('[stock_scanner_dashboard show_notifications="false" show_security_status="false"]'); ?>
            </div>
        </main>
    </div>
</div>

<style>
.account-grid {
    max-width: 1100px;
    margin: 40px auto;
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 24px;
}

.account-sidebar.card {
    background: var(--bg-primary, #ffffff);
    border: 1px solid var(--border-color, #e2e8f0);
    border-radius: var(--radius-lg, 12px);
    box-shadow: var(--shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
    padding: 20px;
}

.account-sidebar-title {
    margin: 0 0 12px 0;
    color: var(--text-primary, #1e293b);
}

.account-nav {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    gap: 8px;
}

.account-nav a {
    display: block;
    color: var(--text-primary, #1e293b);
    text-decoration: none;
    padding: 10px 12px;
    border-radius: var(--radius-md, 8px);
    transition: background var(--transition-fast, .15s), color var(--transition-fast, .15s), transform .2s ease;
}

.account-nav a:hover {
    background: var(--bg-muted, #f1f5f9);
    color: var(--primary-color, #2563eb);
    transform: translateX(2px);
}

.account-card {
    margin-bottom: 16px;
    background: var(--bg-primary, #ffffff);
    border: 1px solid var(--border-color, #e2e8f0);
    border-radius: var(--radius-lg, 12px);
    box-shadow: var(--shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
    padding: 20px;
}

.account-card h2, .account-card h3 {
    margin-top: 0;
    color: var(--text-primary, #1e293b);
}

/* Responsive */
@media (max-width: 960px) {
  .account-grid { grid-template-columns: 1fr; }
}
</style>

<?php get_footer(); ?>