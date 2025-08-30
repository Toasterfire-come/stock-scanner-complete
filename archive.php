<?php
/**
 * Archive Template - Category, Tag, and Date Archives
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main">
  <div class="fade-in">
    <!-- Archive Header -->
    <header class="archive-header mb-12">
      <div class="card p-8 text-center" style="background: linear-gradient(135deg, var(--surface) 0%, var(--surface-hover) 100%);">
        <?php
        $archive_title = get_the_archive_title();
        $archive_description = get_the_archive_description();
        
        // Get archive icon based on type
        $archive_icon = '';
        if (is_category()) {
          $archive_icon = '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>';
        } elseif (is_tag()) {
          $archive_icon = '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>';
        } elseif (is_date()) {
          $archive_icon = '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>';
        } elseif (is_author()) {
          $archive_icon = '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>';
        } else {
          $archive_icon = '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>';
        }
        ?>
        
        <div class="archive-icon mb-4" style="color: var(--primary);">
          <?php echo $archive_icon; ?>
        </div>
        
        <h1 class="text-3xl font-bold mb-4">
          <?php echo wp_kses_post($archive_title); ?>
        </h1>
        
        <?php if ($archive_description) : ?>
          <div class="archive-description text-muted max-w-2xl mx-auto">
            <?php echo wp_kses_post($archive_description); ?>
          </div>
        <?php endif; ?>
        
        <!-- Archive Stats -->
        <div class="archive-stats mt-6 flex items-center justify-center gap-6 text-sm">
          <?php
          global $wp_query;
          $total_posts = $wp_query->found_posts;
          ?>
          <div class="flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
            </svg>
            <span class="font-medium">
              <?php
              printf(
                _n('%s Article', '%s Articles', $total_posts, 'retail-trade-scanner'),
                number_format_i18n($total_posts)
              );
              ?>
            </span>
          </div>
          
          <?php if (is_category() || is_tag()) : ?>
            <div class="flex items-center gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12,6 12,12 16,14"></polyline>
              </svg>
              <span class="text-muted">
                <?php esc_html_e('Updated regularly', 'retail-trade-scanner'); ?>
              </span>
            </div>
          <?php endif; ?>
        </div>
      </div>
    </header>

    <?php if (have_posts()) : ?>
      <!-- Archive Content -->
      <section class="archive-content">
        <!-- Sorting Options -->
        <div class="archive-controls mb-8">
          <div class="flex items-center justify-between">
            <div class="view-options flex items-center gap-3">
              <span class="text-sm font-medium text-muted"><?php esc_html_e('View:', 'retail-trade-scanner'); ?></span>
              <button class="view-btn active" data-view="grid" aria-label="Grid View">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="7" height="7"></rect>
                  <rect x="14" y="3" width="7" height="7"></rect>
                  <rect x="14" y="14" width="7" height="7"></rect>
                  <rect x="3" y="14" width="7" height="7"></rect>
                </svg>
              </button>
              <button class="view-btn" data-view="list" aria-label="List View">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="8" y1="6" x2="21" y2="6"></line>
                  <line x1="8" y1="12" x2="21" y2="12"></line>
                  <line x1="8" y1="18" x2="21" y2="18"></line>
                  <line x1="3" y1="6" x2="3.01" y2="6"></line>
                  <line x1="3" y1="12" x2="3.01" y2="12"></line>
                  <line x1="3" y1="18" x2="3.01" y2="18"></line>
                </svg>
              </button>
            </div>
            
            <div class="sort-options flex items-center gap-3">
              <span class="text-sm font-medium text-muted"><?php esc_html_e('Sort by:', 'retail-trade-scanner'); ?></span>
              <select class="sort-select">
                <option value="date"><?php esc_html_e('Latest First', 'retail-trade-scanner'); ?></option>
                <option value="date_asc"><?php esc_html_e('Oldest First', 'retail-trade-scanner'); ?></option>
                <option value="title"><?php esc_html_e('Title A-Z', 'retail-trade-scanner'); ?></option>
                <option value="title_desc"><?php esc_html_e('Title Z-A', 'retail-trade-scanner'); ?></option>
              </select>
            </div>
          </div>
        </div>

        <!-- Posts Grid -->
        <div class="posts-container grid-view">
          <div class="posts-grid grid grid-3 gap-6" id="posts-container">
            <?php while (have_posts()) : the_post(); ?>
              <article id="post-<?php the_ID(); ?>" <?php post_class('archive-post-item card hover:transform hover:scale-[1.02] transition-all'); ?>>
                <?php if (has_post_thumbnail()) : ?>
                  <div class="post-thumbnail mb-4" style="border-radius: var(--radius-lg) var(--radius-lg) 0 0; overflow: hidden; height: 200px;">
                    <a href="<?php the_permalink(); ?>">
                      <?php the_post_thumbnail('medium_large', ['style' => 'width: 100%; height: 100%; object-fit: cover;']); ?>
                    </a>
                    
                    <!-- Post Date Badge -->
                    <div class="post-date-badge">
                      <time datetime="<?php echo esc_attr(get_the_date('c')); ?>">
                        <?php echo esc_html(get_the_date('M j')); ?>
                      </time>
                    </div>
                  </div>
                <?php endif; ?>
                
                <div class="post-content p-6">
                  <!-- Post Meta -->
                  <div class="post-meta flex items-center gap-4 mb-3 text-sm text-muted">
                    <?php
                    $categories = get_the_category();
                    if (!empty($categories)) :
                    ?>
                      <div class="flex items-center gap-2">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                          <line x1="7" y1="7" x2="7.01" y2="7"></line>
                        </svg>
                        <a href="<?php echo esc_url(get_category_link($categories[0]->term_id)); ?>" 
                           class="text-primary hover:text-primary-hover transition-colors">
                          <?php echo esc_html($categories[0]->name); ?>
                        </a>
                      </div>
                    <?php endif; ?>
                    
                    <div class="flex items-center gap-2">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                      </svg>
                      <span><?php echo esc_html(get_the_author()); ?></span>
                    </div>
                  </div>
                  
                  <!-- Post Title -->
                  <h2 class="post-title text-xl font-semibold mb-3 leading-tight">
                    <a href="<?php the_permalink(); ?>" class="text-foreground hover:text-primary transition-colors">
                      <?php the_title(); ?>
                    </a>
                  </h2>
                  
                  <!-- Post Excerpt -->
                  <div class="post-excerpt text-muted mb-4 leading-relaxed">
                    <?php echo wp_trim_words(get_the_excerpt(), 20, '...'); ?>
                  </div>
                  
                  <!-- Post Footer -->
                  <div class="post-footer flex items-center justify-between pt-4 border-t border-border">
                    <div class="flex items-center gap-2 text-sm text-muted">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12,6 12,12 16,14"></polyline>
                      </svg>
                      <span><?php echo esc_html(estimated_reading_time()); ?></span>
                    </div>
                    
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
              </article>
            <?php endwhile; ?>
          </div>
        </div>
        
        <!-- Pagination -->
        <nav class="archive-pagination mt-12" aria-label="Archive Navigation">
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
      <!-- No Posts -->
      <section class="no-posts text-center py-16">
        <div class="max-w-2xl mx-auto">
          <div class="no-posts-icon mb-6" style="color: var(--muted-foreground);">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="margin: 0 auto;">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
              <line x1="12" y1="11" x2="12" y2="17"></line>
              <line x1="12" y1="21" x2="12.01" y2="21"></line>
            </svg>
          </div>
          
          <h2 class="text-2xl font-bold mb-4">
            <?php esc_html_e('No Articles Found', 'retail-trade-scanner'); ?>
          </h2>
          
          <p class="text-muted mb-8">
            <?php esc_html_e('This archive doesn\'t have any published articles yet. Check back soon for new content!', 'retail-trade-scanner'); ?>
          </p>
          
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="<?php echo esc_url(home_url('/')); ?>" class="btn btn-primary">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9,22 9,12 15,12 15,22"></polyline>
              </svg>
              <?php esc_html_e('Back to Home', 'retail-trade-scanner'); ?>
            </a>
            
            <a href="<?php echo esc_url(home_url('/blog/')); ?>" class="btn btn-outline">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
              </svg>
              <?php esc_html_e('Browse All Articles', 'retail-trade-scanner'); ?>
            </a>
          </div>
        </div>
      </section>
    <?php endif; ?>
  </div>
</main>

<style>
.post-date-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(67, 62, 14, 0.9);
  backdrop-filter: blur(8px);
  color: var(--foreground);
  padding: 4px 8px;
  border-radius: var(--radius);
  font-size: 12px;
  font-weight: 500;
}

.view-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--muted-foreground);
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn:hover {
  background: var(--surface-hover);
  color: var(--foreground);
  transform: translateY(-1px);
}

.view-btn.active {
  background: var(--primary);
  color: var(--primary-foreground);
  border-color: var(--primary);
}

.sort-select {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--foreground);
  padding: 6px 10px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sort-select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(55, 74, 103, 0.1);
}

.posts-container.list-view .posts-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.posts-container.list-view .archive-post-item {
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem;
}

.posts-container.list-view .post-thumbnail {
  flex-shrink: 0;
  width: 200px;
  height: 140px;
  margin-bottom: 0;
  border-radius: var(--radius-lg);
}

.posts-container.list-view .post-content {
  flex: 1;
  padding: 0;
}

.archive-post-item:hover {
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
  .archive-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .archive-controls .flex {
    width: 100%;
    justify-content: center;
  }
  
  .posts-container.list-view .archive-post-item {
    flex-direction: column;
    gap: 1rem;
  }
  
  .posts-container.list-view .post-thumbnail {
    width: 100%;
    height: 200px;
  }
  
  .grid-3 {
    grid-template-columns: 1fr;
  }
}
</style>

<script>
// View switcher functionality
document.addEventListener('DOMContentLoaded', function() {
  const viewBtns = document.querySelectorAll('.view-btn');
  const postsContainer = document.querySelector('.posts-container');
  
  viewBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const view = this.dataset.view;
      
      // Update active button
      viewBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      
      // Update container class
      postsContainer.className = `posts-container ${view}-view`;
      
      // Save preference
      localStorage.setItem('archive-view', view);
    });
  });
  
  // Restore saved view preference
  const savedView = localStorage.getItem('archive-view');
  if (savedView) {
    const targetBtn = document.querySelector(`[data-view="${savedView}"]`);
    if (targetBtn) {
      targetBtn.click();
    }
  }
  
  // Sort functionality (placeholder - would need AJAX implementation)
  const sortSelect = document.querySelector('.sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', function() {
      // This would typically trigger an AJAX request to resort posts
      console.log('Sort by:', this.value);
    });
  }
});

// Estimated reading time function
function estimated_reading_time() {
  // This would be implemented in PHP, included here for reference
  return '3 min read';
}
</script>

<?php get_footer(); ?>

<?php
// Helper function for reading time (same as in single.php)
function estimated_reading_time() {
  $content = get_post_field('post_content', get_the_ID());
  $word_count = str_word_count(strip_tags($content));
  $reading_time = ceil($word_count / 200);
  
  if ($reading_time == 1) {
    return '1 ' . __('min read', 'retail-trade-scanner');
  } else {
    return $reading_time . ' ' . __('min read', 'retail-trade-scanner');
  }
}
?>