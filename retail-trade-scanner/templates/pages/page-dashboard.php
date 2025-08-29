<?php
/**
 * Template Name: Dashboard
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Dashboard', 'retail-trade-scanner'),
  'page_description' => __('Overview of your market and portfolio at a glance.', 'retail-trade-scanner'),
  'page_class'       => 'page-dashboard',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();