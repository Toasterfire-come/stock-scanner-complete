<?php
/**
 * Posts Index (Blog) Template
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <!-- Conversion Offer: 7-day Trial for $1 with code TRIAL -->
  <section class="mb-8 border rounded-xl p-5 bg-muted/30">
    <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-semibold m-0">Start Your 7‑Day Trial for $1</h2>
        <p class="text-muted-foreground m-0">Use code <strong>TRIAL</strong> at checkout. Applies to any plan.</p>
      </div>
      <div class="flex items-center gap-3">
        <a class="inline-flex items-center justify-center px-5 py-2 rounded-md bg-primary text-primary-foreground hover:shadow-sm transition" href="/paypal-checkout/?plan=bronze&billing=monthly">Start $1 Trial</a>
        <a class="inline-flex items-center justify-center px-5 py-2 rounded-md border text-primary hover:shadow-sm transition" href="/paypal-checkout/">Compare Plans</a>
      </div>
    </div>
  </section>
  <header class="mb-8">
    <h1 class="text-2xl font-semibold mb-2"><?php bloginfo('name'); ?></h1>
    <p class="text-muted-foreground"><?php bloginfo('description'); ?> · Try any plan for 7 days — only $1 with code <strong>TRIAL</strong>.</p>
  </header>

  <?php if ( have_posts() ) : ?>
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <?php while ( have_posts() ) : the_post(); ?>
        <article id="post-<?php the_ID(); ?>" <?php post_class('rounded-xl border p-5 hover:shadow-sm transition'); ?>>
          <header class="mb-3">
            <h2 class="text-lg font-semibold leading-snug">
              <a class="hover:underline" href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
            </h2>
            <div class="mt-1 text-xs text-muted-foreground flex flex-wrap items-center gap-2">
              <time datetime="<?php echo esc_attr( get_the_date('c') ); ?>"><?php echo esc_html( get_the_date() ); ?></time>
              <span>•</span>
              <span><?php echo esc_html( get_the_author() ); ?></span>
            </div>
          </header>
          <div class="text-sm leading-relaxed"><?php the_excerpt(); ?></div>
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
      <h2 class="text-xl font-semibold mb-2"><?php esc_html_e('No posts found', 'retail-trade-scanner'); ?></h2>
      <div class="max-w-md mx-auto"><?php get_search_form(); ?></div>
    </section>
  <?php endif; ?>
</main>

<?php get_footer(); ?>

