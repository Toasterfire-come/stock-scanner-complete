<?php
/*
Template Name: Compare Plans (Conversion-Optimized)
*/
get_header(); ?>
<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php _e('Compare Our Plans', 'stock-scanner'); ?></h1>
      <p class="section-subtitle"><?php _e('Choose the perfect plan for your stock analysis needs', 'stock-scanner'); ?></p>
    </header>

    <div class="card glass-card"><div class="card-body">
      <div class="table-responsive">
        <table data-sortable>
          <thead><tr><th><?php _e('Feature', 'stock-scanner'); ?></th><th><?php _e('Basic', 'stock-scanner'); ?></th><th><?php _e('Premium', 'stock-scanner'); ?></th><th><?php _e('Pro', 'stock-scanner'); ?></th></tr></thead>
          <tbody>
            <tr><td><?php _e('Real‑time quotes', 'stock-scanner'); ?></td><td>—</td><td><span class="badge-yes">Yes</span></td><td><span class="badge-yes">Yes</span></td></tr>
            <tr><td><?php _e('Indicators', 'stock-scanner'); ?></td><td>10</td><td>50+</td><td>50+ & AI</td></tr>
            <tr><td><?php _e('Alerts', 'stock-scanner'); ?></td><td>—</td><td><span class="badge-yes">Yes</span></td><td><span class="badge-yes">Yes</span></td></tr>
            <tr><td><?php _e('Portfolio analytics', 'stock-scanner'); ?></td><td>Basic</td><td>Advanced</td><td>Advanced + Risk</td></tr>
            <tr><td><?php _e('Support', 'stock-scanner'); ?></td><td>Email</td><td>Priority</td><td>Priority</td></tr>
          </tbody>
        </table>
      </div>
    </div></div>

    <div class="hero-actions" style="margin-top:1rem">
      <a href="<?php echo wp_registration_url(); ?>" class="btn btn-primary btn-lg" data-cta><?php _e('Start 7‑Day Trial for $1', 'stock-scanner'); ?></a>
      <a href="/premium-plans/" class="btn btn-outline btn-lg" data-cta><?php _e('Go to Plans', 'stock-scanner'); ?></a>
    </div>
  </div>
</section>
<?php get_footer(); ?>