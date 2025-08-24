<?php
/**
 * Template Name: Roadmap (v3)
 */
get_header(); ?>
<section class="glass-section">
  <div class="container" style="max-width:900px;margin:0 auto;">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php the_title(); ?></h1>
    </header>
    <div class="card glass-card">
      <div class="card-body">
        <h3>Q1</h3>
        <ul>
          <li><?php _e('Performance improvements', 'stock-scanner'); ?></li>
          <li><?php _e('More screeners', 'stock-scanner'); ?></li>
        </ul>
        <h3>Q2</h3>
        <ul>
          <li><?php _e('Alerting enhancements', 'stock-scanner'); ?></li>
          <li><?php _e('Portfolio analytics', 'stock-scanner'); ?></li>
        </ul>
      </div>
    </div>
  </div>
</section>
<?php get_footer(); ?>