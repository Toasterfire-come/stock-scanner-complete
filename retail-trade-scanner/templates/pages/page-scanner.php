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
    <input class="border rounded px-3 py-2" name="min_price" type="number" step="0.01" placeholder="<?php esc_attr_e('Min Price','retail-trade-scanner'); ?>" />
    <input class="border rounded px-3 py-2" name="max_price" type="number" step="0.01" placeholder="<?php esc_attr_e('Max Price','retail-trade-scanner'); ?>" />
    <input class="border rounded px-3 py-2" name="min_volume" type="number" placeholder="<?php esc_attr_e('Min Volume','retail-trade-scanner'); ?>" />
    <select class="border rounded px-3 py-2" name="sort_by">
      <option value="last_updated"><?php esc_html_e('Sort: Last Updated','retail-trade-scanner'); ?></option>
      <option value="price"><?php esc_html_e('Price','retail-trade-scanner'); ?></option>
      <option value="volume"><?php esc_html_e('Volume','retail-trade-scanner'); ?></option>
      <option value="change_percent"><?php esc_html_e('Change %','retail-trade-scanner'); ?></option>
    </select>
    <select class="border rounded px-3 py-2" name="sort_order">
      <option value="desc"><?php esc_html_e('Desc','retail-trade-scanner'); ?></option>
      <option value="asc"><?php esc_html_e('Asc','retail-trade-scanner'); ?></option>
    </select>
    <button class="rounded-md bg-primary text-primary-foreground px-4 py-2 md:col-span-1" type="submit"><?php esc_html_e('Run','retail-trade-scanner'); ?></button>
  </form>
  <div id="rts-scanner-results" class="mt-6"></div>
</section>
<?php get_template_part('template-parts/layout/main-shell', null, $layout_args); get_footer(); ?>