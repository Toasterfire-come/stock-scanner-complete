<?php
/**
 * 404 Template
 */
get_header();
?>
<main class="site-main">
  <div class="container">
    <?php get_template_part('template-parts/breadcrumbs'); ?>
    <div class="page-header">
      <h1 class="page-title">Page not found</h1>
      <p class="page-description">We couldn't find the page you were looking for. Try searching or head back to the homepage.</p>
      <div style="max-width:640px; margin: 0 auto;"><?php get_search_form(); ?></div>
      <div style="margin-top:1.5rem;">
        <a class="btn btn-secondary" href="<?php echo esc_url(home_url('/')); ?>"><span>Go to Homepage</span></a>
      </div>
    </div>
  </div>
</main>
<?php get_footer(); ?>