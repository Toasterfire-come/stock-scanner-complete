<?php /* Template Name: Backend Offline */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content" style="max-width:760px;">
    <div class="card" style="padding:24px; text-align:center;">
      <h1 style="color:var(--navy); margin:0 0 8px;">Service Temporarily Unavailable</h1>
      <p class="muted">Our data backend is not connected right now. Public pages remain accessible, but data pages are paused.</p>
      <div style="margin-top:16px;">
        <?php echo do_shortcode('[finm_health]'); ?>
      </div>
      <div style="margin-top:16px; display:flex; gap:8px; justify-content:center; flex-wrap:wrap;">
        <a class="btn" href="<?php echo esc_url(home_url('/')); ?>">Go to Home</a>
        <a class="btn" href="<?php echo esc_url(home_url('/news')); ?>">Market News</a>
        <a class="btn" href="<?php echo esc_url(home_url('/help-center')); ?>">Help Center</a>
      </div>
      <?php if (current_user_can('manage_options')): ?>
      <div class="card" style="padding:12px; margin-top:16px; text-align:left;">
        <strong>Admin tip:</strong>
        <ol style="margin:8px 0 0 18px;">
          <li>Open Appearance → FinMarkets Settings.</li>
          <li>Enter your API Base URL (e.g., https://api.example.com).</li>
          <li>Optionally add your API Key (Bearer), then Save.</li>
          <li>Reload this page to re-run health checks.</li>
        </ol>
      </div>
      <?php endif; ?>
    </div>
  </div>
</section>
<?php get_footer(); ?>