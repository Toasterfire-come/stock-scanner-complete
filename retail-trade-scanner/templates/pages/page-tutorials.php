<?php
/**
 * Template Name: Tutorials
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Tutorials', 'retail-trade-scanner'),
  'page_description' => __('Guided walkthroughs and how-tos.', 'retail-trade-scanner'),
  'page_class'       => 'page-tutorials',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();