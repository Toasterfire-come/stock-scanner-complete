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

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();