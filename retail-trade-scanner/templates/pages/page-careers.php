<?php
/**
 * Template Name: Careers
 * 
 * Careers page with company intro, benefits, and open roles
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('Careers', 'retail-trade-scanner'),
    'page_description' => __('Join us to build the future of trading intelligence', 'retail-trade-scanner'),
    'page_class' => 'careers-page',
    'header_actions' => array(
        array(
            'text' => __('View Open Roles', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'users'
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<!-- Benefits -->
<div class="grid grid-3 gap-xl">
    <?php
    $benefits = [
        ['icon' => 'heart', 'title' => __('Health & Wellness', 'retail-trade-scanner'), 'desc' => __('Comprehensive medical, dental, vision coverage.', 'retail-trade-scanner')],
        ['icon' => 'home', 'title' => __('Remote-first', 'retail-trade-scanner'), 'desc' => __('Flexible, fully-remote culture with home office stipend.', 'retail-trade-scanner')],
        ['icon' => 'zap', 'title' => __('Learning Budget', 'retail-trade-scanner'), 'desc' => __('Annual budget for courses, books, and conferences.', 'retail-trade-scanner')],
    ];
    foreach ($benefits as $b) : ?>
        <div class="card glass-card">
            <div class="card-body">
                <div class="benefit-icon"><?php echo rts_get_icon($b['icon'], ['width' => '28', 'height' => '28']); ?></div>
                <h3 class="m-0"><?php echo esc_html($b['title']); ?></h3>
                <p class="text-muted m-0"><?php echo esc_html($b['desc']); ?></p>
            </div>
        </div>
    <?php endforeach; ?>
</div>

<!-- Open Roles -->
<div class="mt-2xl card glass-card">
    <div class="card-header">
        <h3 class="card-title m-0"><?php esc_html_e('Open Roles', 'retail-trade-scanner'); ?></h3>
        <a class="btn btn-outline btn-sm" href="<?php echo esc_url(home_url('/contact/')); ?>"><?php esc_html_e('General Application', 'retail-trade-scanner'); ?></a>
    </div>
    <div class="card-body">
        <div class="role-list">
            <?php
            $roles = [
                ['title' => __('Senior Frontend Engineer', 'retail-trade-scanner'), 'type' => __('Full-time', 'retail-trade-scanner'), 'location' => __('Remote', 'retail-trade-scanner')],
                ['title' => __('Product Designer (UI/UX)', 'retail-trade-scanner'), 'type' => __('Full-time', 'retail-trade-scanner'), 'location' => __('Remote', 'retail-trade-scanner')],
                ['title' => __('Quant Researcher', 'retail-trade-scanner'), 'type' => __('Contract', 'retail-trade-scanner'), 'location' => __('Remote', 'retail-trade-scanner')],
            ];
            foreach ($roles as $r) : ?>
                <div class="role-item">
                    <div class="role-info">
                        <h4 class="m-0"><?php echo esc_html($r['title']); ?></h4>
                        <p class="text-sm text-muted m-0"><?php echo esc_html($r['type']); ?> • <?php echo esc_html($r['location']); ?></p>
                    </div>
                    <div class="role-actions">
                        <a href="<?php echo esc_url(home_url('/contact/')); ?>" class="btn btn-primary btn-sm"><?php esc_html_e('Apply', 'retail-trade-scanner'); ?></a>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
</div>

<style>
.role-list { display:flex; flex-direction:column; gap: var(--spacing-md); }
.role-item { display:flex; align-items:center; justify-content:space-between; padding: var(--spacing-md); border:1px solid var(--gray-200); border-radius: var(--radius-xl); background: var(--surface-raised); }
.benefit-icon { color: var(--primary-600); margin-bottom: var(--spacing-sm); }
[data-theme="dark"] .role-item { background: var(--gray-800); border-color: var(--gray-700); }
</style>

<?php get_template_part('template-parts/layout/main-shell-end'); ?>

<?php get_footer(); ?>