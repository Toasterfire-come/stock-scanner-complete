<?php
/**
 * 404 Error Page Template
 *
 * @package StockScannerPro
 */

get_header(); ?>

<div class="container mx-auto px-4 py-16">
    <div class="error-404 not-found max-w-2xl mx-auto text-center">
        
        <!-- Error Icon -->
        <div class="error-icon mb-8">
            <div class="text-8xl text-gray-300 mb-4">📈</div>
            <div class="text-6xl font-bold text-gray-900 mb-2">404</div>
        </div>

        <!-- Error Message -->
        <header class="page-header mb-8">
            <h1 class="page-title text-3xl font-bold text-gray-900 mb-4">
                <?php _e('Page Not Found', 'stock-scanner-pro'); ?>
            </h1>
            <p class="text-xl text-gray-600">
                <?php _e('The page you\'re looking for seems to have moved or no longer exists.', 'stock-scanner-pro'); ?>
            </p>
        </header>

        <!-- Search Form -->
        <div class="error-search mb-8">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
                <?php _e('Try searching for what you need:', 'stock-scanner-pro'); ?>
            </h2>
            <?php get_search_form(); ?>
        </div>

        <!-- Quick Links -->
        <div class="error-links mb-8">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
                <?php _e('Or visit one of these popular pages:', 'stock-scanner-pro'); ?>
            </h2>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <a href="<?php echo esc_url(home_url('/')); ?>" 
                   class="quick-link bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <i class="fas fa-home text-blue-600 text-xl mb-2"></i>
                    <div class="font-semibold text-gray-900"><?php _e('Homepage', 'stock-scanner-pro'); ?></div>
                    <div class="text-sm text-gray-600"><?php _e('Return to the main page', 'stock-scanner-pro'); ?></div>
                </a>

                <?php if (get_page_by_path('dashboard')) : ?>
                <a href="<?php echo esc_url(get_permalink(get_page_by_path('dashboard'))); ?>" 
                   class="quick-link bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <i class="fas fa-tachometer-alt text-green-600 text-xl mb-2"></i>
                    <div class="font-semibold text-gray-900"><?php _e('Dashboard', 'stock-scanner-pro'); ?></div>
                    <div class="text-sm text-gray-600"><?php _e('View your portfolio', 'stock-scanner-pro'); ?></div>
                </a>
                <?php endif; ?>

                <?php if (get_page_by_path('stock-lookup')) : ?>
                <a href="<?php echo esc_url(get_permalink(get_page_by_path('stock-lookup'))); ?>" 
                   class="quick-link bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <i class="fas fa-search text-purple-600 text-xl mb-2"></i>
                    <div class="font-semibold text-gray-900"><?php _e('Stock Lookup', 'stock-scanner-pro'); ?></div>
                    <div class="text-sm text-gray-600"><?php _e('Search for stocks', 'stock-scanner-pro'); ?></div>
                </a>
                <?php endif; ?>

                <?php if (get_page_by_path('market-overview')) : ?>
                <a href="<?php echo esc_url(get_permalink(get_page_by_path('market-overview'))); ?>" 
                   class="quick-link bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <i class="fas fa-chart-line text-orange-600 text-xl mb-2"></i>
                    <div class="font-semibold text-gray-900"><?php _e('Market Overview', 'stock-scanner-pro'); ?></div>
                    <div class="text-sm text-gray-600"><?php _e('View market trends', 'stock-scanner-pro'); ?></div>
                </a>
                <?php endif; ?>
            </div>
        </div>

        <!-- Recent Posts -->
        <?php
        $recent_posts = wp_get_recent_posts(array(
            'numberposts' => 3,
            'post_status' => 'publish'
        ));
        
        if (!empty($recent_posts)) : ?>
            <div class="recent-posts">
                <h2 class="text-lg font-semibold text-gray-900 mb-4">
                    <?php _e('Recent Posts:', 'stock-scanner-pro'); ?>
                </h2>
                
                <div class="posts-grid grid grid-cols-1 gap-4">
                    <?php foreach ($recent_posts as $post) : ?>
                        <a href="<?php echo get_permalink($post['ID']); ?>" 
                           class="post-item bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow text-left">
                            <h3 class="font-semibold text-gray-900 mb-2"><?php echo esc_html($post['post_title']); ?></h3>
                            <p class="text-sm text-gray-600"><?php echo wp_trim_words($post['post_content'], 15); ?></p>
                        </a>
                    <?php endforeach; ?>
                </div>
            </div>
        <?php endif; ?>

        <!-- Contact Info -->
        <div class="error-contact mt-12 p-6 bg-gray-50 rounded-lg">
            <h2 class="text-lg font-semibold text-gray-900 mb-2">
                <?php _e('Still can\'t find what you\'re looking for?', 'stock-scanner-pro'); ?>
            </h2>
            <p class="text-gray-600 mb-4">
                <?php _e('Our support team is here to help you get back on track.', 'stock-scanner-pro'); ?>
            </p>
            
            <div class="contact-actions space-y-2 sm:space-y-0 sm:space-x-4 sm:flex sm:justify-center">
                <?php if (get_page_by_path('contact')) : ?>
                    <a href="<?php echo esc_url(get_permalink(get_page_by_path('contact'))); ?>" 
                       class="btn btn-primary">
                        <i class="fas fa-envelope mr-2"></i>
                        <?php _e('Contact Support', 'stock-scanner-pro'); ?>
                    </a>
                <?php endif; ?>
                
                <?php if (get_page_by_path('help-center')) : ?>
                    <a href="<?php echo esc_url(get_permalink(get_page_by_path('help-center'))); ?>" 
                       class="btn btn-outline-primary">
                        <i class="fas fa-question-circle mr-2"></i>
                        <?php _e('Help Center', 'stock-scanner-pro'); ?>
                    </a>
                <?php endif; ?>
            </div>
        </div>
    </div>
</div>

<style>
.error-404 .quick-link,
.error-404 .post-item {
    transition: all 0.3s ease;
}

.error-404 .quick-link:hover,
.error-404 .post-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.error-404 .contact-actions .btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.3s ease;
}

.error-404 .contact-actions .btn-primary {
    background: #3b82f6;
    color: white;
    border: 2px solid #3b82f6;
}

.error-404 .contact-actions .btn-primary:hover {
    background: #2563eb;
    border-color: #2563eb;
}

.error-404 .contact-actions .btn-outline-primary {
    background: transparent;
    color: #3b82f6;
    border: 2px solid #3b82f6;
}

.error-404 .contact-actions .btn-outline-primary:hover {
    background: #3b82f6;
    color: white;
}

@media (max-width: 640px) {
    .error-404 .contact-actions .btn {
        display: block;
        width: 100%;
        text-align: center;
        margin-bottom: 0.5rem;
    }
}
</style>

<?php get_footer(); ?>