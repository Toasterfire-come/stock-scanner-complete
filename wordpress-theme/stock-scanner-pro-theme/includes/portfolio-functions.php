<?php
/**
 * Portfolio Management Functions
 *
 * @package StockScannerPro
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Get user portfolio with complete data
 */
function stock_scanner_get_user_portfolio_complete($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return array(
            'success' => false,
            'error' => 'User not authenticated',
        );
    }
    
    // Get portfolio holdings from database
    $holdings = stock_scanner_get_portfolio_holdings($user_id);
    $portfolio_summary = stock_scanner_calculate_portfolio_summary($holdings);
    
    return array(
        'success' => true,
        'portfolio' => array(
            'user_id' => $user_id,
            'holdings' => $holdings,
            'summary' => $portfolio_summary,
            'performance' => stock_scanner_calculate_portfolio_performance($holdings),
            'allocation' => stock_scanner_calculate_portfolio_allocation($holdings),
            'last_updated' => current_time('mysql'),
        ),
    );
}

/**
 * Get portfolio holdings from database
 */
function stock_scanner_get_portfolio_holdings($user_id) {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'stock_scanner_portfolio';
    
    $holdings = $wpdb->get_results(
        $wpdb->prepare(
            "SELECT * FROM {$table_name} WHERE user_id = %d ORDER BY created_at DESC",
            $user_id
        ),
        ARRAY_A
    );
    
    if (!$holdings) {
        return array();
    }
    
    // Enrich holdings with current market data
    $enriched_holdings = array();
    
    foreach ($holdings as $holding) {
        $stock_data = stock_scanner_get_stock_safe($holding['ticker']);
        
        if ($stock_data) {
            $current_value = $stock_data['current_price'] * $holding['shares'];
            $total_cost = $holding['average_cost'] * $holding['shares'];
            $gain_loss = $current_value - $total_cost;
            $gain_loss_percent = $total_cost > 0 ? ($gain_loss / $total_cost) * 100 : 0;
            
            $enriched_holding = array_merge($holding, array(
                'current_price' => $stock_data['current_price'],
                'current_value' => $current_value,
                'total_cost' => $total_cost,
                'gain_loss' => $gain_loss,
                'gain_loss_percent' => $gain_loss_percent,
                'stock_data' => $stock_data,
            ));
            
            $enriched_holdings[] = $enriched_holding;
        }
    }
    
    return $enriched_holdings;
}

/**
 * Add stock to portfolio
 */
function stock_scanner_add_to_portfolio($user_id, $ticker, $shares, $cost_basis, $purchase_date = null) {
    global $wpdb;
    
    if (!$purchase_date) {
        $purchase_date = current_time('mysql');
    }
    
    $ticker = strtoupper(sanitize_text_field($ticker));
    $shares = floatval($shares);
    $cost_basis = floatval($cost_basis);
    
    if ($shares <= 0 || $cost_basis <= 0) {
        return array(
            'success' => false,
            'error' => 'Invalid shares or cost basis',
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
    
    $table_name = $wpdb->prefix . 'stock_scanner_portfolio';
    
    // Check if holding already exists
    $existing_holding = $wpdb->get_row(
        $wpdb->prepare(
            "SELECT * FROM {$table_name} WHERE user_id = %d AND ticker = %s",
            $user_id,
            $ticker
        ),
        ARRAY_A
    );
    
    if ($existing_holding) {
        // Update existing holding (average cost basis)
        $total_shares = $existing_holding['shares'] + $shares;
        $total_cost = ($existing_holding['shares'] * $existing_holding['average_cost']) + 
                      ($shares * $cost_basis);
        $new_average_cost = $total_cost / $total_shares;
        
        $result = $wpdb->update(
            $table_name,
            array(
                'shares' => $total_shares,
                'average_cost' => $new_average_cost,
                'updated_at' => current_time('mysql'),
            ),
            array('id' => $existing_holding['id']),
            array('%f', '%f', '%s'),
            array('%d')
        );
        
        $holding_id = $existing_holding['id'];
    } else {
        // Insert new holding
        $result = $wpdb->insert(
            $table_name,
            array(
                'user_id' => $user_id,
                'ticker' => $ticker,
                'shares' => $shares,
                'average_cost' => $cost_basis,
                'purchase_date' => $purchase_date,
                'created_at' => current_time('mysql'),
                'updated_at' => current_time('mysql'),
            ),
            array('%d', '%s', '%f', '%f', '%s', '%s', '%s')
        );
        
        $holding_id = $wpdb->insert_id;
    }
    
    if ($result === false) {
        return array(
            'success' => false,
            'error' => 'Failed to add to portfolio',
        );
    }
    
    // Log activity
    stock_scanner_log_user_activity($user_id, 'portfolio_update', array(
        'action' => 'add_stock',
        'ticker' => $ticker,
        'shares' => $shares,
        'cost_basis' => $cost_basis,
    ));
    
    return array(
        'success' => true,
        'holding_id' => $holding_id,
        'message' => "Successfully added {$shares} shares of {$ticker} to portfolio",
    );
}

/**
 * Remove stock from portfolio
 */
function stock_scanner_remove_from_portfolio($user_id, $holding_id) {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'stock_scanner_portfolio';
    
    // Verify ownership
    $holding = $wpdb->get_row(
        $wpdb->prepare(
            "SELECT * FROM {$table_name} WHERE id = %d AND user_id = %d",
            $holding_id,
            $user_id
        ),
        ARRAY_A
    );
    
    if (!$holding) {
        return array(
            'success' => false,
            'error' => 'Holding not found or access denied',
        );
    }
    
    $result = $wpdb->delete(
        $table_name,
        array('id' => $holding_id),
        array('%d')
    );
    
    if ($result === false) {
        return array(
            'success' => false,
            'error' => 'Failed to remove from portfolio',
        );
    }
    
    // Log activity
    stock_scanner_log_user_activity($user_id, 'portfolio_update', array(
        'action' => 'remove_stock',
        'ticker' => $holding['ticker'],
        'shares' => $holding['shares'],
    ));
    
    return array(
        'success' => true,
        'message' => "Successfully removed {$holding['ticker']} from portfolio",
    );
}

/**
 * Calculate portfolio summary
 */
function stock_scanner_calculate_portfolio_summary($holdings) {
    if (empty($holdings)) {
        return array(
            'total_value' => 0,
            'total_cost' => 0,
            'total_gain_loss' => 0,
            'total_gain_loss_percent' => 0,
            'holdings_count' => 0,
            'top_performer' => null,
            'worst_performer' => null,
        );
    }
    
    $total_value = 0;
    $total_cost = 0;
    $best_performer = null;
    $worst_performer = null;
    
    foreach ($holdings as $holding) {
        $total_value += $holding['current_value'];
        $total_cost += $holding['total_cost'];
        
        if ($best_performer === null || $holding['gain_loss_percent'] > $best_performer['gain_loss_percent']) {
            $best_performer = $holding;
        }
        
        if ($worst_performer === null || $holding['gain_loss_percent'] < $worst_performer['gain_loss_percent']) {
            $worst_performer = $holding;
        }
    }
    
    $total_gain_loss = $total_value - $total_cost;
    $total_gain_loss_percent = $total_cost > 0 ? ($total_gain_loss / $total_cost) * 100 : 0;
    
    return array(
        'total_value' => $total_value,
        'total_cost' => $total_cost,
        'total_gain_loss' => $total_gain_loss,
        'total_gain_loss_percent' => $total_gain_loss_percent,
        'holdings_count' => count($holdings),
        'top_performer' => $best_performer,
        'worst_performer' => $worst_performer,
    );
}

/**
 * Calculate portfolio allocation
 */
function stock_scanner_calculate_portfolio_allocation($holdings) {
    if (empty($holdings)) {
        return array();
    }
    
    $total_value = array_sum(array_column($holdings, 'current_value'));
    $allocation = array();
    $sector_allocation = array();
    
    foreach ($holdings as $holding) {
        $percentage = $total_value > 0 ? ($holding['current_value'] / $total_value) * 100 : 0;
        
        $allocation[] = array(
            'ticker' => $holding['ticker'],
            'value' => $holding['current_value'],
            'percentage' => $percentage,
        );
        
        // Get sector information
        $sector_info = stock_scanner_get_stock_sector($holding['ticker']);
        $sector = $sector_info['sector'];
        
        if (!isset($sector_allocation[$sector])) {
            $sector_allocation[$sector] = array(
                'sector' => $sector,
                'value' => 0,
                'percentage' => 0,
                'stocks' => array(),
            );
        }
        
        $sector_allocation[$sector]['value'] += $holding['current_value'];
        $sector_allocation[$sector]['stocks'][] = $holding['ticker'];
    }
    
    // Calculate sector percentages
    foreach ($sector_allocation as &$sector_data) {
        $sector_data['percentage'] = $total_value > 0 ? ($sector_data['value'] / $total_value) * 100 : 0;
    }
    
    return array(
        'by_stock' => $allocation,
        'by_sector' => array_values($sector_allocation),
    );
}

/**
 * Calculate portfolio performance metrics
 */
function stock_scanner_calculate_portfolio_performance($holdings) {
    if (empty($holdings)) {
        return array();
    }
    
    $total_value = array_sum(array_column($holdings, 'current_value'));
    $total_cost = array_sum(array_column($holdings, 'total_cost'));
    
    // Calculate basic metrics
    $metrics = array(
        'total_return' => $total_value - $total_cost,
        'total_return_percent' => $total_cost > 0 ? (($total_value - $total_cost) / $total_cost) * 100 : 0,
        'current_value' => $total_value,
        'invested_amount' => $total_cost,
    );
    
    // Calculate risk metrics (simplified)
    $returns = array();
    foreach ($holdings as $holding) {
        $returns[] = $holding['gain_loss_percent'];
    }
    
    if (!empty($returns)) {
        $avg_return = array_sum($returns) / count($returns);
        $variance = 0;
        
        foreach ($returns as $return) {
            $variance += pow($return - $avg_return, 2);
        }
        
        $variance = $variance / count($returns);
        $volatility = sqrt($variance);
        
        $metrics['average_return'] = $avg_return;
        $metrics['volatility'] = $volatility;
        $metrics['sharpe_ratio'] = $volatility > 0 ? $avg_return / $volatility : 0;
    }
    
    return $metrics;
}

/**
 * Create portfolio database table
 */
function stock_scanner_create_portfolio_table() {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'stock_scanner_portfolio';
    
    $charset_collate = $wpdb->get_charset_collate();
    
    $sql = "CREATE TABLE $table_name (
        id mediumint(9) NOT NULL AUTO_INCREMENT,
        user_id bigint(20) NOT NULL,
        ticker varchar(10) NOT NULL,
        shares decimal(15,4) NOT NULL,
        average_cost decimal(15,4) NOT NULL,
        purchase_date datetime DEFAULT CURRENT_TIMESTAMP,
        created_at datetime DEFAULT CURRENT_TIMESTAMP,
        updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        KEY user_id (user_id),
        KEY ticker (ticker),
        UNIQUE KEY user_ticker (user_id, ticker)
    ) $charset_collate;";
    
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);
}

/**
 * Log user activity
 */
function stock_scanner_log_user_activity($user_id, $activity_type, $data = array()) {
    $activity_log = get_user_meta($user_id, 'stock_scanner_activity_log', true);
    
    if (!is_array($activity_log)) {
        $activity_log = array();
    }
    
    $activity_entry = array(
        'activity' => $activity_type,
        'data' => $data,
        'timestamp' => current_time('mysql'),
        'ip_address' => $_SERVER['REMOTE_ADDR'] ?? '',
    );
    
    array_unshift($activity_log, $activity_entry);
    
    // Keep only last 100 activities
    $activity_log = array_slice($activity_log, 0, 100);
    
    update_user_meta($user_id, 'stock_scanner_activity_log', $activity_log);
}

/**
 * Export portfolio to CSV
 */
function stock_scanner_export_portfolio_csv($user_id) {
    $holdings = stock_scanner_get_portfolio_holdings($user_id);
    
    if (empty($holdings)) {
        return array(
            'success' => false,
            'error' => 'No holdings found',
        );
    }
    
    $csv_data = array();
    $csv_data[] = array(
        'Ticker',
        'Company Name',
        'Shares',
        'Average Cost',
        'Current Price',
        'Current Value',
        'Total Cost',
        'Gain/Loss',
        'Gain/Loss %',
        'Purchase Date',
    );
    
    foreach ($holdings as $holding) {
        $csv_data[] = array(
            $holding['ticker'],
            $holding['stock_data']['company_name'] ?? $holding['ticker'],
            $holding['shares'],
            $holding['average_cost'],
            $holding['current_price'],
            $holding['current_value'],
            $holding['total_cost'],
            $holding['gain_loss'],
            $holding['gain_loss_percent'],
            $holding['purchase_date'],
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
        'filename' => 'portfolio_' . date('Y-m-d_H-i-s') . '.csv',
    );
}