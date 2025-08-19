<?php
/**
 * Main template file
 *
 * @package StockScannerPro
 */

get_header(); ?>

<div class="container mx-auto px-4 py-8">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Main Content -->
        <main class="lg:col-span-2">
            <?php if (have_posts()) : ?>
                
                <?php if (is_home() && !is_front_page()) : ?>
                    <header class="page-header mb-8">
                        <h1 class="page-title text-3xl font-bold text-gray-900">
                            <?php single_post_title(); ?>
                        </h1>
                    </header>
                <?php endif; ?>

                <div class="posts-container space-y-8">
                    <?php while (have_posts()) : the_post(); ?>
                        
                        <article id="post-<?php the_ID(); ?>" <?php post_class('bg-white rounded-lg shadow-sm border p-6'); ?>>
                            
                            <?php if (has_post_thumbnail()) : ?>
                                <div class="post-thumbnail mb-4">
                                    <a href="<?php the_permalink(); ?>">
                                        <?php the_post_thumbnail('medium', array('class' => 'w-full h-48 object-cover rounded-lg')); ?>
                                    </a>
                                </div>
                            <?php endif; ?>

                            <header class="entry-header mb-4">
                                <h2 class="entry-title text-xl font-semibold">
                                    <a href="<?php the_permalink(); ?>" class="text-gray-900 hover:text-blue-600 transition-colors">
                                        <?php the_title(); ?>
                                    </a>
                                </h2>

                                <div class="entry-meta text-sm text-gray-500 mt-2">
                                    <time datetime="<?php echo get_the_date('c'); ?>">
                                        <?php echo get_the_date(); ?>
                                    </time>
                                    <span class="separator mx-2">•</span>
                                    <span class="author">
                                        <?php _e('By', 'stock-scanner-pro'); ?> 
                                        <a href="<?php echo esc_url(get_author_posts_url(get_the_author_meta('ID'))); ?>" class="hover:text-blue-600">
                                            <?php the_author(); ?>
                                        </a>
                                    </span>
                                </div>
                            </header>

                            <div class="entry-content">
                                <?php the_excerpt(); ?>
                            </div>

                            <footer class="entry-footer mt-4 pt-4 border-t border-gray-100">
                                <a href="<?php the_permalink(); ?>" class="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium">
                                    <?php _e('Read more', 'stock-scanner-pro'); ?>
                                    <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                                    </svg>
                                </a>
                            </footer>

                        </article>

                    <?php endwhile; ?>
                </div>

                <!-- Pagination -->
                <nav class="pagination-nav mt-12" aria-label="<?php _e('Posts navigation', 'stock-scanner-pro'); ?>">
                    <?php
                    the_posts_pagination(array(
                        'mid_size' => 2,
                        'prev_text' => '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>' . __('Previous', 'stock-scanner-pro'),
                        'next_text' => __('Next', 'stock-scanner-pro') . '<svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>',
                        'class' => 'flex justify-center items-center space-x-4',
                    ));
                    ?>
                </nav>

            <?php else : ?>
                
                <!-- No Posts Found -->
                <div class="no-posts bg-white rounded-lg shadow-sm border p-8 text-center">
                    <div class="no-posts-icon mb-4">
                        <svg class="w-16 h-16 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                    </div>
                    
                    <h2 class="text-xl font-semibold text-gray-900 mb-2">
                        <?php _e('Nothing here', 'stock-scanner-pro'); ?>
                    </h2>
                    
                    <p class="text-gray-600 mb-6">
                        <?php 
                        if (is_search()) {
                            printf(__('Sorry, no results were found for "%s". Try searching for something else.', 'stock-scanner-pro'), get_search_query());
                        } else {
                            _e('It looks like nothing was found at this location. Maybe try a search?', 'stock-scanner-pro');
                        }
                        ?>
                    </p>

                    <?php get_search_form(); ?>
                </div>

            <?php endif; ?>
        </main>

        <!-- Sidebar -->
        <aside class="sidebar">
            <?php get_sidebar(); ?>
        </aside>

    </div>
</div>

<?php get_footer(); ?>