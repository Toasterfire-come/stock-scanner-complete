<?php
/**
 * Theme Search Form
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
?>
<form role="search" method="get" class="search-form flex gap-2" action="<?php echo esc_url( home_url( '/' ) ); ?>">
  <label class="sr-only" for="search-field-theme"><?php esc_html_e('Search for:', 'retail-trade-scanner'); ?></label>
  <input id="search-field-theme" class="border rounded-md px-3 py-2" type="search" name="s" value="<?php echo esc_attr( get_search_query() ); ?>" placeholder="<?php esc_attr_e('Search…', 'retail-trade-scanner'); ?>" />
  <button class="rounded-md bg-primary text-primary-foreground px-4 py-2" type="submit"><?php esc_html_e('Search', 'retail-trade-scanner'); ?></button>
</form>

