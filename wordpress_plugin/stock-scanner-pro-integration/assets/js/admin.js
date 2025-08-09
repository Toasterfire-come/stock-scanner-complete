/**
 * Stock Scanner Admin Security Dashboard JavaScript
 * Handles bot detection analytics, user management, and security controls
 */

(function($) {
    'use strict';

    // Main Admin Object
    window.StockScannerAdmin = {
        init: function() {
            this.bindEvents();
            this.initCharts();
            this.startRealTimeUpdates();
            this.initNotifications();
        },

        // Event Bindings
        bindEvents: function() {
            // Tab switching
            $(document).on('click', '.nav-tab', this.handleTabSwitch);
            
            // User management
            $(document).on('click', '.ban-user-btn', this.showBanModal);
            $(document).on('click', '.unban-user-btn', this.unbanUser);
            $(document).on('submit', '#ban-user-form', this.banUser);
            $(document).on('click', '.cancel-modal', this.hideModal);
            
            // IP management
            $(document).on('click', '.block-ip-btn', this.blockIP);
            
            // Bulk actions
            $(document).on('click', '#bulk-ban-high-bot-score', this.bulkBanHighBotScore);
            $(document).on('click', '#bulk-reset-limits', this.bulkResetLimits);
            $(document).on('click', '#bulk-unban-system', this.bulkUnbanSystem);
            $(document).on('click', '#analyze-patterns', this.analyzePatterns);
            $(document).on('click', '#export-security-log', this.exportSecurityLog);
            
            // Real-time data refresh
            $(document).on('click', '.refresh-data-btn', this.refreshData);
            
            // Details viewing
            $(document).on('click', '.view-details-btn', this.viewDetails);
            
            // Auto-refresh toggle
            $(document).on('change', '#auto-refresh-toggle', this.toggleAutoRefresh);
            
            // Settings form
            $(document).on('submit', '#rate-limits-form', this.updateRateLimits);
            
            // Search and filters
            $(document).on('input', '.search-filter', this.handleSearch);
            $(document).on('change', '.filter-select', this.handleFilter);
        },

        // Tab Switching
        handleTabSwitch: function(e) {
            e.preventDefault();
            const $tab = $(this);
            const targetTab = $tab.attr('href');
            
            // Update tab states
            $('.nav-tab').removeClass('nav-tab-active');
            $tab.addClass('nav-tab-active');
            
            // Show/hide content
            $('.tab-content').hide();
            $(targetTab).show();
            
            // Load tab-specific data if needed
            StockScannerAdmin.loadTabData(targetTab);
        },

        // Load data for specific tabs
        loadTabData: function(tabId) {
            switch(tabId) {
                case '#suspicious-users':
                    this.loadSuspiciousUsers();
                    break;
                case '#banned-users':
                    this.loadBannedUsers();
                    break;
                case '#bulk-actions':
                    this.loadBulkActionStats();
                    break;
            }
        },

        // Show Ban Modal
        showBanModal: function() {
            const userId = $(this).data('user-id');
            const userName = $(this).closest('tr').find('.user-login').text();
            
            $('#ban-user-id').val(userId);
            $('#ban-user-modal h3').text('Ban User: ' + userName);
            $('#ban-user-modal').show();
            $('#ban-reason').focus();
        },

        // Hide Modal
        hideModal: function() {
            $('.stock-scanner-modal').hide();
            $('form').trigger('reset');
        },

        // Ban User
        banUser: function(e) {
            e.preventDefault();
            
            const $form = $(this);
            const formData = $form.serialize();
            const $submitBtn = $form.find('button[type="submit"]');
            
            // Show loading state
            $submitBtn.prop('disabled', true).text('Banning...');
            
            $.post(ajaxurl, {
                action: 'stock_scanner_ban_user',
                nonce: stockScannerAdmin.nonce,
                ...Object.fromEntries(new URLSearchParams(formData))
            })
            .done(function(response) {
                if (response.success) {
                    StockScannerAdmin.showNotification('User banned successfully', 'success');
                    StockScannerAdmin.hideModal();
                    StockScannerAdmin.refreshCurrentTab();
                } else {
                    StockScannerAdmin.showNotification('Error: ' + response.data, 'error');
                }
            })
            .fail(function() {
                StockScannerAdmin.showNotification('Network error occurred', 'error');
            })
            .always(function() {
                $submitBtn.prop('disabled', false).text('Ban User');
            });
        },

        // Unban User
        unbanUser: function() {
            if (!confirm(stockScannerAdmin.strings.confirm_unban)) {
                return;
            }
            
            const userId = $(this).data('user-id');
            const $btn = $(this);
            
            $btn.prop('disabled', true).text('Unbanning...');
            
            $.post(ajaxurl, {
                action: 'stock_scanner_unban_user',
                nonce: stockScannerAdmin.nonce,
                user_id: userId
            })
            .done(function(response) {
                if (response.success) {
                    StockScannerAdmin.showNotification('User unbanned successfully', 'success');
                    StockScannerAdmin.refreshCurrentTab();
                } else {
                    StockScannerAdmin.showNotification('Error: ' + response.data, 'error');
                }
            })
            .fail(function() {
                StockScannerAdmin.showNotification('Network error occurred', 'error');
            })
            .always(function() {
                $btn.prop('disabled', false).text('Unban');
            });
        },

        // Block IP Address
        blockIP: function() {
            const ip = $(this).data('ip');
            
            if (!confirm('Are you sure you want to block IP: ' + ip + '?')) {
                return;
            }
            
            const $btn = $(this);
            $btn.prop('disabled', true).text('Blocking...');
            
            $.post(ajaxurl, {
                action: 'stock_scanner_block_ip',
                nonce: stockScannerAdmin.nonce,
                ip_address: ip
            })
            .done(function(response) {
                if (response.success) {
                    StockScannerAdmin.showNotification('IP blocked successfully', 'success');
                    $btn.closest('tr').addClass('blocked-ip').fadeTo(500, 0.5);
                } else {
                    StockScannerAdmin.showNotification('Error: ' + response.data, 'error');
                }
            })
            .fail(function() {
                StockScannerAdmin.showNotification('Network error occurred', 'error');
            })
            .always(function() {
                $btn.prop('disabled', false).text('Block IP');
            });
        },

        // Bulk Ban High Bot Score Users
        bulkBanHighBotScore: function() {
            if (!confirm('This will ban ALL users with bot score > 80%. Are you sure?')) {
                return;
            }
            
            const $btn = $(this);
            $btn.prop('disabled', true).text('Processing...');
            
            $.post(ajaxurl, {
                action: 'stock_scanner_bulk_ban_high_score',
                nonce: stockScannerAdmin.nonce,
                threshold: 80
            })
            .done(function(response) {
                if (response.success) {
                    StockScannerAdmin.showNotification(`Banned ${response.data.count} users`, 'success');
                    StockScannerAdmin.refreshCurrentTab();
                } else {
                    StockScannerAdmin.showNotification('Error: ' + response.data, 'error');
                }
            })
            .always(function() {
                $btn.prop('disabled', false).text('Ban All Users with Bot Score > 80%');
            });
        },

        // Bulk Reset Rate Limits
        bulkResetLimits: function() {
            if (!confirm('This will reset all rate limits. Continue?')) {
                return;
            }
            
            const $btn = $(this);
            $btn.prop('disabled', true).text('Resetting...');
            
            $.post(ajaxurl, {
                action: 'stock_scanner_bulk_reset_limits',
                nonce: stockScannerAdmin.nonce
            })
            .done(function(response) {
                if (response.success) {
                    StockScannerAdmin.showNotification('Rate limits reset successfully', 'success');
                    StockScannerAdmin.refreshCurrentTab();
                } else {
                    StockScannerAdmin.showNotification('Error: ' + response.data, 'error');
                }
            })
            .always(function() {
                $btn.prop('disabled', false).text('Reset All Rate Limits');
            });
        },

        // Bulk Unban System-Banned Users
        bulkUnbanSystem: function() {
            if (!confirm('This will unban all system-banned users. Continue?')) {
                return;
            }
            
            const $btn = $(this);
            $btn.prop('disabled', true).text('Unbanning...');
            
            $.post(ajaxurl, {
                action: 'stock_scanner_bulk_unban_system',
                nonce: stockScannerAdmin.nonce
            })
            .done(function(response) {
                if (response.success) {
                    StockScannerAdmin.showNotification(`Unbanned ${response.data.count} users`, 'success');
                    StockScannerAdmin.refreshCurrentTab();
                } else {
                    StockScannerAdmin.showNotification('Error: ' + response.data, 'error');
                }
            })
            .always(function() {
                $btn.prop('disabled', false).text('Unban All System-Banned Users');
            });
        },

        // Analyze Patterns
        analyzePatterns: function() {
            const $btn = $(this);
            $btn.prop('disabled', true).text('Analyzing...');
            
            $.post(ajaxurl, {
                action: 'stock_scanner_analyze_patterns',
                nonce: stockScannerAdmin.nonce
            })
            .done(function(response) {
                if (response.success) {
                    StockScannerAdmin.showNotification('Pattern analysis completed', 'success');
                    if (response.data.suspicious_patterns > 0) {
                        StockScannerAdmin.showNotification(`Found ${response.data.suspicious_patterns} suspicious patterns`, 'warning');
                    }
                    StockScannerAdmin.refreshCurrentTab();
                } else {
                    StockScannerAdmin.showNotification('Error: ' + response.data, 'error');
                }
            })
            .always(function() {
                $btn.prop('disabled', false).text('Run Pattern Analysis');
            });
        },

        // Export Security Log
        exportSecurityLog: function() {
            const $btn = $(this);
            $btn.prop('disabled', true).text('Exporting...');
            
            // Create download link
            const exportUrl = ajaxurl + '?action=stock_scanner_export_log&nonce=' + stockScannerAdmin.nonce;
            
            // Create hidden iframe for download
            const $iframe = $('<iframe>', {
                src: exportUrl,
                style: 'display: none;'
            }).appendTo('body');
            
            // Clean up after download
            setTimeout(function() {
                $iframe.remove();
                $btn.prop('disabled', false).text('Export Security Log');
                StockScannerAdmin.showNotification('Security log exported successfully', 'success');
            }, 2000);
        },

        // Initialize Charts
        initCharts: function() {
            if (typeof Chart === 'undefined') {
                console.warn('Chart.js not loaded');
                return;
            }
            
            this.initBotDetectionChart();
            this.initSecurityEventsChart();
            this.initRateLimitChart();
        },

        // Bot Detection Chart
        initBotDetectionChart: function() {
            const ctx = document.getElementById('botDetectionChart');
            if (!ctx) return;
            
            // Get data from page or via AJAX
            this.loadChartData('bot_detection', function(data) {
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Total Requests',
                            data: data.total_requests,
                            borderColor: '#2271b1',
                            backgroundColor: 'rgba(34, 113, 177, 0.1)',
                            tension: 0.4,
                            fill: true
                        }, {
                            label: 'Suspicious Requests',
                            data: data.suspicious_requests,
                            borderColor: '#d63638',
                            backgroundColor: 'rgba(214, 54, 56, 0.1)',
                            tension: 0.4,
                            fill: true
                        }, {
                            label: 'Blocked Requests',
                            data: data.blocked_requests,
                            borderColor: '#dba617',
                            backgroundColor: 'rgba(219, 166, 23, 0.1)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Bot Detection Trends (7 Days)'
                            },
                            legend: {
                                position: 'bottom'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: {
                                    color: '#f0f0f0'
                                }
                            },
                            x: {
                                grid: {
                                    color: '#f0f0f0'
                                }
                            }
                        },
                        interaction: {
                            intersect: false,
                            mode: 'index'
                        }
                    }
                });
            });
        },

        // Load Chart Data
        loadChartData: function(chartType, callback) {
            $.post(ajaxurl, {
                action: 'stock_scanner_get_chart_data',
                nonce: stockScannerAdmin.nonce,
                chart_type: chartType
            })
            .done(function(response) {
                if (response.success && callback) {
                    callback(response.data);
                }
            })
            .fail(function() {
                console.error('Failed to load chart data for:', chartType);
            });
        },

        // Real-time Updates
        startRealTimeUpdates: function() {
            // Update every 30 seconds
            this.updateInterval = setInterval(function() {
                if ($('#auto-refresh-toggle').is(':checked')) {
                    StockScannerAdmin.updateRealTimeData();
                }
            }, 30000);
        },

        // Update Real-time Data
        updateRealTimeData: function() {
            $.post(ajaxurl, {
                action: 'stock_scanner_get_realtime_data',
                nonce: stockScannerAdmin.nonce
            })
            .done(function(response) {
                if (response.success) {
                    StockScannerAdmin.updateDashboardCards(response.data);
                }
            })
            .fail(function() {
                console.warn('Failed to update real-time data');
            });
        },

        // Update Dashboard Cards
        updateDashboardCards: function(data) {
            // Update security events count
            $('.security-card .card-number').each(function(index) {
                const $card = $(this);
                const cardType = $card.closest('.security-card').find('.card-content h3').text().toLowerCase();
                
                if (cardType.includes('security events')) {
                    $card.text(data.security_events || 0);
                } else if (cardType.includes('bot detection')) {
                    $card.text(data.bot_detection_rate + '%' || '0%');
                } else if (cardType.includes('banned users')) {
                    $card.text(data.banned_users || 0);
                } else if (cardType.includes('rate limited')) {
                    $card.text(data.rate_limited_ips || 0);
                }
            });
            
            // Add pulse animation to updated cards
            $('.security-card').addClass('updated').delay(1000).queue(function() {
                $(this).removeClass('updated').dequeue();
            });
        },

        // Notifications System
        initNotifications: function() {
            // Check for new notifications every minute
            setInterval(function() {
                StockScannerAdmin.checkNewNotifications();
            }, 60000);
        },

        // Show Notification
        showNotification: function(message, type, duration) {
            type = type || 'info';
            duration = duration || 5000;
            
            const $notification = $('<div>', {
                class: 'notice notice-' + type + ' is-dismissible stock-scanner-notification',
                html: '<p>' + message + '</p><button type="button" class="notice-dismiss"><span class="screen-reader-text">Dismiss</span></button>'
            });
            
            // Add to top of admin area
            $('.stock-scanner-admin').prepend($notification);
            
            // Auto-dismiss
            setTimeout(function() {
                $notification.fadeOut(function() {
                    $(this).remove();
                });
            }, duration);
            
            // Manual dismiss
            $notification.on('click', '.notice-dismiss', function() {
                $notification.fadeOut(function() {
                    $(this).remove();
                });
            });
        },

        // Refresh Current Tab
        refreshCurrentTab: function() {
            const activeTab = $('.nav-tab-active').attr('href');
            this.loadTabData(activeTab);
            
            // Also refresh dashboard cards if on main page
            if (window.location.href.includes('stock-scanner-security')) {
                this.updateRealTimeData();
            }
        },

        // View Details Modal
        viewDetails: function() {
            const details = $(this).data('details');
            let formattedDetails;
            
            try {
                const parsedDetails = JSON.parse(details);
                formattedDetails = JSON.stringify(parsedDetails, null, 2);
            } catch (e) {
                formattedDetails = details;
            }
            
            // Create and show details modal
            const $modal = $('<div class="stock-scanner-modal">').html(`
                <div class="modal-content">
                    <h3>Event Details</h3>
                    <pre style="background: #f9f9f9; padding: 15px; border-radius: 4px; max-height: 400px; overflow-y: auto;">${formattedDetails}</pre>
                    <div class="modal-actions">
                        <button type="button" class="button cancel-modal">Close</button>
                    </div>
                </div>
            `);
            
            $('body').append($modal);
        },

        // Toggle Auto-refresh
        toggleAutoRefresh: function() {
            const isEnabled = $(this).is(':checked');
            
            if (isEnabled) {
                StockScannerAdmin.showNotification('Auto-refresh enabled', 'success', 2000);
            } else {
                StockScannerAdmin.showNotification('Auto-refresh disabled', 'info', 2000);
            }
        },

        // Handle Search
        handleSearch: function() {
            const searchTerm = $(this).val().toLowerCase();
            const $table = $(this).closest('.table-container').find('table tbody');
            
            $table.find('tr').each(function() {
                const rowText = $(this).text().toLowerCase();
                $(this).toggle(rowText.includes(searchTerm));
            });
        },

        // Handle Filter
        handleFilter: function() {
            const filterValue = $(this).val();
            const filterType = $(this).data('filter-type');
            const $table = $(this).closest('.table-container').find('table tbody');
            
            if (filterValue === 'all') {
                $table.find('tr').show();
                return;
            }
            
            $table.find('tr').each(function() {
                const $row = $(this);
                let shouldShow = false;
                
                switch (filterType) {
                    case 'severity':
                        shouldShow = $row.hasClass('severity-' + filterValue);
                        break;
                    case 'risk':
                        shouldShow = $row.hasClass(filterValue + '-risk');
                        break;
                    case 'status':
                        shouldShow = $row.find('.status-' + filterValue).length > 0;
                        break;
                }
                
                $row.toggle(shouldShow);
            });
        },

        // Check for new notifications
        checkNewNotifications: function() {
            $.post(ajaxurl, {
                action: 'stock_scanner_check_notifications',
                nonce: stockScannerAdmin.nonce
            })
            .done(function(response) {
                if (response.success && response.data.has_new) {
                    // Update notification indicator
                    StockScannerAdmin.updateNotificationIndicator(response.data.count);
                }
            });
        },

        // Update notification indicator
        updateNotificationIndicator: function(count) {
            let $indicator = $('.notification-indicator');
            
            if ($indicator.length === 0) {
                $indicator = $('<span class="notification-indicator">').appendTo('#adminmenu .toplevel_page_stock-scanner-security a');
            }
            
            if (count > 0) {
                $indicator.text(count).show();
            } else {
                $indicator.hide();
            }
        }
    };

    // Initialize when document is ready
    $(document).ready(function() {
        StockScannerAdmin.init();
    });

    // Add some CSS for animations and notifications
    $('<style>').text(`
        .stock-scanner-notification {
            position: fixed;
            top: 32px;
            right: 20px;
            z-index: 999999;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .security-card.updated {
            animation: cardPulse 0.5s ease;
        }
        
        @keyframes cardPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
        
        .notification-indicator {
            background: #d63638;
            color: white;
            border-radius: 50%;
            padding: 2px 6px;
            font-size: 11px;
            margin-left: 5px;
            font-weight: bold;
        }
        
        .blocked-ip {
            opacity: 0.5;
            text-decoration: line-through;
        }
        
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .table-container {
            position: relative;
        }
        
        .table-filters {
            padding: 15px;
            background: #f9f9f9;
            border-bottom: 1px solid #ddd;
        }
        
        .table-filters input,
        .table-filters select {
            margin-right: 10px;
        }
    `).appendTo('head');

})(jQuery);