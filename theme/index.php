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
        <h4>Get Started</h4>
        <p>Use the navigation to access Dashboard, Watchlist, and Membership.</p>
        <a class="btn btn-primary" href="/stock-dashboard/"><span>Open Dashboard</span></a>
      </div>
      <div class="feature-card">
        <h4>Upgrade Anytime</h4>
        <p>Unlock more features and higher limits by upgrading your plan.</p>
        <a class="btn btn-gold" href="/membership-plans/"><span>See Plans</span></a>
      </div>
    </div>
  </div>
</main>
<?php get_footer(); ?>