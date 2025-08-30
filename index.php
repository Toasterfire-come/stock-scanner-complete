<?php
/**
 * Fallback Index Template - Enhanced Default View
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <!-- Welcome Hero Section -->
  <section class="text-center py-16 mb-12 border-b">
    <h1 class="text-4xl font-bold mb-4">Welcome to <?php bloginfo('name'); ?></h1>
    <p class="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
      Professional stock trading and market analysis platform for retail investors
    </p>
    
    <!-- Quick Action Buttons -->
    <div class="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
      <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="inline-flex items-center justify-center px-6 py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:shadow-lg transition">
        🔍 Start Stock Scanner
      </a>
      <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="inline-flex items-center justify-center px-6 py-3 rounded-lg border border-border font-semibold hover:shadow-sm transition">
        📊 View Dashboard
      </a>
    </div>
    
    <!-- Setup Notice -->
    <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 max-w-2xl mx-auto">
      <p class="text-sm">
        <strong>Getting Started:</strong> This is your theme's default page. 
        <a href="<?php echo admin_url('themes.php?page=rts-create-pages'); ?>" class="text-primary hover:underline">Create your theme pages</a> 
        to unlock the full trading platform experience.
      </p>
    </div>
  </section>

  <?php if ( have_posts() ) : ?>
    <section>
      <header class="mb-8 text-center">
        <h2 class="text-2xl font-semibold mb-2">Latest Content</h2>
        <p class="text-muted-foreground">Recent posts and updates</p>
      </header>
      
      <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <?php while ( have_posts() ) : the_post(); ?>
          <article id="post-<?php the_ID(); ?>" <?php post_class('card p-5 hover:shadow-lg transition'); ?>>
            <header class="mb-3">
              <h3 class="text-lg font-semibold leading-snug">
                <a class="hover:text-primary transition" href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
              </h3>
              <div class="mt-2 text-xs text-muted-foreground flex flex-wrap items-center gap-2">
                <time datetime="<?php echo esc_attr( get_the_date('c') ); ?>"><?php echo esc_html( get_the_date() ); ?></time>
                <span>•</span>
                <span><?php echo esc_html( get_the_author() ); ?></span>
              </div>
            </header>
            <div class="text-sm leading-relaxed text-muted-foreground">
              <?php echo wp_trim_words(get_the_excerpt(), 20, '...'); ?>
            </div>
          </article>
        <?php endwhile; ?>
      </div>
      
      <nav class="mt-10 text-center">
        <?php the_posts_pagination([
          'mid_size'  => 2,
          'prev_text' => '← Previous',
          'next_text' => 'Next →',
        ]); ?>
      </nav>
    </section>
  <?php else : ?>
    <!-- Enhanced Empty State -->
    <section class="text-center py-16">
      <div class="max-w-2xl mx-auto">
        <div class="text-6xl mb-6">📈</div>
        <h2 class="text-2xl font-semibold mb-4">Your Trading Platform Awaits</h2>
        <p class="text-muted-foreground mb-8">
          Welcome to your professional stock trading and analysis platform. Get started by exploring our powerful tools and features.
        </p>
        
        <!-- Feature Grid -->
        <div class="grid gap-6 md:grid-cols-3 mb-8">
          <div class="card p-4">
            <div class="text-2xl mb-2">🔍</div>
            <h3 class="font-semibold mb-1">Stock Scanner</h3>
            <p class="text-xs text-muted-foreground">Find opportunities with advanced filtering</p>
          </div>
          <div class="card p-4">
            <div class="text-2xl mb-2">📊</div>
            <h3 class="font-semibold mb-1">Portfolio Tracking</h3>
            <p class="text-xs text-muted-foreground">Monitor your investments in real-time</p>
          </div>
          <div class="card p-4">
            <div class="text-2xl mb-2">🔔</div>
            <h3 class="font-semibold mb-1">Price Alerts</h3>
            <p class="text-xs text-muted-foreground">Never miss important price movements</p>
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row gap-3 justify-center mb-8">
          <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="inline-flex items-center justify-center px-4 py-2 rounded-lg bg-primary text-primary-foreground font-medium hover:shadow-sm transition">
            Start Scanning Stocks
          </a>
          <a href="<?php echo esc_url(home_url('/help/')); ?>" class="inline-flex items-center justify-center px-4 py-2 rounded-lg border border-border font-medium hover:shadow-sm transition">
            Get Help & Tutorials
          </a>
        </div>
        
        <!-- Search Form -->
        <div class="max-w-md mx-auto">
          <?php get_search_form(); ?>
        </div>
      </div>
    </section>
  <?php endif; ?>
</main>

<?php get_footer(); ?>

