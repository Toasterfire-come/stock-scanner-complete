<?php
/**
 * Template Name: Careers
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Careers', 'retail-trade-scanner'),
  'page_description' => __('Join our team and build the future of retail trading.', 'retail-trade-scanner'),
  'page_class'       => 'page-careers',
);
?>
<section class="container mx-auto px-4 py-10 grid gap-6">
  <?php get_template_part('template-parts/components/card', null, [
    'title' => __('Open Roles', 'retail-trade-scanner'),
    'content' => __('No open roles at the moment. Check back soon!', 'retail-trade-scanner'),
  ]); ?>
</section>
<?php
get_template_part('template-parts/layout/main-shell', null, $layout_args);
get_footer();