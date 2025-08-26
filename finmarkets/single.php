<?php
/**
 * Single Post Template
 */
get_header();
?>
<main class="site-main">
  <div class="container">
    <?php get_template_part('template-parts/breadcrumbs'); ?>
    <?php while (have_posts()): the_post(); ?>
      <article <?php post_class('card'); ?> >
        <div class="card-header">
          <h1 class="card-title"><?php the_title(); ?></h1>
          <div class="card-subtitle">
            <span><?php echo esc_html(get_the_date()); ?></span>
            <span> · </span>
            <span>by <?php the_author_posts_link(); ?></span>
            <?php if (has_category()): ?>
              <span> · in <?php the_category(', '); ?></span>
            <?php endif; ?>
          </div>
        </div>
        <div class="card-body">
          <?php if (has_post_thumbnail()): ?>
            <div style="margin-bottom:1.25rem;">
              <?php the_post_thumbnail('large', ['style' => 'border-radius:12px; width:100%; height:auto;']); ?>
            </div>
          <?php endif; ?>
          <?php the_content(); ?>
          <div class="d-flex justify-content-between" style="margin-top:2rem;">
            <div><?php previous_post_link('%link', '← Previous'); ?></div>
            <div><?php next_post_link('%link', 'Next →'); ?></div>
          </div>
        </div>
      </article>
      <?php if (comments_open() || get_comments_number()): comments_template(); endif; ?>
    <?php endwhile; ?>
  </div>
</main>
<?php get_footer(); ?>