<?php
/**
 * Search Results Template - Modern Design
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main">
  <div class="fade-in">
    <!-- Search Header -->
    <header class="search-header mb-8">
      <div class="flex-between mb-6">
        <div>
          <h1 class="text-3xl font-bold mb-2">
            <?php
            printf(
              esc_html__('Search Results for: %s', 'retail-trade-scanner'),
              '<span class="search-query" style="color: var(--primary);">' . get_search_query() . '</span>'
            );
            ?>
          </h1>
          <?php if (have_posts()) : ?>
            <p class="text-muted">
              <?php
              global $wp_query;
              printf(
                esc_html(_n('Found %s result', 'Found %s results', $wp_query->found_posts, 'retail-trade-scanner')),
                '<strong>' . number_format_i18n($wp_query->found_posts) . '</strong>'
              );
              ?>
            </p>
          <?php endif; ?>
        </div>
        
        <!-- Search Form -->
        <div class="search-form-container">
          <div class="enhanced-search-form">
            <?php get_search_form(); ?>
          </div>
        </div>
      </div>
      
      <!-- Search Filters (Placeholder for future enhancement) -->
      <div class="search-filters mb-6">
        <div class="flex items-center gap-4 flex-wrap">
          <span class="text-sm font-medium text-muted"><?php esc_html_e('Filter by:', 'retail-trade-scanner'); ?></span>
          <button class="filter-btn active" data-filter="all">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M12 1v6m0 6v6"></path>
              <path d="m21 12-6 0m-6 0-6 0"></path>
            </svg>
            <?php esc_html_e('All Content', 'retail-trade-scanner'); ?>
          </button>
          <button class="filter-btn" data-filter="posts">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
            </svg>
            <?php esc_html_e('Articles', 'retail-trade-scanner'); ?>
          </button>
          <button class="filter-btn" data-filter="pages">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
            <?php esc_html_e('Pages', 'retail-trade-scanner'); ?>
          </button>
        </div>
      </div>
    </header>

    <?php if (have_posts()) : ?>
      <!-- Search Results -->
      <section class="search-results">
        <div class="results-grid space-y-6">
          <?php while (have_posts()) : the_post(); ?>
            <article id="post-<?php the_ID(); ?>" <?php post_class('search-result-item card p-6 hover:transform hover:scale-[1.01] transition-all'); ?>>
              <div class="flex gap-6">
                <!-- Thumbnail -->
                <?php if (has_post_thumbnail()) : ?>
                  <div class="result-thumbnail flex-shrink-0 hidden md:block">
                    <a href="<?php the_permalink(); ?>" class="block w-32 h-24 rounded-lg overflow-hidden">
                      <?php the_post_thumbnail('medium', ['class' => 'w-full h-full object-cover']); ?>
                    </a>
                  </div>
                <?php endif; ?>
                
                <!-- Content -->
                <div class="result-content flex-1">
                  <!-- Meta Info -->
                  <div class="result-meta flex items-center gap-4 mb-3 text-sm text-muted">
                    <div class="flex items-center gap-2">
                      <?php if (get_post_type() === 'post') : ?>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                          <polyline points="14,2 14,8 20,8"></polyline>
                        </svg>
                        <span><?php esc_html_e('Article', 'retail-trade-scanner'); ?></span>
                      <?php else : ?>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                        </svg>
                        <span><?php esc_html_e('Page', 'retail-trade-scanner'); ?></span>
                      <?php endif; ?>
                    </div>
                    
                    <div class="flex items-center gap-2">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12,6 12,12 16,14"></polyline>
                      </svg>
                      <time datetime="<?php echo esc_attr(get_the_date('c')); ?>">
                        <?php echo esc_html(get_the_date()); ?>
                      </time>
                    </div>
                    
                    <?php if (get_post_type() === 'post') : ?>
                      <div class="flex items-center gap-2">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                          <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                        <span><?php echo esc_html(get_the_author()); ?></span>
                      </div>
                    <?php endif; ?>
                  </div>
                  
                  <!-- Title -->
                  <h2 class="result-title text-xl font-semibold mb-3 leading-tight">
                    <a href="<?php the_permalink(); ?>" class="text-foreground hover:text-primary transition-colors">
                      <?php
                      $title = get_the_title();
                      $search_query = get_search_query();
                      
                      // Highlight search terms in title
                      if ($search_query) {
                        $highlighted_title = preg_replace(
                          '/(' . preg_quote($search_query, '/') . ')/i',
                          '<mark style="background: var(--accent); color: var(--accent-foreground); padding: 0 2px; border-radius: 3px;">$1</mark>',
                          $title
                        );
                        echo wp_kses($highlighted_title, ['mark' => ['style' => []]]);
                      } else {
                        the_title();
                      }
                      ?>
                    </a>
                  </h2>
                  
                  <!-- Excerpt -->
                  <div class="result-excerpt text-muted mb-4 leading-relaxed">
                    <?php
                    $excerpt = wp_trim_words(get_the_excerpt(), 30, '...');
                    $search_query = get_search_query();
                    
                    // Highlight search terms in excerpt
                    if ($search_query) {
                      $highlighted_excerpt = preg_replace(
                        '/(' . preg_quote($search_query, '/') . ')/i',
                        '<mark style="background: var(--accent); color: var(--accent-foreground); padding: 0 2px; border-radius: 3px;">$1</mark>',
                        $excerpt
                      );
                      echo wp_kses($highlighted_excerpt, ['mark' => ['style' => []]]);
                    } else {
                      echo esc_html($excerpt);
                    }
                    ?>
                  </div>
                  
                  <!-- Tags/Categories -->
                  <?php if (get_post_type() === 'post') : ?>
                    <?php
                    $categories = get_the_category();
                    if (!empty($categories)) :
                    ?>
                      <div class="result-tags flex items-center gap-2 mb-3">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-muted">
                          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                          <line x1="7" y1="7" x2="7.01" y2="7"></line>
                        </svg>
                        <?php foreach (array_slice($categories, 0, 3) as $category) : ?>
                          <a href="<?php echo esc_url(get_category_link($category->term_id)); ?>" 
                             class="inline-flex items-center px-2 py-1 rounded text-xs font-medium transition-colors hover:transform hover:scale-105"
                             style="background: rgba(55, 74, 103, 0.1); color: var(--primary); text-decoration: none;">
                            <?php echo esc_html($category->name); ?>
                          </a>
                        <?php endforeach; ?>
                      </div>
                    <?php endif; ?>
                  <?php endif; ?>
                  
                  <!-- Read More -->
                  <div class="result-action">
                    <a href="<?php the_permalink(); ?>" 
                       class="inline-flex items-center gap-2 text-primary hover:text-primary-hover font-medium text-sm transition-colors">
                      <?php esc_html_e('Read More', 'retail-trade-scanner'); ?>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                        <polyline points="12,5 19,12 12,19"></polyline>
                      </svg>
                    </a>
                  </div>
                </div>
              </div>
            </article>
          <?php endwhile; ?>
        </div>
        
        <!-- Pagination -->
        <nav class="search-pagination mt-12" aria-label="Search Results Navigation">
          <?php
          $pagination = paginate_links([
            'mid_size'  => 2,
            'prev_text' => '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15,18 9,12 15,6"></polyline></svg> ' . __('Previous', 'retail-trade-scanner'),
            'next_text' => __('Next', 'retail-trade-scanner') . ' <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9,18 15,12 9,6"></polyline></svg>',
            'type'      => 'list',
          ]);
          
          if ($pagination) {
            echo str_replace('<ul class=', '<ul class="pagination flex items-center justify-center gap-2', $pagination);
          }
          ?>
        </nav>
      </section>
      
    <?php else : ?>
      <!-- No Results -->
      <section class="no-results text-center py-16">
        <div class="max-w-2xl mx-auto">
          <div class="no-results-icon mb-6" style="color: var(--muted-foreground);">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="margin: 0 auto;">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="21 21l-4.35-4.35"></path>
              <line x1="11" y1="8" x2="11" y2="12"></line>
              <line x1="11" y1="16" x2="11.01" y2="16"></line>
            </svg>
          </div>
          
          <h2 class="text-2xl font-bold mb-4">
            <?php esc_html_e('No Results Found', 'retail-trade-scanner'); ?>
          </h2>
          
          <p class="text-muted mb-8">
            <?php 
            printf(
              esc_html__('Sorry, we couldn\'t find any results for "%s". Try refining your search terms or explore our popular content below.', 'retail-trade-scanner'),
              '<strong>' . get_search_query() . '</strong>'
            );
            ?>
          </p>
          
          <!-- Search Suggestions -->
          <div class="search-suggestions card p-6 mb-8">
            <h3 class="text-lg font-semibold mb-4"><?php esc_html_e('Search Suggestions:', 'retail-trade-scanner'); ?></h3>
            <ul class="text-left space-y-2 text-muted">
              <li>• <?php esc_html_e('Check your spelling and try again', 'retail-trade-scanner'); ?></li>
              <li>• <?php esc_html_e('Try different or more general keywords', 'retail-trade-scanner'); ?></li>
              <li>• <?php esc_html_e('Use fewer keywords for broader results', 'retail-trade-scanner'); ?></li>
              <li>• <?php esc_html_e('Try searching for related trading terms', 'retail-trade-scanner'); ?></li>
            </ul>
          </div>
          
          <!-- Popular Pages -->
          <div class="popular-content">
            <h3 class="text-lg font-semibold mb-6"><?php esc_html_e('Popular Pages', 'retail-trade-scanner'); ?></h3>
            <div class="grid grid-3 gap-4">
              <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="popular-link card p-4 hover:transform hover:scale-105 transition-all">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center" style="background: var(--primary);">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                      <circle cx="11" cy="11" r="8"></circle>
                      <path d="21 21l-4.35-4.35"></path>
                    </svg>
                  </div>
                  <span class="font-medium"><?php esc_html_e('Stock Scanner', 'retail-trade-scanner'); ?></span>
                </div>
              </a>
              
              <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="popular-link card p-4 hover:transform hover:scale-105 transition-all">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center" style="background: var(--accent);">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                      <line x1="18" y1="20" x2="18" y2="10"></line>
                      <line x1="12" y1="20" x2="12" y2="4"></line>
                      <line x1="6" y1="20" x2="6" y2="14"></line>
                    </svg>
                  </div>
                  <span class="font-medium"><?php esc_html_e('Portfolio', 'retail-trade-scanner'); ?></span>
                </div>
              </a>
              
              <a href="<?php echo esc_url(home_url('/help/')); ?>" class="popular-link card p-4 hover:transform hover:scale-105 transition-all">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center" style="background: var(--davys-gray);">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                      <circle cx="12" cy="12" r="10"></circle>
                      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                      <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                  </div>
                  <span class="font-medium"><?php esc_html_e('Help Center', 'retail-trade-scanner'); ?></span>
                </div>
              </a>
            </div>
          </div>
        </div>
      </section>
    <?php endif; ?>
  </div>
</main>

<style>
.search-query {
  position: relative;
}

.search-query::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background: var(--primary);
  border-radius: 1px;
}

.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--muted-foreground);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  background: var(--surface-hover);
  color: var(--foreground);
  transform: translateY(-1px);
}

.filter-btn.active {
  background: var(--primary);
  color: var(--primary-foreground);
  border-color: var(--primary);
}

.enhanced-search-form {
  min-width: 300px;
}

.space-y-6 > * + * {
  margin-top: 1.5rem;
}

.space-y-2 > * + * {
  margin-top: 0.5rem;
}

.search-result-item:hover {
  border-color: var(--primary);
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

@media (max-width: 768px) {
  .flex-between {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .enhanced-search-form {
    min-width: 100%;
  }
  
  .search-filters {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .search-filters .flex {
    flex-wrap: nowrap;
    min-width: max-content;
  }
  
  .result-thumbnail {
    display: none;
  }
  
  .grid-3 {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
</style>

<script>
// Search filter functionality
document.addEventListener('DOMContentLoaded', function() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const searchResults = document.querySelectorAll('.search-result-item');
  
  filterBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const filter = this.dataset.filter;
      
      // Update active button
      filterBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      
      // Filter results
      searchResults.forEach(result => {
        const postType = result.classList.contains('type-post') ? 'posts' : 'pages';
        
        if (filter === 'all' || filter === postType) {
          result.style.display = 'block';
          result.style.animation = 'fadeIn 0.3s ease';
        } else {
          result.style.display = 'none';
        }
      });
    });
  });
});

// Track search analytics
if (typeof gtag !== 'undefined') {
  gtag('event', 'search', {
    search_term: '<?php echo esc_js(get_search_query()); ?>',
    results_count: <?php echo intval($wp_query->found_posts ?? 0); ?>
  });
}
</script>

<?php get_footer(); ?>