<?php
/**
 * Default Page Template - Modern General Page Design
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main">
  <?php while (have_posts()) : the_post(); ?>
    <article id="page-<?php the_ID(); ?>" <?php post_class('fade-in'); ?>>
      <!-- Page Header -->
      <header class="page-header mb-8">
        <?php if (has_post_thumbnail()) : ?>
          <div class="page-featured-image mb-8" style="border-radius: var(--radius-lg); overflow: hidden; max-height: 300px;">
            <?php the_post_thumbnail('large', ['style' => 'width: 100%; height: 100%; object-fit: cover;']); ?>
          </div>
        <?php endif; ?>
        
        <div class="page-title-section max-w-4xl mx-auto text-center">
          <h1 class="page-title text-4xl font-bold mb-4 leading-tight">
            <?php the_title(); ?>
          </h1>
          
          <?php if (get_the_excerpt()) : ?>
            <div class="page-subtitle text-xl text-muted mb-6 max-w-2xl mx-auto">
              <?php the_excerpt(); ?>
            </div>
          <?php endif; ?>
          
          <!-- Page Meta -->
          <div class="page-meta flex items-center justify-center gap-6 text-sm text-muted">
            <div class="flex items-center gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12,6 12,12 16,14"></polyline>
              </svg>
              <span><?php esc_html_e('Last updated:', 'retail-trade-scanner'); ?></span>
              <time datetime="<?php echo esc_attr(get_the_modified_date('c')); ?>">
                <?php echo esc_html(get_the_modified_date()); ?>
              </time>
            </div>
            
            <?php if (estimated_reading_time()) : ?>
              <div class="flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                </svg>
                <span><?php echo esc_html(estimated_reading_time()); ?></span>
              </div>
            <?php endif; ?>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <div class="page-content max-w-4xl mx-auto">
        <div class="prose prose-lg" style="color: var(--foreground);">
          <?php
          the_content();
          
          wp_link_pages([
            'before' => '<div class="page-links mt-8 p-4 rounded-lg" style="background: var(--surface); border: 1px solid var(--border);"><span class="font-semibold">' . __('Pages:', 'retail-trade-scanner') . '</span>',
            'after'  => '</div>',
            'link_before' => '<span class="inline-flex items-center justify-center w-8 h-8 mx-1 rounded font-medium transition-colors" style="background: var(--primary); color: var(--primary-foreground);">',
            'link_after'  => '</span>',
          ]);
          ?>
        </div>
        
        <!-- Page Actions -->
        <?php if (is_page(['contact', 'help', 'support'])) : ?>
          <div class="page-actions mt-12 p-6 rounded-lg text-center" style="background: linear-gradient(135deg, var(--surface) 0%, var(--surface-hover) 100%); border: 1px solid var(--border);">
            <h3 class="text-lg font-semibold mb-4"><?php esc_html_e('Need More Help?', 'retail-trade-scanner'); ?></h3>
            <p class="text-muted mb-6"><?php esc_html_e('Our support team is here to help you with any questions or concerns.', 'retail-trade-scanner'); ?></p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
              <a href="<?php echo esc_url(home_url('/contact/')); ?>" class="btn btn-primary">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                  <polyline points="22,6 12,13 2,6"></polyline>
                </svg>
                <?php esc_html_e('Contact Support', 'retail-trade-scanner'); ?>
              </a>
              
              <a href="<?php echo esc_url(home_url('/tutorials/')); ?>" class="btn btn-outline">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="5,3 19,12 5,21"></polygon>
                </svg>
                <?php esc_html_e('View Tutorials', 'retail-trade-scanner'); ?>
              </a>
            </div>
          </div>
        <?php endif; ?>
        
        <!-- Trading Platform CTA for relevant pages -->
        <?php if (is_page(['about', 'features', 'pricing'])) : ?>
          <div class="platform-cta mt-12 p-8 rounded-lg text-center" style="background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);">
            <h3 class="text-2xl font-bold mb-4" style="color: var(--primary-foreground);">
              <?php esc_html_e('Ready to Start Trading?', 'retail-trade-scanner'); ?>
            </h3>
            <p class="mb-6" style="color: rgba(255, 255, 255, 0.9);">
              <?php esc_html_e('Join thousands of traders who trust our platform for professional market analysis.', 'retail-trade-scanner'); ?>
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
              <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="btn" style="background: rgba(255, 255, 255, 0.2); color: white; border: 1px solid rgba(255, 255, 255, 0.3);">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="8"></circle>
                  <path d="21 21l-4.35-4.35"></path>
                </svg>
                <?php esc_html_e('Try Stock Scanner', 'retail-trade-scanner'); ?>
              </a>
              
              <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="btn" style="background: var(--accent); color: var(--accent-foreground);">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="7" height="7"></rect>
                  <rect x="14" y="3" width="7" height="7"></rect>
                  <rect x="14" y="14" width="7" height="7"></rect>
                  <rect x="3" y="14" width="7" height="7"></rect>
                </svg>
                <?php esc_html_e('View Dashboard', 'retail-trade-scanner'); ?>
              </a>
            </div>
          </div>
        <?php endif; ?>
      </div>

      <!-- Page Navigation -->
      <?php
      $parent_id = wp_get_post_parent_id();
      $child_pages = get_children([
        'post_parent' => get_the_ID(),
        'post_type' => 'page',
        'post_status' => 'publish',
        'orderby' => 'menu_order',
        'order' => 'ASC'
      ]);
      
      if ($parent_id || !empty($child_pages)) :
      ?>
        <aside class="page-navigation mt-12 max-w-4xl mx-auto">
          <?php if ($parent_id) : ?>
            <!-- Parent Page Link -->
            <div class="parent-page-link mb-6">
              <a href="<?php echo esc_url(get_permalink($parent_id)); ?>" 
                 class="inline-flex items-center gap-2 text-primary hover:text-primary-hover font-medium transition-colors">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="15,18 9,12 15,6"></polyline>
                </svg>
                <?php esc_html_e('Back to', 'retail-trade-scanner'); ?> <?php echo esc_html(get_the_title($parent_id)); ?>
              </a>
            </div>
          <?php endif; ?>
          
          <?php if (!empty($child_pages)) : ?>
            <!-- Child Pages -->
            <div class="child-pages">
              <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                </svg>
                <?php esc_html_e('Related Pages', 'retail-trade-scanner'); ?>
              </h3>
              
              <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <?php foreach ($child_pages as $child_page) : ?>
                  <a href="<?php echo esc_url(get_permalink($child_page->ID)); ?>" 
                     class="child-page-link card p-4 hover:transform hover:scale-105 transition-all">
                    <h4 class="font-semibold mb-2"><?php echo esc_html($child_page->post_title); ?></h4>
                    <?php if ($child_page->post_excerpt) : ?>
                      <p class="text-sm text-muted"><?php echo esc_html(wp_trim_words($child_page->post_excerpt, 15)); ?></p>
                    <?php endif; ?>
                  </a>
                <?php endforeach; ?>
              </div>
            </div>
          <?php endif; ?>
        </aside>
      <?php endif; ?>
    </article>

    <!-- Comments -->
    <?php if (comments_open() || get_comments_number()) : ?>
      <section class="comments-section mt-12 max-w-4xl mx-auto">
        <?php comments_template(); ?>
      </section>
    <?php endif; ?>

  <?php endwhile; ?>
</main>

<style>
.page-title {
  background: linear-gradient(135deg, var(--foreground) 0%, var(--primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.prose {
  max-width: none;
}

.prose p {
  margin-bottom: 1.5rem;
  line-height: 1.7;
}

.prose h2,
.prose h3,
.prose h4 {
  margin-top: 2rem;
  margin-bottom: 1rem;
  color: var(--foreground);
  font-weight: 600;
}

.prose h2 {
  font-size: 1.75rem;
  border-bottom: 2px solid var(--border);
  padding-bottom: 0.5rem;
}

.prose h3 {
  font-size: 1.375rem;
}

.prose h4 {
  font-size: 1.125rem;
}

.prose a {
  color: var(--primary);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s ease;
}

.prose a:hover {
  border-bottom-color: var(--primary);
}

.prose blockquote {
  border-left: 4px solid var(--primary);
  padding-left: 1.5rem;
  margin: 2rem 0;
  font-style: italic;
  color: var(--muted-foreground);
  background: var(--surface);
  padding: 1.5rem;
  border-radius: var(--radius);
}

.prose ul,
.prose ol {
  margin: 1.5rem 0;
  padding-left: 2rem;
}

.prose li {
  margin-bottom: 0.5rem;
}

.prose code {
  background: var(--surface);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.9em;
  color: var(--accent);
  border: 1px solid var(--border);
}

.prose pre {
  background: var(--surface);
  padding: 1.5rem;
  border-radius: var(--radius);
  overflow-x: auto;
  border: 1px solid var(--border);
  line-height: 1.5;
}

.prose pre code {
  background: none;
  padding: 0;
  border: none;
  color: var(--foreground);
}

.prose img {
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  margin: 2rem 0;
}

.prose table {
  width: 100%;
  border-collapse: collapse;
  margin: 2rem 0;
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
  border: 1px solid var(--border);
}

.prose th,
.prose td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.prose th {
  background: var(--surface-hover);
  font-weight: 600;
  color: var(--foreground);
}

.prose tr:last-child td {
  border-bottom: none;
}

.child-page-link:hover {
  border-color: var(--primary);
}

/* Special styling for specific page types */
.page-id-contact .prose,
.page-id-help .prose {
  font-size: 1.1rem;
}

.page-id-about .prose p:first-of-type {
  font-size: 1.2rem;
  color: var(--foreground);
  font-weight: 500;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
  
  .page-meta {
    flex-direction: column;
    gap: 1rem;
  }
  
  .prose {
    font-size: 1rem;
  }
  
  .prose h2 {
    font-size: 1.5rem;
  }
  
  .prose h3 {
    font-size: 1.25rem;
  }
  
  .prose table {
    font-size: 0.875rem;
  }
  
  .prose th,
  .prose td {
    padding: 0.5rem;
  }
}

/* Print styles */
@media print {
  .page-actions,
  .platform-cta,
  .page-navigation {
    display: none;
  }
  
  .prose {
    color: black;
  }
  
  .prose a {
    color: black;
    text-decoration: underline;
  }
}
</style>

<?php get_footer(); ?>

<?php
// Helper function for reading time (consistent across templates)
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