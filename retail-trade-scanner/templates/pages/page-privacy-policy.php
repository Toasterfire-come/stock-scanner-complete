<?php
/**
 * Template Name: Privacy Policy
 * 
 * Privacy policy for Retail Trade Scanner
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('Privacy Policy', 'retail-trade-scanner'),
    'page_description' => __('How we collect, use, and protect your information', 'retail-trade-scanner'),
    'page_class' => 'legal-page privacy',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<div class="card glass-card">
    <div class="card-body legal-body">
        <p><em><?php echo esc_html(sprintf(__('Last updated: %s', 'retail-trade-scanner'), date('F j, Y'))); ?></em></p>
        <h3><?php esc_html_e('1. Information We Collect', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('We collect information you provide directly (e.g., account details), and technical data (e.g., device, usage).', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('2. How We Use Information', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('To operate the service, personalize features, provide support, and comply with legal obligations.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('3. Cookies & Tracking', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('We use cookies and similar technologies for authentication, analytics, and feature improvements.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('4. Data Sharing', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('We do not sell personal data. We may share data with processors under strict agreements.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('5. Security', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('We employ administrative, technical, and physical safeguards appropriate to the data we process.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('6. Your Rights', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('Depending on your location, you may have rights to access, correct, or delete your data.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('7. Contact', 'retail-trade-scanner'); ?></h3>
        <p><?php echo wp_kses_post(sprintf(__('Questions about privacy? <a href="%s">Contact us</a>.', 'retail-trade-scanner'), esc_url(home_url('/contact/')))); ?></p>
    </div>
</div>

<style>
.legal-body h3 { margin-top: var(--spacing-xl); }
</style>

<?php get_footer(); ?>