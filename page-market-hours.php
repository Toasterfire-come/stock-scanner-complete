<?php
/**
 * Template Name: Market Hours & Holidays (v3)
 */
get_header(); ?>
<section class="glass-section">
  <div class="container" style="max-width:900px;margin:0 auto;">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php the_title(); ?></h1>
    </header>
    <div class="card glass-card">
      <div class="card-body" style="display:grid;gap:1rem">
        <h3><?php _e('US Markets (NYSE/Nasdaq)', 'stock-scanner'); ?></h3>
        <p><?php _e('Open: 9:30 AM ET • Close: 4:00 PM ET • Pre‑Market and After‑Hours vary by broker.', 'stock-scanner'); ?></p>
        <h3><?php _e('Common US Holidays', 'stock-scanner'); ?></h3>
        <ul>
          <li><?php _e('New Year’s Day', 'stock-scanner'); ?></li>
          <li><?php _e('MLK Jr. Day', 'stock-scanner'); ?></li>
          <li><?php _e('Presidents’ Day', 'stock-scanner'); ?></li>
          <li><?php _e('Good Friday', 'stock-scanner'); ?></li>
          <li><?php _e('Memorial Day', 'stock-scanner'); ?></li>
          <li><?php _e('Juneteenth', 'stock-scanner'); ?></li>
          <li><?php _e('Independence Day', 'stock-scanner'); ?></li>
          <li><?php _e('Labor Day', 'stock-scanner'); ?></li>
          <li><?php _e('Thanksgiving', 'stock-scanner'); ?></li>
          <li><?php _e('Christmas', 'stock-scanner'); ?></li>
        </ul>
        <p><?php _e('Check your exchange for the most accurate schedule.', 'stock-scanner'); ?></p>
      </div>
    </div>
  </div>
</section>
<?php get_footer(); ?>