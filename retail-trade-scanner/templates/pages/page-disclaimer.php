<?php
/**
 * Template Name: Disclaimer
 * 
 * Disclaimer for Retail Trade Scanner
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('Disclaimer', 'retail-trade-scanner'),
    'page_description' => __('Important notes and risk disclosures', 'retail-trade-scanner'),
    'page_class' => 'legal-page disclaimer',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<div class="card glass-card">
    <div class="card-body legal-body">
        <p><em><?php echo esc_html(sprintf(__('Last updated: %s', 'retail-trade-scanner'), date('F j, Y'))); ?></em></p>
        <h3><?php esc_html_e('Not Financial Advice', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('Content provided by Retail Trade Scanner is for informational purposes only and should not be construed as financial advice.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('Market Risks', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('Trading involves substantial risk. Past performance is not indicative of future results.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('Data Sources', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('We rely on multiple third-party data providers and cannot guarantee accuracy or availability at all times.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('No Warranty', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('The platform is provided without warranties of any kind, express or implied.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('Contact', 'retail-trade-scanner'); ?></h3>
        <p><?php echo wp_kses_post(sprintf(__('Questions? <a href="%s">Contact us</a>.', 'retail-trade-scanner'), esc_url(home_url('/contact/')))); ?></p>
    </div>
</div>

<style>
.legal-body h3 { margin-top: var(--spacing-xl); }
</style>

<?php get_template_part('template-parts/layout/main-shell-end'); ?>

<?php get_footer(); ?>