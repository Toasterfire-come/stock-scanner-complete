<?php
/**
 * Main page wrapper providing sticky header/sidebar layout and content container
 *
 * @package RetailTradeScanner
 */

$args = wp_parse_args($args, array(
    'page_title' => '',
    'page_description' => '',
    'page_class' => '',
    'header_actions' => array(),
    'sidebar_enabled' => is_user_logged_in(),
    'breadcrumbs' => true
));

extract($args);
?>

<div class="page-wrapper <?php echo esc_attr($page_class); ?>">
    
    <?php if ($breadcrumbs && !is_front_page()) : ?>
        <nav class="breadcrumbs" aria-label="<?php esc_attr_e('Breadcrumb', 'retail-trade-scanner'); ?>">
            <div class="container">
                <ol class="breadcrumb-list">
                    <li class="breadcrumb-item">
                        <a href="<?php echo esc_url(home_url('/')); ?>">
                            <?php echo rts_get_icon('home', ['width' => '16', 'height' => '16']); ?>
                            <?php esc_html_e('Home', 'retail-trade-scanner'); ?>
                        </a>
                    </li>
                    
                    <?php if (is_user_logged_in() && !is_page('dashboard')) : ?>
                        <li class="breadcrumb-separator">
                            <?php echo rts_get_icon('chevron-right', ['width' => '12', 'height' => '12']); ?>
                        </li>
                        <li class="breadcrumb-item">
                            <a href="<?php echo esc_url(home_url('/dashboard/')); ?>">
                                <?php esc_html_e('Dashboard', 'retail-trade-scanner'); ?>
                            </a>
                        </li>
                    <?php endif; ?>
                    
                    <li class="breadcrumb-separator">
                        <?php echo rts_get_icon('chevron-right', ['width' => '12', 'height' => '12']); ?>
                    </li>
                    <li class="breadcrumb-item active" aria-current="page">
                        <?php echo esc_html($page_title ?: get_the_title()); ?>
                    </li>
                </ol>
            </div>
        </nav>
    <?php endif; ?>
    
    <div class="page-content-section">
        <div class="container <?php echo $sidebar_enabled ? 'has-sidebar' : ''; ?>">
            
            <?php if ($page_title || $page_description || !empty($header_actions)) : ?>
                <header class="page-header animate-fade-up">
                    <div class="page-header-content">
                        <div class="page-header-text">
                            <?php if ($page_title) : ?>
                                <h1 class="page-title"><?php echo esc_html($page_title); ?></h1>
                            <?php endif; ?>
                            
                            <?php if ($page_description) : ?>
                                <p class="page-description"><?php echo esc_html($page_description); ?></p>
                            <?php endif; ?>
                        </div>
                        
                        <?php if (!empty($header_actions)) : ?>
                            <div class="page-header-actions">
                                <?php foreach ($header_actions as $action) : ?>
                                    <button class="btn btn-<?php echo esc_attr($action['variant'] ?? 'primary'); ?> <?php echo esc_attr($action['classes'] ?? ''); ?>">
                                        <?php if (isset($action['icon'])) : ?>
                                            <?php echo rts_get_icon($action['icon'], ['width' => '16', 'height' => '16']); ?>
                                        <?php endif; ?>
                                        <?php echo esc_html($action['text']); ?>
                                    </button>
                                <?php endforeach; ?>
                            </div>
                        <?php endif; ?>
                    </div>
                </header>
            <?php endif; ?>
            
            <main class="main-content-area <?php echo $sidebar_enabled ? 'with-sidebar' : ''; ?>" role="main">
                <div class="page-content animate-scale-in">