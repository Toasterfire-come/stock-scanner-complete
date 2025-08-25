<?php /* Template Name: Payment - Cancel */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <div class="card" style="padding:24px; text-align:center;">
      <h1 style="color:var(--navy);">Payment Canceled</h1>
      <p class="muted">Your payment was canceled. You can restart checkout anytime.</p>
      <a class="btn" href="<?php echo esc_url(home_url('/')); ?>">Return home</a>
    </div>
  </div>
</section>
<?php get_footer(); ?>