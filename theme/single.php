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
      <h1 class="page-title"><?php esc_html_e('Content not available', 'retail-trade-scanner'); ?></h1>
      <p class="page-description"><?php esc_html_e('This site does not publish blog posts. Please use the navigation above.', 'retail-trade-scanner'); ?></p>
      <a class="btn btn-secondary" href="<?php echo esc_url(home_url('/')); ?>">
          <span><?php esc_html_e('Go Home', 'retail-trade-scanner'); ?></span>
      </a>
    </div>
  </div>
</main>
<?php get_footer(); ?>