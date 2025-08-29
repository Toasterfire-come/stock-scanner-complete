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

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();