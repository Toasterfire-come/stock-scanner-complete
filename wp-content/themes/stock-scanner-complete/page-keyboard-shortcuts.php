<?php
/**
 * Template Name: Keyboard Shortcuts (v3)
 */
get_header(); ?>
<section class="glass-section">
  <div class="container" style="max-width:900px;margin:0 auto;">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php the_title(); ?></h1>
    </header>
    <div class="card glass-card">
      <div class="card-body">
        <ul>
          <li>G then D — <?php _e('Go to Dashboard', 'stock-scanner'); ?></li>
          <li>G then L — <?php _e('Go to Stock Lookup', 'stock-scanner'); ?></li>
          <li>/ — <?php _e('Focus search input', 'stock-scanner'); ?></li>
          <li>J / K — <?php _e('Navigate lists', 'stock-scanner'); ?></li>
          <li>Shift + ? — <?php _e('Open this shortcuts list', 'stock-scanner'); ?></li>
        </ul>
      </div>
    </div>
  </div>
</section>
<?php get_footer(); ?>