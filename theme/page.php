<?php
/**
 * Page Template
 */
get_header();
?>
<main id="main-content" class="site-main">
  <div class="container">
    <?php while (have_posts()): the_post(); ?>
      <article <?php post_class(); ?> >
        <div class="page-header">
          <h1 class="page-title"><?php the_title(); ?></h1>
          <?php if (has_excerpt()): ?>
            <p class="page-description"><?php echo esc_html(get_the_excerpt()); ?></p>
          <?php endif; ?>
        </div>
        <div class="page-content">
          <?php the_content(); ?>
        </div>
      </article>
    <?php endwhile; ?>
  </div>
</main>
<?php get_footer(); ?>