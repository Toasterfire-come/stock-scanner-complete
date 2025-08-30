<?php
/** Template Name: News (wired) */
if (!defined('ABSPATH')) { exit; }
get_header();
$layout_args = ['page_title'=>__('News','retail-trade-scanner'),'page_description'=>__('Live market news with filters','retail-trade-scanner'),'page_class'=>'page-news'];
?>
<section class="container mx-auto px-4 py-10">
  <form id="rts-news-filters" class="grid gap-3 md:grid-cols-4">
    <input class="border rounded px-3 py-2" type="number" name="limit" placeholder="<?php esc_attr_e('Limit (<=50)','retail-trade-scanner'); ?>" />
    <select class="border rounded px-3 py-2" name="sentiment">
      <option value=""><?php esc_html_e('Any Sentiment','retail-trade-scanner'); ?></option>
      <option value="positive"><?php esc_html_e('Positive','retail-trade-scanner'); ?></option>
      <option value="negative"><?php esc_html_e('Negative','retail-trade-scanner'); ?></option>
      <option value="neutral"><?php esc_html_e('Neutral','retail-trade-scanner'); ?></option>
    </select>
    <input class="border rounded px-3 py-2" type="text" name="ticker" placeholder="<?php esc_attr_e('Ticker (optional)','retail-trade-scanner'); ?>" />
    <button class="rounded-md bg-primary text-primary-foreground px-4 py-2" type="submit"><?php esc_html_e('Apply','retail-trade-scanner'); ?></button>
  </form>
  <div id="rts-news" class="grid gap-3 mt-6">
    <div class="text-muted-foreground"><?php esc_html_e('Loading news…','retail-trade-scanner'); ?></div>
  </div>
</section>
<?php get_template_part('template-parts/layout/main-shell', null, $layout_args); get_footer(); ?>