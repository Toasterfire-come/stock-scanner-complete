<?php
/**
 * Posts Index (Blog) Template - Enhanced Default View
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <!-- Hero Section for Better Default Experience -->
  <section class="text-center py-16 mb-12">
    <h1 class="text-4xl font-bold mb-4"><?php bloginfo('name'); ?></h1>
    <p class="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
      <?php 
      $description = get_bloginfo('description');
      if (empty($description)) {
        echo 'Professional stock trading and market analysis platform';
      } else {
        echo esc_html($description);
      }
      ?>
    </p>
    
    <!-- Call to Action Buttons -->
    <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
      <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="inline-flex items-center justify-center px-6 py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:shadow-lg transition">
        🔍 Start Scanning Stocks
      </a>
      <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="inline-flex items-center justify-center px-6 py-3 rounded-lg border border-border font-semibold hover:shadow-sm transition">
        📊 View Dashboard
      </a>
    </div>
  </section>

  <!-- Quick Features Overview -->
  <section class="grid gap-6 md:grid-cols-3 mb-12">
    <div class="card p-6 text-center">
      <div class="text-3xl mb-3">📈</div>
      <h3 class="text-lg font-semibold mb-2">Stock Scanner</h3>
      <p class="text-sm text-muted-foreground">Find trading opportunities with advanced filtering and screening tools.</p>
    </div>
    <div class="card p-6 text-center">
      <div class="text-3xl mb-3">📋</div>
      <h3 class="text-lg font-semibold mb-2">Portfolio Tracking</h3>
      <p class="text-sm text-muted-foreground">Monitor your investments and track performance in real-time.</p>
    </div>
    <div class="card p-6 text-center">
      <div class="text-3xl mb-3">🔔</div>
      <h3 class="text-lg font-semibold mb-2">Price Alerts</h3>
      <p class="text-sm text-muted-foreground">Get notified when stocks reach your target prices.</p>
    </div>
  </section>

  <!-- Trial Offer Section -->
  <section class="mb-12 border rounded-xl p-6 lg:p-8 bg-gradient-to-r from-primary/5 to-primary/10">
    <div class="grid gap-6 lg:grid-cols-2 items-center">
      <div>
        <h2 class="text-2xl font-bold mb-3">Start Your 7‑Day Trial for $1</h2>
        <p class="text-muted-foreground mb-4">Get full access to all features with our special trial offer. Use code <strong class="text-primary">TRIAL</strong> at checkout.</p>
        <ul class="text-sm space-y-2 mb-6">
          <li class="flex items-center gap-2">
            <span class="text-green-600 font-bold">✓</span>
            <span>Advanced stock scanning tools</span>
          </li>
          <li class="flex items-center gap-2">
            <span class="text-green-600 font-bold">✓</span>
            <span>Real-time portfolio tracking</span>
          </li>
          <li class="flex items-center gap-2">
            <span class="text-green-600 font-bold">✓</span>
            <span>Unlimited price alerts</span>
          </li>
          <li class="flex items-center gap-2">
            <span class="text-green-600 font-bold">✓</span>
            <span>Market news and analysis</span>
          </li>
        </ul>
      </div>
      <div class="text-center">
        <div class="bg-primary/10 rounded-full p-8 mb-4 inline-block">
          <div class="text-4xl">🚀</div>
        </div>
        <div class="space-y-3">
          <a href="<?php echo esc_url(home_url('/paypal-checkout/?plan=bronze&billing=monthly')); ?>" class="block w-full px-6 py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:shadow-lg transition">
            Start $1 Trial
          </a>
          <a href="<?php echo esc_url(home_url('/help/')); ?>" class="block w-full px-6 py-3 rounded-lg border border-border font-semibold hover:shadow-sm transition">
            Learn More
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- Blog Posts Section -->
  <?php if ( have_posts() ) : ?>
    <section>
      <header class="mb-8 text-center">
        <h2 class="text-2xl font-semibold mb-2">Latest Updates</h2>
        <p class="text-muted-foreground">Stay informed with market insights and platform updates</p>
      </header>
      
      <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <?php while ( have_posts() ) : the_post(); ?>
          <article id="post-<?php the_ID(); ?>" <?php post_class('card p-5 hover:shadow-lg transition'); ?>>
            <?php if (has_post_thumbnail()) : ?>
              <div class="mb-3 rounded-lg overflow-hidden">
                <?php the_post_thumbnail('card-thumb', ['class' => 'w-full h-48 object-cover']); ?>
              </div>
            <?php endif; ?>
            
            <header class="mb-3">
              <h3 class="text-lg font-semibold leading-snug">
                <a class="hover:text-primary transition" href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
              </h3>
              <div class="mt-2 text-xs text-muted-foreground flex flex-wrap items-center gap-2">
                <time datetime="<?php echo esc_attr( get_the_date('c') ); ?>"><?php echo esc_html( get_the_date() ); ?></time>
                <span>•</span>
                <span><?php echo esc_html( get_the_author() ); ?></span>
                <?php if (get_the_category()) : ?>
                  <span>•</span>
                  <span><?php the_category(', '); ?></span>
                <?php endif; ?>
              </div>
            </header>
            
            <div class="text-sm leading-relaxed text-muted-foreground mb-4">
              <?php echo wp_trim_words(get_the_excerpt(), 20, '...'); ?>
            </div>
            
            <footer class="flex items-center justify-between">
              <a class="text-primary hover:underline text-sm font-medium" href="<?php the_permalink(); ?>">
                Read More →
              </a>
              <?php if (get_comments_number() > 0) : ?>
                <span class="text-xs text-muted-foreground">
                  <?php comments_number('0 comments', '1 comment', '% comments'); ?>
                </span>
              <?php endif; ?>
            </footer>
          </article>
        <?php endwhile; ?>
      </div>
      
      <nav class="mt-12 text-center">
        <?php the_posts_pagination([
          'mid_size'  => 2,
          'prev_text' => '← Previous',
          'next_text' => 'Next →',
          'before_page_number' => '<span class="sr-only">Page </span>',
        ]); ?>
      </nav>
    </section>
  <?php else : ?>
    <!-- Empty State with Better Design -->
    <section class="text-center py-16 border border-dashed rounded-xl">
      <div class="text-6xl mb-4">📊</div>
      <h2 class="text-xl font-semibold mb-2">Welcome to Your Trading Platform</h2>
      <p class="text-muted-foreground mb-6 max-w-md mx-auto">
        No blog posts yet, but you can start exploring our powerful trading tools and features.
      </p>
      
      <div class="flex flex-col sm:flex-row gap-3 justify-center">
        <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="inline-flex items-center justify-center px-4 py-2 rounded-lg bg-primary text-primary-foreground font-medium hover:shadow-sm transition">
          Start Scanning
        </a>
        <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="inline-flex items-center justify-center px-4 py-2 rounded-lg border border-border font-medium hover:shadow-sm transition">
          View Dashboard
        </a>
        <a href="<?php echo esc_url(home_url('/help/')); ?>" class="inline-flex items-center justify-center px-4 py-2 rounded-lg border border-border font-medium hover:shadow-sm transition">
          Get Help
        </a>
      </div>
      
      <div class="mt-8">
        <?php get_search_form(); ?>
      </div>
    </section>
  <?php endif; ?>
</main>

<?php get_footer(); ?>

