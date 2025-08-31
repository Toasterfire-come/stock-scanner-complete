<?php
if (!defined('ABSPATH')) { exit; }

function rts_breadcrumbs() {
  if (is_front_page()) { return; }
  echo '<div class="container" style="padding:10px 0;color:#6b7280;font-size:14px;">';
  echo '<nav aria-label="Breadcrumb"><ol style="list-style:none;padding:0;margin:0;display:flex;gap:8px;align-items:center;">';
  echo '<li><a href="' . esc_url(home_url('/')) . '">Home</a></li>';
  echo '<li>›</li>';
  if (is_page()) {
    echo '<li><span>' . esc_html(get_the_title()) . '</span></li>';
  } elseif (is_single()) {
    echo '<li><span>' . esc_html(single_post_title('', false)) . '</span></li>';
  } else {
    echo '<li><span>' . esc_html(wp_get_document_title()) . '</span></li>';
  }
  echo '</ol></nav></div>';
}