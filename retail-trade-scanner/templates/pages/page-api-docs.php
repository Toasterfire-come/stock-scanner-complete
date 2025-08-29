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

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();