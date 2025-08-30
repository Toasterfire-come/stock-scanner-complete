<?php
/** Template Name: Dashboard (wired) */
if (!defined('ABSPATH')) { exit; }
get_header();
$layout_args = array(
  'page_title'       => __('Dashboard', 'retail-trade-scanner'),
  'page_description' => __('Live KPIs and trending market data', 'retail-trade-scanner'),
  'page_class'       => 'page-dashboard',
);
?>
<section class="container mx-auto px-4 py-10">
  <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3" id="rts-kpis">
    <div class="text-muted-foreground"><?php esc_html_e('Loading KPIs…','retail-trade-scanner'); ?></div>
  </div>
  <div class="grid gap-6 md:grid-cols-2 mt-8">
    <div>
      <h3 class="text-lg font-semibold mb-3"><?php esc_html_e('Top Gainers','retail-trade-scanner'); ?></h3>
      <div id="rts-trending-gainers" class="grid gap-2"></div>
    </div>
    <div>
      <h3 class="text-lg font-semibold mb-3"><?php esc_html_e('Most Active','retail-trade-scanner'); ?></h3>
      <div id="rts-trending-active" class="grid gap-2"></div>
    </div>
  </div>
</section>
<?php get_template_part('template-parts/layout/main-shell', null, $layout_args); get_footer(); ?>