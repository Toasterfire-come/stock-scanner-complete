/**
 * Stock Scanner Plugin Integration JavaScript
 * Handles all frontend interactions with the plugin
 */

(function($) {
    'use strict';

    var StockScannerIntegration = {
        init: function() {
            this.bindEvents();
            this.loadRecentCalls();
            this.startUsageUpdates();
        },

        bindEvents: function() {
            // Stock quote lookup
            $(document).on('click', '#get-stock-quote', this.getStockQuote);
            $(document).on('keypress', '#stock-symbol', function(e) {
                if (e.which === 13) { // Enter key
                    StockScannerIntegration.getStockQuote();
                }
            });

            // Membership upgrades
            $(document).on('click', '.upgrade-btn', this.handleUpgrade);

            // Watchlist management
            $(document).on('click', '.add-to-watchlist', this.addToWatchlist);
            $(document).on('click', '.remove-from-watchlist', this.removeFromWatchlist);

            // Market overview refresh
            $(document).on('click', '#refresh-market-data', this.refreshMarketData);

            // Contact form submission
            $(document).on('submit', '#contact-form', this.submitContactForm);
        },

        getStockQuote: function() {
            var symbol = $('#stock-symbol').val().trim().toUpperCase();
            var $button = $('#get-stock-quote');
            var $result = $('#stock-result');

            if (!symbol) {
                $result.html('<div class="error">Please enter a stock symbol.</div>');
                return;
            }

            $button.prop('disabled', true).text('Loading...');
            $result.html('<div class="loading">Fetching quote for ' + symbol + '...</div>');

            $.ajax({
                url: stock_scanner_theme.ajax_url,
                type: 'POST',
                data: {
                    action: 'get_stock_quote',
                    symbol: symbol,
                    nonce: stock_scanner_theme.nonce
                },
                success: function(response) {
                    if (response.success) {
                        var data = response.data;
                        var changeClass = parseFloat(data.change) >= 0 ? 'positive' : 'negative';
                        var changeSymbol = parseFloat(data.change) >= 0 ? '+' : '';
                        
                        var html = '<div class="stock-quote-result">' +
                            '<h4>' + data.symbol + '</h4>' +
                            '<div class="price">$' + data.price + '</div>' +
                            '<div class="change ' + changeClass + '">' +
                                changeSymbol + '$' + data.change + ' (' + changeSymbol + data.change_percent + '%)' +
                            '</div>' +
                            '<div class="volume">Volume: ' + data.volume + '</div>' +
                            '<div class="timestamp">Updated: ' + data.timestamp + '</div>' +
                        '</div>';
                        
                        $result.html(html);
                        
                        // Update usage display
                        StockScannerIntegration.updateUsageDisplay();
                    } else {
                        $result.html('<div class="error">' + response.data + '</div>');
                    }
                },
                error: function() {
                    $result.html('<div class="error">Error fetching stock quote. Please try again.</div>');
                },
                complete: function() {
                    $button.prop('disabled', false).text('Get Quote');
                    $('#stock-symbol').val('');
                }
            });
        },

        handleUpgrade: function(e) {
            e.preventDefault();
            
            var $button = $(this);
            var plan = $button.data('plan');
            var price = $button.data('price');
            
            if (!plan || !price) {
                alert('Invalid plan data. Please refresh the page and try again.');
                return;
            }

            var confirmMessage = 'Upgrade to ' + plan.charAt(0).toUpperCase() + plan.slice(1) + 
                               ' plan for $' + price + '/month?';
            
            if (!confirm(confirmMessage)) {
                return;
            }

            $button.prop('disabled', true).text('Processing...');

            $.ajax({
                url: stock_scanner_theme.ajax_url,
                type: 'POST',
                data: {
                    action: 'upgrade_membership',
                    plan: plan,
                    price: price,
                    nonce: stock_scanner_theme.nonce
                },
                success: function(response) {
                    if (response.success) {
                        // Redirect to PayPal payment
                        var paymentForm = $('<form>', {
                            'method': 'POST',
                            'action': response.data.payment_url,
                            'target': '_blank'
                        });
                        
                        // Add payment data as hidden fields
                        $.each(response.data, function(key, value) {
                            paymentForm.append($('<input>', {
                                'type': 'hidden',
                                'name': key,
                                'value': value
                            }));
                        });
                        
                        $('body').append(paymentForm);
                        paymentForm.submit();
                        paymentForm.remove();
                    } else {
                        alert('Error processing upgrade: ' + response.data);
                    }
                },
                error: function() {
                    alert('Error processing upgrade. Please try again.');
                },
                complete: function() {
                    $button.prop('disabled', false).text('Upgrade');
                }
            });
        },

        addToWatchlist: function(e) {
            e.preventDefault();
            
            var symbol = $(this).data('symbol');
            var $button = $(this);
            
            if (!symbol) {
                alert('No symbol specified.');
                return;
            }

            $button.prop('disabled', true).text('Adding...');

            $.ajax({
                url: stock_scanner_theme.ajax_url,
                type: 'POST',
                data: {
                    action: 'add_to_watchlist',
                    symbol: symbol,
                    nonce: stock_scanner_theme.nonce
                },
                success: function(response) {
                    if (response.success) {
                        $button.text('Added ✓').removeClass('add-to-watchlist').addClass('remove-from-watchlist');
                        StockScannerIntegration.showNotification('Added ' + symbol + ' to watchlist', 'success');
                    } else {
                        alert('Error adding to watchlist: ' + response.data);
                    }
                },
                error: function() {
                    alert('Error adding to watchlist. Please try again.');
                },
                complete: function() {
                    $button.prop('disabled', false);
                }
            });
        },

        removeFromWatchlist: function(e) {
            e.preventDefault();
            
            var symbol = $(this).data('symbol');
            var $button = $(this);
            
            if (!symbol) {
                alert('No symbol specified.');
                return;
            }

            $button.prop('disabled', true).text('Removing...');

            $.ajax({
                url: stock_scanner_theme.ajax_url,
                type: 'POST',
                data: {
                    action: 'remove_from_watchlist',
                    symbol: symbol,
                    nonce: stock_scanner_theme.nonce
                },
                success: function(response) {
                    if (response.success) {
                        $button.text('Add to Watchlist').removeClass('remove-from-watchlist').addClass('add-to-watchlist');
                        StockScannerIntegration.showNotification('Removed ' + symbol + ' from watchlist', 'success');
                    } else {
                        alert('Error removing from watchlist: ' + response.data);
                    }
                },
                error: function() {
                    alert('Error removing from watchlist. Please try again.');
                },
                complete: function() {
                    $button.prop('disabled', false);
                }
            });
        },

        refreshMarketData: function(e) {
            e.preventDefault();
            
            var $button = $(this);
            var $container = $('#market-overview-data');
            
            $button.prop('disabled', true).text('Refreshing...');
            $container.addClass('loading');

            $.ajax({
                url: stock_scanner_theme.ajax_url,
                type: 'POST',
                data: {
                    action: 'get_market_overview',
                    nonce: stock_scanner_theme.nonce
                },
                success: function(response) {
                    if (response.success) {
                        $container.html(response.data.html);
                        StockScannerIntegration.showNotification('Market data updated', 'success');
                    } else {
                        alert('Error refreshing market data: ' + response.data);
                    }
                },
                error: function() {
                    alert('Error refreshing market data. Please try again.');
                },
                complete: function() {
                    $button.prop('disabled', false).text('Refresh Data');
                    $container.removeClass('loading');
                }
            });
        },

        submitContactForm: function(e) {
            e.preventDefault();
            
            var $form = $(this);
            var $button = $form.find('button[type="submit"]');
            var formData = $form.serialize();
            
            $button.prop('disabled', true).text('Sending...');

            $.ajax({
                url: stock_scanner_theme.ajax_url,
                type: 'POST',
                data: formData + '&action=submit_contact_form&nonce=' + stock_scanner_theme.nonce,
                success: function(response) {
                    if (response.success) {
                        $form[0].reset();
                        StockScannerIntegration.showNotification('Message sent successfully!', 'success');
                    } else {
                        alert('Error sending message: ' + response.data);
                    }
                },
                error: function() {
                    alert('Error sending message. Please try again.');
                },
                complete: function() {
                    $button.prop('disabled', false).text('Send Message');
                }
            });
        },

        loadRecentCalls: function() {
            var $container = $('#recent-calls');
            
            if ($container.length === 0) {
                return;
            }

            $.ajax({
                url: stock_scanner_theme.ajax_url,
                type: 'POST',
                data: {
                    action: 'get_recent_calls',
                    nonce: stock_scanner_theme.nonce
                },
                success: function(response) {
                    if (response.success) {
                        var calls = response.data.calls;
                        var html = '';
                        
                        if (calls.length === 0) {
                            html = '<p>No recent API calls.</p>';
                        } else {
                            html = '<ul class="recent-calls-list">';
                            $.each(calls, function(index, call) {
                                html += '<li>' +
                                    '<span class="endpoint">' + call.endpoint + '</span>' +
                                    '<span class="symbol">' + (call.symbol || 'N/A') + '</span>' +
                                    '<span class="timestamp">' + call.created_at + '</span>' +
                                '</li>';
                            });
                            html += '</ul>';
                        }
                        
                        $container.html(html);
                    }
                },
                error: function() {
                    $container.html('<p>Error loading recent calls.</p>');
                }
            });
        },

        updateUsageDisplay: function() {
            // Refresh usage statistics after API call
            location.reload(); // Simple approach - you could implement AJAX update instead
        },

        startUsageUpdates: function() {
            // Update usage display every 30 seconds
            setInterval(function() {
                if ($('.usage-stats').length > 0) {
                    // Only update if on dashboard page
                    StockScannerIntegration.refreshUsageStats();
                }
            }, 30000);
        },

        refreshUsageStats: function() {
            $.ajax({
                url: stock_scanner_theme.ajax_url,
                type: 'POST',
                data: {
                    action: 'get_usage_stats',
                    nonce: stock_scanner_theme.nonce
                },
                success: function(response) {
                    if (response.success) {
                        var usage = response.data;
                        
                        // Update monthly usage
                        var monthlyPercentage = usage.monthly_limit > 0 ? 
                            (usage.monthly_calls / usage.monthly_limit) * 100 : 0;
                        $('.usage-card:first .usage-fill').css('width', Math.min(100, monthlyPercentage) + '%');
                        $('.usage-card:first p').text(usage.monthly_calls + ' / ' + 
                            (usage.monthly_limit === -1 ? 'Unlimited' : usage.monthly_limit) + ' calls');
                        
                        // Update daily usage
                        var dailyPercentage = usage.daily_limit > 0 ? 
                            (usage.daily_calls / usage.daily_limit) * 100 : 0;
                        $('.usage-card:last .usage-fill').css('width', Math.min(100, dailyPercentage) + '%');
                        $('.usage-card:last p').text(usage.daily_calls + ' / ' + 
                            (usage.daily_limit === -1 ? 'Unlimited' : usage.daily_limit) + ' calls today');
                    }
                }
            });
        },

        showNotification: function(message, type) {
            var $notification = $('<div class="stock-scanner-notification ' + type + '">' + message + '</div>');
            
            $('body').append($notification);
            
            $notification.fadeIn(300).delay(3000).fadeOut(300, function() {
                $(this).remove();
            });
        }
    };

    // Initialize when document is ready
    $(document).ready(function() {
        if (typeof stock_scanner_theme !== 'undefined') {
            StockScannerIntegration.init();
        }
    });

})(jQuery);