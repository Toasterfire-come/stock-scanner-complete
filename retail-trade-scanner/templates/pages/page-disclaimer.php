<?php
/**
 * Template Name: Disclaimer
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Disclaimer', 'retail-trade-scanner'),
  'page_description' => __('Important legal and financial disclaimers.', 'retail-trade-scanner'),
  'page_class'       => 'page-disclaimer',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();