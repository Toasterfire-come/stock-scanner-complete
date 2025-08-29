<?php
/**
 * The template for displaying 404 pages (not found)
 *
 * @package RetailTradeScanner
 */

get_header();

// Layout configuration
$layout_args = array(
    'page_title' => __('Page Not Found', 'retail-trade-scanner'),
    'page_description' => __('The page you are looking for could not be found.', 'retail-trade-scanner'),
    'page_class' => 'error-404-page',
    'sidebar' => false,
    'show_page_header' => false
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<div class="error-404-container">
    <div class="error-content text-center">
        <!-- Error Illustration -->
        <div class="error-illustration">
            <div class="error-number">404</div>
            <div class="error-icon">
                <?php echo rts_get_icon('search', array('width' => '120', 'height' => '120', 'class' => 'error-icon-svg')); ?>
            </div>
        </div>

        <!-- Error Message -->
        <div class="error-message">
            <h1 class="error-title"><?php esc_html_e('Oops! Page Not Found', 'retail-trade-scanner'); ?></h1>
            <p class="error-description">
                <?php esc_html_e('The page you\'re looking for doesn\'t exist or has been moved. Don\'t worry, let\'s get you back on track.', 'retail-trade-scanner'); ?>
            </p>
        </div>

        <!-- Search Form -->
        <div class="error-search">
            <h3><?php esc_html_e('Search for what you need', 'retail-trade-scanner'); ?></h3>
            <div class="search-form-container">
                <?php get_search_form(); ?>
            </div>
        </div>

        <!-- Suggested Actions -->
        <div class="error-suggestions">
            <h3><?php esc_html_e('Try these instead', 'retail-trade-scanner'); ?></h3>
            <div class="suggestion-grid">
                <a href="<?php echo esc_url(home_url('/')); ?>" class="suggestion-item card glass-card">
                    <div class="suggestion-icon">
                        <?php echo rts_get_icon('home', array('width' => '32', 'height' => '32')); ?>
                    </div>
                    <h4><?php esc_html_e('Go Home', 'retail-trade-scanner'); ?></h4>
                    <p><?php esc_html_e('Return to the homepage', 'retail-trade-scanner'); ?></p>
                </a>

                <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="suggestion-item card glass-card">
                    <div class="suggestion-icon">
                        <?php echo rts_get_icon('scanner', array('width' => '32', 'height' => '32')); ?>
                    </div>
                    <h4><?php esc_html_e('Stock Scanner', 'retail-trade-scanner'); ?></h4>
                    <p><?php esc_html_e('Find stocks with our scanner', 'retail-trade-scanner'); ?></p>
                </a>

                <?php if (is_user_logged_in()) : ?>
                    <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="suggestion-item card glass-card">
                        <div class="suggestion-icon">
                            <?php echo rts_get_icon('dashboard', array('width' => '32', 'height' => '32')); ?>
                        </div>
                        <h4><?php esc_html_e('Dashboard', 'retail-trade-scanner'); ?></h4>
                        <p><?php esc_html_e('View your dashboard', 'retail-trade-scanner'); ?></p>
                    </a>
                <?php endif; ?>

                <a href="<?php echo esc_url(home_url('/popular/')); ?>" class="suggestion-item card glass-card">
                    <div class="suggestion-icon">
                        <?php echo rts_get_icon('trending-up', array('width' => '32', 'height' => '32')); ?>
                    </div>
                    <h4><?php esc_html_e('Popular Stocks', 'retail-trade-scanner'); ?></h4>
                    <p><?php esc_html_e('Explore trending stocks', 'retail-trade-scanner'); ?></p>
                </a>

                <a href="<?php echo esc_url(home_url('/news/')); ?>" class="suggestion-item card glass-card">
                    <div class="suggestion-icon">
                        <?php echo rts_get_icon('news', array('width' => '32', 'height' => '32')); ?>
                    </div>
                    <h4><?php esc_html_e('Market News', 'retail-trade-scanner'); ?></h4>
                    <p><?php esc_html_e('Latest market updates', 'retail-trade-scanner'); ?></p>
                </a>

                <a href="<?php echo esc_url(home_url('/contact/')); ?>" class="suggestion-item card glass-card">
                    <div class="suggestion-icon">
                        <?php echo rts_get_icon('contact', array('width' => '32', 'height' => '32')); ?>
                    </div>
                    <h4><?php esc_html_e('Contact Support', 'retail-trade-scanner'); ?></h4>
                    <p><?php esc_html_e('Get help from our team', 'retail-trade-scanner'); ?></p>
                </a>
            </div>
        </div>

        <!-- Back Button -->
        <div class="error-actions">
            <button onclick="history.back()" class="btn btn-outline btn-lg">
                <?php echo rts_get_icon('chevron-left', array('width' => '20', 'height' => '20')); ?>
                <?php esc_html_e('Go Back', 'retail-trade-scanner'); ?>
            </button>
            
            <a href="<?php echo esc_url(home_url('/')); ?>" class="btn btn-primary btn-lg btn-magnetic">
                <?php echo rts_get_icon('home', array('width' => '20', 'height' => '20')); ?>
                <?php esc_html_e('Go Home', 'retail-trade-scanner'); ?>
            </a>
        </div>

        <!-- Popular Search Terms -->
        <div class="popular-searches">
            <h4><?php esc_html_e('Popular Search Terms', 'retail-trade-scanner'); ?></h4>
            <div class="search-tags">
                <?php
                $popular_terms = array('AAPL', 'TSLA', 'NVDA', 'S&P 500', 'Portfolio', 'Market News', 'Alerts');
                foreach ($popular_terms as $term) :
                ?>
                    <a href="<?php echo esc_url(home_url('/?s=' . urlencode($term))); ?>" class="search-tag">
                        <?php echo esc_html($term); ?>
                    </a>
                <?php endforeach; ?>
            </div>
        </div>
    </div>
</div>

                </div> <!-- .page-content -->
            </div> <!-- .container -->
        </div> <!-- .page-content-section -->
    </main> <!-- .main-content-area -->
</div> <!-- .page-wrapper -->

<style>
/* 404 Page Styles */
.error-404-container {
    padding: var(--spacing-4xl) 0;
    min-height: 60vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.error-content {
    max-width: 800px;
    margin: 0 auto;
}

/* Error Illustration */
.error-illustration {
    position: relative;
    margin-bottom: var(--spacing-3xl);
}

.error-number {
    font-size: clamp(4rem, 15vw, 12rem);
    font-weight: 900;
    color: var(--primary-500);
    line-height: 0.8;
    margin-bottom: var(--spacing-xl);
    opacity: 0.1;
    position: relative;
    z-index: 1;
}

.error-icon {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 2;
}

.error-icon-svg {
    color: var(--primary-600);
    opacity: 0.6;
}

/* Error Message */
.error-message {
    margin-bottom: var(--spacing-3xl);
}

.error-title {
    font-size: var(--text-4xl);
    font-weight: 800;
    color: var(--gray-900);
    margin-bottom: var(--spacing-lg);
    line-height: 1.1;
}

.error-description {
    font-size: var(--text-lg);
    color: var(--gray-600);
    line-height: 1.6;
    max-width: 600px;
    margin: 0 auto;
}

/* Search Section */
.error-search {
    margin-bottom: var(--spacing-3xl);
}

.error-search h3 {
    font-size: var(--text-xl);
    font-weight: 700;
    color: var(--gray-900);
    margin-bottom: var(--spacing-lg);
}

.search-form-container {
    max-width: 500px;
    margin: 0 auto;
}

.search-form-container .search-form {
    display: flex;
    gap: var(--spacing-sm);
    align-items: stretch;
}

.search-form-container .search-field-wrapper {
    flex: 1;
}

.search-form-container .search-field {
    height: 56px;
    font-size: var(--text-base);
    border-radius: var(--radius-xl);
}

.search-form-container .search-submit {
    height: 56px;
    padding: 0 var(--spacing-xl);
    border-radius: var(--radius-xl);
}

/* Suggestion Grid */
.error-suggestions {
    margin-bottom: var(--spacing-3xl);
}

.error-suggestions h3 {
    font-size: var(--text-xl);
    font-weight: 700;
    color: var(--gray-900);
    margin-bottom: var(--spacing-xl);
}

.suggestion-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-2xl);
}

.suggestion-item {
    padding: var(--spacing-xl);
    text-decoration: none;
    text-align: center;
    transition: all var(--transition-normal) var(--easing-standard);
    border: 1px solid transparent;
}

.suggestion-item:hover {
    text-decoration: none;
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
    border-color: var(--primary-200);
}

.suggestion-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 64px;
    height: 64px;
    margin: 0 auto var(--spacing-lg);
    background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
    color: white;
    border-radius: var(--radius-2xl);
}

.suggestion-item h4 {
    font-size: var(--text-lg);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-sm);
}

.suggestion-item p {
    font-size: var(--text-sm);
    color: var(--gray-600);
    margin: 0;
    line-height: 1.4;
}

/* Error Actions */
.error-actions {
    display: flex;
    justify-content: center;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-3xl);
    flex-wrap: wrap;
}

/* Popular Searches */
.popular-searches h4 {
    font-size: var(--text-base);
    font-weight: 600;
    color: var(--gray-700);
    margin-bottom: var(--spacing-lg);
}

.search-tags {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
}

.search-tag {
    padding: var(--spacing-sm) var(--spacing-lg);
    background: var(--gray-100);
    color: var(--gray-700);
    text-decoration: none;
    border-radius: var(--radius-full);
    font-size: var(--text-sm);
    font-weight: 500;
    transition: all var(--transition-fast) var(--easing-standard);
    border: 1px solid var(--gray-200);
}

.search-tag:hover {
    background: var(--primary-100);
    color: var(--primary-700);
    border-color: var(--primary-300);
    text-decoration: none;
    transform: translateY(-1px);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .error-404-container {
        padding: var(--spacing-2xl) 0;
    }
    
    .error-illustration {
        margin-bottom: var(--spacing-2xl);
    }
    
    .error-number {
        font-size: clamp(3rem, 20vw, 8rem);
    }
    
    .error-icon svg {
        width: 80px;
        height: 80px;
    }
    
    .error-title {
        font-size: var(--text-3xl);
    }
    
    .error-description {
        font-size: var(--text-base);
    }
    
    .suggestion-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: var(--spacing-md);
    }
    
    .suggestion-item {
        padding: var(--spacing-lg);
    }
    
    .suggestion-icon {
        width: 48px;
        height: 48px;
        margin-bottom: var(--spacing-md);
    }
    
    .suggestion-icon svg {
        width: 24px;
        height: 24px;
    }
    
    .error-actions {
        flex-direction: column;
        align-items: center;
    }
    
    .error-actions .btn {
        width: 100%;
        max-width: 300px;
    }
}

@media (max-width: 480px) {
    .suggestion-grid {
        grid-template-columns: 1fr;
    }
    
    .search-form-container .search-form {
        flex-direction: column;
    }
    
    .search-tags {
        justify-content: center;
    }
}

/* Dark mode adjustments */
[data-theme="dark"] .error-title {
    color: var(--gray-100);
}

[data-theme="dark"] .error-description {
    color: var(--gray-400);
}

[data-theme="dark"] .error-search h3,
[data-theme="dark"] .error-suggestions h3 {
    color: var(--gray-100);
}

[data-theme="dark"] .suggestion-item h4 {
    color: var(--gray-100);
}

[data-theme="dark"] .suggestion-item p {
    color: var(--gray-400);
}

[data-theme="dark"] .popular-searches h4 {
    color: var(--gray-300);
}

[data-theme="dark"] .search-tag {
    background: var(--gray-800);
    color: var(--gray-300);
    border-color: var(--gray-700);
}

[data-theme="dark"] .search-tag:hover {
    background: var(--primary-900);
    color: var(--primary-300);
    border-color: var(--primary-700);
}

/* Animation for error illustration */
@keyframes float {
    0%, 100% { transform: translate(-50%, -50%) translateY(0px); }
    50% { transform: translate(-50%, -50%) translateY(-10px); }
}

.error-icon {
    animation: float 3s ease-in-out infinite;
}

/* Pulse animation for error number */
@keyframes pulse {
    0%, 100% { opacity: 0.1; }
    50% { opacity: 0.15; }
}

.error-number {
    animation: pulse 4s ease-in-out infinite;
}
</style>

<?php get_footer(); ?>