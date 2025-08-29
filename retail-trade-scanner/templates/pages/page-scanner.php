<?php
/**
 * Template Name: Scanner
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Scanner', 'retail-trade-scanner'),
  'page_description' => __('Run advanced filters to find actionable opportunities.', 'retail-trade-scanner'),
  'page_class'       => 'page-scanner',
);
?>
<section class="container mx-auto px-4 py-10">
  <div class="grid gap-6 lg:grid-cols-3">
    <div class="lg:col-span-2 grid gap-6">
      <?php
        get_template_part('template-parts/components/card', null, [
          'title' => __('Results', 'retail-trade-scanner'),
          'content' => function () {
            get_template_part('template-parts/components/table', null, [
              'headers' => [__('Symbol','retail-trade-scanner'), __('Name','retail-trade-scanner'), __('Price','retail-trade-scanner'), __('Change','retail-trade-scanner')],
              'rows' => [],
              'empty_text' => __('No results — adjust your filters and try again.', 'retail-trade-scanner'),
            ]);
          },
        ]);
      ?>
    </div>
    <aside class="grid gap-6">
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Filters', 'retail-trade-scanner'),
        'content' => __('Add filtering UI here (price range, volume, RSI, etc.).', 'retail-trade-scanner'),
      ]); ?>
    </aside>
  </div>
</section>
<?php
get_template_part('template-parts/layout/main-shell', null, $layout_args);
get_footer();