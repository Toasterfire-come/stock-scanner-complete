<?php
/**
 * Stock Scanner Theme Functions (with admin-configurable idle policy + session policy notes)
 */
if (!defined('ABSPATH')) { exit; }

/* ... existing code above retained ... */

/* ---------------- Session Policy helpers ---------------- */
function stock_scanner_get_idle_settings() {
    $enabled = (int)get_option('ssc_idle_enabled', 1);
    $hours   = (int)get_option('ssc_idle_hours', 12);
    if ($hours < 1) $hours = 12;
    return array($enabled, $hours);
}

function stock_scanner_session_policy_text() {
    list($enabled, $hours) = stock_scanner_get_idle_settings();
    if ($enabled) {
        return sprintf(
            'For your security, you will be signed out automatically after %d hour%s of inactivity. You will receive a 2-minute warning to stay signed in.',
            $hours,
            $hours === 1 ? '' : 's'
        );
    } else {
        return 'Auto-logout after inactivity is currently disabled on this site.';
    }
}

function stock_scanner_session_policy_shortcode() { 
    return '<p class="description">' . esc_html(stock_scanner_session_policy_text()) . '</p>'; 
}
add_shortcode('session_policy_note', 'stock_scanner_session_policy_shortcode');

/* Show policy note on WP user profile (admin screens) */
function stock_scanner_session_policy_profile_note($user) {
    if (!current_user_can('read', $user->ID)) return;
    echo '<h2>Session Policy</h2><p>' . esc_html(stock_scanner_session_policy_text()) . '</p>';
}
add_action('show_user_profile', 'stock_scanner_session_policy_profile_note');
add_action('edit_user_profile', 'stock_scanner_session_policy_profile_note');

/* ... rest of existing code below retained ... */