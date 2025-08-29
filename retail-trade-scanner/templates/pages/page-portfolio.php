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

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();