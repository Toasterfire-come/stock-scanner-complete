<?php
/**
 * Watchlist Management Functions
 *
 * @package StockScannerPro
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Get user watchlist with current market data
 */
function stock_scanner_get_user_watchlist_complete($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return array(
            'success' => false,
            'error' => 'User not authenticated',
        );
    }
    
    $watchlist_items = stock_scanner_get_watchlist_items($user_id);
    
    return array(
        'success' => true,
        'watchlist' => array(
            'user_id' => $user_id,
            'items' => $watchlist_items,
            'count' => count($watchlist_items),
            'categories' => stock_scanner_get_watchlist_categories($user_id),
            'last_updated' => current_time('mysql'),
        ),
    );
}

/**
 * Get watchlist items from database
 */
function stock_scanner_get_watchlist_items($user_id) {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'stock_scanner_watchlist';
    
    $items = $wpdb->get_results(
        $wpdb->prepare(
            "SELECT * FROM {$table_name} WHERE user_id = %d ORDER BY created_at DESC",
            $user_id
        ),
        ARRAY_A
    );
    
    if (!$items) {
        return array();
    }
    
    // Enrich items with current market data
    $enriched_items = array();
    
    foreach ($items as $item) {
        $stock_data = stock_scanner_get_stock_safe($item['ticker']);
        
        if ($stock_data) {
            $enriched_item = array_merge($item, array(
                'stock_data' => $stock_data,
                'current_price' => $stock_data['current_price'],
                'price_change' => $stock_data['price_change'],
                'price_change_percent' => $stock_data['price_change_percent'],
            ));
            
            // Check for price alerts
            $enriched_item['alerts'] = stock_scanner_get_watchlist_alerts($user_id, $item['ticker']);
            
            $enriched_items[] = $enriched_item;
        }
    }
    
    return $enriched_items;
}

/**
 * Add stock to watchlist
 */
function stock_scanner_add_to_watchlist($user_id, $ticker, $notes = '', $category = 'default') {
    global $wpdb;
    
    $ticker = strtoupper(sanitize_text_field($ticker));
    $notes = sanitize_textarea_field($notes);
    $category = sanitize_text_field($category);
    
    // Validate ticker
    $stock_data = stock_scanner_get_stock_safe($ticker);
    if (!$stock_data) {
        return array(
            'success' => false,
            'error' => 'Invalid ticker symbol',
        );
    }
    
    $table_name = $wpdb->prefix . 'stock_scanner_watchlist';
    
    // Check if already in watchlist
    $existing_item = $wpdb->get_var(
        $wpdb->prepare(
            "SELECT id FROM {$table_name} WHERE user_id = %d AND ticker = %s",
            $user_id,
            $ticker
        )
    );
    
    if ($existing_item) {
        return array(
            'success' => false,
            'error' => 'Stock is already in your watchlist',
        );
    }
    
    // Insert new watchlist item
    $result = $wpdb->insert(
        $table_name,
        array(
            'user_id' => $user_id,
            'ticker' => $ticker,
            'notes' => $notes,
            'category' => $category,
            'created_at' => current_time('mysql'),
            'updated_at' => current_time('mysql'),
        ),
        array('%d', '%s', '%s', '%s', '%s', '%s')
    );
    
    if ($result === false) {
        return array(
            'success' => false,
            'error' => 'Failed to add to watchlist',
        );
    }
    
    $item_id = $wpdb->insert_id;
    
    // Log activity
    stock_scanner_log_user_activity($user_id, 'watchlist_update', array(
        'action' => 'add_stock',
        'ticker' => $ticker,
        'category' => $category,
    ));
    
    return array(
        'success' => true,
        'item_id' => $item_id,
        'message' => "Successfully added {$ticker} to watchlist",
    );
}

/**
 * Remove stock from watchlist
 */
function stock_scanner_remove_from_watchlist($user_id, $item_id) {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'stock_scanner_watchlist';
    
    // Verify ownership
    $item = $wpdb->get_row(
        $wpdb->prepare(
            "SELECT * FROM {$table_name} WHERE id = %d AND user_id = %d",
            $item_id,
            $user_id
        ),
        ARRAY_A
    );
    
    if (!$item) {
        return array(
            'success' => false,
            'error' => 'Watchlist item not found or access denied',
        );
    }
    
    $result = $wpdb->delete(
        $table_name,
        array('id' => $item_id),
        array('%d')
    );
    
    if ($result === false) {
        return array(
            'success' => false,
            'error' => 'Failed to remove from watchlist',
        );
    }
    
    // Log activity
    stock_scanner_log_user_activity($user_id, 'watchlist_update', array(
        'action' => 'remove_stock',
        'ticker' => $item['ticker'],
    ));
    
    return array(
        'success' => true,
        'message' => "Successfully removed {$item['ticker']} from watchlist",
    );
}

/**
 * Update watchlist item
 */
function stock_scanner_update_watchlist_item($user_id, $item_id, $notes = null, $category = null) {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'stock_scanner_watchlist';
    
    // Verify ownership
    $item = $wpdb->get_row(
        $wpdb->prepare(
            "SELECT * FROM {$table_name} WHERE id = %d AND user_id = %d",
            $item_id,
            $user_id
        ),
        ARRAY_A
    );
    
    if (!$item) {
        return array(
            'success' => false,
            'error' => 'Watchlist item not found or access denied',
        );
    }
    
    $update_data = array('updated_at' => current_time('mysql'));
    $update_format = array('%s');
    
    if ($notes !== null) {
        $update_data['notes'] = sanitize_textarea_field($notes);
        $update_format[] = '%s';
    }
    
    if ($category !== null) {
        $update_data['category'] = sanitize_text_field($category);
        $update_format[] = '%s';
    }
    
    $result = $wpdb->update(
        $table_name,
        $update_data,
        array('id' => $item_id),
        $update_format,
        array('%d')
    );
    
    if ($result === false) {
        return array(
            'success' => false,
            'error' => 'Failed to update watchlist item',
        );
    }
    
    return array(
        'success' => true,
        'message' => 'Watchlist item updated successfully',
    );
}

/**
 * Get watchlist categories for user
 */
function stock_scanner_get_watchlist_categories($user_id) {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'stock_scanner_watchlist';
    
    $categories = $wpdb->get_col(
        $wpdb->prepare(
            "SELECT DISTINCT category FROM {$table_name} WHERE user_id = %d ORDER BY category",
            $user_id
        )
    );
    
    if (!$categories) {
        return array('default');
    }
    
    return $categories;
}

/**
 * Get watchlist alerts for ticker
 */
function stock_scanner_get_watchlist_alerts($user_id, $ticker) {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'stock_scanner_alerts';
    
    $alerts = $wpdb->get_results(
        $wpdb->prepare(
            "SELECT * FROM {$table_name} WHERE user_id = %d AND ticker = %s AND is_active = 1",
            $user_id,
            $ticker
        ),
        ARRAY_A
    );
    
    return $alerts ?: array();
}

/**
 * Create price alert for watchlist stock
 */
function stock_scanner_create_price_alert($user_id, $ticker, $target_price, $condition, $email = '', $notification_type = 'email') {
    global $wpdb;
    
    $ticker = strtoupper(sanitize_text_field($ticker));
    $target_price = floatval($target_price);
    $condition = sanitize_text_field($condition); // 'above', 'below', 'equal'
    $email = sanitize_email($email);
    $notification_type = sanitize_text_field($notification_type);
    
    if (!in_array($condition, array('above', 'below', 'equal'))) {
        return array(
            'success' => false,
            'error' => 'Invalid condition. Must be: above, below, or equal',
        );
    }
    
    if ($target_price <= 0) {
        return array(
            'success' => false,
            'error' => 'Target price must be greater than 0',
        );
    }
    
    // Validate ticker
    $stock_data = stock_scanner_get_stock_safe($ticker);
    if (!$stock_data) {
        return array(
            'success' => false,
            'error' => 'Invalid ticker symbol',
        );
    }
    
    $table_name = $wpdb->prefix . 'stock_scanner_alerts';
    
    // Insert new alert
    $result = $wpdb->insert(
        $table_name,
        array(
            'user_id' => $user_id,
            'ticker' => $ticker,
            'target_price' => $target_price,
            'condition' => $condition,
            'notification_email' => $email,
            'notification_type' => $notification_type,
            'is_active' => 1,
            'created_at' => current_time('mysql'),
            'updated_at' => current_time('mysql'),
        ),
        array('%d', '%s', '%f', '%s', '%s', '%s', '%d', '%s', '%s')
    );
    
    if ($result === false) {
        return array(
            'success' => false,
            'error' => 'Failed to create price alert',
        );
    }
    
    $alert_id = $wpdb->insert_id;
    
    // Log activity
    stock_scanner_log_user_activity($user_id, 'alert_created', array(
        'ticker' => $ticker,
        'target_price' => $target_price,
        'condition' => $condition,
    ));
    
    return array(
        'success' => true,
        'alert_id' => $alert_id,
        'message' => "Price alert created for {$ticker} when price goes {$condition} \$" . number_format($target_price, 2),
    );
}

/**
 * Check and trigger price alerts
 */
function stock_scanner_check_price_alerts() {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'stock_scanner_alerts';
    
    // Get all active alerts
    $alerts = $wpdb->get_results(
        "SELECT * FROM {$table_name} WHERE is_active = 1",
        ARRAY_A
    );
    
    if (!$alerts) {
        return;
    }
    
    foreach ($alerts as $alert) {
        $stock_data = stock_scanner_get_stock_safe($alert['ticker']);
        
        if (!$stock_data) {
            continue;
        }
        
        $current_price = $stock_data['current_price'];
        $target_price = floatval($alert['target_price']);
        $condition = $alert['condition'];
        $triggered = false;
        
        switch ($condition) {
            case 'above':
                $triggered = $current_price > $target_price;
                break;
            case 'below':
                $triggered = $current_price < $target_price;
                break;
            case 'equal':
                $triggered = abs($current_price - $target_price) < 0.01; // Within 1 cent
                break;
        }
        
        if ($triggered) {
            stock_scanner_trigger_price_alert($alert, $current_price);
        }
    }
}

/**
 * Trigger price alert notification
 */
function stock_scanner_trigger_price_alert($alert, $current_price) {
    global $wpdb;
    
    $ticker = $alert['ticker'];
    $target_price = $alert['target_price'];
    $condition = $alert['condition'];
    $user_id = $alert['user_id'];
    
    // Deactivate the alert
    $wpdb->update(
        $wpdb->prefix . 'stock_scanner_alerts',
        array(
            'is_active' => 0,
            'triggered_at' => current_time('mysql'),
            'triggered_price' => $current_price,
        ),
        array('id' => $alert['id']),
        array('%d', '%s', '%f'),
        array('%d')
    );
    
    // Send notification
    $message = "Price Alert Triggered: {$ticker} is now \$" . number_format($current_price, 2) . 
               " (target was {$condition} \$" . number_format($target_price, 2) . ")";
    
    if (!empty($alert['notification_email'])) {
        stock_scanner_send_alert_email($alert['notification_email'], $ticker, $message);
    }
    
    // Log activity
    stock_scanner_log_user_activity($user_id, 'alert_triggered', array(
        'ticker' => $ticker,
        'target_price' => $target_price,
        'current_price' => $current_price,
        'condition' => $condition,
    ));
}

/**
 * Send alert email
 */
function stock_scanner_send_alert_email($email, $ticker, $message) {
    $subject = "Stock Alert: {$ticker}";
    $body = $message . "\n\nThis is an automated alert from " . get_bloginfo('name');
    
    wp_mail($email, $subject, $body);
}

/**
 * Create watchlist database table
 */
function stock_scanner_create_watchlist_table() {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'stock_scanner_watchlist';
    
    $charset_collate = $wpdb->get_charset_collate();
    
    $sql = "CREATE TABLE $table_name (
        id mediumint(9) NOT NULL AUTO_INCREMENT,
        user_id bigint(20) NOT NULL,
        ticker varchar(10) NOT NULL,
        notes text,
        category varchar(50) DEFAULT 'default',
        created_at datetime DEFAULT CURRENT_TIMESTAMP,
        updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        KEY user_id (user_id),
        KEY ticker (ticker),
        KEY category (category),
        UNIQUE KEY user_ticker (user_id, ticker)
    ) $charset_collate;";
    
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);
}

/**
 * Create alerts database table
 */
function stock_scanner_create_alerts_table() {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'stock_scanner_alerts';
    
    $charset_collate = $wpdb->get_charset_collate();
    
    $sql = "CREATE TABLE $table_name (
        id mediumint(9) NOT NULL AUTO_INCREMENT,
        user_id bigint(20) NOT NULL,
        ticker varchar(10) NOT NULL,
        target_price decimal(15,4) NOT NULL,
        condition varchar(10) NOT NULL,
        notification_email varchar(255),
        notification_type varchar(20) DEFAULT 'email',
        is_active tinyint(1) DEFAULT 1,
        triggered_at datetime NULL,
        triggered_price decimal(15,4) NULL,
        created_at datetime DEFAULT CURRENT_TIMESTAMP,
        updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        KEY user_id (user_id),
        KEY ticker (ticker),
        KEY is_active (is_active)
    ) $charset_collate;";
    
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);
}

/**
 * Export watchlist to CSV
 */
function stock_scanner_export_watchlist_csv($user_id) {
    $items = stock_scanner_get_watchlist_items($user_id);
    
    if (empty($items)) {
        return array(
            'success' => false,
            'error' => 'No watchlist items found',
        );
    }
    
    $csv_data = array();
    $csv_data[] = array(
        'Ticker',
        'Company Name',
        'Current Price',
        'Price Change',
        'Price Change %',
        'Category',
        'Notes',
        'Added Date',
    );
    
    foreach ($items as $item) {
        $csv_data[] = array(
            $item['ticker'],
            $item['stock_data']['company_name'] ?? $item['ticker'],
            $item['current_price'],
            $item['price_change'],
            $item['price_change_percent'],
            $item['category'],
            $item['notes'],
            $item['created_at'],
        );
    }
    
    // Generate CSV content
    $output = '';
    foreach ($csv_data as $row) {
        $output .= implode(',', array_map(function($field) {
            return '"' . str_replace('"', '""', $field) . '"';
        }, $row)) . "\n";
    }
    
    return array(
        'success' => true,
        'csv_content' => $output,
        'filename' => 'watchlist_' . date('Y-m-d_H-i-s') . '.csv',
    );
}