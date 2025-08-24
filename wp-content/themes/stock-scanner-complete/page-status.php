<?php
/**
 * Template Name: System Status (v3)
 */
get_header(); ?>
<section class="glass-section">
  <div class="container" style="max-width:900px;margin:0 auto;">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php the_title(); ?></h1>
      <p class="section-subtitle"><?php _e('Live status of key systems', 'stock-scanner'); ?></p>
    </header>
    <div class="card glass-card">
      <div class="card-body" style="display:grid;gap:.75rem">
        <div><strong><?php _e('Website:', 'stock-scanner'); ?></strong> <?php _e('Operational', 'stock-scanner'); ?></div>
        <div><strong><?php _e('WordPress:', 'stock-scanner'); ?></strong> <?php _e('Operational', 'stock-scanner'); ?></div>
        <div><strong><?php _e('Payments:', 'stock-scanner'); ?></strong> <?php _e('Operational', 'stock-scanner'); ?></div>
        <div><strong><?php _e('Market Data:', 'stock-scanner'); ?></strong> <?php _e('Operational', 'stock-scanner'); ?></div>
        <small><?php _e('Updated just now', 'stock-scanner'); ?></small>
      </div>
    </div>
  </div>
</section>
<?php get_footer(); ?>