<?php /* Template Name: Premium Plans */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section" id="pricing" aria-label="Pricing plans">
  <div class="container">
    <div class="grid cols-3">
      <div class="card" style="padding:20px;">
        <h3>Free</h3>
        <p class="muted">Basics for casual browsing</p>
        <ul>
          <li>Real-time watchlist</li>
          <li>Community screens</li>
          <li>News summaries</li>
        </ul>
        <a class="btn btn-ghost" href="<?php echo esc_url(home_url('/checkout')); ?>">Start free</a>
      </div>
      <div class="card" style="padding:20px; border:2px solid #d7e3ff; box-shadow: 0 10px 24px rgba(27,110,243,0.15);">
        <h3>Pro</h3>
        <p class="muted">Advanced filtering and export</p>
        <ul>
          <li>All Free features</li>
          <li>Advanced screeners</li>
          <li>Unlimited portfolios</li>
        </ul>
        <a class="btn btn-primary" href="<?php echo esc_url(home_url('/checkout')); ?>">Upgrade</a>
      </div>
      <div class="card" style="padding:20px;">
        <h3>Enterprise</h3>
        <p class="muted">Teams, SSO, priority support</p>
        <ul>
          <li>Team workspaces</li>
          <li>Audit logs</li>
          <li>Dedicated support</li>
        </ul>
        <a class="btn" href="#contact">Contact sales</a>
      </div>
    </div>
  </div>
</section>
<?php get_footer(); ?>