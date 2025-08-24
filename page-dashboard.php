<?php
/**
 * Template Name: Dashboard (v3)
 */
get_header(); ?>
<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php _e('Dashboard', 'stock-scanner'); ?></h1>
      <p class="section-subtitle"><?php _e('Your market overview, alerts and recent activity', 'stock-scanner'); ?></p>
    </header>
    <div class="card glass-card">
      <div class="card-body">
        <?php echo do_shortcode('[stock_scanner_dashboard]'); ?>
      </div>
    </div>
  </div>
</section>
<?php get_footer(); ?>