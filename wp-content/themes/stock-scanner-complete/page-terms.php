<?php
/**
 * Template Name: Terms of Service (v3)
 */
get_header(); ?>
<section class="glass-section">
  <div class="container" style="max-width:900px;margin:0 auto;">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php the_title(); ?></h1>
    </header>
    <div class="card glass-card">
      <div class="card-body">
        <p><?php _e('By using this site, you agree to the following terms and conditions.', 'stock-scanner'); ?></p>
        <h3><?php _e('Use of Service', 'stock-scanner'); ?></h3>
        <p><?php _e('Do not misuse the service or attempt to disrupt operations.', 'stock-scanner'); ?></p>
        <h3><?php _e('No Financial Advice', 'stock-scanner'); ?></h3>
        <p><?php _e('Information provided is for educational purposes only and not investment advice.', 'stock-scanner'); ?></p>
      </div>
    </div>
  </div>
</section>
<?php get_footer(); ?>