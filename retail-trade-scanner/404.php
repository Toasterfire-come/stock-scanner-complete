<?php
/**
 * The template for displaying 404 pages (not found)
 *
 * @package RetailTradeScanner
 */

get_header();
?>

<div class="error-page">
    <div class="container">
        <div class="error-content">
            <!-- Error Visual -->
            <div class="error-visual animate-fade-up">
                <div class="error-icon">
                    <?php echo rts_get_icon('search', ['width' => '120', 'height' => '120', 'class' => 'error-main-icon']); ?>
                    <div class="error-number">404</div>
                </div>
            </div>
            
            <!-- Error Message -->
            <div class="error-text animate-fade-up">
                <h1 class="error-title">
                    <?php esc_html_e('Page Not Found', 'retail-trade-scanner'); ?>
                </h1>
                <p class="error-description">
                    <?php esc_html_e('Sorry, we couldn\'t find the page you\'re looking for. The page might have been moved, deleted, or you entered the wrong URL.', 'retail-trade-scanner'); ?>
                </p>
            </div>
            
            <!-- Search & Actions -->
            <div class="error-actions animate-fade-up">
                <div class="search-section">
                    <h3><?php esc_html_e('Search our site', 'retail-trade-scanner'); ?></h3>
                    <form class="error-search-form" role="search" method="get" action="<?php echo esc_url(home_url('/')); ?>">
                        <div class="search-input-group">
                            <input type="search" 
                                   name="s" 
                                   class="search-input" 
                                   placeholder="<?php esc_attr_e('Search for stocks, features, or help...', 'retail-trade-scanner'); ?>"
                                   value="<?php echo get_search_query(); ?>"
                                   aria-label="<?php esc_attr_e('Search', 'retail-trade-scanner'); ?>">
                            <button type="submit" class="search-button">
                                <?php echo rts_get_icon('search', ['width' => '20', 'height' => '20']); ?>
                                <span class="sr-only"><?php esc_html_e('Search', 'retail-trade-scanner'); ?></span>
                            </button>
                        </div>
                    </form>
                </div>
                
                <div class="quick-actions">
                    <h3><?php esc_html_e('Or try these popular pages', 'retail-trade-scanner'); ?></h3>
                    <div class="action-links">
                        <a href="<?php echo esc_url(home_url('/')); ?>" class="action-link">
                            <?php echo rts_get_icon('home', ['width' => '20', 'height' => '20']); ?>
                            <span><?php esc_html_e('Home', 'retail-trade-scanner'); ?></span>
                        </a>
                        
                        <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="action-link">
                            <?php echo rts_get_icon('dashboard', ['width' => '20', 'height' => '20']); ?>
                            <span><?php esc_html_e('Dashboard', 'retail-trade-scanner'); ?></span>
                        </a>
                        
                        <a href="<?php echo esc_url(home_url('/scanner/')); ?>" class="action-link">
                            <?php echo rts_get_icon('scanner', ['width' => '20', 'height' => '20']); ?>
                            <span><?php esc_html_e('Stock Scanner', 'retail-trade-scanner'); ?></span>
                        </a>
                        
                        <a href="<?php echo esc_url(home_url('/contact/')); ?>" class="action-link">
                            <?php echo rts_get_icon('email', ['width' => '20', 'height' => '20']); ?>
                            <span><?php esc_html_e('Contact Support', 'retail-trade-scanner'); ?></span>
                        </a>
                    </div>
                </div>
                
                <div class="back-button">
                    <button onclick="history.back()" class="btn btn-outline">
                        <?php echo rts_get_icon('arrow-left', ['width' => '16', 'height' => '16']); ?>
                        <?php esc_html_e('Go Back', 'retail-trade-scanner'); ?>
                    </button>
                    
                    <a href="<?php echo esc_url(home_url('/')); ?>" class="btn btn-primary">
                        <?php echo rts_get_icon('home', ['width' => '16', 'height' => '16']); ?>
                        <?php esc_html_e('Return Home', 'retail-trade-scanner'); ?>
                    </a>
                </div>
            </div>
            
            <!-- Help Section -->
            <div class="error-help animate-fade-up">
                <div class="help-card glass-card">
                    <h3><?php esc_html_e('Need Help?', 'retail-trade-scanner'); ?></h3>
                    <p><?php esc_html_e('Our support team is available 24/7 to assist you with any questions or issues.', 'retail-trade-scanner'); ?></p>
                    <div class="help-links">
                        <a href="<?php echo esc_url(home_url('/contact/')); ?>" class="help-link">
                            <?php echo rts_get_icon('help-circle', ['width' => '16', 'height' => '16']); ?>
                            <?php esc_html_e('Contact Support', 'retail-trade-scanner'); ?>
                        </a>
                        <a href="<?php echo esc_url(home_url('/faq/')); ?>" class="help-link">
                            <?php echo rts_get_icon('book-open', ['width' => '16', 'height' => '16']); ?>
                            <?php esc_html_e('FAQ', 'retail-trade-scanner'); ?>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.error-page {
    min-height: 80vh;
    display: flex;
    align-items: center;
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    padding: var(--spacing-2xl) 0;
}

.error-content {
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
}

.error-visual {
    margin-bottom: var(--spacing-2xl);
}

.error-icon {
    position: relative;
    display: inline-block;
    margin-bottom: var(--spacing-xl);
}

.error-main-icon {
    color: var(--gray-300);
    opacity: 0.6;
}

.error-number {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 4rem;
    font-weight: 900;
    color: var(--primary-500);
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.error-title {
    font-size: var(--text-3xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-lg);
}

.error-description {
    font-size: var(--text-lg);
    color: var(--gray-600);
    line-height: 1.6;
    margin: 0 0 var(--spacing-2xl);
}

.error-actions {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2xl);
    margin-bottom: var(--spacing-2xl);
}

.search-section h3,
.quick-actions h3 {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--gray-800);
    margin-bottom: var(--spacing-lg);
}

.search-input-group {
    display: flex;
    max-width: 400px;
    margin: 0 auto;
    border-radius: var(--radius-xl);
    overflow: hidden;
    box-shadow: var(--shadow-lg);
}

.search-input {
    flex: 1;
    padding: var(--spacing-md) var(--spacing-lg);
    border: 2px solid var(--primary-200);
    border-right: none;
    font-size: var(--text-base);
    outline: none;
}

.search-input:focus {
    border-color: var(--primary-500);
}

.search-button {
    padding: var(--spacing-md) var(--spacing-lg);
    background: var(--primary-500);
    color: white;
    border: 2px solid var(--primary-500);
    cursor: pointer;
    transition: background-color var(--transition-fast) var(--easing-standard);
}

.search-button:hover {
    background: var(--primary-600);
    border-color: var(--primary-600);
}

.action-links {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-lg);
    max-width: 600px;
    margin: 0 auto;
}

.action-link {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-lg);
    background: var(--surface);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    text-decoration: none;
    color: var(--gray-700);
    transition: all var(--transition-fast) var(--easing-standard);
}

.action-link:hover {
    background: var(--primary-50);
    border-color: var(--primary-200);
    color: var(--primary-700);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    text-decoration: none;
}

.back-button {
    display: flex;
    gap: var(--spacing-lg);
    justify-content: center;
}

.error-help {
    max-width: 500px;
    margin: 0 auto;
}

.help-card {
    padding: var(--spacing-2xl);
    text-align: center;
}

.help-card h3 {
    font-size: var(--text-xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-md);
}

.help-card p {
    color: var(--gray-600);
    margin: 0 0 var(--spacing-lg);
}

.help-links {
    display: flex;
    gap: var(--spacing-lg);
    justify-content: center;
}

.help-link {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    color: var(--primary-600);
    font-weight: 600;
    text-decoration: none;
    transition: color var(--transition-fast) var(--easing-standard);
}

.help-link:hover {
    color: var(--primary-700);
    text-decoration: none;
}

@media (max-width: 640px) {
    .error-number {
        font-size: 3rem;
    }
    
    .error-title {
        font-size: var(--text-2xl);
    }
    
    .action-links {
        grid-template-columns: 1fr;
        gap: var(--spacing-md);
    }
    
    .back-button {
        flex-direction: column;
        align-items: center;
    }
    
    .help-links {
        flex-direction: column;
        align-items: center;
    }
}

[data-theme="dark"] .error-title {
    color: var(--gray-100);
}

[data-theme="dark"] .error-description {
    color: var(--gray-300);
}

[data-theme="dark"] .search-input {
    background: var(--gray-800);
    border-color: var(--gray-600);
    color: var(--gray-200);
}

[data-theme="dark"] .action-link {
    background: var(--gray-800);
    border-color: var(--gray-700);
    color: var(--gray-300);
}

[data-theme="dark"] .action-link:hover {
    background: var(--gray-700);
    color: var(--primary-400);
}
</style>

<?php get_footer(); ?>