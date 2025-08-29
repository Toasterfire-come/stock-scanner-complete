<?php
/**
 * Template Name: API Docs
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('API Documentation', 'retail-trade-scanner'),
  'page_description' => __('API endpoints and usage examples.', 'retail-trade-scanner'),
  'page_class'       => 'page-api-docs',
);
?>
<section class="container mx-auto px-4 py-10">
  <?php get_template_part('template-parts/components/card', null, [
    'title' => __('Authentication', 'retail-trade-scanner'),
    'content' => __('Use your API key to access authenticated endpoints. Replace placeholders with your credentials.', 'retail-trade-scanner'),
  ]); ?>
  <?php get_template_part('template-parts/components/card', null, [
    'title' => __('Example: List Symbols', 'retail-trade-scanner'),
    'content' => '<pre class="mt-2 rounded bg-muted p-3 text-xs overflow-auto">GET /v1/symbols</pre>',
  ]); ?>
</section>
<?php
get_template_part('template-parts/layout/main-shell', null, $layout_args);
get_footer();