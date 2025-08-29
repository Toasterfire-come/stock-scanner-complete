<?php
/**
 * Template Name: Contact
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Contact', 'retail-trade-scanner'),
  'page_description' => __('Get in touch with our team.', 'retail-trade-scanner'),
  'page_class'       => 'page-contact',
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

get_footer();