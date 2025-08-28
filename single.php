<?php
/**
 * Single post template
 */
get_header(); ?>
<main id="main-content" class="site-main">
  <div class="container">
    <?php get_template_part('template-parts/breadcrumbs'); ?>
    <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
      <article <?php post_class('card'); ?> >
        <div class="card-header">
          <h1 class="card-title"><?php the_title(); ?></h1>
          <div class="card-subtitle"><?php echo esc_html(get_the_date()); ?></div>
        </div>
        <div class="card-body">
          <?php if (has_post_thumbnail()) { echo get_the_post_thumbnail(get_the_ID(), 'large', ['class' => 'card-thumbnail','loading' => 'lazy','decoding' => 'async']); } ?>
          <div class="entry-content">
            <?php the_content(); ?>
          </div>
        </div>
        <div class="card-footer">
          <?php $posts_page = (int) get_option('page_for_posts'); $back_url = $posts_page ? get_permalink($posts_page) : home_url('/'); ?>
          <a class="btn btn-secondary" href="<?php echo esc_url($back_url); ?>"><span><?php esc_html_e('Back', 'retail-trade-scanner'); ?></span></a>
        </div>
      </article>

      <?php if (comments_open() || get_comments_number()) { comments_template(); } ?>
    <?php endwhile; endif; ?>
  </div>
</main>
<?php get_footer(); ?>