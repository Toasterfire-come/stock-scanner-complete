<?php
/**
 * Template Name: Help
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Help', 'retail-trade-scanner'),
  'page_description' => __('Find answers and get support.', 'retail-trade-scanner'),
  'page_class'       => 'page-help',
);
?>
<section class="container mx-auto px-4 py-10 grid gap-6 lg:grid-cols-3">
  <div class="lg:col-span-2 grid gap-6">
    <?php get_template_part('template-parts/components/card', null, [
      'title' => __('FAQs', 'retail-trade-scanner'),
      'content' => __('Add common questions and answers here.', 'retail-trade-scanner'),
    ]); ?>
  </div>
  <aside class="grid gap-6">
    <?php get_template_part('template-parts/components/card', null, [
      'title' => __('Contact Support', 'retail-trade-scanner'),
      'content' => __('Email support@example.com for help.', 'retail-trade-scanner'),
    ]); ?>
  </aside>
</section>
<?php
get_template_part('template-parts/layout/main-shell', null, $layout_args);
get_footer();