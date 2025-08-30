<?php
/**
 * Template Name: Privacy Policy
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Privacy Policy', 'retail-trade-scanner'),
  'page_description' => __('Our commitment to your privacy.', 'retail-trade-scanner'),
  'page_class'       => 'page-privacy-policy',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();