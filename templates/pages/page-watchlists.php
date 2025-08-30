<?php
/**
 * Template Name: Watchlists (wired)
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
$layout_args = [
  'page_title' => __('Watchlists', 'retail-trade-scanner'),
  'page_description' => __('Create, manage and monitor your watchlists.', 'retail-trade-scanner'),
  'page_class' => 'page-watchlists',
];
?>
<section class="container mx-auto px-4 py-10">
  <div class="grid gap-6 lg:grid-cols-3">
    <div class="lg:col-span-2 grid gap-6">
      <h3 class="text-lg font-semibold"><?php esc_html_e('My Watchlist', 'retail-trade-scanner'); ?></h3>
      <div id="rts-watchlist" class="grid gap-2">
        <div class="text-muted-foreground"><?php esc_html_e('Loading watchlist…', 'retail-trade-scanner'); ?></div>
      </div>
    </div>
    <aside class="grid gap-6">
      <div class="card p-3">
        <h4 class="font-semibold mb-2"><?php esc_html_e('Add to Watchlist', 'retail-trade-scanner'); ?></h4>
        <form id="rts-watchlist-add" class="grid gap-2">
          <input class="border rounded px-3 py-2" type="text" name="symbol" placeholder="<?php esc_attr_e('Symbol (e.g., AAPL)', 'retail-trade-scanner'); ?>" required />
          <input class="border rounded px-3 py-2" type="text" name="watchlist_name" placeholder="<?php esc_attr_e('Watchlist name (default: My Watchlist)', 'retail-trade-scanner'); ?>" />
          <input class="border rounded px-3 py-2" type="text" name="notes" placeholder="<?php esc_attr_e('Notes (optional)', 'retail-trade-scanner'); ?>" />
          <input class="border rounded px-3 py-2" type="number" step="0.01" name="alert_price" placeholder="<?php esc_attr_e('Alert price (optional)', 'retail-trade-scanner'); ?>" />
          <button class="rounded-md bg-primary text-primary-foreground px-4 py-2" type="submit"><?php esc_html_e('Add', 'retail-trade-scanner'); ?></button>
        </form>
      </div>
    </aside>
  </div>
</section>
<?php get_template_part('template-parts/layout/main-shell', null, $layout_args); get_footer(); ?>