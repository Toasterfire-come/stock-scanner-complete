<?php
/**
 * Main Layout Shell Template Part - Page Wrapper with Sticky Header/Sidebar
 *
 * @package RetailTradeScanner
 */

// Default layout attributes
$defaults = array(
    'page_title' => '',
    'page_description' => '',
    'page_class' => '',
    'content_class' => '',
    'sidebar' => true, // Show sidebar for authenticated users
    'breadcrumbs' => array(),
    'header_actions' => array(),
    'show_page_header' => true,
    'container_type' => 'container', // container, container-narrow, container-wide, fluid
    'layout' => 'default', // default, centered, full-width
);

// Parse attributes
$args = wp_parse_args($args ?? array(), $defaults);

// Determine if user is logged in and sidebar should be shown
$show_sidebar = $args['sidebar'] && is_user_logged_in();

// Build page classes
$page_classes = array('page-wrapper');
$page_classes[] = 'layout-' . esc_attr($args['layout']);

if ($show_sidebar) {
    $page_classes[] = 'has-sidebar';
}

if (!empty($args['page_class'])) {
    $page_classes[] = $args['page_class'];
}

// Build content classes
$content_classes = array('page-content');
if (!empty($args['content_class'])) {
    $content_classes[] = $args['content_class'];
}

// Generate breadcrumbs if provided
$breadcrumb_items = array();
if (!empty($args['breadcrumbs'])) {
    $breadcrumb_items = $args['breadcrumbs'];
} elseif (!is_front_page()) {
    // Auto-generate breadcrumbs
    $breadcrumb_items[] = array('text' => __('Home', 'retail-trade-scanner'), 'url' => home_url('/'));
    
    if (is_page()) {
        global $post;
        if ($post->post_parent) {
            $parent_ids = get_post_ancestors($post->ID);
            foreach (array_reverse($parent_ids) as $parent_id) {
                $breadcrumb_items[] = array(
                    'text' => get_the_title($parent_id),
                    'url' => get_permalink($parent_id)
                );
            }
        }
        $breadcrumb_items[] = array('text' => get_the_title(), 'url' => '');
    } elseif (is_single()) {
        $categories = get_the_category();
        if (!empty($categories)) {
            $breadcrumb_items[] = array(
                'text' => $categories[0]->name,
                'url' => get_category_link($categories[0]->term_id)
            );
        }
        $breadcrumb_items[] = array('text' => get_the_title(), 'url' => '');
    } elseif (is_category()) {
        $category = get_queried_object();
        if ($category->parent) {
            $parent_categories = get_category_parents($category->parent, true, '|||');
            $parents = explode('|||', rtrim($parent_categories, '|||'));
            foreach ($parents as $parent) {
                if (!empty($parent)) {
                    $breadcrumb_items[] = array('text' => strip_tags($parent), 'url' => '');
                }
            }
        }
        $breadcrumb_items[] = array('text' => $category->name, 'url' => '');
    }
}
?>

<div class="<?php echo implode(' ', $page_classes); ?>">
    <?php if ($show_sidebar) : ?>
        <!-- Sidebar is rendered in header.php -->
    <?php endif; ?>

    <main class="main-content-area" role="main">
        <?php if ($args['show_page_header'] && (!empty($args['page_title']) || !empty($breadcrumb_items) || !empty($args['header_actions']))) : ?>
            <div class="page-header-section">
                <div class="<?php echo esc_attr($args['container_type']); ?>">
                    <?php if (!empty($breadcrumb_items)) : ?>
                        <nav class="breadcrumbs" aria-label="<?php esc_attr_e('Breadcrumb navigation', 'retail-trade-scanner'); ?>">
                            <ol class="breadcrumb-list">
                                <?php foreach ($breadcrumb_items as $index => $item) : ?>
                                    <li class="breadcrumb-item <?php echo empty($item['url']) ? 'active' : ''; ?>">
                                        <?php if (!empty($item['url'])) : ?>
                                            <a href="<?php echo esc_url($item['url']); ?>" class="breadcrumb-link">
                                                <?php echo esc_html($item['text']); ?>
                                            </a>
                                        <?php else : ?>
                                            <span class="breadcrumb-current" aria-current="page">
                                                <?php echo esc_html($item['text']); ?>
                                            </span>
                                        <?php endif; ?>
                                        
                                        <?php if ($index < count($breadcrumb_items) - 1) : ?>
                                            <span class="breadcrumb-separator" aria-hidden="true">
                                                <?php echo rts_get_icon('chevron-right', array('width' => '14', 'height' => '14')); ?>
                                            </span>
                                        <?php endif; ?>
                                    </li>
                                <?php endforeach; ?>
                            </ol>
                        </nav>
                    <?php endif; ?>

                    <?php if (!empty($args['page_title']) || !empty($args['header_actions'])) : ?>
                        <div class="page-header-content">
                            <div class="page-header-main">
                                <?php if (!empty($args['page_title'])) : ?>
                                    <h1 class="page-title"><?php echo esc_html($args['page_title']); ?></h1>
                                <?php endif; ?>
                                
                                <?php if (!empty($args['page_description'])) : ?>
                                    <p class="page-description"><?php echo esc_html($args['page_description']); ?></p>
                                <?php endif; ?>
                            </div>
                            
                            <?php if (!empty($args['header_actions'])) : ?>
                                <div class="page-header-actions">
                                    <?php foreach ($args['header_actions'] as $action) : ?>
                                        <?php if (is_array($action)) : ?>
                                            <?php get_template_part('template-parts/components/button', null, $action); ?>
                                        <?php else : ?>
                                            <?php echo wp_kses_post($action); ?>
                                        <?php endif; ?>
                                    <?php endforeach; ?>
                                </div>
                            <?php endif; ?>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        <?php endif; ?>

        <div class="page-content-section">
            <div class="<?php echo esc_attr($args['container_type']); ?>">
                <div class="<?php echo implode(' ', $content_classes); ?>">
                    <?php
                    // This is where the main page content will be inserted
                    // The calling template should provide content after including this template
                    ?>