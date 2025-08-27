<?php
/**
 * 404 Template
 */
get_header();
?>
<main id="main-content" class="site-main">
  <div class="container">
    <?php get_template_part('template-parts/breadcrumbs'); ?>
    <div class="page-header">
      <h1 class="page-title">Page not found</h1>
      <p class="page-description">We couldn't find the page you were looking for. Try searching or head back to the homepage.</p>
      <div class="search-container"><?php get_search_form(); ?></div>
      <div class="action-buttons text-center">
        <a class="btn btn-secondary" href="<?php echo esc_url(home_url('/')); ?>"><span>Go to Homepage</span></a>
      </div>
    </div>
  </div>
</main>
<?php get_footer(); ?>