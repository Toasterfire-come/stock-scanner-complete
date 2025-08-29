<?php
/**
 * Template Name: News
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('News', 'retail-trade-scanner'),
  'page_description' => __('Market news aggregation and reading pane.', 'retail-trade-scanner'),
  'page_class'       => 'page-news',
);
?>
<section class="container mx-auto px-4 py-10">
  <div class="grid gap-6 lg:grid-cols-3">
    <div class="lg:col-span-2 grid gap-4">
      <?php
        for ($i=0; $i<3; $i++) {
          get_template_part('template-parts/components/card', null, [
            'title' => __('Sample headline', 'retail-trade-scanner'),
            'subtitle' => __('Source · 2h ago', 'retail-trade-scanner'),
            'content' => __('This is a placeholder for a news story. Integrate your news feed to populate items here.', 'retail-trade-scanner'),
          ]);
        }
      ?>
    </div>
    <aside class="grid gap-6">
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Filters', 'retail-trade-scanner'),
        'content' => __('Industry, tickers, and impact filters can be added here as UI controls.', 'retail-trade-scanner'),
      ]); ?>
    </aside>
  </div>
</section>
<?php
get_template_part('template-parts/layout/main-shell', null, $layout_args);
get_footer();