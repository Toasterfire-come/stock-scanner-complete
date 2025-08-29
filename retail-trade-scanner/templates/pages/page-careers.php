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

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();