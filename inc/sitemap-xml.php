<?php
if (!defined('ABSPATH')) { exit; }

// Add rewrite rules and query vars for XML sitemap and OG image
function rts_rewrite_rules() {
  add_rewrite_rule('^sitemap\.xml$', 'index.php?rts_sitemap=1', 'top');
  add_rewrite_rule('^rts-og\.png$', 'index.php?rts_og=1', 'top');
}
add_action('init', 'rts_rewrite_rules');

function rts_query_vars($vars) {
  $vars[] = 'rts_sitemap';
  $vars[] = 'rts_og';
  return $vars;
}
add_filter('query_vars', 'rts_query_vars');

// Output XML Sitemap
function rts_template_redirect() {
  if (get_query_var('rts_sitemap')) {
    header('Content-Type: application/xml; charset=' . get_bloginfo('charset'));
    echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
    echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">';
    // Pages
    $pages = get_pages(['sort_column' => 'post_modified']);
    foreach ($pages as $p) {
      $loc = get_permalink($p->ID);
      $mod = get_post_modified_time('c', true, $p->ID);
      echo "<url><loc>" . esc_url($loc) . "</loc><lastmod>" . esc_html($mod) . "</lastmod></url>";
    }
    // Posts
    $posts = get_posts(['numberposts' => -1, 'post_type' => 'post', 'post_status' => 'publish']);
    foreach ($posts as $po) {
      $loc = get_permalink($po->ID);
      $mod = get_post_modified_time('c', true, $po->ID);
      echo "<url><loc>" . esc_url($loc) . "</loc><lastmod>" . esc_html($mod) . "</lastmod></url>";
    }
    echo '</urlset>';
    exit;
  }

  // Dynamic OG image (PNG) generator using GD
  if (get_query_var('rts_og')) {
    // Title from current query context or site name
    $title = wp_get_document_title();
    if (!extension_loaded('gd')) { // Fallback: serve logo PNG
      header('Content-Type: image/svg+xml');
      readfile(get_template_directory() . '/assets/logo.svg');
      exit;
    }
    $w = 1200; $h = 630; $im = imagecreatetruecolor($w, $h);
    $bg = imagecolorallocate($im, 239, 131, 84); // Coral background
    imagefilledrectangle($im, 0, 0, $w, $h, $bg);
    $white = imagecolorallocate($im, 255, 255, 255);
    // Draw brand box
    $brand = imagecolorallocatealpha($im, 50, 55, 59, 30);
    imagefilledrectangle($im, 60, 60, 180, 180, $brand);
    // Title text (uses built-in font if TTF not present)
    if (function_exists('imagettftext')) {
      $font = __DIR__ . '/OpenSans-SemiBold.ttf';
      if (!file_exists($font)) { $font = __DIR__ . '/../../assets/OpenSans-SemiBold.ttf'; }
      $size = 48;
      $x = 60; $y = 300;
      imagettftext($im, $size, 0, $x, $y, $white, $font, $title);
    } else {
      imagestring($im, 5, 60, 280, $title, $white);
    }
    header('Content-Type: image/png');
    imagepng($im);
    imagedestroy($im);
    exit;
  }
}
add_action('template_redirect', 'rts_template_redirect');