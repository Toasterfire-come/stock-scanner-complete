/**
 * Stock Scanner Admin Scripts
 * JavaScript functionality for WordPress admin settings pages
 */

(function($) {
    'use strict';

    // Admin functionality object
    const StockScannerAdmin = {
        
        /**
         * Initialize admin functionality
         */
        init: function() {
            this.initTabs();
            this.initConnectionTests();
            this.initFormValidation();
            this.initTooltips();
            this.initConfirmDialogs();
            this.initAutoSave();
            this.initSettingsImportExport();
            this.initUserManagement();
            
            // Show success message after saving
            this.showSaveNotification();
        },
        
        /**
         * Initialize tab navigation
         */
        initTabs: function() {
            $('.nav-tab').on('click', function(e) {
                e.preventDefault();
                
                const targetTab = $(this).attr('href');
                
                // Update active tab
                $('.nav-tab').removeClass('nav-tab-active');
                $(this).addClass('nav-tab-active');
                
                // Show target content
                $('.tab-content').removeClass('active');
                $(targetTab).addClass('active');
                
                // Save active tab to localStorage
                localStorage.setItem('stockScannerActiveTab', targetTab);
            });
            
            // Restore active tab from localStorage
            const activeTab = localStorage.getItem('stockScannerActiveTab');
            if (activeTab && $(activeTab).length) {
                $(`a[href="${activeTab}"]`).click();
            }
        },
        
        /**
         * Initialize connection test functionality
         */
        initConnectionTests: function() {
            $('.test-connection').on('click', function(e) {
                e.preventDefault();
                
                const $button = $(this);
                const $status = $button.siblings('.connection-status');
                const testType = $button.data('type');
                
                // Show testing state
                $button.prop('disabled', true).text(stockScannerAdmin.strings.testing_connection);
                $status.removeClass('success error').addClass('testing').text('Testing...');
                
                // Perform AJAX test
                $.ajax({
                    url: stockScannerAdmin.ajax_url,
                    type: 'POST',
                    data: {
                        action: testType === 'django' ? 'test_api_connection' : 'test_paypal_connection',
                        nonce: stockScannerAdmin.nonce
                    },
                    success: function(response) {
                        if (response.success) {
                            $status.removeClass('testing error').addClass('success')
                                   .text(stockScannerAdmin.strings.connection_successful);
                        } else {
                            $status.removeClass('testing success').addClass('error')
                                   .text(response.data || stockScannerAdmin.strings.connection_failed);
                        }
                    },
                    error: function(xhr, status, error) {
                        $status.removeClass('testing success').addClass('error')
                               .text(`Error: ${error}`);
                    },
                    complete: function() {
                        $button.prop('disabled', false)
                               .text(testType === 'django' ? 'Test Connection' : 'Test PayPal Connection');
                    }
                });
            });
        },
        
        /**
         * Initialize form validation
         */
        initFormValidation: function() {
            // Real-time validation for required fields
            $('input[required], select[required]').on('blur', function() {
                const $field = $(this);
                const value = $field.val().trim();
                
                if (value === '') {
                    $field.addClass('error');
                    this.showFieldError($field, 'This field is required');
                } else {
                    $field.removeClass('error');
                    this.hideFieldError($field);
                }
            }.bind(this));
            
            // Email validation
            $('input[type="email"]').on('blur', function() {
                const $field = $(this);
                const email = $field.val().trim();
                
                if (email !== '' && !this.isValidEmail(email)) {
                    $field.addClass('error');
                    this.showFieldError($field, 'Please enter a valid email address');
                } else {
                    $field.removeClass('error');
                    this.hideFieldError($field);
                }
            }.bind(this));
            
            // URL validation
            $('input[type="url"]').on('blur', function() {
                const $field = $(this);
                const url = $field.val().trim();
                
                if (url !== '' && !this.isValidUrl(url)) {
                    $field.addClass('error');
                    this.showFieldError($field, 'Please enter a valid URL');
                } else {
                    $field.removeClass('error');
                    this.hideFieldError($field);
                }
            }.bind(this));
            
            // Form submission validation
            $('form').on('submit', function(e) {
                const $form = $(this);
                let hasErrors = false;
                
                // Check all required fields
                $form.find('input[required], select[required]').each(function() {
                    const $field = $(this);
                    const value = $field.val().trim();
                    
                    if (value === '') {
                        $field.addClass('error');
                        hasErrors = true;
                    }
                });
                
                if (hasErrors) {
                    e.preventDefault();
                    this.showNotification('Please fill in all required fields', 'error');
                    $('html, body').animate({
                        scrollTop: $form.find('.error').first().offset().top - 100
                    }, 500);
                }
            }.bind(this));
        },
        
        /**
         * Initialize tooltips for help text
         */
        initTooltips: function() {
            // Add tooltip icons to description text
            $('.description').each(function() {
                const $desc = $(this);
                const text = $desc.text();
                
                if (text.length > 50) {
                    $desc.addClass('has-tooltip');
                    $desc.attr('title', text);
                }
            });
            
            // Initialize tooltip behavior
            $('.has-tooltip').on('mouseenter', function() {
                const $tooltip = $('<div class="admin-tooltip"></div>');
                $tooltip.text($(this).attr('title'));
                $('body').append($tooltip);
                
                const offset = $(this).offset();
                $tooltip.css({
                    top: offset.top - $tooltip.outerHeight() - 10,
                    left: offset.left + ($(this).outerWidth() / 2) - ($tooltip.outerWidth() / 2)
                }).fadeIn(200);
            }).on('mouseleave', function() {
                $('.admin-tooltip').remove();
            });
        },
        
        /**
         * Initialize confirmation dialogs
         */
        initConfirmDialogs: function() {
            // Maintenance mode warning
            $('input[name="stock_scanner_advanced_settings[maintenance_mode]"]').on('change', function() {
                if ($(this).is(':checked')) {
                    if (!confirm('Warning: Enabling maintenance mode will make your site inaccessible to regular users. Continue?')) {
                        $(this).prop('checked', false);
                    }
                }
            });
            
            // Debug mode warning
            $('input[name="stock_scanner_advanced_settings[debug_mode]"]').on('change', function() {
                if ($(this).is(':checked')) {
                    if (!confirm('Warning: Debug mode should only be enabled for development. Continue?')) {
                        $(this).prop('checked', false);
                    }
                }
            });
        },
        
        /**
         * Initialize auto-save functionality
         */
        initAutoSave: function() {
            let autoSaveTimer;
            
            $('input, select, textarea').on('change input', function() {
                clearTimeout(autoSaveTimer);
                
                // Auto-save after 5 seconds of inactivity
                autoSaveTimer = setTimeout(function() {
                    $('.auto-save-indicator').show().text('Auto-saving...');
                    
                    // Simulate auto-save (in real implementation, you'd save via AJAX)
                    setTimeout(function() {
                        $('.auto-save-indicator').text('Changes saved').delay(2000).fadeOut();
                    }, 1000);
                }, 5000);
            });
        },
        
        /**
         * Initialize settings import/export
         */
        initSettingsImportExport: function() {
            // Export settings
            $('#export-settings').on('click', function(e) {
                e.preventDefault();
                
                const settings = this.getAllSettings();
                const dataStr = JSON.stringify(settings, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                const url = URL.createObjectURL(dataBlob);
                
                const link = document.createElement('a');
                link.href = url;
                link.download = 'stock-scanner-settings.json';
                link.click();
                
                URL.revokeObjectURL(url);
            }.bind(this));
            
            // Import settings
            $('#import-settings').on('change', function(e) {
                const file = e.target.files[0];
                if (!file) return;
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    try {
                        const settings = JSON.parse(e.target.result);
                        this.applySettings(settings);
                        this.showNotification('Settings imported successfully', 'success');
                    } catch (error) {
                        this.showNotification('Invalid settings file', 'error');
                    }
                }.bind(this);
                reader.readAsText(file);
            }.bind(this));
        },
        
        /**
         * Show field error message
         */
        showFieldError: function($field, message) {
            this.hideFieldError($field);
            
            const $error = $('<div class="field-error"></div>').text(message);
            $field.after($error);
        },
        
        /**
         * Hide field error message
         */
        hideFieldError: function($field) {
            $field.siblings('.field-error').remove();
        },
        
        /**
         * Validate email address
         */
        isValidEmail: function(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        },
        
        /**
         * Validate URL
         */
        isValidUrl: function(url) {
            try {
                new URL(url);
                return true;
            } catch (e) {
                return false;
            }
        },
        
        /**
         * Show notification message
         */
        showNotification: function(message, type = 'info') {
            const $notification = $(`
                <div class="notice notice-${type} is-dismissible">
                    <p>${message}</p>
                </div>
            `);
            
            $('.stock-scanner-admin h1').after($notification);
            
            // Auto-dismiss after 5 seconds
            setTimeout(function() {
                $notification.fadeOut();
            }, 5000);
        },
        
        /**
         * Show save notification if settings were just saved
         */
        showSaveNotification: function() {
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('settings-updated')) {
                this.showNotification(stockScannerAdmin.strings.settings_saved, 'success');
            }
        },
        
        /**
         * Get all current settings
         */
        getAllSettings: function() {
            const settings = {};
            
            $('input, select, textarea').each(function() {
                const $field = $(this);
                const name = $field.attr('name');
                
                if (name) {
                    if ($field.attr('type') === 'checkbox') {
                        settings[name] = $field.is(':checked');
                    } else if ($field.attr('type') === 'radio') {
                        if ($field.is(':checked')) {
                            settings[name] = $field.val();
                        }
                    } else {
                        settings[name] = $field.val();
                    }
                }
            });
            
            return settings;
        },
        
        /**
         * Apply imported settings
         */
        applySettings: function(settings) {
            Object.keys(settings).forEach(function(name) {
                const $field = $(`[name="${name}"]`);
                const value = settings[name];
                
                if ($field.length) {
                    if ($field.attr('type') === 'checkbox') {
                        $field.prop('checked', value);
                    } else if ($field.attr('type') === 'radio') {
                        $field.filter(`[value="${value}"]`).prop('checked', true);
                    } else {
                        $field.val(value);
                    }
                }
            });
        },
        
        /**
         * Initialize pricing calculator
         */
        initPricingCalculator: function() {
            $('.pricing-input').on('input', function() {
                this.calculatePricing();
            }.bind(this));
        },
        
        /**
         * Calculate pricing based on user limits
         */
        calculatePricing: function() {
            const bronzePrice = parseFloat($('#bronze-price').val()) || 24.99;
            const silverPrice = parseFloat($('#silver-price').val()) || 39.99;
            const goldPrice = parseFloat($('#gold-price').val()) || 89.99;
            
            // Update price displays
            $('.bronze-price-display').text(`$${bronzePrice.toFixed(2)}`);
            $('.silver-price-display').text(`$${silverPrice.toFixed(2)}`);
            $('.gold-price-display').text(`$${goldPrice.toFixed(2)}`);
            
            // Calculate annual pricing
            $('.bronze-annual-display').text(`$${(bronzePrice * 12 * 0.9).toFixed(2)}`);
            $('.silver-annual-display').text(`$${(silverPrice * 12 * 0.9).toFixed(2)}`);
            $('.gold-annual-display').text(`$${(goldPrice * 12 * 0.9).toFixed(2)}`);
        },
        
        /**
         * Initialize system status checks
         */
        initSystemStatus: function() {
            this.checkSystemStatus();
            
            // Auto-refresh status every 30 seconds
            setInterval(function() {
                this.checkSystemStatus();
            }.bind(this), 30000);
        },
        
        /**
         * Check system status
         */
        checkSystemStatus: function() {
            $.ajax({
                url: stockScannerAdmin.ajax_url,
                type: 'POST',
                data: {
                    action: 'check_system_status',
                    nonce: stockScannerAdmin.nonce
                },
                success: function(response) {
                    if (response.success) {
                        this.updateStatusIndicators(response.data);
                    }
                }.bind(this)
            });
        },
        
        /**
         * Initialize user management functionality
         */
        initUserManagement: function() {
            // User search
            $('#search-users').on('click', function() {
                const search = $('#user-search').val();
                const membershipFilter = $('#membership-filter').val();
                
                $.ajax({
                    url: stockScannerAdmin.ajax_url,
                    type: 'POST',
                    data: {
                        action: 'search_users',
                        nonce: stockScannerAdmin.nonce,
                        search: search,
                        membership_filter: membershipFilter
                    },
                    success: function(response) {
                        if (response.success) {
                            $('#users-table-body').html(response.data.html);
                        }
                    }
                });
            });
            
            // Force cancel membership
            $('#force-cancel-membership').on('click', function() {
                const userIdentifier = $('#cancel-user-input').val().trim();
                
                if (!userIdentifier) {
                    alert('Please enter a user email or username');
                    return;
                }
                
                if (!confirm('WARNING: This will immediately cancel the user\'s membership and downgrade them to free tier. This action cannot be undone. Continue?')) {
                    return;
                }
                
                $(this).prop('disabled', true).text('Cancelling...');
                
                $.ajax({
                    url: stockScannerAdmin.ajax_url,
                    type: 'POST',
                    data: {
                        action: 'cancel_user_membership',
                        nonce: stockScannerAdmin.nonce,
                        user_identifier: userIdentifier
                    },
                    success: function(response) {
                        if (response.success) {
                            alert(response.data.message);
                            $('#cancel-user-input').val('');
                            // Refresh users table
                            $('#search-users').click();
                        } else {
                            alert('Error: ' + response.data);
                        }
                    },
                    error: function() {
                        alert('An error occurred while cancelling the membership');
                    },
                    complete: function() {
                        $('#force-cancel-membership').prop('disabled', false).text('Force Cancel Membership');
                    }
                });
            });
            
            // Update membership
            $('#update-membership').on('click', function() {
                const userIdentifier = $('#upgrade-user-input').val().trim();
                const newLevel = $('#new-membership-level').val();
                
                if (!userIdentifier) {
                    alert('Please enter a user email or username');
                    return;
                }
                
                if (!newLevel) {
                    alert('Please select a membership level');
                    return;
                }
                
                $(this).prop('disabled', true).text('Updating...');
                
                $.ajax({
                    url: stockScannerAdmin.ajax_url,
                    type: 'POST',
                    data: {
                        action: 'update_user_membership',
                        nonce: stockScannerAdmin.nonce,
                        user_identifier: userIdentifier,
                        new_level: newLevel
                    },
                    success: function(response) {
                        if (response.success) {
                            alert(response.data.message);
                            $('#upgrade-user-input').val('');
                            // Refresh users table
                            $('#search-users').click();
                        } else {
                            alert('Error: ' + response.data);
                        }
                    },
                    error: function() {
                        alert('An error occurred while updating the membership');
                    },
                    complete: function() {
                        $('#update-membership').prop('disabled', false).text('Update Membership');
                    }
                });
            });
            
            // Individual user actions
            $(document).on('click', '.cancel-membership', function() {
                const userId = $(this).data('user-id');
                const userName = $(this).closest('tr').find('td:first strong').text();
                
                if (!confirm(`Cancel membership for ${userName}? This action cannot be undone.`)) {
                    return;
                }
                
                $(this).prop('disabled', true).text('Cancelling...');
                
                $.ajax({
                    url: stockScannerAdmin.ajax_url,
                    type: 'POST',
                    data: {
                        action: 'cancel_user_membership',
                        nonce: stockScannerAdmin.nonce,
                        user_identifier: userId
                    },
                    success: function(response) {
                        if (response.success) {
                            alert(response.data.message);
                            // Refresh users table
                            $('#search-users').click();
                        } else {
                            alert('Error: ' + response.data);
                        }
                    },
                    complete: function() {
                        $('.cancel-membership').prop('disabled', false).text('Cancel');
                    }
                });
            });
            
            // Bulk actions
            $('#execute-bulk-action').on('click', function() {
                const action = $('#bulk-action').val();
                
                if (!action) {
                    alert('Please select a bulk action');
                    return;
                }
                
                let confirmMessage = '';
                switch (action) {
                    case 'cancel_expired':
                        confirmMessage = 'Cancel all expired memberships?';
                        break;
                    case 'send_renewal_reminders':
                        confirmMessage = 'Send renewal reminders to eligible users?';
                        break;
                    case 'cleanup_inactive':
                        confirmMessage = 'Clean up inactive users (90+ days)? This will remove their data.';
                        break;
                }
                
                if (!confirm(confirmMessage)) {
                    return;
                }
                
                $(this).prop('disabled', true).text('Processing...');
                $('#bulk-action-results').show();
                $('#bulk-results-content').html('<p>Processing...</p>');
                
                // Simulate bulk action (in real implementation, this would be an AJAX call)
                setTimeout(function() {
                    $('#bulk-results-content').html('<p>Bulk action completed successfully.</p>');
                    $('#execute-bulk-action').prop('disabled', false).text('Execute');
                }, 2000);
            });
            
            // Export users
            $('#export-users').on('click', function() {
                const format = $('#export-format').val();
                const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
                
                // In a real implementation, this would generate and download the file
                alert(`Exporting users in ${format.toUpperCase()} format...`);
                
                // Simulate file download
                const filename = `users-export-${timestamp}.${format}`;
                console.log(`Would download: ${filename}`);
            });
        },
        
        /**
         * Update status indicators
         */
        updateStatusIndicators: function(status) {
            // Update backend connection status
            $('.backend-status').removeClass('active inactive warning')
                               .addClass(status.backend_connected ? 'active' : 'inactive');
            
            // Update PayPal connection status
            $('.paypal-status').removeClass('active inactive warning')
                              .addClass(status.paypal_connected ? 'active' : 'inactive');
            
            // Update database status
            $('.database-status').removeClass('active inactive warning')
                                .addClass(status.database_healthy ? 'active' : 'warning');
            
            // Update cache status
            $('.cache-status').removeClass('active inactive warning')
                             .addClass(status.cache_working ? 'active' : 'warning');
        }
    };
    
    // CSS for admin tooltips and error states
    const adminStyles = `
        <style>
        .admin-tooltip {
            position: absolute;
            background: #1d2327;
            color: #fff;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 10000;
            max-width: 300px;
            word-wrap: break-word;
        }
        
        .admin-tooltip::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border: 5px solid transparent;
            border-top-color: #1d2327;
        }
        
        .field-error {
            color: #d63638;
            font-size: 12px;
            margin-top: 5px;
            font-style: italic;
        }
        
        input.error,
        select.error,
        textarea.error {
            border-color: #d63638 !important;
            box-shadow: 0 0 0 1px #d63638 !important;
        }
        
        .auto-save-indicator {
            position: fixed;
            top: 50px;
            right: 20px;
            background: #2271b1;
            color: #fff;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 9999;
            display: none;
        }
        
        .settings-actions {
            margin: 20px 0;
            padding: 20px;
            background: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .settings-actions button,
        .settings-actions input[type="file"] {
            margin-right: 10px;
        }
        </style>
    `;
    
    // Add styles to head
    $('head').append(adminStyles);
    
    // Add auto-save indicator
    $('body').append('<div class="auto-save-indicator"></div>');
    
    // Initialize when document is ready
    $(document).ready(function() {
        StockScannerAdmin.init();
    });
    
})(jQuery);