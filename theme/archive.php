<?php
/** Archive Template */
get_header();
?>
<main id="main-content" class="site-main">
  <div class="container">
    <?php get_template_part('template-parts/breadcrumbs'); ?>
    <div class="page-header">
      <h1 class="page-title"><?php the_archive_title(); ?></h1>
      <?php if (get_the_archive_description()): ?><p class="page-description"><?php echo wp_kses_post(get_the_archive_description()); ?></p><?php endif; ?>
    </div>

    <div class="content-layout <?php echo is_active_sidebar('primary-sidebar') ? 'has-sidebar' : 'no-sidebar'; ?>">
      <div>
        <?php if (have_posts()): ?>
          <div class="pricing-table large-cards">
            <?php while (have_posts()): the_post(); ?>
              <article <?php post_class('card'); ?> >
                <div class="card-header">
                  <h2 class="card-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
                  <div class="card-subtitle"><?php echo esc_html(get_the_date()); ?></div>
                </div>
                <div class="card-body">
                  <?php if (has_post_thumbnail()) {
                    echo get_the_post_thumbnail(get_the_ID(), 'large', array('style'=>'border-radius:12px;width:100%;height:auto;margin-bottom:10px;','loading'=>'lazy','decoding'=>'async'));
                  } ?>
                  <?php the_excerpt(); ?>
                </div>
                <div class="card-footer"><a class="btn btn-primary" href="<?php the_permalink(); ?>"><span>Read More</span></a></div>
              </article>
            <?php endwhile; ?>
          </div>
          <div class="d-flex justify-content-center"><?php the_posts_pagination(); ?></div>
        <?php else: ?>
          <div class="card"><div class="card-body">No posts found.</div></div>
        <?php endif; ?>
      </div>
      <?php get_sidebar(); ?>
    </div>
  </div>
</main>
<?php get_footer(); ?>