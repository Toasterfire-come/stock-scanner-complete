<?php
/**
 * Template Name: Alerts
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Alerts', 'retail-trade-scanner'),
  'page_description' => __('Manage price, volume and indicator-based alerts.', 'retail-trade-scanner'),
  'page_class'       => 'page-alerts',
);
?>
<section class="container mx-auto px-4 py-10">
  <div class="grid gap-6 lg:grid-cols-3">
    <div class="lg:col-span-2 grid gap-6">
      <?php
        get_template_part('template-parts/components/card', null, [
          'title' => __('Active Alerts', 'retail-trade-scanner'),
          'content' => function () {
            get_template_part('template-parts/components/table', null, [
              'headers' => [__('Name','retail-trade-scanner'), __('Type','retail-trade-scanner'), __('Condition','retail-trade-scanner'), __('Status','retail-trade-scanner')],
              'rows' => [],
              'empty_text' => __('No alerts configured yet.', 'retail-trade-scanner'),
            ]);
          },
        ]);
      ?>
    </div>
    <aside class="grid gap-6">
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Tips', 'retail-trade-scanner'),
        'content' => __('Create alerts based on price crossovers, volume spikes, or RSI thresholds to stay on top of opportunities.', 'retail-trade-scanner'),
      ]); ?>
    </aside>
  </div>
</section>
<?php
get_template_part('template-parts/layout/main-shell', null, $layout_args);
get_footer();