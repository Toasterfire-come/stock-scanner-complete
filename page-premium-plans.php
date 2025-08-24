<?php
/**
 * Template Name: Premium Plans (Conversion-Optimized)
 */
get_header(); ?>
<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php _e('Choose Your Plan', 'stock-scanner'); ?></h1>
      <p class="section-subtitle"><?php _e('Start for $1. Upgrade, downgrade, or cancel anytime.', 'stock-scanner'); ?></p>
    </header>

    <div class="pricing-toggle glass-card" style="margin-bottom:1rem">
      <span class="toggle-label"><?php _e('Monthly', 'stock-scanner'); ?></span>
      <button class="toggle-switch" data-pricing-toggle><span class="toggle-slider"></span></button>
      <span class="toggle-label"><?php _e('Annual', 'stock-scanner'); ?> <span class="savings-badge gradient-primary"><?php _e('Save 20%', 'stock-scanner'); ?></span></span>
    </div>

    <div class="scroll-reveal">
      <?php echo do_shortcode('[stock_scanner_pricing show_trial="true" highlight_plan="premium" show_compare="true"]'); ?>
    </div>

    <div class="card glass-card" style="margin-top:1rem"><div class="card-body">
      <div class="features-grid">
        <div class="callout success"><strong>30‑day money‑back guarantee</strong><br><?php _e('If it’s not a fit, cancel within 30 days for a full refund.', 'stock-scanner'); ?></div>
        <div class="callout info"><strong>$1 full‑access trial</strong><br><?php _e('Try everything for 7 days for just $1. Cancel anytime.', 'stock-scanner'); ?></div>
        <div class="callout warn"><strong>No long‑term contracts</strong><br><?php _e('Upgrade, downgrade, or cancel from your account.', 'stock-scanner'); ?></div>
      </div>
    </div></div>

    <div class="accordion" data-accordion style="margin-top:1rem">
      <div class="accordion-item"><div class="accordion-header"><?php _e('What happens after the trial?', 'stock-scanner'); ?></div><div class="accordion-content"><?php _e('You’ll be billed the standard plan price unless you cancel during the trial.', 'stock-scanner'); ?></div></div>
      <div class="accordion-item"><div class="accordion-header"><?php _e('Can I change plans later?', 'stock-scanner'); ?></div><div class="accordion-content"><?php _e('Yes, switch any time. Changes take effect immediately for upgrades and at period end for downgrades.', 'stock-scanner'); ?></div></div>
      <div class="accordion-item"><div class="accordion-header"><?php _e('Do you offer team plans?', 'stock-scanner'); ?></div><div class="accordion-content"><?php _e('Contact us for team pricing and invoicing.', 'stock-scanner'); ?></div></div>
    </div>

    <div class="hero-actions" style="margin-top:1rem">
      <a href="<?php echo wp_registration_url(); ?>" class="btn btn-primary btn-lg" data-cta><?php _e('Start 7‑Day Trial for $1', 'stock-scanner'); ?></a>
      <a href="/compare-plans/" class="btn btn-outline btn-lg" data-cta><?php _e('Compare Plans', 'stock-scanner'); ?></a>
    </div>
  </div>
</section>
<?php get_footer(); ?>