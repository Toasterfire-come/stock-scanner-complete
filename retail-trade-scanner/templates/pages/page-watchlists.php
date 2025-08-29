<?php
/**
 * Template Name: Watchlists
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Watchlists', 'retail-trade-scanner'),
  'page_description' => __('Create, manage and share watchlists.', 'retail-trade-scanner'),
  'page_class'       => 'page-watchlists',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();