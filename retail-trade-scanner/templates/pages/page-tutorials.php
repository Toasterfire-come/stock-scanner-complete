<?php
/**
 * Template Name: Tutorials
 * 
 * Tutorials index with curated learning paths and featured guides
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('Tutorials', 'retail-trade-scanner'),
    'page_description' => __('Step-by-step guides to master scanning, alerts, and analysis', 'retail-trade-scanner'),
    'page_class' => 'tutorials-page',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<!-- Learning paths -->
<div class="grid grid-3 gap-xl">
    <?php
    $tracks = [
        ['title' => __('Getting Started', 'retail-trade-scanner'), 'desc' => __('Create your account, set preferences, and explore the dashboard.', 'retail-trade-scanner'), 'icon' => 'compass'],
        ['title' => __('Scanning Mastery', 'retail-trade-scanner'), 'desc' => __('Use filters, presets, and charts to find opportunities.', 'retail-trade-scanner'), 'icon' => 'search'],
        ['title' => __('Alerts & Automation', 'retail-trade-scanner'), 'desc' => __('Create intelligent alerts and automate monitoring.', 'retail-trade-scanner'), 'icon' => 'bell'],
    ];
    foreach ($tracks as $t) : ?>
        <a href="#" class="card glass-card tutorial-track">
            <div class="card-body">
                <div class="track-icon"><?php echo rts_get_icon($t['icon'], ['width' => '28', 'height' => '28']); ?></div>
                <h3 class="m-0"><?php echo esc_html($t['title']); ?></h3>
                <p class="text-muted m-0"><?php echo esc_html($t['desc']); ?></p>
            </div>
        </a>
    <?php endforeach; ?>
</div>

<!-- Featured tutorials -->
<div class="mt-2xl grid grid-3 gap-xl">
    <?php
    $items = [
        ['title' => __('Build a Watchlist in 5 Minutes', 'retail-trade-scanner'), 'time' => '5 min', 'icon' => 'bookmark'],
        ['title' => __('Set Up Your First Alert', 'retail-trade-scanner'), 'time' => '7 min', 'icon' => 'bell'],
        ['title' => __('Using the Scanner Like a Pro', 'retail-trade-scanner'), 'time' => '10 min', 'icon' => 'search'],
    ];
    foreach ($items as $it) : ?>
        <a href="#" class="card glass-card tutorial-card">
            <div class="card-body">
                <div class="track-icon"><?php echo rts_get_icon($it['icon'], ['width' => '24', 'height' => '24']); ?></div>
                <h4 class="m-0"><?php echo esc_html($it['title']); ?></h4>
                <p class="text-sm text-muted m-0"><?php echo esc_html($it['time']); ?></p>
            </div>
        </a>
    <?php endforeach; ?>
</div>

<style>
.tutorial-track, .tutorial-card { text-decoration:none; }
.track-icon { color: var(--primary-600); margin-bottom: var(--spacing-sm); }
</style>

<?php get_template_part('template-parts/layout/main-shell-end'); ?>

<?php get_footer(); ?>