/**
 * Stock Scanner Professional - Admin Dashboard JavaScript
 * Version: 3.0.0
 * 
 * Comprehensive admin dashboard functionality with:
 * - Real-time analytics and charts
 * - User management interface
 * - Plugin settings and configuration
 * - Performance monitoring
 */

(function($) {
    'use strict';

    /**
     * Admin Dashboard Manager
     */
    const StockScannerAdmin = {
        
        // Configuration
        config: {
            refreshInterval: 60000, // 1 minute
            chartUpdateInterval: 300000, // 5 minutes
            maxDataPoints: 24, // 24 hours of hourly data
            animationDuration: 300
        },
        
        // State management
        state: {
            charts: new Map(),
            timers: new Map(),
            currentTab: 'dashboard',
            isLoading: false
        },
        
        // Data cache
        cache: new Map(),
        
        /**
         * Initialize admin dashboard
         */
        init() {
            this.bindEvents();
            this.initializeCharts();
            this.loadDashboardData();
            this.startPeriodicUpdates();
            this.setupTabNavigation();
            
            console.log('Stock Scanner Admin Dashboard initialized');
        },
        
        /**
         * Bind dashboard events
         */
        bindEvents() {
            // Tab navigation
            $(document).on('click', '.admin-nav-tab a', (e) => {
                e.preventDefault();
                this.switchTab($(e.currentTarget));
            });
            
            // Refresh buttons
            $(document).on('click', '[data-action="refresh"]', (e) => {
                e.preventDefault();
                this.refreshData();
            });
            
            // Settings form submission
            $(document).on('submit', '.admin-form', (e) => {
                e.preventDefault();
                this.handleFormSubmission($(e.currentTarget));
            });
            
            // User management actions
            $(document).on('click', '[data-action="edit-user"]', (e) => {
                e.preventDefault();
                this.editUser($(e.currentTarget).data('user-id'));
            });
            
            $(document).on('click', '[data-action="delete-user"]', (e) => {
                e.preventDefault();
                this.deleteUser($(e.currentTarget).data('user-id'));
            });
            
            // Chart controls
            $(document).on('change', '.chart-timeframe', (e) => {
                const timeframe = $(e.currentTarget).val();
                const chartId = $(e.currentTarget).data('chart');
                this.updateChartTimeframe(chartId, timeframe);
            });
            
            // Modal controls
            $(document).on('click', '.admin-modal-close, .modal-cancel', () => {
                this.closeModal();
            });
            
            $(document).on('click', '.admin-modal-overlay', (e) => {
                if ($(e.target).hasClass('admin-modal-overlay')) {
                    this.closeModal();
                }
            });
            
            // Real-time toggle
            $(document).on('change', '.realtime-updates-toggle', (e) => {
                this.toggleRealTimeUpdates($(e.currentTarget).is(':checked'));
            });
        },
        
        /**
         * Setup tab navigation
         */
        setupTabNavigation() {
            const hash = window.location.hash.substring(1);
            if (hash && $('.admin-nav-tab[data-tab="' + hash + '"]').length) {
                this.state.currentTab = hash;
                this.showTab(hash);
            } else {
                this.showTab('dashboard');
            }
        },
        
        /**
         * Switch between tabs
         */
        switchTab($tabLink) {
            const tab = $tabLink.closest('.admin-nav-tab').data('tab');
            
            if (tab === this.state.currentTab) {
                return;
            }
            
            this.showTab(tab);
            window.location.hash = tab;
        },
        
        /**
         * Show specific tab
         */
        showTab(tabName) {
            // Update navigation
            $('.admin-nav-tab').removeClass('nav-tab-active');
            $('.admin-nav-tab[data-tab="' + tabName + '"]').addClass('nav-tab-active');
            
            // Update content
            $('.admin-tab-content').hide();
            $('#tab-' + tabName).show();
            
            // Load tab-specific data
            this.loadTabData(tabName);
            
            this.state.currentTab = tabName;
        },
        
        /**
         * Load tab-specific data
         */
        async loadTabData(tabName) {
            switch (tabName) {
                case 'dashboard':
                    await this.loadDashboardData();
                    break;
                case 'analytics':
                    await this.loadAnalyticsData();
                    break;
                case 'users':
                    await this.loadUsersData();
                    break;
                case 'settings':
                    await this.loadSettingsData();
                    break;
            }
        },
        
        /**
         * Load dashboard overview data
         */
        async loadDashboardData() {
            this.showLoading(true);
            
            try {
                const response = await this.apiCall('get_dashboard_data');
                
                if (response.success) {
                    this.updateDashboardStats(response.data.stats);
                    this.updateRecentActivity(response.data.activity);
                    this.updateSystemStatus(response.data.system);
                }
                
            } catch (error) {
                console.error('Failed to load dashboard data:', error);
                this.showNotice('Failed to load dashboard data', 'error');
            } finally {
                this.showLoading(false);
            }
        },
        
        /**
         * Load analytics data
         */
        async loadAnalyticsData() {
            try {
                const response = await this.apiCall('get_analytics_data');
                
                if (response.success) {
                    this.updateAnalyticsCharts(response.data);
                }
                
            } catch (error) {
                console.error('Failed to load analytics data:', error);
                this.showNotice('Failed to load analytics data', 'error');
            }
        },
        
        /**
         * Load users data
         */
        async loadUsersData() {
            try {
                const response = await this.apiCall('get_users_data');
                
                if (response.success) {
                    this.updateUsersTable(response.data.users);
                    this.updateUserStats(response.data.stats);
                }
                
            } catch (error) {
                console.error('Failed to load users data:', error);
                this.showNotice('Failed to load users data', 'error');
            }
        },
        
        /**
         * Load settings data
         */
        async loadSettingsData() {
            try {
                const response = await this.apiCall('get_settings_data');
                
                if (response.success) {
                    this.populateSettingsForm(response.data);
                }
                
            } catch (error) {
                console.error('Failed to load settings data:', error);
                this.showNotice('Failed to load settings data', 'error');
            }
        },
        
        /**
         * Initialize charts
         */
        initializeCharts() {
            // API Usage Chart
            this.createChart('api-usage-chart', {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'API Calls',
                        data: [],
                        borderColor: '#2271b1',
                        backgroundColor: 'rgba(34, 113, 177, 0.1)',
                        tension: 0.4
                    }]
                },
                options: this.getChartOptions('API Usage Over Time')
            });
            
            // User Growth Chart
            this.createChart('user-growth-chart', {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'New Users',
                        data: [],
                        backgroundColor: '#00a32a',
                        borderColor: '#00a32a',
                        borderWidth: 1
                    }]
                },
                options: this.getChartOptions('User Growth')
            });
            
            // Revenue Chart
            this.createChart('revenue-chart', {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Revenue',
                        data: [],
                        borderColor: '#dba617',
                        backgroundColor: 'rgba(219, 166, 23, 0.1)',
                        tension: 0.4
                    }]
                },
                options: this.getChartOptions('Revenue', true)
            });
        },
        
        /**
         * Create individual chart
         */
        createChart(canvasId, config) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, config);
            
            this.state.charts.set(canvasId, chart);
            return chart;
        },
        
        /**
         * Get default chart options
         */
        getChartOptions(title, isCurrency = false) {
            return {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: title,
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return isCurrency ? '$' + value.toLocaleString() : value.toLocaleString();
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            };
        },
        
        /**
         * Update dashboard statistics
         */
        updateDashboardStats(stats) {
            // Update stat widgets
            Object.keys(stats).forEach(key => {
                const $stat = $(`[data-stat="${key}"]`);
                if ($stat.length) {
                    const value = stats[key];
                    $stat.find('.stat-number').text(this.formatStatValue(key, value.current));
                    
                    if (value.change !== undefined) {
                        const $change = $stat.find('.stat-change');
                        $change.removeClass('positive negative');
                        $change.addClass(value.change >= 0 ? 'positive' : 'negative');
                        $change.text((value.change >= 0 ? '+' : '') + value.change.toFixed(2) + '%');
                    }
                }
            });
        },
        
        /**
         * Update recent activity
         */
        updateRecentActivity(activities) {
            const $container = $('.recent-activity-list');
            $container.empty();
            
            activities.forEach(activity => {
                $container.append(`
                    <div class="activity-item">
                        <div class="activity-icon">
                            <span class="dashicons dashicons-${activity.icon}"></span>
                        </div>
                        <div class="activity-content">
                            <div class="activity-text">${activity.text}</div>
                            <div class="activity-time">${activity.time}</div>
                        </div>
                    </div>
                `);
            });
        },
        
        /**
         * Update system status
         */
        updateSystemStatus(system) {
            // API Status
            const $apiStatus = $('.api-status-indicator');
            $apiStatus.removeClass('online offline warning');
            $apiStatus.addClass(system.api_status);
            
            $('.api-status-text').text(system.api_status_text);
            
            // Database Status
            $('.db-status').text(system.database_status);
            
            // Cache Status
            $('.cache-status').text(system.cache_status);
            
            // Server Load
            $('.server-load').text(system.server_load + '%');
            $('.server-load-bar').css('width', system.server_load + '%');
        },
        
        /**
         * Update analytics charts
         */
        updateAnalyticsCharts(data) {
            // Update API Usage Chart
            const apiChart = this.state.charts.get('api-usage-chart');
            if (apiChart && data.api_usage) {
                apiChart.data.labels = data.api_usage.labels;
                apiChart.data.datasets[0].data = data.api_usage.data;
                apiChart.update('none');
            }
            
            // Update User Growth Chart
            const userChart = this.state.charts.get('user-growth-chart');
            if (userChart && data.user_growth) {
                userChart.data.labels = data.user_growth.labels;
                userChart.data.datasets[0].data = data.user_growth.data;
                userChart.update('none');
            }
            
            // Update Revenue Chart
            const revenueChart = this.state.charts.get('revenue-chart');
            if (revenueChart && data.revenue) {
                revenueChart.data.labels = data.revenue.labels;
                revenueChart.data.datasets[0].data = data.revenue.data;
                revenueChart.update('none');
            }
        },
        
        /**
         * Update users table
         */
        updateUsersTable(users) {
            const $tbody = $('.users-table tbody');
            $tbody.empty();
            
            users.forEach(user => {
                $tbody.append(`
                    <tr>
                        <td>
                            <div class="user-info">
                                <img src="${user.avatar}" class="user-avatar" alt="">
                                <div class="user-details">
                                    <div class="user-name">${user.name}</div>
                                    <div class="user-email">${user.email}</div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="membership-badge ${user.membership.toLowerCase()}">${user.membership}</span>
                        </td>
                        <td>${user.api_calls}</td>
                        <td>${user.last_login}</td>
                        <td>
                            <div class="table-actions">
                                <a href="#" class="table-action edit" data-action="edit-user" data-user-id="${user.id}">Edit</a>
                                <a href="#" class="table-action delete" data-action="delete-user" data-user-id="${user.id}">Delete</a>
                            </div>
                        </td>
                    </tr>
                `);
            });
        },
        
        /**
         * Handle form submissions
         */
        async handleFormSubmission($form) {
            if (this.state.isLoading) return;
            
            this.state.isLoading = true;
            const $submitBtn = $form.find('[type="submit"]');
            const originalText = $submitBtn.text();
            
            $submitBtn.prop('disabled', true).text('Saving...');
            
            try {
                const formData = new FormData($form[0]);
                formData.append('action', 'stock_scanner_admin_save_settings');
                formData.append('nonce', stockScannerAdmin.nonce);
                
                const response = await $.ajax({
                    url: stockScannerAdmin.ajaxUrl,
                    method: 'POST',
                    data: formData,
                    processData: false,
                    contentType: false
                });
                
                if (response.success) {
                    this.showNotice('Settings saved successfully', 'success');
                } else {
                    throw new Error(response.data.message || 'Save failed');
                }
                
            } catch (error) {
                console.error('Form submission error:', error);
                this.showNotice('Failed to save settings', 'error');
            } finally {
                $submitBtn.prop('disabled', false).text(originalText);
                this.state.isLoading = false;
            }
        },
        
        /**
         * Edit user modal
         */
        editUser(userId) {
            // Implementation for user editing modal
            this.showModal('Edit User', this.getUserEditForm(userId));
        },
        
        /**
         * Delete user confirmation
         */
        deleteUser(userId) {
            if (confirm('Are you sure you want to delete this user?')) {
                this.apiCall('delete_user', { user_id: userId })
                    .then(response => {
                        if (response.success) {
                            this.showNotice('User deleted successfully', 'success');
                            this.loadUsersData();
                        } else {
                            throw new Error(response.data.message);
                        }
                    })
                    .catch(error => {
                        this.showNotice('Failed to delete user', 'error');
                    });
            }
        },
        
        /**
         * Start periodic updates
         */
        startPeriodicUpdates() {
            // Refresh dashboard data
            this.state.timers.set('dashboard', setInterval(() => {
                if (this.state.currentTab === 'dashboard') {
                    this.loadDashboardData();
                }
            }, this.config.refreshInterval));
            
            // Update charts
            this.state.timers.set('charts', setInterval(() => {
                if (this.state.currentTab === 'analytics') {
                    this.loadAnalyticsData();
                }
            }, this.config.chartUpdateInterval));
        },
        
        /**
         * Toggle real-time updates
         */
        toggleRealTimeUpdates(enabled) {
            if (enabled) {
                this.config.refreshInterval = 30000; // 30 seconds
                this.config.chartUpdateInterval = 60000; // 1 minute
            } else {
                this.config.refreshInterval = 60000; // 1 minute
                this.config.chartUpdateInterval = 300000; // 5 minutes
            }
            
            // Restart timers with new intervals
            this.state.timers.forEach((timer, key) => {
                clearInterval(timer);
            });
            this.state.timers.clear();
            this.startPeriodicUpdates();
        },
        
        /**
         * Refresh all data
         */
        refreshData() {
            this.loadTabData(this.state.currentTab);
        },
        
        /**
         * Show loading state
         */
        showLoading(show) {
            if (show) {
                $('.admin-content').addClass('loading');
            } else {
                $('.admin-content').removeClass('loading');
            }
        },
        
        /**
         * Show modal
         */
        showModal(title, content) {
            const modal = `
                <div class="admin-modal-overlay active">
                    <div class="admin-modal">
                        <div class="admin-modal-header">
                            <h3 class="admin-modal-title">${title}</h3>
                            <button class="admin-modal-close">&times;</button>
                        </div>
                        <div class="admin-modal-body">${content}</div>
                    </div>
                </div>
            `;
            
            $('body').append(modal);
        },
        
        /**
         * Close modal
         */
        closeModal() {
            $('.admin-modal-overlay').removeClass('active');
            setTimeout(() => {
                $('.admin-modal-overlay').remove();
            }, 300);
        },
        
        /**
         * Show admin notice
         */
        showNotice(message, type = 'info') {
            const notice = `
                <div class="admin-notice notice-${type}">
                    <p>${message}</p>
                    <button class="notice-dismiss">&times;</button>
                </div>
            `;
            
            $('.admin-content').prepend(notice);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                $('.admin-notice').fadeOut(() => {
                    $(this).remove();
                });
            }, 5000);
            
            // Manual dismiss
            $('.notice-dismiss').on('click', function() {
                $(this).parent().fadeOut(() => {
                    $(this).remove();
                });
            });
        },
        
        /**
         * Make API call
         */
        async apiCall(action, data = {}) {
            return $.ajax({
                url: stockScannerAdmin.ajaxUrl,
                method: 'POST',
                data: {
                    action: 'stock_scanner_admin_' + action,
                    nonce: stockScannerAdmin.nonce,
                    ...data
                }
            });
        },
        
        /**
         * Format stat values
         */
        formatStatValue(type, value) {
            switch (type) {
                case 'revenue':
                    return '$' + value.toLocaleString();
                case 'api_calls':
                case 'users':
                    return value.toLocaleString();
                default:
                    return value;
            }
        },
        
        /**
         * Get user edit form HTML
         */
        getUserEditForm(userId) {
            return `
                <form class="admin-form" data-user-id="${userId}">
                    <div class="form-group">
                        <label class="form-label">Name</label>
                        <input type="text" name="name" class="admin-input" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Email</label>
                        <input type="email" name="email" class="admin-input" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Membership Level</label>
                        <select name="membership" class="admin-select">
                            <option value="free">Free</option>
                            <option value="bronze">Bronze</option>
                            <option value="silver">Silver</option>
                            <option value="gold">Gold</option>
                        </select>
                    </div>
                    <div class="admin-modal-footer">
                        <button type="button" class="admin-button admin-button-secondary modal-cancel">Cancel</button>
                        <button type="submit" class="admin-button admin-button-primary">Save Changes</button>
                    </div>
                </form>
            `;
        }
    };
    
    /**
     * Initialize when document is ready
     */
    $(document).ready(function() {
        // Only initialize on admin pages
        if (typeof stockScannerAdmin !== 'undefined' && $('.stock-scanner-admin').length > 0) {
            StockScannerAdmin.init();
            
            // Make available globally
            window.StockScannerAdmin = StockScannerAdmin;
        }
    });
    
})(jQuery);