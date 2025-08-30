<?php
/**
 * Search Results Template
 *
 * Styles the default WordPress search results without altering the query.
 * Includes: filters header (UI-only), result cards with meta, excerpt highlighting,
 * and a clear empty state.
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$search_query = get_search_query();
$allowed_markup = [ 'mark' => [] ];
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <header class="mb-8">
    <h1 class="text-2xl font-semibold mb-2">
      <?php printf( esc_html__( 'Search results for: %s', 'retail-trade-scanner' ), '<span class="text-primary">' . esc_html( $search_query ) . '</span>' ); ?>
    </h1>

    <!-- Filters header (UI only, does not change WP_Query) -->
    <div class="flex flex-wrap items-center gap-3 mt-4">
      <span class="text-sm text-muted-foreground"><?php esc_html_e('Filters (visual only):', 'retail-trade-scanner'); ?></span>
      <div class="flex gap-2">
        <button type="button" class="inline-flex items-center rounded-full border px-3 py-1 text-sm hover:shadow-sm">
          <?php esc_html_e('All', 'retail-trade-scanner'); ?>
        </button>
        <button type="button" class="inline-flex items-center rounded-full border px-3 py-1 text-sm hover:shadow-sm">
          <?php esc_html_e('Posts', 'retail-trade-scanner'); ?>
        </button>
        <button type="button" class="inline-flex items-center rounded-full border px-3 py-1 text-sm hover:shadow-sm">
          <?php esc_html_e('Pages', 'retail-trade-scanner'); ?>
        </button>
      </div>

      <form role="search" method="get" class="ml-auto flex gap-2" action="<?php echo esc_url( home_url( '/' ) ); ?>">
        <label class="sr-only" for="search-field"><?php esc_html_e('Search for:', 'retail-trade-scanner'); ?></label>
        <input id="search-field" class="border rounded-md px-3 py-2" type="search" name="s" value="<?php echo esc_attr( $search_query ); ?>" placeholder="<?php esc_attr_e('Refine search…', 'retail-trade-scanner'); ?>" />
        <button class="rounded-md bg-primary text-primary-foreground px-4 py-2" type="submit"><?php esc_html_e('Search', 'retail-trade-scanner'); ?></button>
      </form>
    </div>
  </header>

  <?php if ( have_posts() ) : ?>
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <?php
      while ( have_posts() ) :
        the_post();
        $excerpt = get_the_excerpt();
        if ( $search_query ) {
          $pattern = '/' . preg_quote( $search_query, '/' ) . '/i';
          $excerpt = preg_replace( $pattern, '<mark>$0</mark>', $excerpt );
        }
      ?>
        <article id="post-<?php the_ID(); ?>" <?php post_class('rounded-xl border p-5 hover:shadow-sm transition'); ?>>
          <header class="mb-3">
            <h2 class="text-lg font-semibold leading-snug">
              <a class="hover:underline" href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
            </h2>
            <div class="mt-1 text-xs text-muted-foreground flex flex-wrap items-center gap-2">
              <time datetime="<?php echo esc_attr( get_the_date('c') ); ?>"><?php echo esc_html( get_the_date() ); ?></time>
              <span>•</span>
              <span><?php echo esc_html( get_the_author() ); ?></span>
              <?php $cats = get_the_category_list( ', ' ); if ( $cats ) : ?>
                <span>•</span><span class="truncate"><?php echo wp_kses_post( $cats ); ?></span>
              <?php endif; ?>
            </div>
          </header>

          <div class="prose dark:prose-invert max-w-none text-sm leading-relaxed">
            <?php echo wp_kses( $excerpt, $allowed_markup ); ?>
          </div>

          <footer class="mt-4 flex items-center justify-between">
            <a class="text-sm text-primary hover:underline" href="<?php the_permalink(); ?>"><?php esc_html_e('Read more', 'retail-trade-scanner'); ?></a>
            <?php $tags = get_the_tag_list('', ', '); if ( $tags ) : ?>
              <div class="text-xs text-muted-foreground truncate"><?php echo wp_kses_post( $tags ); ?></div>
            <?php endif; ?>
          </footer>
        </article>
      <?php endwhile; ?>
    </div>

    <nav class="mt-10">
      <?php the_posts_pagination([
        'mid_size'  => 2,
        'prev_text' => esc_html__('Previous', 'retail-trade-scanner'),
        'next_text' => esc_html__('Next', 'retail-trade-scanner'),
      ]); ?>
    </nav>

  <?php else : ?>
    <section class="text-center py-16 border rounded-xl">
      <h2 class="text-xl font-semibold mb-2"><?php esc_html_e('No results found', 'retail-trade-scanner'); ?></h2>
      <p class="text-muted-foreground mb-6"><?php esc_html_e('Try broadening your search or check your spelling.', 'retail-trade-scanner'); ?></p>
      <div class="max-w-md mx-auto">
        <?php get_search_form(); ?>
      </div>
    </section>
  <?php endif; ?>
</main>

<?php get_footer(); ?>