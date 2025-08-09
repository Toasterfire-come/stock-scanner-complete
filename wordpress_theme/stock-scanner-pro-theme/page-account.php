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
    <div class="container">
        <div class="page-header">
            <h1>⚙️ My Account</h1>
            <p class="page-description">Manage your membership, usage, and settings</p>
        </div>
        <div class="account-grid">
            <aside class="account-sidebar card">
                <h3 class="account-sidebar-title">Account</h3>
                <ul class="account-nav">
                    <li><a href="/account/">Overview</a></li>
                    <li><a href="/watchlist/">Watchlists</a></li>
                    <li><a href="/portfolio/">Portfolios</a></li>
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
</div>

<?php get_footer(); ?>