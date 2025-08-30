<?php
/**
 * Template Name: Alerts (wired)
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
$layout_args = [
  'page_title' => __('Alerts', 'retail-trade-scanner'),
  'page_description' => __('Create and manage price alerts.', 'retail-trade-scanner'),
  'page_class' => 'page-alerts',
];
?>
<section class="container mx-auto px-4 py-10">
  <div class="grid gap-6 lg:grid-cols-3">
    <div class="lg:col-span-2 grid gap-4">
      <h3 class="text-lg font-semibold"><?php esc_html_e('Active Alerts', 'retail-trade-scanner'); ?></h3>
      <div id="rts-alerts-list" class="grid gap-2">
        <div class="text-muted-foreground"><?php esc_html_e('Loading alerts…', 'retail-trade-scanner'); ?></div>
      </div>
    </div>
    <aside class="grid gap-4">
      <div class="card p-3">
        <h4 class="font-semibold mb-2"><?php esc_html_e('Create Alert', 'retail-trade-scanner'); ?></h4>
        <div id="rts-alert-descriptor" class="text-sm text-muted-foreground mb-2"></div>
        <form id="rts-alert-form" class="grid gap-2">
          <input class="border rounded px-3 py-2" type="text" name="ticker" placeholder="<?php esc_attr_e('Ticker (e.g., AAPL)', 'retail-trade-scanner'); ?>" required />
          <input class="border rounded px-3 py-2" type="number" step="0.01" name="target_price" placeholder="<?php esc_attr_e('Target Price', 'retail-trade-scanner'); ?>" required />
          <select class="border rounded px-3 py-2" name="condition" required>
            <option value="above"><?php esc_html_e('Above', 'retail-trade-scanner'); ?></option>
            <option value="below"><?php esc_html_e('Below', 'retail-trade-scanner'); ?></option>
          </select>
          <input class="border rounded px-3 py-2" type="email" name="email" placeholder="<?php esc_attr_e('Your Email', 'retail-trade-scanner'); ?>" required />
          <button class="rounded-md bg-primary text-primary-foreground px-4 py-2" type="submit"><?php esc_html_e('Create', 'retail-trade-scanner'); ?></button>
        </form>
        <div id="rts-alert-msg" class="notice mt-2" aria-live="polite"></div>
        <details class="mt-3">
          <summary class="text-sm text-muted-foreground cursor-pointer"><?php esc_html_e('Show required fields and usage','retail-trade-scanner'); ?></summary>
          <div class="text-xs text-muted-foreground mt-2">
            <div><?php esc_html_e('POST /api/alerts/create/','retail-trade-scanner'); ?></div>
            <div><?php esc_html_e('ticker: string (required)','retail-trade-scanner'); ?></div>
            <div><?php esc_html_e('target_price: number (required)','retail-trade-scanner'); ?></div>
            <div><?php esc_html_e('condition: above|below (required)','retail-trade-scanner'); ?></div>
            <div><?php esc_html_e('email: string (required)','retail-trade-scanner'); ?></div>
          </div>
        </details>
      </div>
    </aside>
  </div>
</section>
<?php get_template_part('template-parts/layout/main-shell', null, $layout_args); get_footer(); ?>