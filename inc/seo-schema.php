<?php
if (!defined('ABSPATH')) { exit; }

function rts_schema_org() {
  $site_name = get_bloginfo('name');
  $site_desc = get_bloginfo('description');
  $site_url  = home_url('/');
  $logo      = get_site_icon_url() ?: get_template_directory_uri() . '/assets/logo.png';

  $schemas = [];

  // WebSite with SearchAction
  $schemas[] = [
    '@context' => 'https://schema.org',
    '@type' => 'WebSite',
    'name' => $site_name,
    'url'  => $site_url,
    'description' => $site_desc,
    'potentialAction' => [
      '@type' => 'SearchAction',
      'target' => $site_url . '?s={search_term_string}',
      'query-input' => 'required name=search_term_string'
    ]
  ];

  // Organization
  $schemas[] = [
    '@context' => 'https://schema.org',
    '@type' => 'Organization',
    'name' => $site_name,
    'url'  => $site_url,
    'logo' => [ '@type' => 'ImageObject', 'url' => $logo ],
    'sameAs' => []
  ];

  // Breadcrumbs
  if (!is_front_page()) {
    $position = 1; $items = [];
    $items[] = [ '@type' => 'ListItem', 'position' => $position++, 'name' => 'Home', 'item' => $site_url ];
    if (is_page()) {
      $items[] = [ '@type' => 'ListItem', 'position' => $position++, 'name' => get_the_title(), 'item' => get_permalink() ];
    } elseif (is_single()) {
      $items[] = [ '@type' => 'ListItem', 'position' => $position++, 'name' => single_post_title('', false), 'item' => get_permalink() ];
    }
    if ($items) {
      $schemas[] = [ '@context' => 'https://schema.org', '@type' => 'BreadcrumbList', 'itemListElement' => $items ];
    }
  }

  // Article schema for posts
  if (is_single()) {
    global $post; $author = get_the_author_meta('display_name', $post->post_author);
    $schemas[] = [
      '@context' => 'https://schema.org',
      '@type' => 'BlogPosting',
      'headline' => get_the_title(),
      'datePublished' => get_the_date('c'),
      'dateModified' => get_the_modified_date('c'),
      'author' => [ '@type' => 'Person', 'name' => $author ],
      'mainEntityOfPage' => get_permalink(),
      'publisher' => [ '@type' => 'Organization', 'name' => $site_name, 'logo' => [ '@type' => 'ImageObject', 'url' => $logo ] ],
    ];
  }

  echo "\n<script type=\"application/ld+json\">" . wp_json_encode($schemas) . "</script>\n";
}
add_action('wp_head', 'rts_schema_org', 5);