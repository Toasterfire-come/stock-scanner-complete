<?php
/** Template Name: Scanner (wired) */
if (!defined('ABSPATH')) { exit; }
get_header();
$layout_args = array(
  'page_title'       => __('Scanner', 'retail-trade-scanner'),
  'page_description' => __('Filter and search stocks', 'retail-trade-scanner'),
  'page_class'       => 'page-scanner',
);
?>
<section class="container mx-auto px-4 py-10">
  <form id="rts-scanner-form" class="grid gap-3 md:grid-cols-6">
    <input class="border rounded px-3 py-2 md:col-span-2" id="rts-search" name="search" type="search" placeholder="<?php esc_attr_e('Search (ticker or company)','retail-trade-scanner'); ?>" />
    <div id="rts-autocomplete" class="md:col-span-2"></div>
    <select class="border rounded px-3 py-2" name="category">
      <option value="all"><?php esc_html_e('Any Category','retail-trade-scanner'); ?></option>
      <option value="gainers"><?php esc_html_e('Gainers','retail-trade-scanner'); ?></option>
      <option value="losers"><?php esc_html_e('Losers','retail-trade-scanner'); ?></option>
      <option value="high_volume"><?php esc_html_e('High Volume','retail-trade-scanner'); ?></option>
      <option value="large_cap"><?php esc_html_e('Large Cap','retail-trade-scanner'); ?></option>
      <option value="small_cap"><?php esc_html_e('Small Cap','retail-trade-scanner'); ?></option>
    </select>
    <select class="border rounded px-3 py-2" name="exchange">
      <option value="">
        <?php esc_html_e('Any Exchange','retail-trade-scanner'); ?>
      </option>
      <option value="NYSE">NYSE</option>
      <option value="NASDAQ">NASDAQ</option>
      <option value="AMEX">AMEX</option>
    </select>
    <input class="border rounded px-3 py-2" name="min_price" type="number" step="0.01" placeholder="<?php esc_attr_e('Min Price','retail-trade-scanner'); ?>" />
    <input class="border rounded px-3 py-2" name="max_price" type="number" step="0.01" placeholder="<?php esc_attr_e('Max Price','retail-trade-scanner'); ?>" />
    <input class="border rounded px-3 py-2" name="min_volume" type="number" placeholder="<?php esc_attr_e('Min Volume','retail-trade-scanner'); ?>" />
    <input class="border rounded px-3 py-2" name="min_market_cap" type="number" placeholder="<?php esc_attr_e('Min Market Cap','retail-trade-scanner'); ?>" />
    <input class="border rounded px-3 py-2" name="max_market_cap" type="number" placeholder="<?php esc_attr_e('Max Market Cap','retail-trade-scanner'); ?>" />
    <input class="border rounded px-3 py-2" name="min_pe" type="number" step="0.01" placeholder="<?php esc_attr_e('Min P/E','retail-trade-scanner'); ?>" />
    <input class="border rounded px-3 py-2" name="max_pe" type="number" step="0.01" placeholder="<?php esc_attr_e('Max P/E','retail-trade-scanner'); ?>" />
    <select class="border rounded px-3 py-2" name="sort_by">
      <option value="last_updated"><?php esc_html_e('Sort: Last Updated','retail-trade-scanner'); ?></option>
      <option value="price"><?php esc_html_e('Price','retail-trade-scanner'); ?></option>
      <option value="volume"><?php esc_html_e('Volume','retail-trade-scanner'); ?></option>
      <option value="market_cap"><?php esc_html_e('Market Cap','retail-trade-scanner'); ?></option>
      <option value="change_percent"><?php esc_html_e('Change %','retail-trade-scanner'); ?></option>
    </select>
    <select class="border rounded px-3 py-2" name="sort_order">
      <option value="desc"><?php esc_html_e('Desc','retail-trade-scanner'); ?></option>
      <option value="asc"><?php esc_html_e('Asc','retail-trade-scanner'); ?></option>
    </select>
    <input class="border rounded px-3 py-2" name="limit" type="number" min="1" max="1000" placeholder="<?php esc_attr_e('Limit (<=1000)','retail-trade-scanner'); ?>" />
    <button class="rounded-md bg-primary text-primary-foreground px-4 py-2 md:col-span-1" type="submit"><?php esc_html_e('Run','retail-trade-scanner'); ?></button>
  </form>
  <details class="mt-4">
    <summary class="text-sm text-muted-foreground cursor-pointer"><?php esc_html_e('Show allowed filters','retail-trade-scanner'); ?></summary>
    <div class="text-sm mt-2 text-muted-foreground">
      <div><?php esc_html_e('category: gainers|losers|high_volume|large_cap|small_cap|all','retail-trade-scanner'); ?></div>
      <div><?php esc_html_e('exchange: string (empty or "all" = all)','retail-trade-scanner'); ?></div>
      <div><?php esc_html_e('min_price, max_price: number','retail-trade-scanner'); ?></div>
      <div><?php esc_html_e('min_volume: int; min_market_cap, max_market_cap: int','retail-trade-scanner'); ?></div>
      <div><?php esc_html_e('min_pe, max_pe: number','retail-trade-scanner'); ?></div>
      <div><?php esc_html_e('sort_by: last_updated|price|volume|market_cap|change_percent','retail-trade-scanner'); ?></div>
      <div><?php esc_html_e('sort_order: asc|desc','retail-trade-scanner'); ?></div>
    </div>
  </details>
  <div id="rts-scanner-results" class="mt-6"></div>
</section>
<?php get_template_part('template-parts/layout/main-shell', null, $layout_args); get_footer(); ?>