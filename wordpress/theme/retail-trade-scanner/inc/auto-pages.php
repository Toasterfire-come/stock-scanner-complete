<?php
/** Automatically create key pages on theme activation and assign templates. */
if (!defined('ABSPATH')) { exit; }

function rts_create_page($title, $slug, $template) {
  $existing = get_page_by_path($slug);
  if ($existing) { return $existing->ID; }
  $id = wp_insert_post([
    'post_title' => $title,
    'post_name' => $slug,
    'post_status' => 'publish',
    'post_type' => 'page',
  ]);
  if (!is_wp_error($id)) { update_post_meta($id, '_wp_page_template', $template); }
  return $id;
}

function rts_on_activate() {
  $map = [
    ['Home','home','page-home.php'],
    ['Features','features','page-features.php'],
    ['Pricing','pricing','page-pricing.php'],
    ['Screeners','app/screeners','page-screeners.php'],
    ['Alerts','app/alerts','page-alerts.php'],
    ['Notifications','app/notifications','page-notifications.php'],
    ['Portfolio','app/portfolio','page-app-portfolio.php'],
    ['Watchlists','app/watchlists','page-app-watchlists.php'],
    ['Status','status','page-status.php'],
    ['Docs','docs','page-docs.php'],
    ['About','about','page-about.php'],
    ['Careers','careers','page-careers.php'],
    ['Contact','contact','page-contact.php'],
    ['Guides','guides','page-guides.php'],
    ['Tutorials','tutorials','page-tutorials.php'],
    ['Terms','legal/terms','page-legal-terms.php'],
    ['Privacy','legal/privacy','page-legal-privacy.php'],
    ['Cookies','legal/cookies','page-legal-cookies.php'],
    ['Security','legal/security','page-legal-security.php'],
    ['Generic','generic','page-generic.php'],
  ];

  $home_id = null;
  foreach ($map as $cfg) {
    $id = rts_create_page($cfg[0], $cfg[1], $cfg[2]);
    if ($cfg[1] === 'home') { $home_id = $id; }
  }
  if ($home_id) {
    update_option('show_on_front', 'page');
    update_option('page_on_front', $home_id);
  }
}
add_action('after_switch_theme', 'rts_on_activate');