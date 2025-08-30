<?php
/**
 * Template Name: Terms of Service
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Terms of Service', 'retail-trade-scanner'),
  'page_description' => __('Please review our terms and conditions.', 'retail-trade-scanner'),
  'page_class'       => 'page-terms-of-service',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();