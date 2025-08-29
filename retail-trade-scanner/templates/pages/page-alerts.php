<?php
/**
 * Template Name: Alerts
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Alerts', 'retail-trade-scanner'),
  'page_description' => __('Manage price, volume and indicator-based alerts.', 'retail-trade-scanner'),
  'page_class'       => 'page-alerts',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();