<?php
/**
 * Template Name: Watchlists
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Watchlists', 'retail-trade-scanner'),
  'page_description' => __('Create, manage and share watchlists.', 'retail-trade-scanner'),
  'page_class'       => 'page-watchlists',
);

?>
<section class="container mx-auto px-4 py-10">
  <div class="grid gap-6 lg:grid-cols-3">
    <div class="lg:col-span-2 grid gap-6">
      <?php
        get_template_part('template-parts/components/card', null, [
          'title' => __('My Watchlists', 'retail-trade-scanner'),
          'subtitle' => __('Quick access to your saved lists', 'retail-trade-scanner'),
          'content' => function () {
            get_template_part('template-parts/components/table', null, [
              'headers' => [__('Name','retail-trade-scanner'), __('Symbols','retail-trade-scanner'), __('Updated','retail-trade-scanner')],
              'rows' => [],
              'empty_text' => __('No watchlists yet. Create your first one from the Scanner page.', 'retail-trade-scanner'),
            ]);
          },
        ]);
      ?>
    </div>
    <aside class="grid gap-6">
      <?php get_template_part('template-parts/components/chart-shell', null, [
        'title' => __('Market Snapshot', 'retail-trade-scanner'),
        'description' => __('A quick view of current market mood.', 'retail-trade-scanner'),
      ]); ?>
    </aside>
  </div>
</section>
<?php

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();