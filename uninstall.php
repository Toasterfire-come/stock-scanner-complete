<?php
// If uninstall not called from WordPress, then exit
if (!defined('WP_UNINSTALL_PLUGIN')) {
	exit;
}

// Delete plugin options
$option_keys = array(
	'stock_scanner_api_url',
	'stock_scanner_api_secret',
	'paypal_mode',
	'paypal_client_id',
	'paypal_client_secret',
	'paypal_webhook_url',
	'paypal_webhook_id',
	'paypal_return_url',
	'paypal_cancel_url',
	'stock_scanner_dashboard_page_id'
);

foreach ($option_keys as $key) {
	delete_option($key);
}

// Optionally remove logs directory
$upload_dir = wp_upload_dir();
$log_dir = trailingslashit($upload_dir['basedir']) . 'stock-scanner-logs/';
if (is_dir($log_dir)) {
	foreach (glob($log_dir . '*') as $file) {
		@unlink($file);
	}
	@rmdir($log_dir);
}