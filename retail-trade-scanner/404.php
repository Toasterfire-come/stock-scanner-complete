<?php
/**
 * The template for displaying 404 pages (Not Found)
 *
 * @package RetailTradeScanner
 */

get_header();
?>

<div class="container">
    <div class="glass-card" style="margin: var(--spacing-4xl) auto; max-width: 760px;">
        <div class="card-body" style="text-align: center; padding: var(--spacing-3xl);">
            <div style="margin-bottom: var(--spacing-lg); color: var(--primary-600); display:inline-flex; align-items:center; justify-content:center; width:72px; height:72px; border-radius: var(--radius-full); background: var(--primary-100);">
                <?php echo rts_get_icon('search', ['width' => '36', 'height' => '36']); ?>
            </div>
            <h1 style="margin: 0 0 var(--spacing-sm);"><?php esc_html_e('Page not found', 'retail-trade-scanner'); ?></h1>
            <p class="text-muted" style="margin: 0 0 var(--spacing-xl);">
                <?php esc_html_e("We couldn't find the page you're looking for. Try searching or return to a known page.", 'retail-trade-scanner'); ?>
            </p>
            <div style="display:flex; gap: var(--spacing-sm); justify-content:center; flex-wrap: wrap;">
                <a class="btn btn-primary" href="<?php echo esc_url(home_url('/')); ?>">
                    <?php echo rts_get_icon('home', ['width' => '16', 'height' => '16']); ?>
                    <?php esc_html_e('Go Home', 'retail-trade-scanner'); ?>
                </a>
                <a class="btn btn-outline" href="<?php echo esc_url(home_url('/dashboard/')); ?>">
                    <?php echo rts_get_icon('dashboard', ['width' => '16', 'height' => '16']); ?>
                    <?php esc_html_e('Dashboard', 'retail-trade-scanner'); ?>
                </a>
                <a class="btn btn-outline" href="<?php echo esc_url(home_url('/scanner/')); ?>">
                    <?php echo rts_get_icon('scanner', ['width' => '16', 'height' => '16']); ?>
                    <?php esc_html_e('Stock Scanner', 'retail-trade-scanner'); ?>
                </a>
            </div>
            <div style="margin-top: var(--spacing-2xl); max-width:560px; margin-left:auto; margin-right:auto;">
                <?php get_search_form(); ?>
            </div>
        </div>
    </div>
</div>

<?php
get_footer();