<?php
/**
 * Single (block posts): 404
 */
get_header();
?>
<main id="main-content" class="site-main">
  <div class="container">
    <?php get_template_part('template-parts/breadcrumbs'); ?>
    <div class="page-header">
      <h1 class="page-title">Content not available</h1>
      <p class="page-description">This site does not publish blog posts. Please use the navigation above.</p>
      <a class="btn btn-secondary" href="<?php echo esc_url(home_url('/')); ?>"><span>Go Home</span></a>
    </div>
  </div>
</main>
<?php get_footer(); ?>