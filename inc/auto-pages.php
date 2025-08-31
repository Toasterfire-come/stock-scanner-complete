<?php
/** Automatically create key pages on theme activation and assign templates. */
if (!defined('ABSPATH')) { exit; }

function rts_create_page($title, $slug, $template) {
  // Legacy single‑slug creator kept for backward compatibility
  $existing = get_page_by_path($slug);
  if ($existing) { update_post_meta($existing->ID, '_wp_page_template', $template); return $existing->ID; }
  $id = wp_insert_post([
    'post_title' => $title,
    'post_name' => $slug,
    'post_status' => 'publish',
    'post_type' => 'page',
  ]);
  if (!is_wp_error($id)) { update_post_meta($id, '_wp_page_template', $template); }
  return $id;
}

/**
 * Create or ensure a page exists using any of the provided slugs.
 * - If any slug already exists, apply the template to that page.
 * - Otherwise create the page using the first slug.
 */
function rts_create_page_multi($title, $slugs, $template) {
  foreach ((array)$slugs as $slug) {
    $existing = get_page_by_path($slug);
    if ($existing) {
      update_post_meta($existing->ID, '_wp_page_template', $template);
      return $existing->ID;
    }
  }
  $primary_slug = is_array($slugs) ? reset($slugs) : $slugs;
  $id = wp_insert_post([
    'post_title'   => $title,
    'post_name'    => $primary_slug,
    'post_status'  => 'publish',
    'post_type'    => 'page',
  ]);
  if (!is_wp_error($id)) { update_post_meta($id, '_wp_page_template', $template); }
  return $id;
}

function rts_on_activate() {
  // Multiple slugs are provided to ensure compatibility with pre-existing URLs
  // (e.g., legacy "/app-portfolio" vs nested "/app/portfolio" vs top-level "/portfolio").
  $map = [
    ['Home', ['home'], 'page-home.php'],
    ['Dashboard', ['dashboard'], 'page-dashboard.php'],
    ['Features', ['features'], 'page-features.php'],
    ['Pricing', ['pricing'], 'page-pricing.php'],
    ['Screeners', ['screeners','app/screeners','app-screeners'], 'page-screeners.php'],
    ['Alerts', ['alerts','price-alerts','app/alerts','app-alerts'], 'page-alerts.php'],
    ['Notifications', ['notifications','app/notifications','app-notifications'], 'page-notifications.php'],
    ['Portfolio', ['portfolio','app/portfolio','app-portfolio'], 'page-app-portfolio.php'],
    ['Watchlists', ['watchlists','app/watchlists','app-watchlists'], 'page-app-watchlists.php'],
    ['Status', ['status'], 'page-status.php'],
    ['Docs', ['docs'], 'page-docs.php'],
    ['Design System', ['design-system'], 'page-design-system.php'],
    ['About', ['about'], 'page-about.php'],
    ['Careers', ['careers'], 'page-careers.php'],
    ['Contact', ['contact'], 'page-contact.php'],
    ['Guides', ['guides'], 'page-guides.php'],
    ['Tutorials', ['tutorials'], 'page-tutorials.php'],
    ['Terms', ['legal/terms'], 'page-legal-terms.php'],
    ['Privacy', ['legal/privacy'], 'page-legal-privacy.php'],
    ['Cookies', ['legal/cookies'], 'page-legal-cookies.php'],
    ['Security', ['legal/security'], 'page-legal-security.php'],
    ['Data Coverage', ['data'], 'page-data.php'],
    ['Glossary', ['glossary'], 'page-glossary.php'],
    ['Changelog', ['changelog'], 'page-changelog.php'],
    ['Sitemap', ['sitemap'], 'page-sitemap.php'],
    ['Generic', ['generic'], 'page-generic.php'],
  ];

  $home_id = null;
  foreach ($map as $cfg) {
    $id = rts_create_page_multi($cfg[0], $cfg[1], $cfg[2]);
    if (in_array('home', (array)$cfg[1], true)) { $home_id = $id; }
  }
  if ($home_id) {
    update_option('show_on_front', 'page');
    update_option('page_on_front', $home_id);
  }
}
add_action('after_switch_theme', 'rts_on_activate');

/**
 * Ensure critical pages exist and the front page points to the Home template.
 * Runs once per version to avoid overhead.
 */
function rts_ensure_pages() {
  $version = '2';
  $stored = get_option('rts_pages_version');
  if ($stored === $version) { return; }

  // Reuse activation routine to (re)create missing pages and align templates
  rts_on_activate();
  update_option('rts_pages_version', $version);
}
add_action('init', 'rts_ensure_pages', 20);