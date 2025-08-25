<?php /* Template Name: Payment - Success */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <div class="card" style="padding:24px; text-align:center;">
      <h1 style="color:var(--navy);">Payment Successful</h1>
      <p class="muted">Your Pro plan is active. Enjoy advanced screeners and exports.</p>
      <a class="btn btn-primary" href="<?php echo esc_url(home_url('/')); ?>">Go to Dashboard</a>
    </div>
  </div>
</section>
<?php get_footer(); ?>