<?php
/**
 * Template Name: Alerts
 * 
 * Alert management system for price, volume, and technical alerts
 *
 * @package RetailTradeScanner
 */

// Restrict to logged-in users
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header();

// Sample alerts data
$active_alerts = array(
    array(
        'id' => '1',
        'symbol' => 'AAPL',
        'company' => 'Apple Inc.',
        'type' => 'price_above',
        'condition' => 'Above $185.00',
        'current_value' => '$182.34',
        'created_date' => '2024-01-10',
        'status' => 'active',
        'triggered' => false
    ),
    array(
        'id' => '2',
        'symbol' => 'TSLA',
        'company' => 'Tesla Inc.',
        'type' => 'volume',
        'condition' => 'Volume > 30M',
        'current_value' => '28.9M',
        'created_date' => '2024-01-12',
        'status' => 'active',
        'triggered' => false
    ),
    array(
        'id' => '3',
        'symbol' => 'NVDA',
        'company' => 'NVIDIA Corporation',
        'type' => 'price_below',
        'condition' => 'Below $450.00',
        'current_value' => '$456.78',
        'created_date' => '2024-01-08',
        'status' => 'triggered',
        'triggered' => true,
        'triggered_date' => '2024-01-14'
    )
);

$layout_args = array(
    'page_title' => __('Price & Volume Alerts', 'retail-trade-scanner'),
    'page_description' => __('Create and manage intelligent market alerts to never miss trading opportunities', 'retail-trade-scanner'),
    'page_class' => 'alerts-page',
    'header_actions' => array(
        array(
            'text' => __('Create Alert', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'plus',
            'action' => 'create-alert'
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<!-- Alert Stats Cards -->
<div class="alerts-overview grid grid-4 gap-lg mb-2xl">
    <div class="stat-card glass-card">
        <div class="stat-icon">
            <?php echo rts_get_icon('alerts', ['width' => '32', 'height' => '32']); ?>
        </div>
        <div class="stat-content">
            <h3 class="stat-value">12</h3>
            <p class="stat-label"><?php esc_html_e('Active Alerts', 'retail-trade-scanner'); ?></p>
        </div>
    </div>
    
    <div class="stat-card glass-card">
        <div class="stat-icon triggered">
            <?php echo rts_get_icon('bell', ['width' => '32', 'height' => '32']); ?>
        </div>
        <div class="stat-content">
            <h3 class="stat-value">3</h3>
            <p class="stat-label"><?php esc_html_e('Triggered Today', 'retail-trade-scanner'); ?></p>
        </div>
    </div>
    
    <div class="stat-card glass-card">
        <div class="stat-icon success">
            <?php echo rts_get_icon('trending-up', ['width' => '32', 'height' => '32']); ?>
        </div>
        <div class="stat-content">
            <h3 class="stat-value">87%</h3>
            <p class="stat-label"><?php esc_html_e('Accuracy Rate', 'retail-trade-scanner'); ?></p>
        </div>
    </div>
    
    <div class="stat-card glass-card">
        <div class="stat-icon">
            <?php echo rts_get_icon('clock', ['width' => '32', 'height' => '32']); ?>
        </div>
        <div class="stat-content">
            <h3 class="stat-value">2.3s</h3>
            <p class="stat-label"><?php esc_html_e('Avg Response', 'retail-trade-scanner'); ?></p>
        </div>
    </div>
</div>

<!-- Main Alerts Content -->
<div class="alerts-layout grid grid-cols-12 gap-lg">
    
    <!-- Alerts List -->
    <div class="alerts-list col-span-8">
        <!-- Filter Bar -->
        <div class="alerts-filter-bar flex items-center justify-between mb-lg">
            <div class="filter-controls flex items-center gap-md">
                <select class="form-select" name="status_filter">
                    <option value="all"><?php esc_html_e('All Alerts', 'retail-trade-scanner'); ?></option>
                    <option value="active"><?php esc_html_e('Active', 'retail-trade-scanner'); ?></option>
                    <option value="triggered"><?php esc_html_e('Triggered', 'retail-trade-scanner'); ?></option>
                    <option value="paused"><?php esc_html_e('Paused', 'retail-trade-scanner'); ?></option>
                </select>
                
                <select class="form-select" name="type_filter">
                    <option value="all"><?php esc_html_e('All Types', 'retail-trade-scanner'); ?></option>
                    <option value="price"><?php esc_html_e('Price Alerts', 'retail-trade-scanner'); ?></option>
                    <option value="volume"><?php esc_html_e('Volume Alerts', 'retail-trade-scanner'); ?></option>
                    <option value="technical"><?php esc_html_e('Technical', 'retail-trade-scanner'); ?></option>
                </select>
                
                <input type="text" class="form-input" placeholder="<?php esc_attr_e('Search symbols...', 'retail-trade-scanner'); ?>">
            </div>
            
            <div class="view-controls flex items-center gap-sm">
                <button class="btn btn-ghost btn-sm">
                    <?php echo rts_get_icon('filter', ['width' => '16', 'height' => '16']); ?>
                    <?php esc_html_e('Filter', 'retail-trade-scanner'); ?>
                </button>
                
                <button class="btn btn-outline btn-sm">
                    <?php echo rts_get_icon('download', ['width' => '16', 'height' => '16']); ?>
                    <?php esc_html_e('Export', 'retail-trade-scanner'); ?>
                </button>
            </div>
        </div>
        
        <!-- Alerts Table -->
        <div class="alerts-table card">
            <div class="table-header">
                <h3><?php esc_html_e('Your Alerts', 'retail-trade-scanner'); ?></h3>
            </div>
            
            <div class="table-content">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th><?php esc_html_e('Symbol', 'retail-trade-scanner'); ?></th>
                            <th><?php esc_html_e('Alert Type', 'retail-trade-scanner'); ?></th>
                            <th><?php esc_html_e('Condition', 'retail-trade-scanner'); ?></th>
                            <th><?php esc_html_e('Current Value', 'retail-trade-scanner'); ?></th>
                            <th><?php esc_html_e('Status', 'retail-trade-scanner'); ?></th>
                            <th><?php esc_html_e('Created', 'retail-trade-scanner'); ?></th>
                            <th><?php esc_html_e('Actions', 'retail-trade-scanner'); ?></th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($active_alerts as $alert) : ?>
                            <tr class="alert-row" data-alert-id="<?php echo esc_attr($alert['id']); ?>">
                                <td>
                                    <div class="symbol-cell">
                                        <span class="symbol"><?php echo esc_html($alert['symbol']); ?></span>
                                        <span class="company"><?php echo esc_html($alert['company']); ?></span>
                                    </div>
                                </td>
                                <td>
                                    <div class="alert-type">
                                        <?php
                                        $type_icons = array(
                                            'price_above' => 'trending-up',
                                            'price_below' => 'trending-down',
                                            'volume' => 'activity'
                                        );
                                        echo rts_get_icon($type_icons[$alert['type']] ?? 'bell', ['width' => '16', 'height' => '16']);
                                        ?>
                                        <span><?php echo esc_html(ucfirst(str_replace('_', ' ', $alert['type']))); ?></span>
                                    </div>
                                </td>
                                <td>
                                    <span class="condition"><?php echo esc_html($alert['condition']); ?></span>
                                </td>
                                <td>
                                    <span class="current-value"><?php echo esc_html($alert['current_value']); ?></span>
                                </td>
                                <td>
                                    <span class="status-badge <?php echo esc_attr($alert['status']); ?>">
                                        <?php echo esc_html(ucfirst($alert['status'])); ?>
                                    </span>
                                </td>
                                <td>
                                    <time datetime="<?php echo esc_attr($alert['created_date']); ?>">
                                        <?php echo esc_html(date('M j, Y', strtotime($alert['created_date']))); ?>
                                    </time>
                                </td>
                                <td>
                                    <div class="action-buttons">
                                        <button class="action-btn edit-alert" data-alert-id="<?php echo esc_attr($alert['id']); ?>" title="<?php esc_attr_e('Edit', 'retail-trade-scanner'); ?>">
                                            <?php echo rts_get_icon('edit', ['width' => '14', 'height' => '14']); ?>
                                        </button>
                                        
                                        <?php if ($alert['status'] === 'active') : ?>
                                            <button class="action-btn pause-alert" data-alert-id="<?php echo esc_attr($alert['id']); ?>" title="<?php esc_attr_e('Pause', 'retail-trade-scanner'); ?>">
                                                <?php echo rts_get_icon('pause', ['width' => '14', 'height' => '14']); ?>
                                            </button>
                                        <?php else : ?>
                                            <button class="action-btn resume-alert" data-alert-id="<?php echo esc_attr($alert['id']); ?>" title="<?php esc_attr_e('Resume', 'retail-trade-scanner'); ?>">
                                                <?php echo rts_get_icon('play', ['width' => '14', 'height' => '14']); ?>
                                            </button>
                                        <?php endif; ?>
                                        
                                        <button class="action-btn delete-alert" data-alert-id="<?php echo esc_attr($alert['id']); ?>" title="<?php esc_attr_e('Delete', 'retail-trade-scanner'); ?>">
                                            <?php echo rts_get_icon('trash', ['width' => '14', 'height' => '14']); ?>
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
    
    <!-- Alert Creation Panel -->
    <div class="alert-creation col-span-4">
        <div class="card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Create New Alert', 'retail-trade-scanner'); ?></h3>
                <button class="minimize-btn btn-ghost btn-sm">
                    <?php echo rts_get_icon('minus', ['width' => '16', 'height' => '16']); ?>
                </button>
            </div>
            
            <div class="card-body">
                <form id="create-alert-form" class="alert-form">
                    <!-- Stock Symbol Input -->
                    <div class="form-group">
                        <label class="form-label" for="alert-symbol">
                            <?php esc_html_e('Stock Symbol', 'retail-trade-scanner'); ?>
                        </label>
                        <input type="text" 
                               id="alert-symbol" 
                               name="symbol" 
                               class="form-input" 
                               placeholder="<?php esc_attr_e('e.g., AAPL', 'retail-trade-scanner'); ?>"
                               required
                               autocomplete="off">
                        <div class="symbol-suggestions hidden"></div>
                    </div>
                    
                    <!-- Alert Type Selection -->
                    <div class="form-group">
                        <label class="form-label"><?php esc_html_e('Alert Type', 'retail-trade-scanner'); ?></label>
                        <div class="alert-type-tabs">
                            <button type="button" class="type-tab active" data-type="price">
                                <?php echo rts_get_icon('trending-up', ['width' => '16', 'height' => '16']); ?>
                                <?php esc_html_e('Price', 'retail-trade-scanner'); ?>
                            </button>
                            <button type="button" class="type-tab" data-type="volume">
                                <?php echo rts_get_icon('activity', ['width' => '16', 'height' => '16']); ?>
                                <?php esc_html_e('Volume', 'retail-trade-scanner'); ?>
                            </button>
                            <button type="button" class="type-tab" data-type="technical">
                                <?php echo rts_get_icon('bar-chart', ['width' => '16', 'height' => '16']); ?>
                                <?php esc_html_e('Technical', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                    </div>
                    
                    <!-- Price Alert Options -->
                    <div class="alert-options" data-type="price">
                        <div class="form-group">
                            <label class="form-label"><?php esc_html_e('Price Condition', 'retail-trade-scanner'); ?></label>
                            <div class="condition-selector">
                                <select name="price_condition" class="form-select">
                                    <option value="above"><?php esc_html_e('Price rises above', 'retail-trade-scanner'); ?></option>
                                    <option value="below"><?php esc_html_e('Price falls below', 'retail-trade-scanner'); ?></option>
                                    <option value="change_percent"><?php esc_html_e('Price change %', 'retail-trade-scanner'); ?></option>
                                </select>
                                <input type="number" 
                                       name="price_value" 
                                       class="form-input" 
                                       placeholder="0.00" 
                                       step="0.01"
                                       required>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Volume Alert Options -->
                    <div class="alert-options hidden" data-type="volume">
                        <div class="form-group">
                            <label class="form-label"><?php esc_html_e('Volume Condition', 'retail-trade-scanner'); ?></label>
                            <div class="condition-selector">
                                <select name="volume_condition" class="form-select">
                                    <option value="above"><?php esc_html_e('Volume above', 'retail-trade-scanner'); ?></option>
                                    <option value="spike"><?php esc_html_e('Volume spike', 'retail-trade-scanner'); ?></option>
                                    <option value="unusual"><?php esc_html_e('Unusual volume', 'retail-trade-scanner'); ?></option>
                                </select>
                                <input type="number" 
                                       name="volume_value" 
                                       class="form-input" 
                                       placeholder="1000000"
                                       min="0">
                            </div>
                        </div>
                    </div>
                    
                    <!-- Technical Alert Options -->
                    <div class="alert-options hidden" data-type="technical">
                        <div class="form-group">
                            <label class="form-label"><?php esc_html_e('Technical Indicator', 'retail-trade-scanner'); ?></label>
                            <select name="technical_indicator" class="form-select">
                                <option value="rsi"><?php esc_html_e('RSI crosses threshold', 'retail-trade-scanner'); ?></option>
                                <option value="macd"><?php esc_html_e('MACD signal change', 'retail-trade-scanner'); ?></option>
                                <option value="sma_cross"><?php esc_html_e('Moving average crossover', 'retail-trade-scanner'); ?></option>
                                <option value="bollinger"><?php esc_html_e('Bollinger band breakout', 'retail-trade-scanner'); ?></option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label"><?php esc_html_e('Threshold Value', 'retail-trade-scanner'); ?></label>
                            <input type="number" 
                                   name="technical_value" 
                                   class="form-input" 
                                   placeholder="70"
                                   min="0" 
                                   max="100">
                        </div>
                    </div>
                    
                    <!-- Notification Options -->
                    <div class="form-group">
                        <label class="form-label"><?php esc_html_e('Notification Methods', 'retail-trade-scanner'); ?></label>
                        <div class="notification-options">
                            <label class="checkbox-option">
                                <input type="checkbox" name="notify_email" checked>
                                <span class="checkmark"></span>
                                <span><?php esc_html_e('Email', 'retail-trade-scanner'); ?></span>
                            </label>
                            
                            <label class="checkbox-option">
                                <input type="checkbox" name="notify_push" checked>
                                <span class="checkmark"></span>
                                <span><?php esc_html_e('Push Notification', 'retail-trade-scanner'); ?></span>
                            </label>
                            
                            <label class="checkbox-option">
                                <input type="checkbox" name="notify_sms">
                                <span class="checkmark"></span>
                                <span><?php esc_html_e('SMS', 'retail-trade-scanner'); ?></span>
                            </label>
                        </div>
                    </div>
                    
                    <!-- Additional Options -->
                    <div class="form-group">
                        <label class="form-label" for="alert-notes">
                            <?php esc_html_e('Notes (Optional)', 'retail-trade-scanner'); ?>
                        </label>
                        <textarea id="alert-notes" 
                                  name="notes" 
                                  class="form-textarea" 
                                  rows="3" 
                                  placeholder="<?php esc_attr_e('Add any additional notes about this alert...', 'retail-trade-scanner'); ?>"></textarea>
                    </div>
                    
                    <!-- Form Actions -->
                    <div class="form-actions">
                        <button type="button" class="btn btn-outline preview-alert">
                            <?php echo rts_get_icon('eye', ['width' => '16', 'height' => '16']); ?>
                            <?php esc_html_e('Preview', 'retail-trade-scanner'); ?>
                        </button>
                        
                        <button type="submit" class="btn btn-primary">
                            <?php echo rts_get_icon('bell', ['width' => '16', 'height' => '16']); ?>
                            <?php esc_html_e('Create Alert', 'retail-trade-scanner'); ?>
                        </button>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Alert Templates -->
        <div class="card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Quick Templates', 'retail-trade-scanner'); ?></h3>
            </div>
            
            <div class="card-body">
                <div class="alert-templates">
                    <button class="template-btn" data-template="breakout">
                        <div class="template-icon">
                            <?php echo rts_get_icon('trending-up', ['width' => '20', 'height' => '20']); ?>
                        </div>
                        <div class="template-content">
                            <div class="template-title"><?php esc_html_e('Breakout Alert', 'retail-trade-scanner'); ?></div>
                            <div class="template-desc"><?php esc_html_e('Price breaks above resistance', 'retail-trade-scanner'); ?></div>
                        </div>
                    </button>
                    
                    <button class="template-btn" data-template="volume_spike">
                        <div class="template-icon">
                            <?php echo rts_get_icon('activity', ['width' => '20', 'height' => '20']); ?>
                        </div>
                        <div class="template-content">
                            <div class="template-title"><?php esc_html_e('Volume Spike', 'retail-trade-scanner'); ?></div>
                            <div class="template-desc"><?php esc_html_e('Unusual volume activity', 'retail-trade-scanner'); ?></div>
                        </div>
                    </button>
                    
                    <button class="template-btn" data-template="rsi_oversold">
                        <div class="template-icon">
                            <?php echo rts_get_icon('bar-chart', ['width' => '20', 'height' => '20']); ?>
                        </div>
                        <div class="template-content">
                            <div class="template-title"><?php esc_html_e('RSI Oversold', 'retail-trade-scanner'); ?></div>
                            <div class="template-desc"><?php esc_html_e('RSI below 30', 'retail-trade-scanner'); ?></div>
                        </div>
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Alert Modal -->
<div id="alert-modal" class="modal-overlay hidden">
    <div class="modal glass-card">
        <div class="modal-header">
            <h2 class="modal-title"><?php esc_html_e('Alert Details', 'retail-trade-scanner'); ?></h2>
            <button class="modal-close btn-icon btn-ghost">
                <?php echo rts_get_icon('x', ['width' => '20', 'height' => '20']); ?>
            </button>
        </div>
        
        <div class="modal-body">
            <div class="alert-preview"></div>
        </div>
        
        <div class="modal-footer">
            <button class="btn btn-secondary modal-close"><?php esc_html_e('Cancel', 'retail-trade-scanner'); ?></button>
            <button class="btn btn-primary confirm-alert"><?php esc_html_e('Confirm Alert', 'retail-trade-scanner'); ?></button>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initAlertsPage();
});

function initAlertsPage() {
    // Alert type tabs
    document.querySelectorAll('.type-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const type = this.dataset.type;
            
            // Update active tab
            document.querySelectorAll('.type-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Show/hide options
            document.querySelectorAll('.alert-options').forEach(option => {
                if (option.dataset.type === type) {
                    option.classList.remove('hidden');
                } else {
                    option.classList.add('hidden');
                }
            });
        });
    });
    
    // Alert form submission
    const alertForm = document.getElementById('create-alert-form');
    if (alertForm) {
        alertForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createAlert();
        });
    }
    
    // Preview alert
    const previewBtn = document.querySelector('.preview-alert');
    if (previewBtn) {
        previewBtn.addEventListener('click', function() {
            previewAlert();
        });
    }
    
    // Template buttons
    document.querySelectorAll('.template-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const template = this.dataset.template;
            applyTemplate(template);
        });
    });
    
    // Action buttons
    document.addEventListener('click', function(e) {
        const target = e.target.closest('.action-btn');
        if (!target) return;
        
        const alertId = target.dataset.alertId;
        
        if (target.classList.contains('edit-alert')) {
            editAlert(alertId);
        } else if (target.classList.contains('pause-alert')) {
            pauseAlert(alertId);
        } else if (target.classList.contains('resume-alert')) {
            resumeAlert(alertId);
        } else if (target.classList.contains('delete-alert')) {
            deleteAlert(alertId);
        }
    });
    
    // Symbol autocomplete
    const symbolInput = document.getElementById('alert-symbol');
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
    
    function createAlert() {
        const form = document.getElementById('create-alert-form');
        const formData = new FormData(form);
        
        // Show loading
        const submitBtn = form.querySelector('[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        
        // Simulate API call
        setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
            
            RTS.showSuccess('Alert created successfully!');
            form.reset();
            
            // Refresh alerts table
            refreshAlertsTable();
        }, 2000);
    }
    
    function previewAlert() {
        const form = document.getElementById('create-alert-form');
        const formData = new FormData(form);
        
        const symbol = formData.get('symbol');
        if (!symbol) {
            RTS.showError('Please enter a stock symbol');
            return;
        }
        
        // Build preview content
        const previewContent = buildAlertPreview(formData);
        
        // Show in modal
        const modal = document.getElementById('alert-modal');
        modal.querySelector('.alert-preview').innerHTML = previewContent;
        modal.classList.remove('hidden');
    }
    
    function buildAlertPreview(formData) {
        const symbol = formData.get('symbol');
        const activeType = document.querySelector('.type-tab.active').dataset.type;
        
        let conditionText = '';
        
        if (activeType === 'price') {
            const condition = formData.get('price_condition');
            const value = formData.get('price_value');
            conditionText = `Price ${condition} $${value}`;
        } else if (activeType === 'volume') {
            const condition = formData.get('volume_condition');
            const value = formData.get('volume_value');
            conditionText = `Volume ${condition} ${value ? value.toLocaleString() : ''}`;
        } else if (activeType === 'technical') {
            const indicator = formData.get('technical_indicator');
            const value = formData.get('technical_value');
            conditionText = `${indicator.toUpperCase()} ${value}`;
        }
        
        const notifications = [];
        if (formData.get('notify_email')) notifications.push('Email');
        if (formData.get('notify_push')) notifications.push('Push');
        if (formData.get('notify_sms')) notifications.push('SMS');
        
        return `
            <div class="alert-preview-content">
                <div class="preview-header">
                    <div class="preview-symbol">
                        <h3>${symbol}</h3>
                        <span class="preview-type">${activeType.charAt(0).toUpperCase() + activeType.slice(1)} Alert</span>
                    </div>
                </div>
                
                <div class="preview-body">
                    <div class="preview-condition">
                        <h4>Condition:</h4>
                        <p>${conditionText}</p>
                    </div>
                    
                    <div class="preview-notifications">
                        <h4>Notifications:</h4>
                        <p>${notifications.join(', ')}</p>
                    </div>
                    
                    ${formData.get('notes') ? `
                        <div class="preview-notes">
                            <h4>Notes:</h4>
                            <p>${formData.get('notes')}</p>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    function applyTemplate(template) {
        const form = document.getElementById('create-alert-form');
        
        const templates = {
            breakout: {
                type: 'price',
                price_condition: 'above',
                notify_email: true,
                notify_push: true
            },
            volume_spike: {
                type: 'volume',
                volume_condition: 'spike',
                notify_email: true,
                notify_push: true
            },
            rsi_oversold: {
                type: 'technical',
                technical_indicator: 'rsi',
                technical_value: '30',
                notify_email: true
            }
        };
        
        const templateData = templates[template];
        if (templateData) {
            // Reset form
            form.reset();
            
            // Apply template values
            Object.entries(templateData).forEach(([key, value]) => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = value;
                    } else {
                        input.value = value;
                    }
                }
            });
            
            // Switch to correct tab
            if (templateData.type) {
                document.querySelector(`[data-type="${templateData.type}"]`).click();
            }
        }
    }
    
    function editAlert(alertId) {
        console.log('Editing alert:', alertId);
        RTS.showInfo('Edit alert functionality would open here');
    }
    
    function pauseAlert(alertId) {
        console.log('Pausing alert:', alertId);
        RTS.showInfo('Alert paused');
    }
    
    function resumeAlert(alertId) {
        console.log('Resuming alert:', alertId);
        RTS.showSuccess('Alert resumed');
    }
    
    function deleteAlert(alertId) {
        if (confirm('Are you sure you want to delete this alert?')) {
            console.log('Deleting alert:', alertId);
            RTS.showSuccess('Alert deleted');
        }
    }
    
    function refreshAlertsTable() {
        console.log('Refreshing alerts table...');
    }
    
    function showSymbolSuggestions(query) {
        const suggestions = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL'].filter(symbol => 
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
                });
            });
        } else {
            hideSymbolSuggestions();
        }
    }
    
    function hideSymbolSuggestions() {
        document.querySelector('.symbol-suggestions').classList.add('hidden');
    }
}
</script>

<style>
/* Alert Page Styles */
.alerts-page {
    min-height: 100vh;
}

.alerts-overview {
    margin-bottom: var(--spacing-2xl);
}

.stat-card {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
    padding: var(--spacing-xl);
    transition: all var(--transition-normal) var(--easing-standard);
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}

.stat-icon {
    width: 60px;
    height: 60px;
    border-radius: var(--radius-xl);
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--primary-100);
    color: var(--primary-600);
}

.stat-icon.triggered {
    background: var(--warning-light);
    color: var(--warning);
}

.stat-icon.success {
    background: var(--success-light);
    color: var(--success);
}

.stat-value {
    font-size: var(--text-2xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-xs);
}

.stat-label {
    font-size: var(--text-sm);
    color: var(--gray-600);
    margin: 0;
}

.alerts-filter-bar {
    padding: var(--spacing-lg) 0;
    margin-bottom: var(--spacing-lg);
}

.filter-controls {
    display: flex;
    gap: var(--spacing-md);
}

.alerts-table {
    overflow: hidden;
}

.table-header {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--gray-200);
    background: var(--gray-50);
}

.table-header h3 {
    margin: 0;
    font-size: var(--text-lg);
    font-weight: 700;
}

.table-content {
    overflow-x: auto;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table th,
.data-table td {
    padding: var(--spacing-md);
    text-align: left;
    border-bottom: 1px solid var(--gray-200);
}

.data-table th {
    font-weight: 600;
    color: var(--gray-700);
    font-size: var(--text-sm);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.symbol-cell {
    display: flex;
    flex-direction: column;
}

.symbol {
    font-weight: 700;
    color: var(--gray-900);
}

.company {
    font-size: var(--text-xs);
    color: var(--gray-500);
}

.alert-type {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--text-sm);
}

.status-badge {
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: 600;
    text-transform: uppercase;
}

.status-badge.active {
    background: var(--success-light);
    color: var(--success-dark);
}

.status-badge.triggered {
    background: var(--warning-light);
    color: var(--warning-dark);
}

.status-badge.paused {
    background: var(--gray-200);
    color: var(--gray-600);
}

.action-buttons {
    display: flex;
    gap: var(--spacing-xs);
}

.action-btn {
    padding: var(--spacing-xs);
    background: transparent;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
    color: var(--gray-500);
}

.action-btn:hover {
    color: var(--primary-600);
    border-color: var(--primary-600);
}

/* Alert Creation Panel */
.alert-creation {
    position: sticky;
    top: calc(var(--header-height, 72px) + var(--spacing-lg));
    align-self: flex-start;
}

.alert-form {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.alert-type-tabs {
    display: flex;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.type-tab {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-md);
    background: transparent;
    border: none;
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
    font-size: var(--text-sm);
}

.type-tab:hover,
.type-tab.active {
    background: var(--primary-500);
    color: white;
}

.condition-selector {
    display: flex;
    gap: var(--spacing-sm);
}

.condition-selector select {
    flex: 1;
}

.condition-selector input {
    width: 120px;
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
    cursor: pointer;
}

.checkbox-option input {
    display: none;
}

.checkbox-option .checkmark {
    width: 18px;
    height: 18px;
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
    left: 6px;
    width: 4px;
    height: 8px;
    border: solid white;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg);
}

.form-actions {
    display: flex;
    gap: var(--spacing-md);
}

.form-actions .btn {
    flex: 1;
}

/* Symbol Suggestions */
.symbol-suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--surface-raised);
    border: 1px solid var(--gray-200);
    border-top: none;
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    box-shadow: var(--shadow-lg);
    z-index: 10;
    max-height: 200px;
    overflow-y: auto;
}

.suggestion-item {
    padding: var(--spacing-sm) var(--spacing-md);
    cursor: pointer;
    transition: background-color var(--transition-fast) var(--easing-standard);
}

.suggestion-item:hover {
    background: var(--primary-100);
    color: var(--primary-700);
}

/* Alert Templates */
.alert-templates {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.template-btn {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
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
    width: 40px;
    height: 40px;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--primary-100);
    color: var(--primary-600);
    flex-shrink: 0;
}

.template-content {
    flex: 1;
}

.template-title {
    font-weight: 600;
    color: var(--gray-900);
    margin-bottom: var(--spacing-xs);
}

.template-desc {
    font-size: var(--text-sm);
    color: var(--gray-600);
}

/* Alert Preview */
.alert-preview-content {
    padding: var(--spacing-lg);
}

.preview-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--spacing-lg);
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--gray-200);
}

.preview-symbol h3 {
    margin: 0;
    font-size: var(--text-xl);
    font-weight: 700;
}

.preview-type {
    font-size: var(--text-sm);
    color: var(--primary-600);
    font-weight: 600;
}

.preview-body > div {
    margin-bottom: var(--spacing-md);
}

.preview-body h4 {
    margin: 0 0 var(--spacing-xs);
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--gray-700);
}

.preview-body p {
    margin: 0;
    color: var(--gray-800);
}

/* Responsive */
@media (max-width: 1024px) {
    .alerts-layout {
        grid-template-columns: 1fr;
    }
    
    .alert-creation {
        position: static;
        order: -1;
    }
    
    .filter-controls {
        flex-wrap: wrap;
    }
}

@media (max-width: 640px) {
    .alerts-overview {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .stat-card {
        flex-direction: column;
        text-align: center;
    }
    
    .table-content {
        font-size: var(--text-sm);
    }
    
    .data-table th,
    .data-table td {
        padding: var(--spacing-sm);
    }
    
    .alert-type-tabs {
        flex-direction: column;
    }
}

/* Dark Mode */
[data-theme="dark"] .stat-icon {
    background: var(--gray-800);
    color: var(--primary-400);
}

[data-theme="dark"] .table-header {
    background: var(--gray-800);
    border-color: var(--gray-700);
}

[data-theme="dark"] .data-table th,
[data-theme="dark"] .data-table td {
    border-color: var(--gray-700);
}

[data-theme="dark"] .symbol-suggestions {
    background: var(--gray-800);
    border-color: var(--gray-700);
}

[data-theme="dark"] .suggestion-item:hover {
    background: var(--gray-700);
}
</style>

<?php get_template_part('template-parts/layout/main-shell-end'); ?>

<?php get_footer(); ?>