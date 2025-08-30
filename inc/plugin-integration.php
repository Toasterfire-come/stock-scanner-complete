<?php
/**
 * Plugin Integration – PayPal Checkout (TRIAL/REF50)
 */
if (!defined('ABSPATH')) { exit; }

// AJAX: Create PayPal order
function rts_create_paypal_order_ajax(){
  check_ajax_referer('paypal_nonce', 'nonce');
  $user_id = get_current_user_id();
  if (!$user_id) { wp_send_json_error('Not logged in'); }

  $plan = sanitize_text_field($_POST['plan'] ?? '');
  $billing_cycle = sanitize_text_field($_POST['billing_cycle'] ?? 'monthly');
  $promo_code = strtoupper(sanitize_text_field($_POST['promo_code'] ?? ''));
  $valid_plans = array('bronze','silver','gold');
  if (!in_array($plan, $valid_plans, true)) { wp_send_json_error('Invalid plan'); }
  $billing_cycle = 'monthly'; // enforce monthly for promos

  $prices = array('bronze'=>24.99, 'silver'=>39.99, 'gold'=>89.99);
  $base = floatval($prices[$plan]);
  $first = $base; $msg = ''; $promo = false;
  if ($promo_code === 'TRIAL'){ $first = 1.00; $promo=true; $msg='TRIAL applied: $1 for 7 days, then renews monthly at full price.'; }
  else if ($promo_code === 'REF50'){ $first = round($base*0.5, 2); $promo=true; $msg='REF50 applied: 50% off first month, then renews monthly at full price.'; }

  $order_id = 'ORD-'.wp_generate_uuid4();
  set_transient('rts_order_'.$order_id, array(
    'user_id'=>$user_id, 'plan'=>$plan, 'billing_cycle'=>$billing_cycle, 'promo_code'=>$promo_code,
    'base_amount'=>$base, 'first_charge'=>$first, 'created_at'=>time()
  ), 30 * MINUTE_IN_SECONDS);

  wp_send_json_success(array('order_id'=>$order_id,'amount'=>$first,'promo_applied'=>$promo,'message'=>$msg,'auto_renew'=>'monthly'));
}
add_action('wp_ajax_create_paypal_order','rts_create_paypal_order_ajax');

// AJAX: Capture PayPal order
function rts_capture_paypal_order_ajax(){
  check_ajax_referer('paypal_nonce', 'nonce');
  $user_id = get_current_user_id();
  if (!$user_id) { wp_send_json_error('Not logged in'); }
  $order_id = sanitize_text_field($_POST['order_id'] ?? '');
  if (!$order_id) { wp_send_json_error('Missing order id'); }
  $ctx = get_transient('rts_order_'.$order_id);
  if (!$ctx || intval($ctx['user_id']) !== intval($user_id)) { wp_send_json_error('Invalid or expired order'); }

  $plan = $ctx['plan'];
  $promo = strtoupper($ctx['promo_code'] ?? '');
  $billing_cycle = 'monthly';

  update_user_meta($user_id, 'membership_level', $plan);
  update_user_meta($user_id, 'membership_plan', $plan);
  update_user_meta($user_id, 'billing_cycle', $billing_cycle);

  // Optional: write to subscriptions table if present (best-effort)
  global $wpdb; $subs = $wpdb->prefix.'stock_scanner_subscriptions';
  $expires = ($promo==='TRIAL') ? date('Y-m-d H:i:s', strtotime('+7 days', current_time('timestamp'))) : date('Y-m-d H:i:s', strtotime('+30 days', current_time('timestamp')));
  $now = current_time('mysql');
  if ($wpdb->get_var($wpdb->prepare("SHOW TABLES LIKE %s", $wpdb->esc_like($subs)))){
    $existing = $wpdb->get_var($wpdb->prepare("SELECT id FROM $subs WHERE user_id=%d", $user_id));
    if ($existing){ $wpdb->update($subs, array('plan'=>$plan,'status'=>'active','expires_at'=>$expires,'updated_at'=>$now), array('id'=>$existing)); }
    else { $wpdb->insert($subs, array('user_id'=>$user_id,'plan'=>$plan,'status'=>'active','started_at'=>$now,'expires_at'=>$expires,'created_at'=>$now,'updated_at'=>$now)); }
  }

  delete_transient('rts_order_'.$order_id);
  wp_send_json_success(array('order_id'=>$order_id,'orderID'=>$order_id,'activated_plan'=>$plan));
}
add_action('wp_ajax_capture_paypal_order','rts_capture_paypal_order_ajax');

