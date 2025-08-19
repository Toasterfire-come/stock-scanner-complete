<?php
/**
 * Default page template
 *
 * @package StockScannerPro
 */

get_header(); ?>

<div class="container mx-auto px-4 py-8">
    
    <?php while (have_posts()) : the_post(); ?>
        
        <article id="post-<?php the_ID(); ?>" <?php post_class('default-page'); ?>>
            
            <!-- Page Header -->
            <header class="page-header mb-8">
                
                <!-- Breadcrumb -->
                <nav class="breadcrumb text-sm text-gray-600 mb-4">
                    <a href="<?php echo esc_url(home_url('/')); ?>" class="hover:text-blue-600">
                        <?php _e('Home', 'stock-scanner-pro'); ?>
                    </a>
                    <span class="mx-2">›</span>
                    <span class="text-gray-500"><?php the_title(); ?></span>
                </nav>

                <!-- Page Title -->
                <h1 class="page-title text-4xl font-bold text-gray-900 mb-4 leading-tight">
                    <?php the_title(); ?>
                </h1>

                <!-- Page Meta (if applicable) -->
                <?php if (get_the_modified_date() !== get_the_date()) : ?>
                    <div class="page-meta text-sm text-gray-600 mb-4">
                        <i class="fas fa-calendar-alt mr-1"></i>
                        <?php _e('Last updated:', 'stock-scanner-pro'); ?> 
                        <time datetime="<?php echo get_the_modified_date('c'); ?>">
                            <?php echo get_the_modified_date(); ?>
                        </time>
                    </div>
                <?php endif; ?>
            </header>

            <!-- Page Content -->
            <div class="page-content">
                
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

                <!-- Main Content -->
                <div class="content-wrapper">
                    <?php if (is_page_template() || has_shortcode(get_the_content(), 'stock_scanner')) : ?>
                        
                        <!-- For custom page templates or pages with shortcodes -->
                        <div class="template-content">
                            <?php
                            the_content();
                            
                            wp_link_pages(array(
                                'before' => '<div class="page-links text-center mt-8">' . __('Pages:', 'stock-scanner-pro'),
                                'after'  => '</div>',
                                'link_before' => '<span class="page-number bg-blue-100 text-blue-800 px-3 py-1 rounded-md mx-1">',
                                'link_after' => '</span>',
                            ));
                            ?>
                        </div>
                        
                    <?php else : ?>
                        
                        <!-- Regular page with prose styling -->
                        <div class="prose prose-lg max-w-none">
                            <?php
                            the_content();
                            
                            wp_link_pages(array(
                                'before' => '<div class="page-links text-center mt-8">' . __('Pages:', 'stock-scanner-pro'),
                                'after'  => '</div>',
                                'link_before' => '<span class="page-number bg-blue-100 text-blue-800 px-3 py-1 rounded-md mx-1">',
                                'link_after' => '</span>',
                            ));
                            ?>
                        </div>
                        
                    <?php endif; ?>
                </div>

                <!-- Page Actions -->
                <?php if (is_user_logged_in() && current_user_can('edit_post', get_the_ID())) : ?>
                    <div class="page-actions mt-8 pt-8 border-t border-gray-200">
                        <a href="<?php echo get_edit_post_link(); ?>" 
                           class="edit-page-link inline-flex items-center text-blue-600 hover:text-blue-700 font-medium">
                            <i class="fas fa-edit mr-2"></i>
                            <?php _e('Edit Page', 'stock-scanner-pro'); ?>
                        </a>
                    </div>
                <?php endif; ?>
            </div>

            <!-- Table of Contents (for long pages) -->
            <?php if (strlen(get_the_content()) > 3000) : ?>
                <aside class="table-of-contents bg-gray-50 rounded-lg p-6 mt-8">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">
                        <?php _e('Table of Contents', 'stock-scanner-pro'); ?>
                    </h3>
                    <div id="toc-container">
                        <!-- Table of contents will be generated by JavaScript -->
                    </div>
                </aside>
            <?php endif; ?>

            <!-- Page Footer Info -->
            <footer class="page-footer mt-12 pt-8 border-t border-gray-200">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    
                    <!-- Page Info -->
                    <div class="page-info">
                        <h3 class="text-lg font-semibold text-gray-900 mb-4">
                            <?php _e('Page Information', 'stock-scanner-pro'); ?>
                        </h3>
                        
                        <dl class="space-y-2 text-sm">
                            <div class="flex">
                                <dt class="text-gray-600 w-20"><?php _e('Published:', 'stock-scanner-pro'); ?></dt>
                                <dd class="text-gray-900"><?php echo get_the_date(); ?></dd>
                            </div>
                            
                            <?php if (get_the_modified_date() !== get_the_date()) : ?>
                                <div class="flex">
                                    <dt class="text-gray-600 w-20"><?php _e('Updated:', 'stock-scanner-pro'); ?></dt>
                                    <dd class="text-gray-900"><?php echo get_the_modified_date(); ?></dd>
                                </div>
                            <?php endif; ?>
                            
                            <div class="flex">
                                <dt class="text-gray-600 w-20"><?php _e('Author:', 'stock-scanner-pro'); ?></dt>
                                <dd class="text-gray-900"><?php the_author(); ?></dd>
                            </div>
                        </dl>
                    </div>

                    <!-- Contact/Support -->
                    <div class="page-support">
                        <h3 class="text-lg font-semibold text-gray-900 mb-4">
                            <?php _e('Need Help?', 'stock-scanner-pro'); ?>
                        </h3>
                        
                        <p class="text-gray-600 mb-4">
                            <?php _e('If you have questions about this page or need assistance with our platform, we\'re here to help.', 'stock-scanner-pro'); ?>
                        </p>
                        
                        <div class="support-actions space-y-2">
                            <?php if (get_page_by_path('contact')) : ?>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('contact'))); ?>" 
                                   class="support-link inline-flex items-center text-blue-600 hover:text-blue-700">
                                    <i class="fas fa-envelope mr-2"></i>
                                    <?php _e('Contact Support', 'stock-scanner-pro'); ?>
                                </a>
                            <?php endif; ?>
                            
                            <?php if (get_page_by_path('help-center')) : ?>
                                <a href="<?php echo esc_url(get_permalink(get_page_by_path('help-center'))); ?>" 
                                   class="support-link inline-flex items-center text-blue-600 hover:text-blue-700 block">
                                    <i class="fas fa-question-circle mr-2"></i>
                                    <?php _e('Visit Help Center', 'stock-scanner-pro'); ?>
                                </a>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>
            </footer>
        </article>

        <!-- Comments (if enabled) -->
        <?php
        if (comments_open() || get_comments_number()) :
            comments_template();
        endif;
        ?>

    <?php endwhile; ?>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Generate table of contents for long pages
    const tocContainer = document.getElementById('toc-container');
    if (tocContainer) {
        generateTableOfContents();
    }
});

function generateTableOfContents() {
    const headings = document.querySelectorAll('.prose h2, .prose h3, .prose h4');
    if (headings.length === 0) return;
    
    let tocHTML = '<ul class="toc-list space-y-1 text-sm">';
    
    headings.forEach((heading, index) => {
        // Add ID to heading if it doesn't have one
        if (!heading.id) {
            heading.id = 'heading-' + index;
        }
        
        const level = parseInt(heading.tagName.charAt(1));
        const indent = level === 2 ? '' : level === 3 ? 'ml-4' : 'ml-8';
        
        tocHTML += `
            <li class="${indent}">
                <a href="#${heading.id}" class="toc-link text-gray-700 hover:text-blue-600 transition-colors">
                    ${heading.textContent}
                </a>
            </li>
        `;
    });
    
    tocHTML += '</ul>';
    
    document.getElementById('toc-container').innerHTML = tocHTML;
    
    // Add smooth scrolling for TOC links
    document.querySelectorAll('.toc-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}
</script>

<style>
/* Page-specific styles */
.default-page .prose {
    color: #374151;
    line-height: 1.75;
}

.default-page .prose h2,
.default-page .prose h3,
.default-page .prose h4 {
    color: #1f2937;
    font-weight: 600;
    margin-top: 2em;
    margin-bottom: 1em;
}

.default-page .prose h2 {
    font-size: 1.5em;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 0.5em;
}

.default-page .prose h3 {
    font-size: 1.25em;
}

.default-page .prose p {
    margin-bottom: 1.25em;
}

.default-page .prose blockquote {
    border-left: 4px solid #3b82f6;
    padding-left: 1rem;
    margin: 1.5rem 0;
    font-style: italic;
    background: #f8fafc;
    padding: 1rem;
    border-radius: 0.375rem;
}

.default-page .prose ul,
.default-page .prose ol {
    padding-left: 1.5rem;
    margin-bottom: 1.25rem;
}

.default-page .prose li {
    margin-bottom: 0.5rem;
}

.default-page .prose a {
    color: #3b82f6;
    text-decoration: underline;
    text-decoration-color: rgba(59, 130, 246, 0.3);
    transition: text-decoration-color 0.3s ease;
}

.default-page .prose a:hover {
    text-decoration-color: #3b82f6;
}

.default-page .prose img {
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.default-page .prose code {
    background: #f3f4f6;
    padding: 0.125rem 0.25rem;
    border-radius: 0.25rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.875em;
}

.default-page .prose pre {
    background: #1f2937;
    color: #f9fafb;
    padding: 1rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    margin: 1.5rem 0;
}

.default-page .prose pre code {
    background: transparent;
    color: inherit;
}

/* Table of Contents */
.table-of-contents {
    position: sticky;
    top: 2rem;
}

.toc-link {
    display: block;
    padding: 0.25rem 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .page-footer .grid {
        grid-template-columns: 1fr;
    }
    
    .table-of-contents {
        position: static;
    }
}
</style>

<?php get_footer(); ?>