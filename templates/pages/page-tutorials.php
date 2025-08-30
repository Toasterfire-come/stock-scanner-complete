<?php
/**
 * Template Name: Tutorials
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Tutorials', 'retail-trade-scanner'),
  'page_description' => __('Guided walkthroughs and how-tos.', 'retail-trade-scanner'),
  'page_class'       => 'page-tutorials',
);
?>
<section class="container mx-auto px-4 py-10 grid gap-6 lg:grid-cols-3">
  <div class="lg:col-span-2 grid gap-6">
    <?php for ($i=0; $i<3; $i++) { get_template_part('template-parts/components/card', null, [
      'title' => __('Getting Started', 'retail-trade-scanner'),
      'content' => __('Walkthrough content placeholder.', 'retail-trade-scanner'),
    ]);} ?>
  </div>
  <aside class="grid gap-6">
    <?php get_template_part('template-parts/components/card', null, [
      'title' => __('Resources', 'retail-trade-scanner'),
      'content' => __('Links to docs, videos, and examples.', 'retail-trade-scanner'),
    ]); ?>
  </aside>
</section>
<?php
get_template_part('template-parts/layout/main-shell', null, $layout_args);
get_footer();