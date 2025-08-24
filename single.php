<?php
/**
 * Single Post Template (Modernized for v3 styles)
 */
get_header(); ?>

<section class="glass-section">
  <div class="container">
    <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
      <article id="post-<?php the_ID(); ?>" <?php post_class('card glass-card'); ?>>
        <header class="card-header" style="text-align:center">
          <div class="post-meta" style="display:flex;justify-content:center;gap:.5rem;color:var(--color-text-muted);font-size:.875rem">
            <span><?php echo esc_html(get_the_date()); ?></span>
            <span>•</span>
            <span><?php the_author(); ?></span>
            <?php if (has_category()) : ?>
              <span>•</span>
              <span><?php the_category(', '); ?></span>
            <?php endif; ?>
          </div>
          <h1 class="section-title" style="margin-top:.5rem"><?php the_title(); ?></h1>
          <?php if (has_post_thumbnail()) : ?>
            <div style="margin-top:1rem">
              <?php the_post_thumbnail('large', array('class' => 'w-100', 'alt' => esc_attr(get_the_title()), 'style' => 'border-radius:var(--radius-xl);box-shadow:var(--shadow-md)')); ?>
            </div>
          <?php endif; ?>
        </header>

        <div class="card-body">
          <?php the_content(); ?>
          <?php
          wp_link_pages(array(
            'before' => '<div class="page-links">',
            'after'  => '</div>',
            'link_before' => '<span class="page-number">',
            'link_after'  => '</span>',
          ));
          ?>
        </div>

        <footer class="card-footer" style="display:grid;gap:1rem">
          <?php if (has_tag()) : ?>
            <div class="stock-scanner-widget" style="padding:1rem;border-radius:var(--radius-lg)">
              <strong><?php _e('Tags:', 'stock-scanner'); ?></strong> <?php the_tags('', ', ', ''); ?>
            </div>
          <?php endif; ?>

          <div class="post-navigation" style="display:grid;grid-template-columns:1fr 1fr;gap:1rem">
            <?php $prev_post = get_previous_post(); $next_post = get_next_post(); ?>
            <div>
              <?php if ($prev_post) : ?>
                <a class="btn btn-outline w-100" href="<?php echo esc_url(get_permalink($prev_post)); ?>">← <?php echo esc_html(get_the_title($prev_post)); ?></a>
              <?php endif; ?>
            </div>
            <div style="text-align:right">
              <?php if ($next_post) : ?>
                <a class="btn btn-outline w-100" href="<?php echo esc_url(get_permalink($next_post)); ?>"><?php echo esc_html(get_the_title($next_post)); ?> →</a>
              <?php endif; ?>
            </div>
          </div>
        </footer>
      </article>

      <?php if (comments_open() || get_comments_number()) : comments_template(); endif; ?>
    <?php endwhile; endif; ?>
  </div>
</section>

<?php get_footer(); ?>