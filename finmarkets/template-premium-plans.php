<?php /* Template Name: Premium Plans */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient">Choose Your Plan</h1>
      <p class="section-subtitle">Start for $1. Upgrade, downgrade, or cancel anytime.</p>
    </header>

    <div class="pricing-toggle glass-card" style="margin-bottom:1rem">
      <span class="toggle-label">Monthly</span>
      <button class="toggle-switch" data-pricing-toggle><span class="toggle-slider"></span></button>
      <span class="toggle-label">Annual <span class="savings-badge gradient-primary">Save 20%</span></span>
    </div>

    <div class="scroll-reveal">
      <?php if (shortcode_exists('stock_scanner_pricing')) { echo do_shortcode('[stock_scanner_pricing show_trial="true" highlight_plan="premium" show_compare="true"]'); } ?>
    </div>

    <div class="card glass-card" style="margin-top:1rem"><div class="card-body">
      <div class="features-grid">
        <div class="callout success"><strong>30‑day money‑back guarantee</strong><br>If it’s not a fit, cancel within 30 days for a full refund.</div>
        <div class="callout info"><strong>$1 full‑access trial</strong><br>Try everything for 7 days for just $1. Cancel anytime.</div>
        <div class="callout warn"><strong>No long‑term contracts</strong><br>Upgrade, downgrade, or cancel from your account.</div>
      </div>
    </div></div>

    <div class="accordion" data-accordion style="margin-top:1rem">
      <div class="accordion-item"><div class="accordion-header">What happens after the trial?</div><div class="accordion-content">You’ll be billed the standard plan price unless you cancel during the trial.</div></div>
      <div class="accordion-item"><div class="accordion-header">Can I change plans later?</div><div class="accordion-content">Yes, switch any time. Changes take effect immediately for upgrades and at period end for downgrades.</div></div>
      <div class="accordion-item"><div class="accordion-header">Do you offer team plans?</div><div class="accordion-content">Contact us for team pricing and invoicing.</div></div>
    </div>

    <div class="hero-actions" style="margin-top:1rem">
      <a href="<?php echo esc_url(wp_registration_url()); ?>" class="btn btn-primary btn-lg" data-cta>Start 7‑Day Trial for $1</a>
      <a href="/compare-plans/" class="btn btn-outline btn-lg" data-cta>Compare Plans</a>
    </div>
  </div>
</section>
<?php get_footer(); ?>