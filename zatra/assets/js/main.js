/**
 * Stock Scanner Pro - Main JavaScript
 * 
 * Provides interactive functionality while maintaining Zatra theme compatibility
 */

(function($) {
    'use strict';

    // Global variables
    let stockScannerApp = {
        initialized: false,
        cache: {},
        settings: {
            apiTimeout: 10000,
            refreshInterval: 30000,
            animationDuration: 300
        }
    };

    /**
     * Initialize the application
     */
    function init() {
        if (stockScannerApp.initialized) return;
        
        // Wait for DOM and dependencies
        $(document).ready(function() {
            initializeComponents();
            bindEvents();
            loadInitialData();
            stockScannerApp.initialized = true;
        });
    }

    /**
     * Initialize all components
     */
    function initializeComponents() {
        // Initialize tooltips if available
        if (typeof $.fn.tooltip === 'function') {
            $('[data-toggle="tooltip"]').tooltip();
        }

        // Initialize modals if available
        if (typeof $.fn.modal === 'function') {
            $('.modal').modal({ show: false });
        }

        // Initialize scroll animations
        initScrollAnimations();

        // Initialize form validations
        initFormValidations();

        // Initialize charts if Chart.js is available
        if (typeof Chart !== 'undefined') {
            initCharts();
        }

        // Initialize real-time updates
        initRealTimeUpdates();
    }

    /**
     * Bind all event handlers
     */
    function bindEvents() {
        // Navigation events
        $(document).on('click', '.nav-toggle', handleNavToggle);
        
        // Search events
        $(document).on('input', '#stock-search', debounce(handleStockSearch, 300));
        $(document).on('click', '.suggestion-item', handleSuggestionClick);
        $(document).on('click', '#search-btn', handleSearchSubmit);
        
        // Form events
        $(document).on('submit', '.ajax-form', handleAjaxForm);
        $(document).on('click', '.password-toggle', handlePasswordToggle);
        
        // Interactive elements
        $(document).on('click', '.action-btn', handleActionButton);
        $(document).on('click', '.upgrade-btn', handleUpgradeButton);
        $(document).on('click', '.chart-period', handleChartPeriod);
        
        // Watchlist events
        $(document).on('click', '#add-to-watchlist', handleAddToWatchlist);
        $(document).on('click', '.remove-from-watchlist', handleRemoveFromWatchlist);
        
        // Portfolio events
        $(document).on('click', '#add-to-portfolio', handleAddToPortfolio);
        
        // Window events
        $(window).on('scroll', throttle(handleScroll, 100));
        $(window).on('resize', debounce(handleResize, 250));
        
        // Keyboard events
        $(document).on('keypress', '#stock-search', function(e) {
            if (e.which === 13) { // Enter key
                e.preventDefault();
                handleSearchSubmit();
            }
        });
    }

    /**
     * Load initial data
     */
    function loadInitialData() {
        // Load user data if logged in
        if (typeof stockScannerAjax !== 'undefined' && stockScannerAjax.user_tier) {
            loadUserData();
        }

        // Load market data on relevant pages
        if ($('#market-indices').length) {
            loadMarketData();
        }

        // Load watchlist preview
        if ($('#watchlist-preview').length) {
            loadWatchlistPreview();
        }

        // Load news feed
        if ($('#recent-news').length) {
            loadNewsFeed();
        }
    }

    /**
     * Initialize scroll animations
     */
    function initScrollAnimations() {
        if ('IntersectionObserver' in window) {
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };

            const observer = new IntersectionObserver(function(entries) {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate');
                        // Stagger animations for child elements
                        const children = entry.target.querySelectorAll('.animate-child');
                        children.forEach((child, index) => {
                            setTimeout(() => {
                                child.classList.add('animate');
                            }, index * 100);
                        });
                    }
                });
            }, observerOptions);

            // Observe elements
            document.querySelectorAll('.stat-item, .feature-card, .testimonial-card, .pricing-card, .faq-item, .news-item').forEach(el => {
                observer.observe(el);
            });
        }
    }

    /**
     * Initialize form validations
     */
    function initFormValidations() {
        // Real-time validation for forms
        $(document).on('blur', 'input[required], select[required]', function() {
            validateField($(this));
        });

        // Password strength indicator
        $(document).on('input', 'input[type="password"]', function() {
            if ($(this).attr('id') === 'password') {
                updatePasswordStrength($(this));
            }
        });

        // Confirm password validation
        $(document).on('input', '#confirm_password', function() {
            validatePasswordConfirmation($(this));
        });
    }

    /**
     * Initialize charts
     */
    function initCharts() {
        // Set global Chart.js defaults
        if (typeof Chart !== 'undefined') {
            Chart.defaults.font.family = "'Poppins', sans-serif";
            Chart.defaults.color = '#666666';
            Chart.defaults.borderColor = '#e1e5e9';
            Chart.defaults.backgroundColor = 'rgba(54, 133, 251, 0.1)';
        }
    }

    /**
     * Initialize real-time updates
     */
    function initRealTimeUpdates() {
        // Auto-refresh data every 30 seconds on dashboard
        if ($('.stock-scanner-dashboard').length) {
            setInterval(function() {
                loadUserData();
                loadMarketData();
                loadWatchlistPreview();
            }, stockScannerApp.settings.refreshInterval);
        }
    }

    /**
     * Handle navigation toggle
     */
    function handleNavToggle(e) {
        e.preventDefault();
        const $nav = $('.main-navigation');
        $nav.toggleClass('active');
        $(this).toggleClass('active');
    }

    /**
     * Handle stock search
     */
    function handleStockSearch(e) {
        const query = $(this).val().trim();
        const $suggestions = $('#search-suggestions');

        if (query.length < 2) {
            $suggestions.hide();
            return;
        }

        // Show loading
        $suggestions.html('<div class="suggestion-loading">Searching...</div>').show();

        // Make API request
        makeApiRequest('search/', { q: query, limit: 5 })
            .then(data => {
                displaySearchSuggestions(data.results || [], $suggestions);
            })
            .catch(error => {
                console.error('Search error:', error);
                $suggestions.hide();
            });
    }

    /**
     * Display search suggestions
     */
    function displaySearchSuggestions(suggestions, $container) {
        if (suggestions.length === 0) {
            $container.hide();
            return;
        }

        let html = '';
        suggestions.forEach(stock => {
            html += `
                <div class="suggestion-item" data-symbol="${stock.ticker}">
                    <span class="suggestion-symbol">${stock.ticker}</span>
                    <span class="suggestion-name">${stock.company_name || stock.name}</span>
                </div>
            `;
        });

        $container.html(html).show();
    }

    /**
     * Handle suggestion click
     */
    function handleSuggestionClick(e) {
        const symbol = $(this).data('symbol');
        $('#stock-search').val(symbol);
        $('#search-suggestions').hide();
        handleSearchSubmit();
    }

    /**
     * Handle search submit
     */
    function handleSearchSubmit(e) {
        if (e) e.preventDefault();
        
        const symbol = $('#stock-search').val().trim().toUpperCase();
        if (!symbol) return;

        showLoading('#loading-indicator');
        hideError('#error-message');

        makeApiRequest(`stock/${symbol}/`)
            .then(data => {
                hideLoading('#loading-indicator');
                if (data.error) {
                    showError('#error-message', data.error);
                } else {
                    displayStockData(data);
                }
            })
            .catch(error => {
                hideLoading('#loading-indicator');
                showError('#error-message', 'Failed to fetch stock data. Please try again.');
                console.error('Stock lookup error:', error);
            });
    }

    /**
     * Display stock data
     */
    function displayStockData(data) {
        // Populate basic info
        $('#stock-name').text(data.company_name || data.name || 'Unknown');
        $('#stock-symbol').text(data.ticker || data.symbol || '');
        $('#stock-exchange').text(data.exchange || 'NYSE');
        $('#current-price').text('$' + (data.current_price || data.price || '0.00'));

        // Handle price changes
        const change = data.change || 0;
        const changePercent = data.change_percent || 0;
        const changeClass = change >= 0 ? 'positive' : 'negative';

        $('#price-change')
            .text((change >= 0 ? '+' : '') + change.toFixed(2))
            .removeClass('positive negative')
            .addClass(changeClass);

        $('#change-percent')
            .text('(' + (changePercent >= 0 ? '+' : '') + changePercent.toFixed(2) + '%)')
            .removeClass('positive negative')
            .addClass(changeClass);

        // Populate key statistics
        updateKeyStatistics(data);

        // Show result
        $('#stock-result').show();

        // Initialize price chart
        if (typeof Chart !== 'undefined') {
            initializePriceChart(data);
        }

        // Load related news
        loadStockNews(data.ticker || data.symbol);
    }

    /**
     * Update key statistics
     */
    function updateKeyStatistics(data) {
        const $statsGrid = $('#key-stats');
        const stats = [
            { label: 'Market Cap', value: data.market_cap || 'N/A' },
            { label: 'P/E Ratio', value: data.pe_ratio || 'N/A' },
            { label: 'Volume', value: data.volume ? formatNumber(data.volume) : 'N/A' },
            { label: '52W High', value: data.week_52_high ? '$' + data.week_52_high : 'N/A' },
            { label: '52W Low', value: data.week_52_low ? '$' + data.week_52_low : 'N/A' },
            { label: 'Dividend Yield', value: data.dividend_yield ? data.dividend_yield + '%' : 'N/A' }
        ];

        let html = '';
        stats.forEach(stat => {
            html += `
                <div class="stat-item">
                    <span class="stat-label">${stat.label}</span>
                    <span class="stat-value">${stat.value}</span>
                </div>
            `;
        });

        $statsGrid.html(html);
    }

    /**
     * Initialize price chart
     */
    function initializePriceChart(stockData) {
        const canvas = document.getElementById('price-chart');
        if (!canvas || typeof Chart === 'undefined') return;

        const ctx = canvas.getContext('2d');
        
        // Generate sample data (in production, fetch from API)
        const chartData = {
            labels: generateTimeLabels(),
            datasets: [{
                label: 'Price',
                data: generateSamplePriceData(stockData.current_price || 100, 14),
                borderColor: '#3685fb',
                backgroundColor: 'rgba(54, 133, 251, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 5
            }]
        };

        new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: '#e1e5e9'
                        }
                    },
                    x: {
                        grid: {
                            color: '#e1e5e9'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#3685fb',
                        borderWidth: 1
                    }
                }
            }
        });
    }

    /**
     * Handle AJAX forms
     */
    function handleAjaxForm(e) {
        e.preventDefault();
        
        const $form = $(this);
        const $submitBtn = $form.find('button[type="submit"]');
        const originalText = $submitBtn.text();

        // Show loading state
        $submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Processing...');

        // Get form data
        const formData = new FormData(this);
        const action = $form.attr('action') || window.location.href;

        // Make request
        $.ajax({
            url: action,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-WP-Nonce': stockScannerAjax.nonce
            }
        })
        .done(function(response) {
            if (response.success) {
                showSuccess($form, response.message || 'Success!');
                if (response.redirect) {
                    setTimeout(() => {
                        window.location.href = response.redirect;
                    }, 1500);
                }
            } else {
                showFormError($form, response.message || 'An error occurred.');
            }
        })
        .fail(function() {
            showFormError($form, 'Network error. Please try again.');
        })
        .always(function() {
            $submitBtn.prop('disabled', false).text(originalText);
        });
    }

    /**
     * Handle password toggle
     */
    function handlePasswordToggle(e) {
        e.preventDefault();
        
        const $toggle = $(this);
        const $input = $toggle.siblings('input');
        const $icon = $toggle.find('i');

        if ($input.attr('type') === 'password') {
            $input.attr('type', 'text');
            $icon.removeClass('fa-eye').addClass('fa-eye-slash');
        } else {
            $input.attr('type', 'password');
            $icon.removeClass('fa-eye-slash').addClass('fa-eye');
        }
    }

    /**
     * Handle action buttons
     */
    function handleActionButton(e) {
        e.preventDefault();
        
        const $btn = $(this);
        const href = $btn.attr('href');
        
        // Add loading state
        $btn.addClass('loading');
        
        // Navigate after short delay for visual feedback
        setTimeout(() => {
            window.location.href = href;
        }, 200);
    }

    /**
     * Handle upgrade buttons
     */
    function handleUpgradeButton(e) {
        e.preventDefault();
        
        const plan = $(this).data('plan');
        const isYearly = $('#billing-toggle').is(':checked');
        
        // Redirect to checkout
        const checkoutUrl = `/paypal-checkout/?plan=${plan}&billing=${isYearly ? 'yearly' : 'monthly'}`;
        window.location.href = checkoutUrl;
    }

    /**
     * Handle chart period selection
     */
    function handleChartPeriod(e) {
        e.preventDefault();
        
        const $btn = $(this);
        const period = $btn.data('period');
        
        // Update active state
        $btn.siblings().removeClass('active');
        $btn.addClass('active');
        
        // Update chart (implement based on your needs)
        updateChartPeriod(period);
    }

    /**
     * Handle add to watchlist
     */
    function handleAddToWatchlist(e) {
        e.preventDefault();
        
        const symbol = $('#stock-symbol').text();
        if (!symbol) return;

        const $btn = $(this);
        const originalText = $btn.text();
        
        $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Adding...');

        makeApiRequest('watchlist/', { ticker: symbol }, 'POST')
            .then(data => {
                if (data.success) {
                    showNotification('Stock added to watchlist!', 'success');
                    $btn.html('<i class="fas fa-check"></i> Added');
                } else {
                    showNotification(data.error || 'Failed to add to watchlist', 'error');
                    $btn.prop('disabled', false).text(originalText);
                }
            })
            .catch(error => {
                console.error('Watchlist error:', error);
                showNotification('Failed to add to watchlist', 'error');
                $btn.prop('disabled', false).text(originalText);
            });
    }

    /**
     * Handle remove from watchlist
     */
    function handleRemoveFromWatchlist(e) {
        e.preventDefault();
        
        const symbol = $(this).data('symbol');
        if (!symbol) return;

        if (!confirm('Remove this stock from your watchlist?')) return;

        const $btn = $(this);
        $btn.prop('disabled', true);

        makeApiRequest(`watchlist/${symbol}/`, {}, 'DELETE')
            .then(data => {
                if (data.success) {
                    $btn.closest('.watchlist-item').fadeOut(() => {
                        $btn.closest('.watchlist-item').remove();
                    });
                    showNotification('Stock removed from watchlist', 'success');
                } else {
                    showNotification(data.error || 'Failed to remove from watchlist', 'error');
                    $btn.prop('disabled', false);
                }
            })
            .catch(error => {
                console.error('Watchlist error:', error);
                showNotification('Failed to remove from watchlist', 'error');
                $btn.prop('disabled', false);
            });
    }

    /**
     * Handle add to portfolio
     */
    function handleAddToPortfolio(e) {
        e.preventDefault();
        
        const symbol = $('#stock-symbol').text();
        if (!symbol) return;

        // Redirect to portfolio page with symbol
        window.location.href = `/portfolio/?add=${symbol}`;
    }

    /**
     * Handle scroll events
     */
    function handleScroll() {
        const scrollTop = $(window).scrollTop();
        
        // Add/remove scrolled class to header
        if (scrollTop > 100) {
            $('body').addClass('scrolled');
        } else {
            $('body').removeClass('scrolled');
        }
    }

    /**
     * Handle resize events
     */
    function handleResize() {
        // Refresh charts on resize
        if (typeof Chart !== 'undefined') {
            Chart.helpers.each(Chart.instances, function(instance) {
                instance.resize();
            });
        }
    }

    /**
     * Load user data
     */
    function loadUserData() {
        makeApiRequest('user/api-usage/')
            .then(data => {
                if (data.current_usage) {
                    $('#api-usage-count').text(data.current_usage.this_month || 0);
                }
            })
            .catch(error => {
                console.error('Error loading user data:', error);
            });
    }

    /**
     * Load market data
     */
    function loadMarketData() {
        makeApiRequest('market-stats/')
            .then(data => {
                updateMarketIndices(data);
            })
            .catch(error => {
                console.error('Error loading market data:', error);
                // Show sample data on error
                updateMarketIndices(null);
            });
    }

    /**
     * Update market indices
     */
    function updateMarketIndices(data) {
        const $container = $('#market-indices');
        if (!$container.length) return;

        let indices;
        if (data && data.indices) {
            indices = data.indices;
        } else {
            // Sample data
            indices = [
                { name: 'S&P 500', value: '4,567.89', change: 0.75 },
                { name: 'NASDAQ', value: '14,234.56', change: 1.23 },
                { name: 'DOW', value: '35,678.90', change: -0.45 }
            ];
        }

        let html = '';
        indices.forEach(index => {
            const changeClass = index.change >= 0 ? 'positive' : 'negative';
            html += `
                <div class="index-item">
                    <span class="index-name">${index.name}</span>
                    <span class="index-value">${index.value}</span>
                    <span class="index-change ${changeClass}">${index.change >= 0 ? '+' : ''}${index.change}%</span>
                </div>
            `;
        });

        $container.html(html);
    }

    /**
     * Load watchlist preview
     */
    function loadWatchlistPreview() {
        makeApiRequest('watchlist/')
            .then(data => {
                updateWatchlistPreview(data);
            })
            .catch(error => {
                console.error('Error loading watchlist:', error);
                updateWatchlistPreview(null);
            });
    }

    /**
     * Update watchlist preview
     */
    function updateWatchlistPreview(data) {
        const $container = $('#watchlist-preview');
        if (!$container.length) return;

        if (data && data.results && data.results.length > 0) {
            let html = '';
            data.results.slice(0, 5).forEach(stock => {
                const changeClass = stock.change >= 0 ? 'positive' : 'negative';
                html += `
                    <div class="watchlist-item">
                        <span class="stock-symbol">${stock.ticker}</span>
                        <span class="stock-price">$${stock.current_price}</span>
                        <span class="stock-change ${changeClass}">${stock.change >= 0 ? '+' : ''}${stock.change}%</span>
                    </div>
                `;
            });
            $container.html(html);
        } else {
            $container.html('<div class="empty-state">No stocks in watchlist. <a href="/stock-lookup/">Add some stocks</a></div>');
        }
    }

    /**
     * Load news feed
     */
    function loadNewsFeed() {
        makeApiRequest('news/')
            .then(data => {
                updateNewsFeed(data);
            })
            .catch(error => {
                console.error('Error loading news:', error);
                updateNewsFeed(null);
            });
    }

    /**
     * Update news feed
     */
    function updateNewsFeed(data) {
        const $container = $('#recent-news');
        if (!$container.length) return;

        let articles;
        if (data && data.results && data.results.length > 0) {
            articles = data.results.slice(0, 3);
        } else {
            // Sample news
            articles = [
                {
                    title: 'Market Opens Higher on Strong Earnings',
                    summary: 'Major indices climb as tech companies report better-than-expected quarterly results...',
                    url: '#',
                    published_at: new Date().toISOString()
                },
                {
                    title: 'Fed Signals Potential Rate Changes',
                    summary: 'Federal Reserve officials hint at policy adjustments in upcoming meetings...',
                    url: '#',
                    published_at: new Date().toISOString()
                }
            ];
        }

        let html = '';
        articles.forEach(article => {
            html += `
                <div class="news-item">
                    <h4><a href="${article.url}" target="_blank">${article.title}</a></h4>
                    <p class="news-summary">${article.summary || article.description || 'No summary available.'}</p>
                    <span class="news-time">${new Date(article.published_at).toLocaleDateString()}</span>
                </div>
            `;
        });

        $container.html(html);
    }

    /**
     * Load stock news
     */
    function loadStockNews(symbol) {
        makeApiRequest(`news/?symbol=${symbol}&limit=3`)
            .then(data => {
                const $container = $('#stock-news');
                if (data.results && data.results.length > 0) {
                    let html = '';
                    data.results.forEach(article => {
                        html += `
                            <div class="news-item">
                                <h4><a href="${article.url}" target="_blank">${article.title}</a></h4>
                                <p class="news-summary">${article.summary || article.description || 'No summary available.'}</p>
                                <span class="news-time">${new Date(article.published_at).toLocaleDateString()}</span>
                            </div>
                        `;
                    });
                    $container.html(html);
                } else {
                    $container.html('<div class="empty-state">No recent news available for this stock.</div>');
                }
            })
            .catch(error => {
                console.error('Error loading stock news:', error);
                $('#stock-news').html('<div class="error-state">Failed to load news.</div>');
            });
    }

    /**
     * Make API request
     */
    function makeApiRequest(endpoint, data = {}, method = 'GET') {
        const url = stockScannerAjax.backend_url + endpoint;
        
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-WP-Nonce': stockScannerAjax.nonce
            }
        };

        if (method === 'POST' || method === 'PUT') {
            options.body = JSON.stringify(data);
        } else if (method === 'GET' && Object.keys(data).length > 0) {
            const params = new URLSearchParams(data);
            url += (url.includes('?') ? '&' : '?') + params.toString();
        }

        return fetch(url, options)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            });
    }

    /**
     * Utility functions
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    function formatNumber(num) {
        if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
        return num.toString();
    }

    function generateTimeLabels() {
        const labels = [];
        for (let i = 9; i <= 16; i++) {
            labels.push(`${i}:30`);
        }
        return labels;
    }

    function generateSamplePriceData(basePrice, count) {
        const data = [];
        let currentPrice = basePrice;
        
        for (let i = 0; i < count; i++) {
            const change = (Math.random() - 0.5) * 2;
            currentPrice += change;
            data.push(parseFloat(currentPrice.toFixed(2)));
        }
        
        return data;
    }

    function showLoading(selector) {
        $(selector).show();
    }

    function hideLoading(selector) {
        $(selector).hide();
    }

    function showError(selector, message) {
        $(selector).find('#error-text').text(message);
        $(selector).show();
    }

    function hideError(selector) {
        $(selector).hide();
    }

    function showNotification(message, type = 'info') {
        // Create notification element
        const $notification = $(`
            <div class="notification notification-${type}">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `);

        // Add to page
        $('body').append($notification);

        // Show with animation
        setTimeout(() => $notification.addClass('show'), 100);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            $notification.removeClass('show');
            setTimeout(() => $notification.remove(), 300);
        }, 5000);
    }

    function showFormError($form, message) {
        let $error = $form.find('.form-error');
        if (!$error.length) {
            $error = $('<div class="form-error"></div>');
            $form.prepend($error);
        }
        $error.html(`<i class="fas fa-exclamation-circle"></i> ${message}`).show();
    }

    function showSuccess($form, message) {
        let $success = $form.find('.form-success');
        if (!$success.length) {
            $success = $('<div class="form-success"></div>');
            $form.prepend($success);
        }
        $success.html(`<i class="fas fa-check-circle"></i> ${message}`).show();
    }

    function validateField($field) {
        const value = $field.val().trim();
        const isRequired = $field.prop('required');
        const fieldType = $field.attr('type') || $field.prop('tagName').toLowerCase();

        let isValid = true;
        let message = '';

        if (isRequired && !value) {
            isValid = false;
            message = 'This field is required';
        } else if (value) {
            switch (fieldType) {
                case 'email':
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(value)) {
                        isValid = false;
                        message = 'Please enter a valid email address';
                    }
                    break;
                case 'password':
                    if (value.length < 8) {
                        isValid = false;
                        message = 'Password must be at least 8 characters';
                    }
                    break;
            }
        }

        // Update field state
        $field.toggleClass('is-invalid', !isValid);
        $field.toggleClass('is-valid', isValid && value);

        // Show/hide error message
        let $error = $field.siblings('.field-error');
        if (!isValid && message) {
            if (!$error.length) {
                $error = $('<div class="field-error"></div>');
                $field.after($error);
            }
            $error.text(message).show();
        } else {
            $error.hide();
        }

        return isValid;
    }

    function updatePasswordStrength($field) {
        const password = $field.val();
        const $strength = $('#password-strength');
        
        if (!$strength.length) return;

        let score = 0;
        if (password.length >= 8) score++;
        if (password.match(/[a-z]/)) score++;
        if (password.match(/[A-Z]/)) score++;
        if (password.match(/[0-9]/)) score++;
        if (password.match(/[^a-zA-Z0-9]/)) score++;

        const strengths = [
            { class: 'weak', text: 'Very weak' },
            { class: 'weak', text: 'Weak' },
            { class: 'fair', text: 'Fair' },
            { class: 'good', text: 'Good' },
            { class: 'strong', text: 'Strong' },
            { class: 'strong', text: 'Very strong' }
        ];

        const strength = strengths[score] || strengths[0];
        $strength.removeClass('weak fair good strong').addClass(strength.class).text(strength.text);
    }

    function validatePasswordConfirmation($field) {
        const password = $('#password').val();
        const confirmPassword = $field.val();
        
        if (confirmPassword && password !== confirmPassword) {
            $field.addClass('is-invalid').removeClass('is-valid');
            let $error = $field.siblings('.field-error');
            if (!$error.length) {
                $error = $('<div class="field-error"></div>');
                $field.after($error);
            }
            $error.text('Passwords do not match').show();
        } else if (confirmPassword) {
            $field.addClass('is-valid').removeClass('is-invalid');
            $field.siblings('.field-error').hide();
        }
    }

    function updateChartPeriod(period) {
        // Implement chart period update logic
        console.log('Updating chart period to:', period);
    }

    // Initialize the application
    init();

    // Expose public API
    window.StockScannerPro = {
        makeApiRequest,
        showNotification,
        formatNumber,
        loadMarketData,
        loadWatchlistPreview
    };

})(jQuery);