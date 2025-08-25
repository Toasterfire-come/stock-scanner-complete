<?php /* Template Name: Compare Plans */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient">Compare Our Plans</h1>
      <p class="section-subtitle">Choose the perfect plan for your stock analysis needs</p>
    </header>

    <div class="card glass-card"><div class="card-body">
      <div class="table-responsive">
        <table class="table" data-sortable>
          <thead><tr><th>Feature</th><th>Basic</th><th>Premium</th><th>Pro</th></tr></thead>
          <tbody>
            <tr><td>Real‑time quotes</td><td>—</td><td><span class="badge badge-green">Yes</span></td><td><span class="badge badge-green">Yes</span></td></tr>
            <tr><td>Indicators</td><td>10</td><td>50+</td><td>50+ &amp; AI</td></tr>
            <tr><td>Alerts</td><td>—</td><td><span class="badge badge-green">Yes</span></td><td><span class="badge badge-green">Yes</span></td></tr>
            <tr><td>Portfolio analytics</td><td>Basic</td><td>Advanced</td><td>Advanced + Risk</td></tr>
            <tr><td>Support</td><td>Email</td><td>Priority</td><td>Priority</td></tr>
          </tbody>
        </table>
      </div>
    </div></div>

    <div class="hero-actions" style="margin-top:1rem">
      <a href="<?php echo esc_url(wp_registration_url()); ?>" class="btn btn-primary btn-lg" data-cta>Start 7‑Day Trial for $1</a>
      <a href="/premium-plans/" class="btn btn-outline btn-lg" data-cta>Go to Plans</a>
    </div>
  </div>
</section>
<?php get_footer(); ?>