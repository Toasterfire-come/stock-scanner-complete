<?php
/**
 * Template Name: Cookie Policy (v3)
 */
get_header(); ?>
<section class="glass-section">
  <div class="container" style="max-width:900px;margin:0 auto;">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php the_title(); ?></h1>
    </header>
    <div class="card glass-card">
      <div class="card-body">
        <p><?php _e('We use cookies to provide core site functionality, improve performance, and analyze usage.', 'stock-scanner'); ?></p>
        <ul>
          <li><?php _e('Strictly necessary cookies for login/session', 'stock-scanner'); ?></li>
          <li><?php _e('Preference cookies to remember settings', 'stock-scanner'); ?></li>
          <li><?php _e('Analytics cookies to improve the product', 'stock-scanner'); ?></li>
        </ul>
        <p><?php _e('You can control cookies in your browser settings.', 'stock-scanner'); ?></p>
      </div>
    </div>
  </div>
</section>
<?php get_footer(); ?>