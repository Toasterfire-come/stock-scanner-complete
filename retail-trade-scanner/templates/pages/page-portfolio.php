<?php
/**
 * Template Name: Portfolio
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Portfolio', 'retail-trade-scanner'),
  'page_description' => __('Track positions, performance and allocations.', 'retail-trade-scanner'),
  'page_class'       => 'page-portfolio',
);
?>
<section class="container mx-auto px-4 py-10">
  <div class="grid gap-6 lg:grid-cols-3">
    <div class="lg:col-span-2 grid gap-6">
      <?php
        get_template_part('template-parts/components/card', null, [
          'title' => __('Holdings', 'retail-trade-scanner'),
          'content' => function () {
            get_template_part('template-parts/components/table', null, [
              'headers' => [__('Symbol','retail-trade-scanner'), __('Qty','retail-trade-scanner'), __('Avg. Price','retail-trade-scanner'), __('P/L','retail-trade-scanner')],
              'rows' => [],
              'empty_text' => __('No positions yet.', 'retail-trade-scanner'),
            ]);
          },
        ]);
        get_template_part('template-parts/components/card', null, [
          'title' => __('Recent Activity', 'retail-trade-scanner'),
          'content' => function () {
            get_template_part('template-parts/components/table', null, [
              'headers' => [__('Date','retail-trade-scanner'), __('Action','retail-trade-scanner'), __('Symbol','retail-trade-scanner'), __('Qty','retail-trade-scanner')],
              'rows' => [],
              'empty_text' => __('No recent transactions.', 'retail-trade-scanner'),
            ]);
          },
        ]);
      ?>
    </div>
    <aside class="grid gap-6">
      <?php get_template_part('template-parts/components/chart-shell', null, [
        'title' => __('Allocation', 'retail-trade-scanner'),
        'description' => __('Portfolio allocation by sector.', 'retail-trade-scanner'),
      ]); ?>
    </aside>
  </div>
</section>
<?php
get_template_part('template-parts/layout/main-shell', null, $layout_args);
get_footer();