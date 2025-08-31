<?php
/**
 * Enhanced Index Template with Modern Design
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main">
  <?php if ( have_posts() ) : ?>
    <!-- Modern Content Grid -->
    <section class="fade-in">
      <header class="text-center mb-8">
        <h1 class="text-4xl font-bold mb-4">
          <?php
          if (is_home() && !is_front_page()) {
            single_post_title();
          } elseif (is_front_page()) {
            esc_html_e('Welcome to ', 'retail-trade-scanner');
            bloginfo('name');
          } else {
            esc_html_e('Latest Updates', 'retail-trade-scanner');
          }
          ?>
        </h1>
        <p class="text-xl text-muted mb-8">
          <?php esc_html_e('Stay informed with the latest market insights and platform updates', 'retail-trade-scanner'); ?>
        </p>
      </header>
      
      <div class="grid grid-3 gap-6">
        <?php while ( have_posts() ) : the_post(); ?>
          <article id="post-<?php the_ID(); ?>" <?php post_class('card hover-effect'); ?>>
            <?php if ( has_post_thumbnail() ) : ?>
              <div class="card-image mb-4" style="border-radius: var(--radius); overflow: hidden; height: 200px;">
                <a href="<?php the_permalink(); ?>">
                  <?php the_post_thumbnail('card-thumb', ['style' => 'width: 100%; height: 100%; object-fit: cover;']); ?>
                </a>
              </div>
            <?php endif; ?>
            
            <header class="mb-4">
              <div class="flex items-center gap-3 mb-3 text-sm text-muted">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12,6 12,12 16,14"></polyline>
                </svg>
                <time datetime="<?php echo esc_attr( get_the_date('c') ); ?>">
                  <?php echo esc_html( get_the_date() ); ?>
                </time>
                <span>•</span>
                <span><?php echo esc_html( get_the_author() ); ?></span>
              </div>
              
              <h2 class="text-xl font-semibold leading-tight mb-3">
                <a class="hover:text-primary transition-colors" href="<?php the_permalink(); ?>">
                  <?php the_title(); ?>
                </a>
              </h2>
            </header>
            
            <div class="text-muted mb-4 leading-relaxed">
              <?php echo wp_trim_words(get_the_excerpt(), 25, '...'); ?>
            </div>
            
            <footer class="flex items-center justify-between pt-4 border-t border-border">
              <div class="flex items-center gap-2 text-sm">
                <?php
                $categories = get_the_category();
                if (!empty($categories)) :
                ?>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                    <line x1="7" y1="7" x2="7.01" y2="7"></line>
                  </svg>
                  <span class="text-primary"><?php echo esc_html($categories[0]->name); ?></span>
                <?php endif; ?>
              </div>
              
              <a href="<?php the_permalink(); ?>" class="text-sm font-medium text-primary hover:text-primary-hover transition-colors flex items-center gap-1">
                <?php esc_html_e('Read More', 'retail-trade-scanner'); ?>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12,5 19,12 12,19"></polyline>
                </svg>
              </a>
            </footer>
          </article>
        <?php endwhile; ?>
      </div>
      
      <!-- Pagination -->
      <nav class="mt-12 flex justify-center" aria-label="Posts navigation">
        <?php
        $pagination = paginate_links([
          'mid_size'  => 2,
          'prev_text' => '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15,18 9,12 15,6"></polyline></svg> ' . __('Previous', 'retail-trade-scanner'),
          'next_text' => __('Next', 'retail-trade-scanner') . ' <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9,18 15,12 9,6"></polyline></svg>',
          'type'      => 'list',
        ]);
        
        if ($pagination) {
          echo str_replace('<ul class=', '<ul class="pagination flex items-center gap-2', $pagination);
        }
        ?>
      </nav>
    </section>
  <?php else : ?>
    <!-- Enhanced Welcome Screen for No Content -->
    <section class="text-center py-16 fade-in">
      <!-- Hero Section -->
      <div class="card p-8 mb-8 max-w-4xl mx-auto" style="background: linear-gradient(135deg, var(--surface) 0%, var(--surface-hover) 100%);">
        <div class="text-6xl mb-6">📈</div>
        <h1 class="text-4xl font-bold mb-4">
          <?php esc_html_e('Welcome to Your Trading Platform', 'retail-trade-scanner'); ?>
        </h1>
        <p class="text-xl text-muted mb-8 max-w-2xl mx-auto">
          <?php esc_html_e('Professional stock trading and market analysis platform designed for retail investors. Get started with our powerful tools and features.', 'retail-trade-scanner'); ?>
        </p>
        
        <!-- Quick Action Buttons -->
        <div class="flex flex-mobile-col gap-4 justify-center mb-8">
          <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="btn btn-primary">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="21 21l-4.35-4.35"></path>
            </svg>
            <?php esc_html_e('Start Stock Scanner', 'retail-trade-scanner'); ?>
          </a>
          <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="btn btn-outline">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
            <?php esc_html_e('View Dashboard', 'retail-trade-scanner'); ?>
          </a>
        </div>
        
        <!-- Setup Notice for Admins -->
        <?php if (current_user_can('manage_options')) : ?>
          <div class="card p-4 mb-6" style="background: rgba(225, 85, 84, 0.1); border-color: var(--accent);">
            <div class="flex items-center gap-3 text-sm">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--accent);">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              <div>
                <strong><?php esc_html_e('Admin Notice:', 'retail-trade-scanner'); ?></strong>
                <?php esc_html_e('This is your theme\'s default page.', 'retail-trade-scanner'); ?>
                <a href="<?php echo admin_url('themes.php?page=rts-create-pages'); ?>" class="text-accent hover:underline font-medium">
                  <?php esc_html_e('Create your theme pages', 'retail-trade-scanner'); ?>
                </a>
                <?php esc_html_e('to unlock the full trading platform experience.', 'retail-trade-scanner'); ?>
              </div>
            </div>
          </div>
        <?php endif; ?>
      </div>
      
      <!-- Feature Grid -->
      <div class="grid grid-3 gap-6 mb-12">
        <div class="card p-6">
          <div class="text-3xl mb-4" style="color: var(--primary);">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="21 21l-4.35-4.35"></path>
            </svg>
          </div>
          <h3 class="text-xl font-semibold mb-3"><?php esc_html_e('Stock Scanner', 'retail-trade-scanner'); ?></h3>
          <p class="text-muted mb-4"><?php esc_html_e('Advanced stock screening tool to find trading opportunities based on your custom criteria and technical indicators.', 'retail-trade-scanner'); ?></p>
          <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="text-primary hover:text-primary-hover font-medium flex items-center gap-2">
            <?php esc_html_e('Explore Scanner', 'retail-trade-scanner'); ?>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12,5 19,12 12,19"></polyline>
            </svg>
          </a>
        </div>
        
        <div class="card p-6">
          <div class="text-3xl mb-4" style="color: var(--primary);">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
          </div>
          <h3 class="text-xl font-semibold mb-3"><?php esc_html_e('Portfolio Tracking', 'retail-trade-scanner'); ?></h3>
          <p class="text-muted mb-4"><?php esc_html_e('Monitor your investments in real-time with comprehensive analytics, performance metrics, and risk assessment tools.', 'retail-trade-scanner'); ?></p>
          <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="text-primary hover:text-primary-hover font-medium flex items-center gap-2">
            <?php esc_html_e('View Portfolio', 'retail-trade-scanner'); ?>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12,5 19,12 12,19"></polyline>
            </svg>
          </a>
        </div>
        
        <div class="card p-6">
          <div class="text-3xl mb-4" style="color: var(--primary);">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <path d="M16 10a4 4 0 0 1-8 0"></path>
            </svg>
          </div>
          <h3 class="text-xl font-semibold mb-3"><?php esc_html_e('Price Alerts', 'retail-trade-scanner'); ?></h3>
          <p class="text-muted mb-4"><?php esc_html_e('Never miss important price movements with customizable alerts sent directly to your device or email.', 'retail-trade-scanner'); ?></p>
          <a href="<?php echo esc_url(home_url('/alerts/')); ?>" class="text-primary hover:text-primary-hover font-medium flex items-center gap-2">
            <?php esc_html_e('Setup Alerts', 'retail-trade-scanner'); ?>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12,5 19,12 12,19"></polyline>
            </svg>
          </a>
        </div>
      </div>
      
      <!-- CTA Section -->
      <div class="card p-8 max-w-2xl mx-auto" style="background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);">
        <h2 class="text-2xl font-bold mb-4" style="color: var(--primary-foreground);">
          <?php esc_html_e('Ready to Start Trading Smarter?', 'retail-trade-scanner'); ?>
        </h2>
        <p class="mb-6" style="color: rgba(255, 255, 255, 0.9);">
          <?php esc_html_e('Join thousands of retail investors who trust our platform for professional-grade market analysis and trading tools.', 'retail-trade-scanner'); ?>
        </p>
        <div class="flex flex-mobile-col gap-4 justify-center">
          <a href="<?php echo esc_url(home_url('/help/')); ?>" class="btn" style="background: rgba(255, 255, 255, 0.2); color: white; border: 1px solid rgba(255, 255, 255, 0.3);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <?php esc_html_e('Get Help & Tutorials', 'retail-trade-scanner'); ?>
          </a>
        </div>
      </div>
    </section>
  <?php endif; ?>
</main>

<style>
/* Custom pagination styles */
.pagination {
  list-style: none;
  padding: 0;
  margin: 0;
}

.pagination li {
  margin: 0;
}

.pagination a,
.pagination .current {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: var(--surface);
  color: var(--foreground);
  text-decoration: none;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
}

.pagination a:hover {
  background: var(--primary);
  color: var(--primary-foreground);
  border-color: var(--primary);
  transform: translateY(-1px);
}

.pagination .current {
  background: var(--primary);
  color: var(--primary-foreground);
  border-color: var(--primary);
}

/* Hover effects */
.hover-effect {
  transition: all 0.3s ease;
}

.hover-effect:hover {
  transform: translateY(-2px);
}

/* Card image hover effect */
.card-image a {
  display: block;
  position: relative;
  overflow: hidden;
}

.card-image a::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(55, 74, 103, 0.8);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-image a:hover::before {
  opacity: 1;
}
</style>

<?php get_footer(); ?>