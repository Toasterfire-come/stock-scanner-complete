<?php
/**
 * Search Results Template (Modernized for v3 styles)
 */
get_header(); ?>

<section class="glass-section">
  <div class="container">
    <header class="section-intro scroll-reveal">
      <h1 class="section-title">
        <?php
        global $wp_query; $total_results = $wp_query->found_posts;
        if (have_posts()) {
          printf(
            _n('%1$s result found for "%2$s"', '%1$s results found for "%2$s"', $total_results, 'stock-scanner'),
            number_format_i18n($total_results),
            '<span class="text-gradient">' . esc_html(get_search_query()) . '</span>'
          );
        } else {
          printf(__('No results found for "%s"', 'stock-scanner'), '<span class="text-gradient">' . esc_html(get_search_query()) . '</span>');
        }
        ?>
      </h1>

      <form role="search" method="get" class="search-form" action="<?php echo esc_url(home_url('/')); ?>" style="max-width:600px;margin:1rem auto 0;display:flex;gap:.5rem">
        <label class="screen-reader-text"><?php _e('Search for:', 'stock-scanner'); ?></label>
        <input type="search" class="form-control" placeholder="<?php echo esc_attr_x('Search...', 'placeholder', 'stock-scanner'); ?>" value="<?php echo esc_attr(get_search_query()); ?>" name="s" />
        <button type="submit" class="btn btn-primary">🔍 <?php _e('Search', 'stock-scanner'); ?></button>
      </form>
    </header>

    <div class="search-content">
      <?php if (have_posts()) : ?>
        <div class="features-grid">
          <?php while (have_posts()) : the_post(); ?>
            <article id="post-<?php the_ID(); ?>" <?php post_class('card glass-card scroll-reveal'); ?>>
              <div class="card-body">
                <div class="result-meta" style="display:flex;gap:.5rem;color:var(--color-text-muted);font-size:.875rem">
                  <span>
                    <?php $post_type_obj = get_post_type_object(get_post_type()); echo esc_html($post_type_obj->labels->singular_name); ?>
                  </span>
                  <span>•</span>
                  <span><?php echo esc_html(get_the_date()); ?></span>
                </div>
                <h2 class="card-title" style="margin:.5rem 0 1rem 0;">
                  <a href="<?php the_permalink(); ?>" style="text-decoration:none;color:var(--color-text)"><?php the_title(); ?></a>
                </h2>
                <p style="color:var(--color-text-light)">
                  <?php
                  $excerpt = get_the_excerpt();
                  if (empty($excerpt)) { $content = get_the_content(); $excerpt = wp_trim_words(strip_tags($content), 30, '...'); }
                  $search_query = get_search_query();
                  if (!empty($search_query)) { $excerpt = preg_replace('/(' . preg_quote($search_query, '/') . ')/i', '<mark>$1</mark>', $excerpt); }
                  echo wp_kses_post($excerpt);
                  ?>
                </p>
                <div class="card-footer" style="display:flex;justify-content:space-between;align-items:center">
                  <a class="btn btn-outline btn-sm" href="<?php the_permalink(); ?>"><?php _e('Read More', 'stock-scanner'); ?> →</a>
                  <span class="result-url" style="font-size:.75rem;color:var(--color-text-muted)"><?php echo esc_url(get_permalink()); ?></span>
                </div>
              </div>
            </article>
          <?php endwhile; ?>
        </div>

        <div class="search-pagination" style="text-align:center;margin-top:2rem;">
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
          <div style="font-size:3rem;opacity:.6">🔍</div>
          <h2 class="section-title" style="font-size:1.5rem;margin:.5rem 0;"><?php _e('No results found', 'stock-scanner'); ?></h2>
          <p class="section-subtitle" style="max-width:560px;margin:0 auto 1rem;">
            <?php printf(__('Sorry, we couldn\'t find any results for "%s". Try adjusting your search terms or browse our popular content.', 'stock-scanner'), esc_html(get_search_query())); ?>
          </p>
          <div class="hero-actions">
            <a href="<?php echo esc_url(home_url('/stock-screener/')); ?>" class="btn btn-outline">Stock Screener</a>
            <a href="<?php echo esc_url(home_url('/market-overview/')); ?>" class="btn btn-outline">Market Overview</a>
            <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="btn btn-outline">Portfolio</a>
          </div>
        </div>
      <?php endif; ?>
    </div>
  </div>
</section>

<?php get_footer(); ?>