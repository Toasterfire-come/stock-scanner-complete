<?php
/**
 * Single Post Template - Modern Blog Post Design
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main">
  <?php while (have_posts()) : the_post(); ?>
    <article id="post-<?php the_ID(); ?>" <?php post_class('fade-in'); ?>>
      <!-- Article Header -->
      <header class="article-header mb-8 text-center">
        <?php if (has_post_thumbnail()) : ?>
          <div class="featured-image mb-6" style="border-radius: var(--radius-lg); overflow: hidden; max-height: 400px;">
            <?php the_post_thumbnail('large', ['style' => 'width: 100%; height: 100%; object-fit: cover;']); ?>
          </div>
        <?php endif; ?>
        
        <div class="max-w-4xl mx-auto">
          <?php
          $categories = get_the_category();
          if (!empty($categories)) :
          ?>
            <div class="article-category mb-4">
              <span class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium" style="background: rgba(55, 74, 103, 0.1); color: var(--primary);">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                  <line x1="7" y1="7" x2="7.01" y2="7"></line>
                </svg>
                <?php echo esc_html($categories[0]->name); ?>
              </span>
            </div>
          <?php endif; ?>
          
          <h1 class="article-title text-4xl font-bold mb-6 leading-tight"><?php the_title(); ?></h1>
          
          <div class="article-meta flex items-center justify-center gap-6 text-sm text-muted mb-8">
            <div class="flex items-center gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              <span><?php echo esc_html(get_the_author()); ?></span>
            </div>
            
            <div class="flex items-center gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12,6 12,12 16,14"></polyline>
              </svg>
              <time datetime="<?php echo esc_attr(get_the_date('c')); ?>">
                <?php echo esc_html(get_the_date()); ?>
              </time>
            </div>
            
            <div class="flex items-center gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
              </svg>
              <span><?php echo esc_html(estimated_reading_time()); ?></span>
            </div>
          </div>
        </div>
      </header>

      <!-- Article Content -->
      <div class="article-content max-w-4xl mx-auto">
        <div class="prose prose-lg" style="color: var(--foreground);">
          <?php the_content(); ?>
        </div>
        
        <?php
        wp_link_pages([
          'before' => '<div class="page-links mt-8 p-4 rounded-lg" style="background: var(--surface); border: 1px solid var(--border);"><span class="font-semibold">' . __('Pages:', 'retail-trade-scanner') . '</span>',
          'after'  => '</div>',
          'link_before' => '<span class="inline-flex items-center justify-center w-8 h-8 mx-1 rounded font-medium transition-colors" style="background: var(--primary); color: var(--primary-foreground);">',
          'link_after'  => '</span>',
        ]);
        ?>
      </div>

      <!-- Article Footer -->
      <footer class="article-footer mt-12 max-w-4xl mx-auto">
        <?php
        $tags = get_the_tags();
        if ($tags) :
        ?>
          <div class="article-tags mb-8">
            <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                <line x1="7" y1="7" x2="7.01" y2="7"></line>
              </svg>
              <?php esc_html_e('Tags', 'retail-trade-scanner'); ?>
            </h3>
            <div class="flex flex-wrap gap-2">
              <?php foreach ($tags as $tag) : ?>
                <a href="<?php echo esc_url(get_tag_link($tag->term_id)); ?>" 
                   class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium transition-colors hover:transform hover:scale-105"
                   style="background: var(--muted); color: var(--foreground); text-decoration: none;">
                  <?php echo esc_html($tag->name); ?>
                </a>
              <?php endforeach; ?>
            </div>
          </div>
        <?php endif; ?>
        
        <!-- Share Buttons -->
        <div class="article-share mb-8">
          <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
              <polyline points="16,6 12,2 8,6"></polyline>
              <line x1="12" y1="2" x2="12" y2="15"></line>
            </svg>
            <?php esc_html_e('Share This Article', 'retail-trade-scanner'); ?>
          </h3>
          <div class="flex gap-3">
            <a href="https://twitter.com/intent/tweet?url=<?php echo urlencode(get_permalink()); ?>&text=<?php echo urlencode(get_the_title()); ?>" 
               target="_blank" rel="noopener" 
               class="share-btn flex items-center justify-center w-10 h-10 rounded-full transition-all hover:transform hover:scale-110"
               style="background: #1da1f2; color: white;"
               aria-label="Share on Twitter">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"></path>
              </svg>
            </a>
            
            <a href="https://www.linkedin.com/sharing/share-offsite/?url=<?php echo urlencode(get_permalink()); ?>" 
               target="_blank" rel="noopener"
               class="share-btn flex items-center justify-center w-10 h-10 rounded-full transition-all hover:transform hover:scale-110"
               style="background: #0077b5; color: white;"
               aria-label="Share on LinkedIn">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                <rect x="2" y="9" width="4" height="12"></rect>
                <circle cx="4" cy="4" r="2"></circle>
              </svg>
            </a>
            
            <a href="mailto:?subject=<?php echo urlencode(get_the_title()); ?>&body=<?php echo urlencode(get_permalink()); ?>" 
               class="share-btn flex items-center justify-center w-10 h-10 rounded-full transition-all hover:transform hover:scale-110"
               style="background: var(--davys-gray); color: white;"
               aria-label="Share via Email">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
              </svg>
            </a>
          </div>
        </div>
      </footer>
    </article>

    <!-- Author Bio -->
    <?php
    $author_bio = get_the_author_meta('description');
    if ($author_bio) :
    ?>
      <section class="author-bio card p-6 mt-12 max-w-4xl mx-auto">
        <div class="flex items-start gap-4">
          <div class="flex-shrink-0">
            <?php echo get_avatar(get_the_author_meta('ID'), 80, '', '', ['class' => 'rounded-full']); ?>
          </div>
          <div class="flex-1">
            <h3 class="text-xl font-semibold mb-2">
              <?php esc_html_e('About', 'retail-trade-scanner'); ?> <?php echo esc_html(get_the_author()); ?>
            </h3>
            <p class="text-muted mb-4"><?php echo wp_kses_post($author_bio); ?></p>
            <a href="<?php echo esc_url(get_author_posts_url(get_the_author_meta('ID'))); ?>" 
               class="inline-flex items-center gap-2 text-primary hover:text-primary-hover font-medium transition-colors">
              <?php esc_html_e('View all posts by', 'retail-trade-scanner'); ?> <?php echo esc_html(get_the_author()); ?>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12,5 19,12 12,19"></polyline>
              </svg>
            </a>
          </div>
        </div>
      </section>
    <?php endif; ?>

    <!-- Navigation -->
    <nav class="post-navigation mt-12 max-w-4xl mx-auto" aria-label="Post Navigation">
      <?php
      $prev_post = get_previous_post();
      $next_post = get_next_post();
      
      if ($prev_post || $next_post) :
      ?>
        <div class="grid gap-4 md:grid-cols-2">
          <?php if ($prev_post) : ?>
            <a href="<?php echo esc_url(get_permalink($prev_post)); ?>" 
               class="nav-link card p-6 hover:transform hover:scale-[1.02] transition-all">
              <div class="flex items-center gap-3 mb-2 text-sm text-muted">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="15,18 9,12 15,6"></polyline>
                </svg>
                <?php esc_html_e('Previous Article', 'retail-trade-scanner'); ?>
              </div>
              <h4 class="font-semibold text-foreground"><?php echo esc_html(get_the_title($prev_post)); ?></h4>
            </a>
          <?php else : ?>
            <div></div>
          <?php endif; ?>
          
          <?php if ($next_post) : ?>
            <a href="<?php echo esc_url(get_permalink($next_post)); ?>" 
               class="nav-link card p-6 hover:transform hover:scale-[1.02] transition-all text-right">
              <div class="flex items-center justify-end gap-3 mb-2 text-sm text-muted">
                <?php esc_html_e('Next Article', 'retail-trade-scanner'); ?>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9,18 15,12 9,6"></polyline>
                </svg>
              </div>
              <h4 class="font-semibold text-foreground"><?php echo esc_html(get_the_title($next_post)); ?></h4>
            </a>
          <?php endif; ?>
        </div>
      <?php endif; ?>
    </nav>

    <!-- Comments -->
    <?php if (comments_open() || get_comments_number()) : ?>
      <section class="comments-section mt-12 max-w-4xl mx-auto">
        <?php comments_template(); ?>
      </section>
    <?php endif; ?>

  <?php endwhile; ?>
</main>

<style>
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
}

.prose code {
  background: var(--surface);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.9em;
  color: var(--accent);
}

.prose pre {
  background: var(--surface);
  padding: 1.5rem;
  border-radius: var(--radius);
  overflow-x: auto;
  border: 1px solid var(--border);
}

.prose img {
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
}

.article-title {
  background: linear-gradient(135deg, var(--foreground) 0%, var(--primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

@media (max-width: 768px) {
  .article-meta {
    flex-direction: column;
    gap: 1rem;
  }
  
  .article-title {
    font-size: 2rem;
  }
  
  .prose {
    font-size: 1rem;
  }
}
</style>

<?php get_footer(); ?>

<?php
// Helper function for reading time
function estimated_reading_time() {
  $content = get_post_field('post_content', get_the_ID());
  $word_count = str_word_count(strip_tags($content));
  $reading_time = ceil($word_count / 200); // Average reading speed: 200 words per minute
  
  if ($reading_time == 1) {
    return '1 ' . __('min read', 'retail-trade-scanner');
  } else {
    return $reading_time . ' ' . __('min read', 'retail-trade-scanner');
  }
}
?>