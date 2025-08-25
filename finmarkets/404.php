<?php if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <div class="card" style="padding:32px; text-align:center;">
      <h1 style="margin:0; color:var(--navy);">Page not found</h1>
      <p class="muted">The page you’re looking for doesn’t exist or was moved.</p>
      <a class="btn btn-primary" href="<?php echo esc_url(home_url('/')); ?>">Go home</a>
    </div>
  </div>
</section>
<?php get_footer(); ?>