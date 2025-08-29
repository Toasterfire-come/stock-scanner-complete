<?php
/**
 * Template Name: Help Center
 * 
 * Help Center with categories, search, and popular articles
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('Help Center', 'retail-trade-scanner'),
    'page_description' => __('Find answers, how-tos, and troubleshooting guides', 'retail-trade-scanner'),
    'page_class' => 'help-page',
    'header_actions' => array(
        array(
            'text' => __('Contact Support', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'life-buoy'
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<!-- Search -->
<div class="card glass-card">
    <div class="card-body">
        <label class="sr-only" for="help-search"><?php esc_html_e('Search Help Center', 'retail-trade-scanner'); ?></label>
        <div class="input-with-icon">
            <?php echo rts_get_icon('search', ['width' => '18', 'height' => '18']); ?>
            <input id="help-search" class="form-input" type="search" placeholder="<?php esc_attr_e('Search articles, topics, or keywords…', 'retail-trade-scanner'); ?>">
        </div>
    </div>
</div>

<!-- Categories -->
<div class="grid grid-4 gap-lg mt-lg">
    <?php
    $categories = [
        ['icon' => 'user', 'title' => __('Account & Settings', 'retail-trade-scanner'), 'desc' => __('Profile, preferences, security', 'retail-trade-scanner'), 'slug' => 'account'],
        ['icon' => 'credit-card', 'title' => __('Billing', 'retail-trade-scanner'), 'desc' => __('Plans, invoices, refunds', 'retail-trade-scanner'), 'slug' => 'billing'],
        ['icon' => 'cpu', 'title' => __('Data & API', 'retail-trade-scanner'), 'desc' => __('API keys, rate limits, endpoints', 'retail-trade-scanner'), 'slug' => 'api'],
        ['icon' => 'alert-triangle', 'title' => __('Troubleshooting', 'retail-trade-scanner'), 'desc' => __('Common errors and fixes', 'retail-trade-scanner'), 'slug' => 'troubleshooting'],
    ];
    foreach ($categories as $cat) : ?>
        <a class="card glass-card cat-card" href="#<?php echo esc_attr($cat['slug']); ?>">
            <div class="card-body">
                <div class="cat-icon"><?php echo rts_get_icon($cat['icon'], ['width' => '28', 'height' => '28']); ?></div>
                <h3 class="m-0"><?php echo esc_html($cat['title']); ?></h3>
                <p class="text-muted m-0"><?php echo esc_html($cat['desc']); ?></p>
            </div>
        </a>
    <?php endforeach; ?>
</div>

<!-- Popular articles -->
<div class="mt-2xl">
    <div class="card glass-card">
        <div class="card-header">
            <h3 class="card-title m-0"><?php esc_html_e('Popular Articles', 'retail-trade-scanner'); ?></h3>
            <a class="btn btn-outline btn-sm" href="<?php echo esc_url(home_url('/contact/')); ?>"><?php esc_html_e('Still need help?', 'retail-trade-scanner'); ?></a>
        </div>
        <div class="card-body">
            <div class="grid grid-2 gap-xl">
                <ul class="article-list">
                    <li><a href="#"><?php esc_html_e('Getting started with the Stock Scanner', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="#"><?php esc_html_e('Creating and managing price alerts', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="#"><?php esc_html_e('Building your first watchlist', 'retail-trade-scanner'); ?></a></li>
                </ul>
                <ul class="article-list">
                    <li><a href="#"><?php esc_html_e('Understanding portfolio performance metrics', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="#"><?php esc_html_e('API authentication and rate limits', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="#"><?php esc_html_e('Troubleshooting data refresh issues', 'retail-trade-scanner'); ?></a></li>
                </ul>
            </div>
        </div>
    </div>
</div>

<style>
.input-with-icon { display:flex; gap: var(--spacing-sm); align-items:center; border:1px solid var(--gray-200); border-radius: var(--radius-xl); padding: var(--spacing-sm) var(--spacing-md); background: var(--surface-raised); }
.input-with-icon input { border:0; outline:0; width:100%; background: transparent; }
.cat-card { text-decoration: none; }
.cat-card .card-body { display:flex; flex-direction:column; gap: var(--spacing-sm); }
.cat-icon { color: var(--primary-600); }
.article-list { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap: var(--spacing-sm); }
.article-list a { color: var(--gray-700); text-decoration:none; }
.article-list a:hover { color: var(--primary-600); text-decoration: underline; }
</style>

<?php get_footer(); ?>