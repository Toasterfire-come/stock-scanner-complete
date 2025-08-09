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
    <div class="container" style="max-width:1100px;margin:40px auto;display:grid;grid-template-columns:280px 1fr;gap:24px;">
        <aside class="account-sidebar card">
            <h3>Account</h3>
            <ul style="list-style:none;padding:0;margin:0;">
                <li><a href="/account/">Overview</a></li>
                <li><a href="/watchlist/">Watchlists</a></li>
                <li><a href="/premium-plans/">Upgrade</a></li>
                <li><a href="<?php echo esc_url(wp_logout_url(home_url('/'))); ?>">Sign out</a></li>
            </ul>
        </aside>
        <main class="account-content">
            <div class="card" style="margin-bottom:16px;">
                <h2 style="margin-top:0;">Your Membership</h2>
                <?php echo do_shortcode('[stock_scanner_dashboard show_notifications="false" show_security_status="true"]'); ?>
            </div>
            <div class="card">
                <h3 style="margin-top:0;">Usage & Limits</h3>
                <?php echo do_shortcode('[stock_scanner_dashboard show_notifications="false" show_security_status="false"]'); ?>
            </div>
        </main>
    </div>
</div>

<?php get_footer(); ?>