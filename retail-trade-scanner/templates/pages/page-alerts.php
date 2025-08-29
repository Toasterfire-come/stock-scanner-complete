<?php
/**
 * Template Name: Alerts
 * 
 * Alerts management page with list/manage/add/edit price/volume/PE alerts
 *
 * @package RetailTradeScanner
 */

// Restrict to logged-in users
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header();

// Sample alerts data - in real implementation this would come from API/database
$active_alerts = array(
    array(
        'id' => 1,
        'symbol' => 'AAPL',
        'company' => 'Apple Inc.',
        'type' => 'price',
        'condition' => 'above',
        'target_value' => '$185.00',
        'current_value' => '$182.34',
        'status' => 'active',
        'created_date' => '2024-01-10',
        'triggered_count' => 0,
        'enabled' => true
    ),
    array(
        'id' => 2,
        'symbol' => 'TSLA',
        'company' => 'Tesla Inc.',
        'type' => 'volume',
        'condition' => 'above',
        'target_value' => '30M',
        'current_value' => '28.9M',
        'status' => 'active',
        'created_date' => '2024-01-12',
        'triggered_count' => 2,
        'enabled' => true
    ),
    array(
        'id' => 3,
        'symbol' => 'NVDA',
        'company' => 'NVIDIA Corporation',
        'type' => 'price',
        'condition' => 'below',
        'target_value' => '$450.00',
        'current_value' => '$456.78',
        'status' => 'triggered',
        'created_date' => '2024-01-08',
        'triggered_count' => 1,
        'enabled' => false
    )
);

$alert_history = array(
    array(
        'symbol' => 'AAPL',
        'type' => 'price',
        'condition' => 'above $180',
        'triggered_at' => '2024-01-14 14:30:00',
        'triggered_value' => '$181.25',
        'action_taken' => 'Email sent'
    ),
    array(
        'symbol' => 'NVDA',
        'type' => 'volume',
        'condition' => 'above 40M',
        'triggered_at' => '2024-01-13 09:45:00',
        'triggered_value' => '42.5M',
        'action_taken' => 'Push notification'
    )
);

$layout_args = array(
    'page_title' => __('Price Alerts', 'retail-trade-scanner'),
    'page_description' => __('Create and manage price, volume, and technical alerts for your watchlist', 'retail-trade-scanner'),
    'page_class' => 'alerts-page',
    'header_actions' => array(
        array(
            'text' => __('New Alert', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'plus',
            'classes' => 'new-alert-btn'
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<div class="alerts-layout grid grid-cols-12 gap-lg">
    
    <!-- Active Alerts -->
    <div class="alerts-main col-span-8">
        
        <!-- Quick Stats -->
        <div class="alerts-stats grid grid-4 gap-lg mb-2xl">
            <div class="stat-card">
                <?php
                get_template_part('template-parts/components/card', null, array(
                    'title' => __('Active Alerts', 'retail-trade-scanner'),
                    'value' => count(array_filter($active_alerts, function($alert) { return $alert['enabled']; })),
                    'icon' => 'bell',
                    'variant' => 'glass',
                    'size' => 'sm'
                ));
                ?>
            </div>
            
            <div class="stat-card">
                <?php
                get_template_part('template-parts/components/card', null, array(
                    'title' => __('Triggered Today', 'retail-trade-scanner'),
                    'value' => '3',
                    'icon' => 'activity',
                    'variant' => 'glass',
                    'size' => 'sm'
                ));
                ?>
            </div>
            
            <div class="stat-card">
                <?php
                get_template_part('template-parts/components/card', null, array(
                    'title' => __('Price Alerts', 'retail-trade-scanner'),
                    'value' => count(array_filter($active_alerts, function($alert) { return $alert['type'] === 'price'; })),
                    'icon' => 'dollar-sign',
                    'variant' => 'glass',
                    'size' => 'sm'
                ));
                ?>
            </div>
            
            <div class="stat-card">
                <?php
                get_template_part('template-parts/components/card', null, array(
                    'title' => __('Volume Alerts', 'retail-trade-scanner'),
                    'value' => count(array_filter($active_alerts, function($alert) { return $alert['type'] === 'volume'; })),
                    'icon' => 'bar-chart',
                    'variant' => 'glass',
                    'size' => 'sm'
                ));
                ?>
            </div>
        </div>
        
        <!-- Alerts Table -->
        <div class="alerts-table-container card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('My Alerts', 'retail-trade-scanner'); ?></h3>
                <div class="table-actions">
                    <div class="filter-dropdown">
                        <select class="form-select" id="alert-filter">
                            <option value="all"><?php esc_html_e('All Alerts', 'retail-trade-scanner'); ?></option>
                            <option value="active"><?php esc_html_e('Active Only', 'retail-trade-scanner'); ?></option>
                            <option value="triggered"><?php esc_html_e('Triggered', 'retail-trade-scanner'); ?></option>
                            <option value="price"><?php esc_html_e('Price Alerts', 'retail-trade-scanner'); ?></option>
                            <option value="volume"><?php esc_html_e('Volume Alerts', 'retail-trade-scanner'); ?></option>
                        </select>
                    </div>
                    
                    <button class="btn btn-outline btn-sm bulk-edit-btn hidden">
                        <?php echo rts_get_icon('settings', ['width' => '16', 'height' => '16']); ?>
                        <?php esc_html_e('Bulk Edit', 'retail-trade-scanner'); ?>
                    </button>
                </div>
            </div>
            
            <div class="card-body">
                <div class="alerts-table-wrapper">
                    <table class="alerts-table data-table">
                        <thead>
                            <tr>
                                <th>
                                    <input type="checkbox" class="select-all-alerts" aria-label="<?php esc_attr_e('Select all alerts', 'retail-trade-scanner'); ?>">
                                </th>
                                <th><?php esc_html_e('Symbol', 'retail-trade-scanner'); ?></th>
                                <th><?php esc_html_e('Type', 'retail-trade-scanner'); ?></th>
                                <th><?php esc_html_e('Condition', 'retail-trade-scanner'); ?></th>
                                <th><?php esc_html_e('Target', 'retail-trade-scanner'); ?></th>
                                <th><?php esc_html_e('Current', 'retail-trade-scanner'); ?></th>
                                <th><?php esc_html_e('Status', 'retail-trade-scanner'); ?></th>
                                <th><?php esc_html_e('Actions', 'retail-trade-scanner'); ?></th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($active_alerts as $alert) : ?>
                                <tr class="alert-row" data-alert-id="<?php echo esc_attr($alert['id']); ?>">
                                    <td>
                                        <input type="checkbox" class="alert-select" value="<?php echo esc_attr($alert['id']); ?>">
                                    </td>
                                    <td>
                                        <div class="symbol-cell">
                                            <div class="symbol-info">
                                                <span class="symbol-ticker"><?php echo esc_html($alert['symbol']); ?></span>
                                                <span class="symbol-company"><?php echo esc_html($alert['company']); ?></span>
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <?php
                                        $type_labels = array(
                                            'price' => __('Price', 'retail-trade-scanner'),
                                            'volume' => __('Volume', 'retail-trade-scanner'),
                                            'pe' => __('P/E Ratio', 'retail-trade-scanner')
                                        );
                                        
                                        $type_colors = array(
                                            'price' => 'info',
                                            'volume' => 'warning',
                                            'pe' => 'success'
                                        );
                                        
                                        get_template_part('template-parts/components/badge', null, array(
                                            'value' => $type_labels[$alert['type']] ?? ucfirst($alert['type']),
                                            'type' => $type_colors[$alert['type']] ?? 'neutral',
                                            'size' => 'xs'
                                        ));
                                        ?>
                                    </td>
                                    <td>
                                        <span class="condition-text">
                                            <?php echo esc_html(ucfirst($alert['condition'])); ?>
                                        </span>
                                    </td>
                                    <td>
                                        <span class="target-value">
                                            <?php echo esc_html($alert['target_value']); ?>
                                        </span>
                                    </td>
                                    <td>
                                        <span class="current-value">
                                            <?php echo esc_html($alert['current_value']); ?>
                                        </span>
                                    </td>
                                    <td>
                                        <div class="status-cell">
                                            <?php
                                            $status_types = array(
                                                'active' => 'success',
                                                'triggered' => 'warning',
                                                'paused' => 'neutral'
                                            );
                                            
                                            get_template_part('template-parts/components/badge', null, array(
                                                'value' => ucfirst($alert['status']),
                                                'type' => $status_types[$alert['status']] ?? 'neutral',
                                                'size' => 'sm'
                                            ));
                                            ?>
                                            
                                            <div class="status-toggle">
                                                <label class="switch">
                                                    <input type="checkbox" class="alert-toggle" data-alert-id="<?php echo esc_attr($alert['id']); ?>" <?php checked($alert['enabled']); ?>>
                                                    <span class="slider"></span>
                                                </label>
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <div class="alert-actions">
                                            <button class="action-btn edit-alert-btn" data-alert-id="<?php echo esc_attr($alert['id']); ?>" title="<?php esc_attr_e('Edit Alert', 'retail-trade-scanner'); ?>">
                                                <?php echo rts_get_icon('settings', ['width' => '14', 'height' => '14']); ?>
                                            </button>
                                            
                                            <button class="action-btn test-alert-btn" data-alert-id="<?php echo esc_attr($alert['id']); ?>" title="<?php esc_attr_e('Test Alert', 'retail-trade-scanner'); ?>">
                                                <?php echo rts_get_icon('bell', ['width' => '14', 'height' => '14']); ?>
                                            </button>
                                            
                                            <button class="action-btn delete-alert-btn" data-alert-id="<?php echo esc_attr($alert['id']); ?>" title="<?php esc_attr_e('Delete Alert', 'retail-trade-scanner'); ?>">
                                                <?php echo rts_get_icon('x', ['width' => '14', 'height' => '14']); ?>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Recent History -->
        <div class="alert-history-section mt-2xl">
            <div class="card glass-card">
                <div class="card-header">
                    <h3 class="card-title"><?php esc_html_e('Recent Triggers', 'retail-trade-scanner'); ?></h3>
                    <a href="#" class="view-all-link">
                        <?php esc_html_e('View All History', 'retail-trade-scanner'); ?>
                        <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
                    </a>
                </div>
                
                <div class="card-body">
                    <div class="history-timeline">
                        <?php foreach ($alert_history as $history_item) : ?>
                            <div class="timeline-item">
                                <div class="timeline-marker">
                                    <?php echo rts_get_icon('bell', ['width' => '16', 'height' => '16']); ?>
                                </div>
                                
                                <div class="timeline-content">
                                    <div class="timeline-header">
                                        <h4 class="timeline-title">
                                            <?php echo esc_html($history_item['symbol']); ?> - <?php echo esc_html($history_item['condition']); ?>
                                        </h4>
                                        <time class="timeline-time">
                                            <?php echo esc_html(date('M j, g:i A', strtotime($history_item['triggered_at']))); ?>
                                        </time>
                                    </div>
                                    
                                    <div class="timeline-details">
                                        <p><?php esc_html_e('Triggered at:', 'retail-trade-scanner'); ?> <strong><?php echo esc_html($history_item['triggered_value']); ?></strong></p>
                                        <p><?php esc_html_e('Action:', 'retail-trade-scanner'); ?> <?php echo esc_html($history_item['action_taken']); ?></p>
                                    </div>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Create Alert Sidebar -->
    <div class="create-alert-sidebar col-span-4">
        <div class="create-alert-card card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Create New Alert', 'retail-trade-scanner'); ?></h3>
            </div>
            
            <div class="card-body">
                <form class="create-alert-form" id="create-alert-form">
                    
                    <!-- Symbol Input -->
                    <div class="form-field">
                        <label class="form-label" for="alert-symbol">
                            <?php esc_html_e('Stock Symbol', 'retail-trade-scanner'); ?>
                        </label>
                        <input type="text" 
                               class="form-input" 
                               id="alert-symbol" 
                               name="symbol" 
                               placeholder="<?php esc_attr_e('Enter symbol (e.g., AAPL)', 'retail-trade-scanner'); ?>"
                               autocomplete="off"
                               required>
                        <div class="symbol-suggestions hidden"></div>
                    </div>
                    
                    <!-- Alert Type -->
                    <div class="form-field">
                        <label class="form-label" for="alert-type">
                            <?php esc_html_e('Alert Type', 'retail-trade-scanner'); ?>
                        </label>
                        <select class="form-select" id="alert-type" name="type" required>
                            <option value=""><?php esc_html_e('Select type', 'retail-trade-scanner'); ?></option>
                            <option value="price"><?php esc_html_e('Price Alert', 'retail-trade-scanner'); ?></option>
                            <option value="volume"><?php esc_html_e('Volume Alert', 'retail-trade-scanner'); ?></option>
                            <option value="pe"><?php esc_html_e('P/E Ratio Alert', 'retail-trade-scanner'); ?></option>
                            <option value="change"><?php esc_html_e('Price Change %', 'retail-trade-scanner'); ?></option>
                        </select>
                    </div>
                    
                    <!-- Condition -->
                    <div class="form-field">
                        <label class="form-label" for="alert-condition">
                            <?php esc_html_e('Condition', 'retail-trade-scanner'); ?>
                        </label>
                        <div class="condition-group">
                            <select class="form-select condition-select" id="alert-condition" name="condition" required>
                                <option value=""><?php esc_html_e('Select condition', 'retail-trade-scanner'); ?></option>
                                <option value="above"><?php esc_html_e('Above', 'retail-trade-scanner'); ?></option>
                                <option value="below"><?php esc_html_e('Below', 'retail-trade-scanner'); ?></option>
                                <option value="equals"><?php esc_html_e('Equals', 'retail-trade-scanner'); ?></option>
                            </select>
                            
                            <input type="number" 
                                   class="form-input condition-value" 
                                   id="alert-value" 
                                   name="value" 
                                   placeholder="<?php esc_attr_e('Enter value', 'retail-trade-scanner'); ?>"
                                   step="0.01"
                                   required>
                        </div>
                    </div>
                    
                    <!-- Current Value Display -->
                    <div class="current-value-display hidden">
                        <div class="current-info">
                            <span class="current-label"><?php esc_html_e('Current Value:', 'retail-trade-scanner'); ?></span>
                            <span class="current-amount">$0.00</span>
                        </div>
                    </div>
                    
                    <!-- Notification Settings -->
                    <div class="form-field">
                        <label class="form-label">
                            <?php esc_html_e('Notification Method', 'retail-trade-scanner'); ?>
                        </label>
                        
                        <div class="notification-options">
                            <label class="checkbox-option">
                                <input type="checkbox" name="notifications[]" value="email" checked>
                                <span class="checkmark"></span>
                                <span class="option-label">
                                    <?php echo rts_get_icon('email', ['width' => '16', 'height' => '16']); ?>
                                    <?php esc_html_e('Email', 'retail-trade-scanner'); ?>
                                </span>
                            </label>
                            
                            <label class="checkbox-option">
                                <input type="checkbox" name="notifications[]" value="push">
                                <span class="checkmark"></span>
                                <span class="option-label">
                                    <?php echo rts_get_icon('bell', ['width' => '16', 'height' => '16']); ?>
                                    <?php esc_html_e('Push Notification', 'retail-trade-scanner'); ?>
                                </span>
                            </label>
                            
                            <label class="checkbox-option">
                                <input type="checkbox" name="notifications[]" value="sms">
                                <span class="checkmark"></span>
                                <span class="option-label">
                                    <?php echo rts_get_icon('smartphone', ['width' => '16', 'height' => '16']); ?>
                                    <?php esc_html_e('SMS', 'retail-trade-scanner'); ?>
                                </span>
                            </label>
                        </div>
                    </div>
                    
                    <!-- Advanced Options -->
                    <div class="form-field">
                        <button type="button" class="toggle-advanced-btn">
                            <span class="toggle-text"><?php esc_html_e('Advanced Options', 'retail-trade-scanner'); ?></span>
                            <?php echo rts_get_icon('chevron-down', ['width' => '16', 'height' => '16']); ?>
                        </button>
                        
                        <div class="advanced-options hidden">
                            <div class="form-field">
                                <label class="form-label" for="alert-frequency">
                                    <?php esc_html_e('Frequency', 'retail-trade-scanner'); ?>
                                </label>
                                <select class="form-select" id="alert-frequency" name="frequency">
                                    <option value="once"><?php esc_html_e('Once', 'retail-trade-scanner'); ?></option>
                                    <option value="daily"><?php esc_html_e('Daily', 'retail-trade-scanner'); ?></option>
                                    <option value="continuous"><?php esc_html_e('Continuous', 'retail-trade-scanner'); ?></option>
                                </select>
                            </div>
                            
                            <div class="form-field">
                                <label class="form-label" for="alert-expires">
                                    <?php esc_html_e('Expires After', 'retail-trade-scanner'); ?>
                                </label>
                                <select class="form-select" id="alert-expires" name="expires">
                                    <option value="never"><?php esc_html_e('Never', 'retail-trade-scanner'); ?></option>
                                    <option value="1d"><?php esc_html_e('1 Day', 'retail-trade-scanner'); ?></option>
                                    <option value="7d"><?php esc_html_e('7 Days', 'retail-trade-scanner'); ?></option>
                                    <option value="30d"><?php esc_html_e('30 Days', 'retail-trade-scanner'); ?></option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Submit Buttons -->
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary btn-block">
                            <?php echo rts_get_icon('plus', ['width' => '16', 'height' => '16']); ?>
                            <?php esc_html_e('Create Alert', 'retail-trade-scanner'); ?>
                        </button>
                        
                        <button type="button" class="btn btn-outline btn-block test-alert-setup">
                            <?php echo rts_get_icon('bell', ['width' => '16', 'height' => '16']); ?>
                            <?php esc_html_e('Test Setup', 'retail-trade-scanner'); ?>
                        </button>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Quick Templates -->
        <div class="alert-templates-card card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Quick Templates', 'retail-trade-scanner'); ?></h3>
            </div>
            
            <div class="card-body">
                <div class="template-buttons">
                    <button class="template-btn" data-template="breakout">
                        <span class="template-icon"><?php echo rts_get_icon('trending-up', ['width' => '16', 'height' => '16']); ?></span>
                        <span class="template-label"><?php esc_html_e('Breakout Alert', 'retail-trade-scanner'); ?></span>
                    </button>
                    
                    <button class="template-btn" data-template="volume-spike">
                        <span class="template-icon"><?php echo rts_get_icon('bar-chart', ['width' => '16', 'height' => '16']); ?></span>
                        <span class="template-label"><?php esc_html_e('Volume Spike', 'retail-trade-scanner'); ?></span>
                    </button>
                    
                    <button class="template-btn" data-template="support-level">
                        <span class="template-icon"><?php echo rts_get_icon('trending-down', ['width' => '16', 'height' => '16']); ?></span>
                        <span class="template-label"><?php esc_html_e('Support Level', 'retail-trade-scanner'); ?></span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initAlertsPage();
});

function initAlertsPage() {
    const createForm = document.getElementById('create-alert-form');
    const symbolInput = document.getElementById('alert-symbol');
    const alertTypeSelect = document.getElementById('alert-type');
    const newAlertBtn = document.querySelector('.new-alert-btn');
    
    // Create alert form submission
    if (createForm) {
        createForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleCreateAlert();
        });
    }
    
    // Symbol autocomplete
    if (symbolInput) {
        symbolInput.addEventListener('input', function() {
            const query = this.value;
            if (query.length >= 1) {
                showSymbolSuggestions(query);
            } else {
                hideSymbolSuggestions();
            }
        });
    }
    
    // Alert type change
    if (alertTypeSelect) {
        alertTypeSelect.addEventListener('change', function() {
            updateFormForAlertType(this.value);
        });
    }
    
    // Alert toggles
    document.querySelectorAll('.alert-toggle').forEach(toggle => {
        toggle.addEventListener('change', function() {
            const alertId = this.dataset.alertId;
            const enabled = this.checked;
            toggleAlert(alertId, enabled);
        });
    });
    
    // Alert actions
    document.addEventListener('click', function(e) {
        const editBtn = e.target.closest('.edit-alert-btn');
        const testBtn = e.target.closest('.test-alert-btn');
        const deleteBtn = e.target.closest('.delete-alert-btn');
        
        if (editBtn) {
            const alertId = editBtn.dataset.alertId;
            editAlert(alertId);
        } else if (testBtn) {
            const alertId = testBtn.dataset.alertId;
            testAlert(alertId);
        } else if (deleteBtn) {
            const alertId = deleteBtn.dataset.alertId;
            deleteAlert(alertId);
        }
    });
    
    // Template buttons
    document.querySelectorAll('.template-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const template = this.dataset.template;
            applyTemplate(template);
        });
    });
    
    // Advanced options toggle
    const toggleAdvancedBtn = document.querySelector('.toggle-advanced-btn');
    if (toggleAdvancedBtn) {
        toggleAdvancedBtn.addEventListener('click', function() {
            const advancedOptions = document.querySelector('.advanced-options');
            const icon = this.querySelector('svg');
            
            advancedOptions.classList.toggle('hidden');
            icon.style.transform = advancedOptions.classList.contains('hidden') ? 'rotate(0deg)' : 'rotate(180deg)';
        });
    }
    
    // Bulk selection
    const selectAllCheckbox = document.querySelector('.select-all-alerts');
    const alertCheckboxes = document.querySelectorAll('.alert-select');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            alertCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            updateBulkActions();
        });
    }
    
    alertCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectAllState();
            updateBulkActions();
        });
    });
    
    // Filter alerts
    const alertFilter = document.getElementById('alert-filter');
    if (alertFilter) {
        alertFilter.addEventListener('change', function() {
            filterAlerts(this.value);
        });
    }
    
    function handleCreateAlert() {
        const formData = new FormData(createForm);
        const alertData = Object.fromEntries(formData.entries());
        
        console.log('Creating alert:', alertData);
        
        // Validate required fields
        if (!alertData.symbol || !alertData.type || !alertData.condition || !alertData.value) {
            RTS.showError('Please fill in all required fields');
            return;
        }
        
        // Simulate API call
        const submitBtn = createForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating...';
        
        setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg> Create Alert';
            
            RTS.showSuccess('Alert created successfully!');
            createForm.reset();
            hideSymbolSuggestions();
            
            // Refresh alerts table
            refreshAlertsTable();
        }, 2000);
    }
    
    function showSymbolSuggestions(query) {
        // Mock suggestions
        const suggestions = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA'].filter(symbol => 
            symbol.toLowerCase().includes(query.toLowerCase())
        );
        
        const container = document.querySelector('.symbol-suggestions');
        if (suggestions.length > 0) {
            container.innerHTML = suggestions.map(symbol => 
                `<div class="suggestion-item" data-symbol="${symbol}">${symbol}</div>`
            ).join('');
            container.classList.remove('hidden');
            
            // Add click handlers
            container.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', function() {
                    symbolInput.value = this.dataset.symbol;
                    hideSymbolSuggestions();
                    fetchCurrentValue(this.dataset.symbol);
                });
            });
        } else {
            hideSymbolSuggestions();
        }
    }
    
    function hideSymbolSuggestions() {
        document.querySelector('.symbol-suggestions').classList.add('hidden');
    }
    
    function updateFormForAlertType(type) {
        const valueInput = document.getElementById('alert-value');
        const currentDisplay = document.querySelector('.current-value-display');
        
        switch (type) {
            case 'price':
                valueInput.placeholder = 'Enter price (e.g., 150.00)';
                valueInput.step = '0.01';
                break;
            case 'volume':
                valueInput.placeholder = 'Enter volume (e.g., 1000000)';
                valueInput.step = '1';
                break;
            case 'pe':
                valueInput.placeholder = 'Enter P/E ratio (e.g., 25.5)';
                valueInput.step = '0.1';
                break;
            case 'change':
                valueInput.placeholder = 'Enter percentage (e.g., 5.0)';
                valueInput.step = '0.1';
                break;
        }
        
        if (type && symbolInput.value) {
            currentDisplay.classList.remove('hidden');
            fetchCurrentValue(symbolInput.value, type);
        } else {
            currentDisplay.classList.add('hidden');
        }
    }
    
    function fetchCurrentValue(symbol, type) {
        // Mock current values
        const mockValues = {
            price: '$182.34',
            volume: '28.9M',
            pe: '28.5',
            change: '+2.34%'
        };
        
        const currentAmount = document.querySelector('.current-amount');
        if (currentAmount) {
            currentAmount.textContent = mockValues[type] || mockValues.price;
        }
    }
    
    function toggleAlert(alertId, enabled) {
        console.log(`Toggling alert ${alertId}: ${enabled}`);
        
        const message = enabled ? 'Alert enabled' : 'Alert disabled';
        RTS.showSuccess(message);
        
        // Update status in the table
        const row = document.querySelector(`[data-alert-id="${alertId}"]`);
        if (row) {
            const statusBadge = row.querySelector('.badge');
            if (enabled) {
                statusBadge.textContent = 'Active';
                statusBadge.className = 'badge badge-success badge-sm';
            } else {
                statusBadge.textContent = 'Paused';
                statusBadge.className = 'badge badge-neutral badge-sm';
            }
        }
    }
    
    function editAlert(alertId) {
        console.log('Editing alert:', alertId);
        RTS.showInfo('Edit alert modal would open here');
    }
    
    function testAlert(alertId) {
        console.log('Testing alert:', alertId);
        RTS.showSuccess('Test notification sent!');
    }
    
    function deleteAlert(alertId) {
        if (confirm('Are you sure you want to delete this alert?')) {
            console.log('Deleting alert:', alertId);
            
            const row = document.querySelector(`[data-alert-id="${alertId}"]`);
            if (row) {
                row.remove();
                RTS.showSuccess('Alert deleted successfully');
            }
        }
    }
    
    function applyTemplate(template) {
        const templates = {
            'breakout': {
                type: 'price',
                condition: 'above',
                notifications: ['email', 'push']
            },
            'volume-spike': {
                type: 'volume',
                condition: 'above',
                notifications: ['push']
            },
            'support-level': {
                type: 'price',
                condition: 'below',
                notifications: ['email']
            }
        };
        
        const templateData = templates[template];
        if (templateData) {
            document.getElementById('alert-type').value = templateData.type;
            document.getElementById('alert-condition').value = templateData.condition;
            
            // Update notification checkboxes
            document.querySelectorAll('input[name="notifications[]"]').forEach(cb => {
                cb.checked = templateData.notifications.includes(cb.value);
            });
            
            updateFormForAlertType(templateData.type);
            RTS.showInfo(`Applied ${template} template`);
        }
    }
    
    function updateSelectAllState() {
        const checkedCount = document.querySelectorAll('.alert-select:checked').length;
        const totalCount = document.querySelectorAll('.alert-select').length;
        
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = checkedCount === totalCount && totalCount > 0;
            selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < totalCount;
        }
    }
    
    function updateBulkActions() {
        const checkedCount = document.querySelectorAll('.alert-select:checked').length;
        const bulkEditBtn = document.querySelector('.bulk-edit-btn');
        
        if (bulkEditBtn) {
            if (checkedCount > 0) {
                bulkEditBtn.classList.remove('hidden');
                bulkEditBtn.textContent = `Bulk Edit (${checkedCount})`;
            } else {
                bulkEditBtn.classList.add('hidden');
            }
        }
    }
    
    function filterAlerts(filter) {
        const rows = document.querySelectorAll('.alert-row');
        
        rows.forEach(row => {
            let shouldShow = true;
            
            if (filter !== 'all') {
                const type = row.querySelector('.badge').textContent.toLowerCase();
                const status = row.querySelector('.status-cell .badge').textContent.toLowerCase();
                
                switch (filter) {
                    case 'active':
                        shouldShow = status === 'active';
                        break;
                    case 'triggered':
                        shouldShow = status === 'triggered';
                        break;
                    case 'price':
                        shouldShow = type === 'price';
                        break;
                    case 'volume':
                        shouldShow = type === 'volume';
                        break;
                }
            }
            
            row.style.display = shouldShow ? '' : 'none';
        });
        
        console.log('Filtered alerts by:', filter);
    }
    
    function refreshAlertsTable() {
        // Simulate refreshing the table
        console.log('Refreshing alerts table...');
    }
}
</script>

<style>
/* Alerts Page Styles */
.alerts-layout {
    margin-bottom: var(--spacing-2xl);
}

.alerts-stats {
    margin-bottom: var(--spacing-2xl);
}

.table-actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.alerts-table-wrapper {
    overflow-x: auto;
}

.symbol-suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--surface-raised);
    border: 1px solid var(--gray-200);
    border-top: none;
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    max-height: 200px;
    overflow-y: auto;
    z-index: var(--z-dropdown);
}

.suggestion-item {
    padding: var(--spacing-sm) var(--spacing-md);
    cursor: pointer;
    transition: background-color var(--transition-fast) var(--easing-standard);
}

.suggestion-item:hover {
    background: var(--gray-50);
}

.status-cell {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.switch {
    position: relative;
    width: 44px;
    height: 24px;
}

.switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: var(--gray-300);
    transition: var(--transition-normal);
    border-radius: 24px;
}

.slider:before {
    position: absolute;
    content: "";
    height: 20px;
    width: 20px;
    left: 2px;
    bottom: 2px;
    background-color: white;
    transition: var(--transition-normal);
    border-radius: 50%;
}

input:checked + .slider {
    background-color: var(--success);
}

input:checked + .slider:before {
    transform: translateX(20px);
}

.alert-actions {
    display: flex;
    gap: var(--spacing-xs);
}

.condition-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-sm);
}

.current-value-display {
    margin-top: var(--spacing-sm);
    padding: var(--spacing-sm);
    background: var(--gray-50);
    border-radius: var(--radius-lg);
}

.current-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.current-label {
    font-size: var(--text-sm);
    color: var(--gray-600);
}

.current-amount {
    font-weight: 600;
    color: var(--gray-900);
}

.notification-options {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.checkbox-option {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
}

.checkbox-option:hover {
    background: var(--gray-50);
    border-color: var(--primary-500);
}

.checkbox-option input[type="checkbox"] {
    display: none;
}

.checkbox-option .checkmark {
    width: 16px;
    height: 16px;
    border: 2px solid var(--gray-300);
    border-radius: var(--radius-sm);
    position: relative;
    transition: all var(--transition-fast) var(--easing-standard);
}

.checkbox-option input:checked + .checkmark {
    background: var(--primary-500);
    border-color: var(--primary-500);
}

.checkbox-option input:checked + .checkmark::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 5px;
    width: 4px;
    height: 8px;
    border: solid white;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg);
}

.option-label {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: var(--text-sm);
    color: var(--gray-700);
}

.toggle-advanced-btn {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: var(--spacing-sm);
    background: transparent;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    cursor: pointer;
    font-size: var(--text-sm);
    transition: all var(--transition-fast) var(--easing-standard);
}

.toggle-advanced-btn:hover {
    background: var(--gray-50);
}

.advanced-options {
    margin-top: var(--spacing-md);
    padding-top: var(--spacing-md);
    border-top: 1px solid var(--gray-200);
}

.form-actions {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    margin-top: var(--spacing-xl);
}

.template-buttons {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.template-btn {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-md);
    background: transparent;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
    text-align: left;
}

.template-btn:hover {
    background: var(--primary-50);
    border-color: var(--primary-500);
}

.template-icon {
    color: var(--primary-600);
}

.template-label {
    font-size: var(--text-sm);
    color: var(--gray-700);
}

/* Timeline Styles */
.history-timeline {
    position: relative;
}

.timeline-item {
    position: relative;
    padding-left: var(--spacing-2xl);
    padding-bottom: var(--spacing-lg);
}

.timeline-item:last-child {
    padding-bottom: 0;
}

.timeline-item::before {
    content: '';
    position: absolute;
    left: 12px;
    top: 24px;
    bottom: -16px;
    width: 2px;
    background: var(--gray-200);
}

.timeline-item:last-child::before {
    display: none;
}

.timeline-marker {
    position: absolute;
    left: 0;
    top: 0;
    width: 24px;
    height: 24px;
    background: var(--primary-500);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.timeline-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--spacing-sm);
}

.timeline-title {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--gray-900);
    margin: 0;
}

.timeline-time {
    font-size: var(--text-xs);
    color: var(--gray-500);
}

.timeline-details {
    font-size: var(--text-sm);
    color: var(--gray-600);
}

.timeline-details p {
    margin: 0 0 var(--spacing-xs);
}

.timeline-details strong {
    color: var(--gray-900);
}

/* Responsive Design */
@media (max-width: 1024px) {
    .alerts-layout {
        grid-template-columns: 1fr;
    }
    
    .create-alert-sidebar {
        order: -1;
    }
}

@media (max-width: 640px) {
    .alerts-stats {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .table-actions {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--spacing-sm);
    }
    
    .condition-group {
        grid-template-columns: 1fr;
    }
    
    .current-info {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--spacing-xs);
    }
    
    .notification-options {
        gap: var(--spacing-xs);
    }
    
    .checkbox-option {
        padding: var(--spacing-sm);
    }
}

/* Dark Mode Adjustments */
[data-theme="dark"] .suggestion-item:hover {
    background: var(--gray-700);
}

[data-theme="dark"] .current-value-display,
[data-theme="dark"] .toggle-advanced-btn:hover,
[data-theme="dark"] .checkbox-option:hover {
    background: var(--gray-700);
}

[data-theme="dark"] .advanced-options,
[data-theme="dark"] .timeline-item::before {
    border-color: var(--gray-700);
}

[data-theme="dark"] .timeline-title,
[data-theme="dark"] .current-amount {
    color: var(--gray-100);
}

[data-theme="dark"] .timeline-details,
[data-theme="dark"] .current-label,
[data-theme="dark"] .template-label,
[data-theme="dark"] .option-label {
    color: var(--gray-300);
}
</style>

<?php get_footer(); ?>