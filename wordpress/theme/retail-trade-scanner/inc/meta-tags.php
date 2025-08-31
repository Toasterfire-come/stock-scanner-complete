<?php
if (!defined('ABSPATH')) { exit; }

function rts_canonical_url() {
  if (is_front_page()) { return home_url('/'); }
  return (is_singular() || is_page()) ? get_permalink() : home_url(add_query_arg(NULL, NULL));
}

function rts_meta_tags() {
  $title = wp_get_document_title();
  $desc  = get_bloginfo('description');
  if (is_singular()) {
    global $post; $excerpt = get_the_excerpt($post) ?: $desc; $desc = wp_strip_all_tags($excerpt);
  }
  $url   = rts_canonical_url();
  $site  = get_bloginfo('name');
  $logo  = get_site_icon_url() ?: get_template_directory_uri() . '/assets/logo.svg';

  echo "\n<link rel=\"canonical\" href=\"" . esc_url($url) . "\" />\n";
  echo "<meta name=\"description\" content=\"" . esc_attr($desc) . "\" />\n";
  // Open Graph
  echo "<meta property=\"og:type\" content=\"website\" />\n";
  echo "<meta property=\"og:title\" content=\"" . esc_attr($title) . "\" />\n";
  echo "<meta property=\"og:description\" content=\"" . esc_attr($desc) . "\" />\n";
  echo "<meta property=\"og:url\" content=\"" . esc_url($url) . "\" />\n";
  echo "<meta property=\"og:site_name\" content=\"" . esc_attr($site) . "\" />\n";
  echo "<meta property=\"og:image\" content=\"" . esc_url($logo) . "\" />\n";
  // Twitter
  echo "<meta name=\"twitter:card\" content=\"summary_large_image\" />\n";
  echo "<meta name=\"twitter:title\" content=\"" . esc_attr($title) . "\" />\n";
  echo "<meta name=\"twitter:description\" content=\"" . esc_attr($desc) . "\" />\n";
  echo "<meta name=\"twitter:image\" content=\"" . esc_url($logo) . "\" />\n";
}
add_action('wp_head', 'rts_meta_tags', 3);