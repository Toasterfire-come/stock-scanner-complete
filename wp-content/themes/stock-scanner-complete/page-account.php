<?php
/**
 * Template Name: My Account (v3)
 */
if (!is_user_logged_in()) { wp_redirect(wp_login_url(get_permalink())); exit; }
get_header(); ?>

<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient">⚙️ <?php _e('My Account', 'stock-scanner'); ?></h1>
      <p class="section-subtitle"><?php _e('Manage your membership, usage, and settings', 'stock-scanner'); ?></p>
    </header>

    <div class="features-grid">
      <aside class="card glass-card">
        <div class="card-body">
          <h3 class="section-title" style="font-size:1.1rem;margin-bottom:.75rem"><?php _e('Account', 'stock-scanner'); ?></h3>
          <ul style="list-style:none;padding:0;display:grid;gap:.25rem">
            <li><a class="user-menu-item" href="/account/">Overview</a></li>
            <li><a class="user-menu-item" href="/watchlist/">Watchlists</a></li>
            <li><a class="user-menu-item" href="/portfolio/">Portfolios</a></li>
            <li><a class="user-menu-item" href="/premium-plans/">Upgrade</a></li>
            <li><a class="user-menu-item" href="<?php echo esc_url(wp_logout_url(home_url('/'))); ?>"><?php _e('Sign out', 'stock-scanner'); ?></a></li>
          </ul>
        </div>
      </aside>

      <section class="card glass-card" role="region" aria-label="Account content">
        <div class="card-body">
          <h2 class="section-title" style="font-size:1.25rem"><?php _e('Your Membership', 'stock-scanner'); ?></h2>
          <?php echo do_shortcode('[stock_scanner_dashboard show_notifications="false" show_security_status="true"]'); ?>
        </div>
      </section>

      <section class="card glass-card">
        <div class="card-body">
          <h3 class="section-title" style="font-size:1.25rem"><?php _e('Usage & Limits', 'stock-scanner'); ?></h3>
          <?php echo do_shortcode('[stock_scanner_dashboard show_notifications="false" show_security_status="false"]'); ?>
        </div>
      </section>
    </div>
  </div>
</section>

<?php get_footer(); ?>