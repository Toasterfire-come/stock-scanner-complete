<?php
/**
 * Template Name: Email Lists
 * 
 * Newsletter subscriptions and email list management
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('Email Lists', 'retail-trade-scanner'),
    'page_description' => __('Manage your newsletter subscriptions and email preferences', 'retail-trade-scanner'),
    'page_class' => 'email-page'
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

// Sample email lists
$email_lists = array(
    array(
        'id' => 'daily-digest',
        'title' => 'Daily Market Digest',
        'description' => 'Daily summary of market activity, top movers, and key events',
        'frequency' => 'Daily',
        'subscribers' => '12,547',
        'subscribed' => true
    ),
    array(
        'id' => 'weekly-analysis',
        'title' => 'Weekly Analysis Report',
        'description' => 'In-depth weekly market analysis with sector performance and outlook',
        'frequency' => 'Weekly',
        'subscribers' => '8,923',
        'subscribed' => false
    ),
    array(
        'id' => 'earnings-alerts',
        'title' => 'Earnings Alerts',
        'description' => 'Get notified about upcoming earnings for stocks in your watchlist',
        'frequency' => 'As needed',
        'subscribers' => '15,632',
        'subscribed' => true
    )
);
?>

<div class="email-content grid grid-cols-12 gap-lg">
    
    <!-- Email Lists -->
    <div class="email-lists col-span-8">
        
        <!-- Newsletter Lists -->
        <div class="newsletter-section">
            <div class="section-header">
                <h2><?php esc_html_e('Newsletter Subscriptions', 'retail-trade-scanner'); ?></h2>
                <p><?php esc_html_e('Stay informed with our curated market insights and analysis', 'retail-trade-scanner'); ?></p>
            </div>
            
            <div class="newsletter-grid">
                <?php foreach ($email_lists as $list) : ?>
                    <div class="newsletter-card card">
                        <div class="card-header">
                            <div class="newsletter-info">
                                <h3 class="newsletter-title"><?php echo esc_html($list['title']); ?></h3>
                                <p class="newsletter-description"><?php echo esc_html($list['description']); ?></p>
                            </div>
                            
                            <div class="subscription-toggle">
                                <label class="switch">
                                    <input type="checkbox" class="newsletter-toggle" 
                                           data-list-id="<?php echo esc_attr($list['id']); ?>"
                                           <?php checked($list['subscribed']); ?>>
                                    <span class="slider"></span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="card-body">
                            <div class="newsletter-meta">
                                <div class="meta-item">
                                    <span class="meta-label"><?php esc_html_e('Frequency:', 'retail-trade-scanner'); ?></span>
                                    <span class="meta-value"><?php echo esc_html($list['frequency']); ?></span>
                                </div>
                                <div class="meta-item">
                                    <span class="meta-label"><?php esc_html_e('Subscribers:', 'retail-trade-scanner'); ?></span>
                                    <span class="meta-value"><?php echo esc_html($list['subscribers']); ?></span>
                                </div>
                            </div>
                            
                            <?php if ($list['subscribed']) : ?>
                                <div class="subscription-status subscribed">
                                    <?php echo rts_get_icon('check-circle', ['width' => '16', 'height' => '16']); ?>
                                    <?php esc_html_e('You\'re subscribed', 'retail-trade-scanner'); ?>
                                </div>
                            <?php else : ?>
                                <div class="subscription-status unsubscribed">
                                    <?php echo rts_get_icon('x-circle', ['width' => '16', 'height' => '16']); ?>
                                    <?php esc_html_e('Not subscribed', 'retail-trade-scanner'); ?>
                                </div>
                            <?php endif; ?>
                        </div>
                        
                        <div class="card-footer">
                            <button class="btn btn-outline btn-sm preview-newsletter" data-list-id="<?php echo esc_attr($list['id']); ?>">
                                <?php esc_html_e('Preview', 'retail-trade-scanner'); ?>
                            </button>
                            
                            <button class="btn btn-ghost btn-sm view-archive" data-list-id="<?php echo esc_attr($list['id']); ?>">
                                <?php esc_html_e('View Archive', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
        
        <!-- Custom Alert Lists -->
        <div class="custom-alerts-section mt-2xl">
            <div class="section-header">
                <h2><?php esc_html_e('Custom Email Alerts', 'retail-trade-scanner'); ?></h2>
                <p><?php esc_html_e('Create personalized email alerts based on your trading criteria', 'retail-trade-scanner'); ?></p>
            </div>
            
            <div class="custom-alerts-list">
                <div class="alert-item card">
                    <div class="card-body">
                        <div class="alert-info">
                            <h3><?php esc_html_e('Watchlist Movers', 'retail-trade-scanner'); ?></h3>
                            <p><?php esc_html_e('Get notified when stocks in your watchlist move more than 5%', 'retail-trade-scanner'); ?></p>
                        </div>
                        
                        <div class="alert-actions">
                            <button class="btn btn-outline btn-sm">
                                <?php esc_html_e('Edit', 'retail-trade-scanner'); ?>
                            </button>
                            <label class="switch">
                                <input type="checkbox" checked>
                                <span class="slider"></span>
                            </label>
                        </div>
                    </div>
                </div>
                
                <div class="alert-item card">
                    <div class="card-body">
                        <div class="alert-info">
                            <h3><?php esc_html_e('Volume Spikes', 'retail-trade-scanner'); ?></h3>
                            <p><?php esc_html_e('Alert me when any stock has 2x average volume', 'retail-trade-scanner'); ?></p>
                        </div>
                        
                        <div class="alert-actions">
                            <button class="btn btn-outline btn-sm">
                                <?php esc_html_e('Edit', 'retail-trade-scanner'); ?>
                            </button>
                            <label class="switch">
                                <input type="checkbox">
                                <span class="slider"></span>
                            </label>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="add-alert-btn-container">
                <button class="btn btn-primary create-custom-alert">
                    <?php echo rts_get_icon('plus', ['width' => '16', 'height' => '16']); ?>
                    <?php esc_html_e('Create Custom Alert', 'retail-trade-scanner'); ?>
                </button>
            </div>
        </div>
    </div>
    
    <!-- Email Preferences Sidebar -->
    <div class="email-preferences col-span-4">
        
        <!-- Preferences Card -->
        <div class="preferences-card card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Email Preferences', 'retail-trade-scanner'); ?></h3>
            </div>
            
            <div class="card-body">
                <form class="preferences-form" id="email-preferences-form">
                    
                    <div class="form-field">
                        <label class="form-label" for="email-frequency">
                            <?php esc_html_e('Default Frequency', 'retail-trade-scanner'); ?>
                        </label>
                        <select class="form-select" id="email-frequency" name="frequency">
                            <option value="immediate"><?php esc_html_e('Immediate', 'retail-trade-scanner'); ?></option>
                            <option value="hourly"><?php esc_html_e('Hourly Digest', 'retail-trade-scanner'); ?></option>
                            <option value="daily" selected><?php esc_html_e('Daily Digest', 'retail-trade-scanner'); ?></option>
                            <option value="weekly"><?php esc_html_e('Weekly Summary', 'retail-trade-scanner'); ?></option>
                        </select>
                    </div>
                    
                    <div class="form-field">
                        <label class="form-label" for="email-format">
                            <?php esc_html_e('Email Format', 'retail-trade-scanner'); ?>
                        </label>
                        <div class="format-options">
                            <label class="radio-option">
                                <input type="radio" name="format" value="html" checked>
                                <span class="radio-label"><?php esc_html_e('HTML (Formatted)', 'retail-trade-scanner'); ?></span>
                            </label>
                            <label class="radio-option">
                                <input type="radio" name="format" value="text">
                                <span class="radio-label"><?php esc_html_e('Plain Text', 'retail-trade-scanner'); ?></span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-field">
                        <label class="form-label"><?php esc_html_e('Content Preferences', 'retail-trade-scanner'); ?></label>
                        <div class="content-options">
                            <label class="checkbox-option">
                                <input type="checkbox" name="content[]" value="market-summary" checked>
                                <span class="option-label"><?php esc_html_e('Market Summary', 'retail-trade-scanner'); ?></span>
                            </label>
                            <label class="checkbox-option">
                                <input type="checkbox" name="content[]" value="top-movers" checked>
                                <span class="option-label"><?php esc_html_e('Top Movers', 'retail-trade-scanner'); ?></span>
                            </label>
                            <label class="checkbox-option">
                                <input type="checkbox" name="content[]" value="earnings" checked>
                                <span class="option-label"><?php esc_html_e('Earnings Calendar', 'retail-trade-scanner'); ?></span>
                            </label>
                            <label class="checkbox-option">
                                <input type="checkbox" name="content[]" value="news">
                                <span class="option-label"><?php esc_html_e('Market News', 'retail-trade-scanner'); ?></span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary btn-block">
                            <?php esc_html_e('Save Preferences', 'retail-trade-scanner'); ?>
                        </button>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Statistics Card -->
        <div class="stats-card card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Email Statistics', 'retail-trade-scanner'); ?></h3>
            </div>
            
            <div class="card-body">
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value">47</div>
                        <div class="stat-label"><?php esc_html_e('Emails This Month', 'retail-trade-scanner'); ?></div>
                    </div>
                    
                    <div class="stat-item">
                        <div class="stat-value">89%</div>
                        <div class="stat-label"><?php esc_html_e('Open Rate', 'retail-trade-scanner'); ?></div>
                    </div>
                    
                    <div class="stat-item">
                        <div class="stat-value">3</div>
                        <div class="stat-label"><?php esc_html_e('Active Subscriptions', 'retail-trade-scanner'); ?></div>
                    </div>
                    
                    <div class="stat-item">
                        <div class="stat-value">12</div>
                        <div class="stat-label"><?php esc_html_e('Custom Alerts', 'retail-trade-scanner'); ?></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="quick-actions-card card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Quick Actions', 'retail-trade-scanner'); ?></h3>
            </div>
            
            <div class="card-body">
                <div class="action-buttons">
                    <button class="action-btn" id="pause-all-emails">
                        <?php echo rts_get_icon('pause', ['width' => '16', 'height' => '16']); ?>
                        <span><?php esc_html_e('Pause All Emails', 'retail-trade-scanner'); ?></span>
                    </button>
                    
                    <button class="action-btn" id="export-preferences">
                        <?php echo rts_get_icon('download', ['width' => '16', 'height' => '16']); ?>
                        <span><?php esc_html_e('Export Preferences', 'retail-trade-scanner'); ?></span>
                    </button>
                    
                    <button class="action-btn" id="test-email">
                        <?php echo rts_get_icon('send', ['width' => '16', 'height' => '16']); ?>
                        <span><?php esc_html_e('Send Test Email', 'retail-trade-scanner'); ?></span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initEmailPage();
});

function initEmailPage() {
    // Newsletter subscription toggles
    document.querySelectorAll('.newsletter-toggle').forEach(toggle => {
        toggle.addEventListener('change', function() {
            const listId = this.dataset.listId;
            const isSubscribed = this.checked;
            toggleNewsletterSubscription(listId, isSubscribed);
        });
    });
    
    // Preview newsletter
    document.querySelectorAll('.preview-newsletter').forEach(btn => {
        btn.addEventListener('click', function() {
            const listId = this.dataset.listId;
            previewNewsletter(listId);
        });
    });
    
    // View archive
    document.querySelectorAll('.view-archive').forEach(btn => {
        btn.addEventListener('click', function() {
            const listId = this.dataset.listId;
            viewArchive(listId);
        });
    });
    
    // Email preferences form
    const preferencesForm = document.getElementById('email-preferences-form');
    if (preferencesForm) {
        preferencesForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveEmailPreferences();
        });
    }
    
    // Create custom alert
    const createAlertBtn = document.querySelector('.create-custom-alert');
    if (createAlertBtn) {
        createAlertBtn.addEventListener('click', function() {
            createCustomAlert();
        });
    }
    
    // Quick actions
    document.getElementById('pause-all-emails')?.addEventListener('click', pauseAllEmails);
    document.getElementById('export-preferences')?.addEventListener('click', exportPreferences);
    document.getElementById('test-email')?.addEventListener('click', sendTestEmail);
    
    function toggleNewsletterSubscription(listId, isSubscribed) {
        console.log(`${isSubscribed ? 'Subscribing to' : 'Unsubscribing from'} ${listId}`);
        
        // Update UI
        const card = document.querySelector(`[data-list-id="${listId}"]`).closest('.newsletter-card');
        const statusElement = card.querySelector('.subscription-status');
        
        if (isSubscribed) {
            statusElement.className = 'subscription-status subscribed';
            statusElement.innerHTML = '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> You\'re subscribed';
            RTS.showSuccess('Successfully subscribed to newsletter');
        } else {
            statusElement.className = 'subscription-status unsubscribed';
            statusElement.innerHTML = '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> Not subscribed';
            RTS.showInfo('Unsubscribed from newsletter');
        }
    }
    
    function previewNewsletter(listId) {
        console.log('Previewing newsletter:', listId);
        RTS.showInfo('Newsletter preview would open here');
    }
    
    function viewArchive(listId) {
        console.log('Viewing archive for:', listId);
        RTS.showInfo('Newsletter archive would open here');
    }
    
    function saveEmailPreferences() {
        const formData = new FormData(preferencesForm);
        const preferences = Object.fromEntries(formData.entries());
        
        console.log('Saving email preferences:', preferences);
        
        const submitBtn = preferencesForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving...';
        
        setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Save Preferences';
            RTS.showSuccess('Email preferences saved successfully');
        }, 1500);
    }
    
    function createCustomAlert() {
        console.log('Creating custom alert');
        RTS.showInfo('Custom alert creator would open here');
    }
    
    function pauseAllEmails() {
        console.log('Pausing all emails');
        RTS.showWarning('All email notifications paused');
    }
    
    function exportPreferences() {
        console.log('Exporting preferences');
        RTS.showSuccess('Preferences exported successfully');
    }
    
    function sendTestEmail() {
        const btn = document.getElementById('test-email');
        btn.disabled = true;
        btn.innerHTML = '<svg width="16" height="16" class="animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg> <span>Sending...</span>';
        
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg> <span>Send Test Email</span>';
            RTS.showSuccess('Test email sent successfully');
        }, 2000);
    }
}
</script>

<style>
/* Email Page Styles */
.email-content {
    margin-bottom: var(--spacing-2xl);
}

.section-header {
    margin-bottom: var(--spacing-xl);
}

.section-header h2 {
    font-size: var(--text-2xl);
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-sm);
}

.section-header p {
    color: var(--gray-600);
    font-size: var(--text-base);
    margin: 0;
}

.newsletter-grid {
    display: grid;
    gap: var(--spacing-lg);
}

.newsletter-card {
    transition: all var(--transition-fast) var(--easing-standard);
}

.newsletter-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.newsletter-info h3 {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-xs);
}

.newsletter-info p {
    color: var(--gray-600);
    font-size: var(--text-sm);
    margin: 0;
    line-height: 1.5;
}

.subscription-toggle {
    flex-shrink: 0;
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

.newsletter-meta {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.meta-item {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.meta-label {
    font-size: var(--text-xs);
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.meta-value {
    font-weight: 600;
    color: var(--gray-900);
    font-size: var(--text-sm);
}

.subscription-status {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: var(--text-sm);
    font-weight: 600;
    padding: var(--spacing-sm);
    border-radius: var(--radius-lg);
}

.subscription-status.subscribed {
    background: var(--success-light);
    color: var(--success);
}

.subscription-status.unsubscribed {
    background: var(--gray-100);
    color: var(--gray-600);
}

.custom-alerts-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
}

.alert-item .card-body {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--spacing-lg);
}

.alert-info h3 {
    font-size: var(--text-base);
    font-weight: 600;
    color: var(--gray-900);
    margin: 0 0 var(--spacing-xs);
}

.alert-info p {
    font-size: var(--text-sm);
    color: var(--gray-600);
    margin: 0;
}

.alert-actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    flex-shrink: 0;
}

.add-alert-btn-container {
    text-align: center;
}

.format-options,
.content-options {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.radio-option,
.checkbox-option {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-lg);
}

.stat-item {
    text-align: center;
}

.stat-value {
    font-size: var(--text-2xl);
    font-weight: 700;
    color: var(--primary-600);
    margin-bottom: var(--spacing-xs);
}

.stat-label {
    font-size: var(--text-xs);
    color: var(--gray-600);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.action-buttons {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.action-btn {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-md);
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
    text-align: left;
    width: 100%;
}

.action-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateX(4px);
}

/* Responsive Design */
@media (max-width: 1024px) {
    .email-content {
        grid-template-columns: 1fr;
    }
    
    .email-preferences {
        order: -1;
    }
}

@media (max-width: 640px) {
    .newsletter-card .card-header {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--spacing-md);
    }
    
    .subscription-toggle {
        align-self: stretch;
    }
    
    .newsletter-meta {
        grid-template-columns: 1fr;
    }
    
    .alert-item .card-body {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .alert-actions {
        width: 100%;
        justify-content: space-between;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
}

/* Dark Mode */
[data-theme="dark"] .section-header h2 {
    color: var(--gray-100);
}

[data-theme="dark"] .section-header p,
[data-theme="dark"] .newsletter-info p,
[data-theme="dark"] .alert-info p {
    color: var(--gray-400);
}

[data-theme="dark"] .newsletter-info h3,
[data-theme="dark"] .alert-info h3,
[data-theme="dark"] .meta-value {
    color: var(--gray-200);
}

[data-theme="dark"] .subscription-status.unsubscribed {
    background: var(--gray-700);
    color: var(--gray-300);
}
</style>

<?php get_footer(); ?>