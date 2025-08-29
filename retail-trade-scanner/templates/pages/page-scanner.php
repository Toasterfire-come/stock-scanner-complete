<?php
/**
 * Template Name: Scanner
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Scanner', 'retail-trade-scanner'),
  'page_description' => __('Run advanced filters to find actionable opportunities.', 'retail-trade-scanner'),
  'page_class'       => 'page-scanner',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();