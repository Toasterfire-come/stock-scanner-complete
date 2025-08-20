<?php
/**
 * Single post template
 *
 * @package StockScannerPro
 */

get_header(); ?>

<div class="container mx-auto px-4 py-8">
    <div class="max-w-4xl mx-auto">
        
        <?php while (have_posts()) : the_post(); ?>
            
            <article id="post-<?php the_ID(); ?>" <?php post_class('single-post'); ?>>
                
                <!-- Post Header -->
                <header class="post-header mb-8">
                    
                    <!-- Breadcrumb -->
                    <nav class="breadcrumb text-sm text-gray-600 mb-4">
                        <a href="<?php echo esc_url(home_url('/')); ?>" class="hover:text-blue-600">
                            <?php _e('Home', 'stock-scanner-pro'); ?>
                        </a>
                        <span class="mx-2">›</span>
                        
                        <?php
                        $categories = get_the_category();
                        if (!empty($categories)) :
                            $category = $categories[0];
                        ?>
                            <a href="<?php echo esc_url(get_category_link($category->term_id)); ?>" class="hover:text-blue-600">
                                <?php echo esc_html($category->name); ?>
                            </a>
                            <span class="mx-2">›</span>
                        <?php endif; ?>
                        
                        <span class="text-gray-500"><?php the_title(); ?></span>
                    </nav>

                    <!-- Post Title -->
                    <h1 class="post-title text-4xl font-bold text-gray-900 mb-4 leading-tight">
                        <?php the_title(); ?>
                    </h1>

                    <!-- Post Meta -->
                    <div class="post-meta flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-6">
                        
                        <!-- Author -->
                        <div class="author-meta flex items-center">
                            <?php echo get_avatar(get_the_author_meta('ID'), 32, '', '', array('class' => 'w-8 h-8 rounded-full mr-2')); ?>
                            <span>
                                <?php _e('By', 'stock-scanner-pro'); ?> 
                                <a href="<?php echo esc_url(get_author_posts_url(get_the_author_meta('ID'))); ?>" 
                                   class="text-blue-600 hover:text-blue-700 font-medium">
                                    <?php the_author(); ?>
                                </a>
                            </span>
                        </div>

                        <!-- Date -->
                        <div class="date-meta">
                            <i class="fas fa-calendar-alt mr-1"></i>
                            <time datetime="<?php echo get_the_date('c'); ?>">
                                <?php echo get_the_date(); ?>
                            </time>
                        </div>

                        <!-- Reading Time -->
                        <div class="reading-time">
                            <i class="fas fa-clock mr-1"></i>
                            <?php
                            $word_count = str_word_count(strip_tags(get_the_content()));
                            $reading_time = ceil($word_count / 200);
                            printf(__('%d min read', 'stock-scanner-pro'), $reading_time);
                            ?>
                        </div>

                        <!-- Comments -->
                        <?php if (comments_open() && get_comments_number()) : ?>
                            <div class="comments-meta">
                                <i class="fas fa-comment mr-1"></i>
                                <a href="#comments" class="text-blue-600 hover:text-blue-700">
                                    <?php
                                    printf(
                                        _nx('1 Comment', '%1$s Comments', get_comments_number(), 'comments title', 'stock-scanner-pro'),
                                        number_format_i18n(get_comments_number())
                                    );
                                    ?>
                                </a>
                            </div>
                        <?php endif; ?>
                    </div>

                    <!-- Categories and Tags -->
                    <div class="post-taxonomy mb-6">
                        <?php
                        $categories = get_the_category();
                        if (!empty($categories)) :
                        ?>
                            <div class="post-categories mb-2">
                                <span class="text-sm text-gray-600 mr-2"><?php _e('Categories:', 'stock-scanner-pro'); ?></span>
                                <?php foreach ($categories as $category) : ?>
                                    <a href="<?php echo esc_url(get_category_link($category->term_id)); ?>" 
                                       class="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full mr-2 hover:bg-blue-200 transition-colors">
                                        <?php echo esc_html($category->name); ?>
                                    </a>
                                <?php endforeach; ?>
                            </div>
                        <?php endif; ?>

                        <?php
                        $tags = get_the_tags();
                        if (!empty($tags)) :
                        ?>
                            <div class="post-tags">
                                <span class="text-sm text-gray-600 mr-2"><?php _e('Tags:', 'stock-scanner-pro'); ?></span>
                                <?php foreach ($tags as $tag) : ?>
                                    <a href="<?php echo esc_url(get_tag_link($tag->term_id)); ?>" 
                                       class="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full mr-2 hover:bg-gray-200 transition-colors">
                                        #<?php echo esc_html($tag->name); ?>
                                    </a>
                                <?php endforeach; ?>
                            </div>
                        <?php endif; ?>
                    </div>

                    <!-- Featured Image -->
                    <?php if (has_post_thumbnail()) : ?>
                        <div class="featured-image mb-8">
                            <?php the_post_thumbnail('full', array('class' => 'w-full h-auto rounded-lg shadow-lg')); ?>
                            
                            <?php
                            $caption = get_the_post_thumbnail_caption();
                            if ($caption) :
                            ?>
                                <figcaption class="text-sm text-gray-600 text-center mt-2 italic">
                                    <?php echo esc_html($caption); ?>
                                </figcaption>
                            <?php endif; ?>
                        </div>
                    <?php endif; ?>
                </header>

                <!-- Post Content -->
                <div class="post-content prose prose-lg max-w-none mb-8">
                    <?php
                    the_content(sprintf(
                        __('Continue reading<span class="screen-reader-text"> "%s"</span>', 'stock-scanner-pro'),
                        get_the_title()
                    ));
                    
                    wp_link_pages(array(
                        'before' => '<div class="page-links text-center mt-8">' . __('Pages:', 'stock-scanner-pro'),
                        'after'  => '</div>',
                        'link_before' => '<span class="page-number bg-blue-100 text-blue-800 px-3 py-1 rounded-md mx-1">',
                        'link_after' => '</span>',
                    ));
                    ?>
                </div>

                <!-- Social Share -->
                <div class="social-share bg-gray-50 rounded-lg p-6 mb-8">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">
                        <?php _e('Share this article:', 'stock-scanner-pro'); ?>
                    </h3>
                    
                    <div class="share-buttons flex flex-wrap gap-3">
                        <?php
                        $post_url = urlencode(get_permalink());
                        $post_title = urlencode(get_the_title());
                        ?>
                        
                        <a href="https://twitter.com/intent/tweet?url=<?php echo $post_url; ?>&text=<?php echo $post_title; ?>" 
                           target="_blank" rel="noopener noreferrer"
                           class="share-btn bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors">
                            <i class="fab fa-twitter mr-2"></i>
                            <?php _e('Twitter', 'stock-scanner-pro'); ?>
                        </a>
                        
                        <a href="https://www.linkedin.com/sharing/share-offsite/?url=<?php echo $post_url; ?>" 
                           target="_blank" rel="noopener noreferrer"
                           class="share-btn bg-blue-700 text-white px-4 py-2 rounded-md hover:bg-blue-800 transition-colors">
                            <i class="fab fa-linkedin mr-2"></i>
                            <?php _e('LinkedIn', 'stock-scanner-pro'); ?>
                        </a>
                        
                        <a href="https://www.facebook.com/sharer/sharer.php?u=<?php echo $post_url; ?>" 
                           target="_blank" rel="noopener noreferrer"
                           class="share-btn bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                            <i class="fab fa-facebook mr-2"></i>
                            <?php _e('Facebook', 'stock-scanner-pro'); ?>
                        </a>
                        
                        <button onclick="navigator.clipboard.writeText('<?php echo get_permalink(); ?>'); StockScannerAPI.Toast.show('Link copied!', 'success');" 
                                class="share-btn bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors">
                            <i class="fas fa-link mr-2"></i>
                            <?php _e('Copy Link', 'stock-scanner-pro'); ?>
                        </button>
                    </div>
                </div>

                <!-- Author Bio -->
                <?php
                $author_bio = get_the_author_meta('description');
                if ($author_bio) :
                ?>
                    <div class="author-bio bg-white border border-gray-200 rounded-lg p-6 mb-8">
                        <div class="flex items-start gap-4">
                            <div class="author-avatar">
                                <?php echo get_avatar(get_the_author_meta('ID'), 64, '', '', array('class' => 'w-16 h-16 rounded-full')); ?>
                            </div>
                            <div class="author-info flex-1">
                                <h3 class="author-name text-lg font-semibold text-gray-900 mb-2">
                                    <a href="<?php echo esc_url(get_author_posts_url(get_the_author_meta('ID'))); ?>" 
                                       class="hover:text-blue-600 transition-colors">
                                        <?php the_author(); ?>
                                    </a>
                                </h3>
                                <p class="author-description text-gray-600 mb-3">
                                    <?php echo esc_html($author_bio); ?>
                                </p>
                                <a href="<?php echo esc_url(get_author_posts_url(get_the_author_meta('ID'))); ?>" 
                                   class="text-blue-600 hover:text-blue-700 text-sm font-medium">
                                    <?php _e('View all posts by', 'stock-scanner-pro'); ?> <?php the_author(); ?> →
                                </a>
                            </div>
                        </div>
                    </div>
                <?php endif; ?>
            </article>

            <!-- Related Posts -->
            <?php
            $related_posts = get_posts(array(
                'category__in' => wp_get_post_categories(get_the_ID()),
                'numberposts' => 3,
                'post__not_in' => array(get_the_ID()),
                'orderby' => 'rand'
            ));

            if (!empty($related_posts)) :
            ?>
                <div class="related-posts mb-8">
                    <h2 class="text-2xl font-bold text-gray-900 mb-6">
                        <?php _e('Related Articles', 'stock-scanner-pro'); ?>
                    </h2>
                    
                    <div class="related-posts-grid grid grid-cols-1 md:grid-cols-3 gap-6">
                        <?php foreach ($related_posts as $related_post) : ?>
                            <article class="related-post bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
                                <?php if (has_post_thumbnail($related_post->ID)) : ?>
                                    <div class="related-post-thumbnail">
                                        <a href="<?php echo get_permalink($related_post->ID); ?>">
                                            <?php echo get_the_post_thumbnail($related_post->ID, 'medium', array('class' => 'w-full h-48 object-cover')); ?>
                                        </a>
                                    </div>
                                <?php endif; ?>
                                
                                <div class="related-post-content p-4">
                                    <h3 class="related-post-title text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                                        <a href="<?php echo get_permalink($related_post->ID); ?>" class="hover:text-blue-600 transition-colors">
                                            <?php echo esc_html($related_post->post_title); ?>
                                        </a>
                                    </h3>
                                    
                                    <p class="related-post-excerpt text-gray-600 text-sm mb-3 line-clamp-3">
                                        <?php echo wp_trim_words($related_post->post_content, 20); ?>
                                    </p>
                                    
                                    <div class="related-post-meta text-xs text-gray-500">
                                        <?php echo get_the_date('', $related_post->ID); ?>
                                    </div>
                                </div>
                            </article>
                        <?php endforeach; ?>
                    </div>
                </div>
            <?php endif; ?>

            <!-- Comments -->
            <?php
            if (comments_open() || get_comments_number()) :
                comments_template();
            endif;
            ?>

        <?php endwhile; ?>
    </div>
</div>

<style>
/* Post Content Styling */
.prose {
    color: #374151;
    line-height: 1.75;
}

.prose h2, .prose h3, .prose h4 {
    color: #1f2937;
    font-weight: 600;
    margin-top: 2em;
    margin-bottom: 1em;
}

.prose h2 {
    font-size: 1.5em;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 0.5em;
}

.prose h3 {
    font-size: 1.25em;
}

.prose p {
    margin-bottom: 1.25em;
}

.prose blockquote {
    border-left: 4px solid #3b82f6;
    padding-left: 1rem;
    margin: 1.5rem 0;
    font-style: italic;
    background: #f8fafc;
    padding: 1rem;
    border-radius: 0.375rem;
}

.prose ul, .prose ol {
    padding-left: 1.5rem;
    margin-bottom: 1.25rem;
}

.prose li {
    margin-bottom: 0.5rem;
}

.prose code {
    background: #f3f4f6;
    padding: 0.125rem 0.25rem;
    border-radius: 0.25rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.875em;
}

.prose pre {
    background: #1f2937;
    color: #f9fafb;
    padding: 1rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    margin: 1.5rem 0;
}

.prose pre code {
    background: transparent;
    color: inherit;
}

.prose a {
    color: #3b82f6;
    text-decoration: underline;
    text-decoration-color: rgba(59, 130, 246, 0.3);
    transition: text-decoration-color 0.3s ease;
}

.prose a:hover {
    text-decoration-color: #3b82f6;
}

.prose img {
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.prose table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
}

.prose th, .prose td {
    border: 1px solid #e5e7eb;
    padding: 0.75rem;
    text-align: left;
}

.prose th {
    background: #f9fafb;
    font-weight: 600;
}

/* Line clamping for related posts */
.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .post-meta {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
    
    .share-buttons {
        justify-content: center;
    }
    
    .author-bio .flex {
        flex-direction: column;
        text-align: center;
    }
    
    .related-posts-grid {
        grid-template-columns: 1fr;
    }
}
</style>

<?php get_footer(); ?>