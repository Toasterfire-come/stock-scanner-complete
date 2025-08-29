<?php
/**
 * Template Name: Terms of Service
 * 
 * Terms of Service for Retail Trade Scanner
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('Terms of Service', 'retail-trade-scanner'),
    'page_description' => __('The rules and conditions for using our services', 'retail-trade-scanner'),
    'page_class' => 'legal-page terms',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<div class="card glass-card">
    <div class="card-body legal-body">
        <p><em><?php echo esc_html(sprintf(__('Last updated: %s', 'retail-trade-scanner'), date('F j, Y'))); ?></em></p>
        <h3><?php esc_html_e('1. Acceptance of Terms', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('By accessing or using Retail Trade Scanner, you agree to be bound by these terms.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('2. Use of the Service', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('You agree to use the service in compliance with applicable laws and not to misuse the platform.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('3. Accounts', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('You are responsible for safeguarding your account credentials and for all activities under your account.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('4. Subscription & Billing', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('Paid features may require a subscription. Fees are billed in advance and non-refundable unless stated otherwise.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('5. Disclaimers', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('The platform is provided "as is" without warranties. Not financial advice.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('6. Limitation of Liability', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('We are not liable for indirect, incidental, or consequential damages associated with your use of the platform.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('7. Changes to Terms', 'retail-trade-scanner'); ?></h3>
        <p><?php esc_html_e('We may update these terms from time to time. Continued use constitutes acceptance of changes.', 'retail-trade-scanner'); ?></p>
        <h3><?php esc_html_e('8. Contact', 'retail-trade-scanner'); ?></h3>
        <p><?php echo wp_kses_post(sprintf(__('Questions about these terms? <a href="%s">Contact us</a>.', 'retail-trade-scanner'), esc_url(home_url('/contact/')))); ?></p>
    </div>
</div>

<style>
.legal-body h3 { margin-top: var(--spacing-xl); }
</style>

<?php get_template_part('template-parts/layout/main-shell-end'); ?>

<?php get_footer(); ?>