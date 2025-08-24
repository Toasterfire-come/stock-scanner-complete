<?php
/**
 * Template Name: Accessibility (v3)
 */
get_header(); ?>
<section class="glass-section">
  <div class="container" style="max-width:900px;margin:0 auto;">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php the_title(); ?></h1>
    </header>
    <div class="card glass-card">
      <div class="card-body">
        <p><?php _e('We aim to meet WCAG 2.1 AA guidelines and continuously improve accessibility.', 'stock-scanner'); ?></p>
        <ul>
          <li><?php _e('Keyboard navigable components', 'stock-scanner'); ?></li>
          <li><?php _e('High-contrast color options', 'stock-scanner'); ?></li>
          <li><?php _e('Semantic HTML and ARIA labels', 'stock-scanner'); ?></li>
          <li><?php _e('Responsive design', 'stock-scanner'); ?></li>
        </ul>
        <p><?php _e('If you find any issues, please', 'stock-scanner'); ?> <a href="/contact/"><?php _e('contact us', 'stock-scanner'); ?></a>.</p>
      </div>
    </div>
  </div>
</section>
<?php get_footer(); ?>