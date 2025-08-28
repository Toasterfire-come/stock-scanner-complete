<?php
/**
 * Index fallback (no posts). If used as front page, consider setting a static page.
 */
get_header();
?>
<main id="main-content" class="site-main">
  <div class="container">
    <div class="page-header">
      <h1 class="page-title"><?php echo esc_html(get_bloginfo('name')); ?></h1>
      <p class="page-description"><?php echo esc_html(get_bloginfo('description')); ?></p>
    </div>

    <div class="grid-2">
      <div class="feature-card">
        <h4><?php esc_html_e('Get Started', 'retail-trade-scanner'); ?></h4>
        <p><?php esc_html_e('Use the navigation to access Dashboard, Watchlist, and Membership.', 'retail-trade-scanner'); ?></p>
        <a class="btn btn-primary" href="<?php echo esc_url(home_url('/stock-dashboard/')); ?>">
            <span><?php esc_html_e('Open Dashboard', 'retail-trade-scanner'); ?></span>
        </a>
      </div>
      <div class="feature-card">
        <h4><?php esc_html_e('Upgrade Anytime', 'retail-trade-scanner'); ?></h4>
        <p><?php esc_html_e('Unlock more features and higher limits by upgrading your plan.', 'retail-trade-scanner'); ?></p>
        <a class="btn btn-gold" href="<?php echo esc_url(home_url('/membership-plans/')); ?>">
            <span><?php esc_html_e('See Plans', 'retail-trade-scanner'); ?></span>
        </a>
      </div>
    </div>
  </div>
</main>
<?php get_footer(); ?>