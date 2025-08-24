<?php
/**
 * Archive Template (Modernized for v3 styles)
 */
get_header(); ?>

<section class="glass-section">
  <div class="container">
    <header class="section-intro scroll-reveal">
      <h1 class="section-title text-gradient">
        <?php
        if (is_category()) {
          single_cat_title();
        } elseif (is_tag()) {
          single_tag_title();
        } elseif (is_author()) {
          printf(__('Posts by %s', 'stock-scanner'), get_the_author());
        } elseif (is_day()) {
          printf(__('Daily Archives: %s', 'stock-scanner'), get_the_date());
        } elseif (is_month()) {
          printf(__('Monthly Archives: %s', 'stock-scanner'), get_the_date('F Y'));
        } elseif (is_year()) {
          printf(__('Yearly Archives: %s', 'stock-scanner'), get_the_date('Y'));
        } else {
          _e('Archives', 'stock-scanner');
        }
        ?>
      </h1>
      <?php if (category_description() || tag_description()) : ?>
        <p class="section-subtitle"><?php echo wp_kses_post(category_description() . tag_description()); ?></p>
      <?php endif; ?>
    </header>

    <div class="archive-content">
      <?php if (have_posts()) : ?>
        <div class="features-grid">
          <?php while (have_posts()) : the_post(); ?>
            <article id="post-<?php the_ID(); ?>" <?php post_class('card glass-card scroll-reveal'); ?>>
              <?php if (has_post_thumbnail()) : ?>
                <a href="<?php the_permalink(); ?>" class="block">
                  <?php the_post_thumbnail('medium', array('class' => 'w-100', 'alt' => esc_attr(get_the_title()))); ?>
                </a>
              <?php endif; ?>

              <div class="card-body">
                <div class="post-meta" style="display:flex;gap:.5rem;color:var(--color-text-muted);font-size:.875rem">
                  <span><?php echo esc_html(get_the_date()); ?></span>
                  <span>•</span>
                  <span><?php the_author(); ?></span>
                </div>

                <h2 class="card-title" style="margin:.5rem 0 1rem 0;">
                  <a href="<?php the_permalink(); ?>" style="text-decoration:none;color:var(--color-text)"><?php the_title(); ?></a>
                </h2>

                <p style="color:var(--color-text-light)">
                  <?php echo has_excerpt() ? esc_html(get_the_excerpt()) : esc_html(wp_trim_words(get_the_content(), 30, '...')); ?>
                </p>

                <div class="card-footer" style="display:flex;justify-content:space-between;align-items:center">
                  <a class="btn btn-outline btn-sm" href="<?php the_permalink(); ?>"><?php _e('Read More', 'stock-scanner'); ?> →</a>
                  <?php if (has_category()) : ?>
                    <div class="post-categories" style="font-size:.75rem;color:var(--color-text-muted)">
                      <?php the_category(', '); ?>
                    </div>
                  <?php endif; ?>
                </div>
              </div>
            </article>
          <?php endwhile; ?>
        </div>

        <div class="archive-pagination" style="text-align:center;margin-top:2rem;">
          <?php
          the_posts_pagination(array(
            'mid_size'  => 2,
            'prev_text' => __('← Previous', 'stock-scanner'),
            'next_text' => __('Next →', 'stock-scanner'),
          ));
          ?>
        </div>
      <?php else : ?>
        <div class="card glass-card" style="text-align:center;padding:2rem;">
          <div style="font-size:3rem;opacity:.6">📝</div>
          <h2 class="section-title" style="font-size:1.5rem;margin:.5rem 0;"><?php _e('No posts found', 'stock-scanner'); ?></h2>
          <p class="section-subtitle" style="max-width:560px;margin:0 auto 1rem;"><?php _e('Sorry, no posts were found in this archive. Try searching for something else.', 'stock-scanner'); ?></p>
          <a href="<?php echo esc_url(home_url('/')); ?>" class="btn btn-primary"><?php _e('Back to Home', 'stock-scanner'); ?></a>
        </div>
      <?php endif; ?>
    </div>
  </div>
</section>

<?php get_footer(); ?>