/**
 * Stock Scanner Pro Plugin - Performance Optimized JavaScript
 * Handles AJAX caching, lazy loading, and plugin-specific optimizations
 */

(function($) {
    'use strict';
    
    // Plugin performance manager
    const pluginPerf = {
        
        // Cache for AJAX requests
        ajaxCache: new Map(),
        
        // Performance settings
        settings: {
            cacheTimeout: 300000, // 5 minutes
            lazyLoadThreshold: 50,
            debounceDelay: 300,
            maxCacheSize: 100
        },
        
        /**
         * Initialize plugin performance features
         */
        init() {
            this.initAjaxCaching();
            this.initLazyLoading();
            this.initStockDataOptimization();
            this.initPerformanceMonitoring();
            this.cleanupOldCache();
        },
        
        /**
         * Initialize AJAX caching system
         */
        initAjaxCaching() {
            // Override jQuery AJAX for plugin requests
            const originalAjax = $.ajax;
            
            $.ajax = (options) => {
                // Only cache GET requests to plugin endpoints
                if (options.type === 'GET' || !options.type) {
                    const cacheKey = this.generateCacheKey(options);
                    const cached = this.getFromCache(cacheKey);
                    
                    if (cached) {
                        // Return cached data as a resolved promise
                        const deferred = $.Deferred();
                        setTimeout(() => {
                            deferred.resolve(cached.data, 'success', {});
                        }, 1);
                        return deferred.promise();
                    }
                    
                    // Cache the response
                    const originalSuccess = options.success;
                    options.success = (data, textStatus, jqXHR) => {
                        this.setCache(cacheKey, data);
                        if (originalSuccess) {
                            originalSuccess(data, textStatus, jqXHR);
                        }
                    };
                }
                
                return originalAjax(options);
            };
        },
        
        /**
         * Generate cache key for AJAX request
         */
        generateCacheKey(options) {
            const key = {
                url: options.url,
                data: options.data || {},
                type: options.type || 'GET'
            };
            
            return 'plugin_' + btoa(JSON.stringify(key)).replace(/[^a-zA-Z0-9]/g, '');
        },
        
        /**
         * Get data from cache
         */
        getFromCache(key) {
            const cached = this.ajaxCache.get(key);
            
            if (cached && (Date.now() - cached.timestamp) < this.settings.cacheTimeout) {
                return cached;
            }
            
            // Remove expired cache
            if (cached) {
                this.ajaxCache.delete(key);
            }
            
            return null;
        },
        
        /**
         * Set data in cache
         */
        setCache(key, data) {
            // Prevent cache from growing too large
            if (this.ajaxCache.size >= this.settings.maxCacheSize) {
                const firstKey = this.ajaxCache.keys().next().value;
                this.ajaxCache.delete(firstKey);
            }
            
            this.ajaxCache.set(key, {
                data: data,
                timestamp: Date.now()
            });
        },
        
        /**
         * Initialize lazy loading for plugin content
         */
        initLazyLoading() {
            // Lazy load stock widgets
            const stockWidgets = document.querySelectorAll('.stock-widget[data-lazy="true"]');
            
            if (stockWidgets.length > 0 && 'IntersectionObserver' in window) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            this.loadStockWidget(entry.target);
                            observer.unobserve(entry.target);
                        }
                    });
                }, {
                    rootMargin: this.settings.lazyLoadThreshold + 'px'
                });
                
                stockWidgets.forEach(widget => observer.observe(widget));
            } else {
                // Fallback for browsers without Intersection Observer
                stockWidgets.forEach(widget => this.loadStockWidget(widget));
            }
        },
        
        /**
         * Load stock widget content
         */
        loadStockWidget(widget) {
            const symbol = widget.dataset.symbol;
            const type = widget.dataset.type || 'basic';
            
            if (!symbol) return;
            
            // Show loading state
            widget.innerHTML = '<div class="loading">Loading stock data...</div>';
            
            // Make optimized AJAX request
            this.getStockData(symbol, type)
                .then(data => {
                    this.renderStockWidget(widget, data);
                })
                .catch(error => {
                    widget.innerHTML = '<div class="error">Failed to load stock data</div>';
                    console.error('Stock widget error:', error);
                });
        },
        
        /**
         * Get stock data with caching
         */
        getStockData(symbol, type = 'basic') {
            return new Promise((resolve, reject) => {
                $.ajax({
                    url: stockScannerPerf.ajaxurl,
                    type: 'POST',
                    data: {
                        action: 'stock_scanner_get_data',
                        type: 'stock_details',
                        symbol: symbol,
                        nonce: stockScannerPerf.nonce
                    },
                    success: (response) => {
                        if (response.success) {
                            resolve(response.data);
                        } else {
                            reject(response.data);
                        }
                    },
                    error: (xhr, status, error) => {
                        reject(error);
                    }
                });
            });
        },
        
        /**
         * Render stock widget with data
         */
        renderStockWidget(widget, data) {
            const template = this.getWidgetTemplate(widget.dataset.type || 'basic');
            
            widget.innerHTML = template
                .replace('{symbol}', data.symbol)
                .replace('{price}', data.price)
                .replace('{change}', data.change)
                .replace('{volume}', data.volume || 'N/A')
                .replace('{market_cap}', data.market_cap || 'N/A');
            
            // Add CSS class for styling
            widget.classList.add('loaded');
            
            // Trigger custom event
            $(widget).trigger('stockWidgetLoaded', [data]);
        },
        
        /**
         * Get widget template based on type
         */
        getWidgetTemplate(type) {
            const templates = {
                basic: `
                    <div class="stock-basic">
                        <h3>{symbol}</h3>
                        <div class="price">{price}</div>
                        <div class="change">{change}</div>
                    </div>
                `,
                detailed: `
                    <div class="stock-detailed">
                        <h3>{symbol}</h3>
                        <div class="price">{price}</div>
                        <div class="change">{change}</div>
                        <div class="volume">Volume: {volume}</div>
                        <div class="market-cap">Market Cap: {market_cap}</div>
                    </div>
                `,
                compact: `
                    <div class="stock-compact">
                        <span class="symbol">{symbol}</span>
                        <span class="price">{price}</span>
                        <span class="change">{change}</span>
                    </div>
                `
            };
            
            return templates[type] || templates.basic;
        },
        
        /**
         * Initialize stock data optimization
         */
        initStockDataOptimization() {
            // Debounce stock price updates
            let updateTimeout;
            
            $(document).on('stockPriceUpdate', this.debounce((event, data) => {
                this.updateStockPrices(data);
            }, this.settings.debounceDelay));
            
            // Batch multiple stock requests
            this.initBatchedRequests();
            
            // Auto-refresh stock data
            this.initAutoRefresh();
        },
        
        /**
         * Initialize batched requests for efficiency
         */
        initBatchedRequests() {
            let batchQueue = [];
            let batchTimeout;
            
            window.stockScannerBatch = {
                add: (symbol, callback) => {
                    batchQueue.push({ symbol, callback });
                    
                    clearTimeout(batchTimeout);
                    batchTimeout = setTimeout(() => {
                        this.processBatch(batchQueue);
                        batchQueue = [];
                    }, 100); // Batch requests within 100ms
                }
            };
        },
        
        /**
         * Process batched stock requests
         */
        processBatch(batch) {
            if (batch.length === 0) return;
            
            const symbols = batch.map(item => item.symbol);
            
            $.ajax({
                url: stockScannerPerf.ajaxurl,
                type: 'POST',
                data: {
                    action: 'stock_scanner_get_batch_data',
                    symbols: symbols.join(','),
                    nonce: stockScannerPerf.nonce
                },
                success: (response) => {
                    if (response.success) {
                        batch.forEach(item => {
                            const data = response.data[item.symbol];
                            if (data && item.callback) {
                                item.callback(data);
                            }
                        });
                    }
                },
                error: (xhr, status, error) => {
                    console.error('Batch request failed:', error);
                }
            });
        },
        
        /**
         * Initialize auto-refresh for stock data
         */
        initAutoRefresh() {
            // Only refresh when page is visible
            let refreshInterval;
            
            const startRefresh = () => {
                refreshInterval = setInterval(() => {
                    if (!document.hidden) {
                        this.refreshVisibleStockWidgets();
                    }
                }, 30000); // Refresh every 30 seconds
            };
            
            const stopRefresh = () => {
                clearInterval(refreshInterval);
            };
            
            // Start/stop based on page visibility
            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    stopRefresh();
                } else {
                    startRefresh();
                }
            });
            
            // Start immediately if page is visible
            if (!document.hidden) {
                startRefresh();
            }
        },
        
        /**
         * Refresh visible stock widgets
         */
        refreshVisibleStockWidgets() {
            const visibleWidgets = document.querySelectorAll('.stock-widget.loaded');
            
            visibleWidgets.forEach(widget => {
                const rect = widget.getBoundingClientRect();
                const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
                
                if (isVisible && widget.dataset.symbol) {
                    this.updateStockWidget(widget);
                }
            });
        },
        
        /**
         * Update individual stock widget
         */
        updateStockWidget(widget) {
            const symbol = widget.dataset.symbol;
            
            this.getStockData(symbol)
                .then(data => {
                    this.renderStockWidget(widget, data);
                })
                .catch(error => {
                    console.error('Failed to update widget:', error);
                });
        },
        
        /**
         * Initialize performance monitoring
         */
        initPerformanceMonitoring() {
            if (!stockScannerPerf.debug_mode) return;
            
            // Monitor AJAX performance
            let ajaxCount = 0;
            let totalAjaxTime = 0;
            
            $(document).ajaxStart(() => {
                this.ajaxStartTime = performance.now();
            });
            
            $(document).ajaxComplete((event, xhr, settings) => {
                if (settings.url.includes('stock_scanner')) {
                    ajaxCount++;
                    totalAjaxTime += performance.now() - this.ajaxStartTime;
                    
                    // Log slow requests
                    const requestTime = performance.now() - this.ajaxStartTime;
                    if (requestTime > 1000) {
                        console.warn('Slow AJAX request:', settings.url, requestTime + 'ms');
                    }
                }
            });
            
            // Log performance stats every minute
            setInterval(() => {
                if (ajaxCount > 0) {
                    console.log('Stock Scanner Performance:', {
                        'AJAX Requests': ajaxCount,
                        'Average Response Time': (totalAjaxTime / ajaxCount).toFixed(2) + 'ms',
                        'Cache Size': this.ajaxCache.size,
                        'Memory Usage': this.getMemoryUsage()
                    });
                }
            }, 60000);
        },
        
        /**
         * Get memory usage estimate
         */
        getMemoryUsage() {
            if (performance.memory) {
                return {
                    used: (performance.memory.usedJSHeapSize / 1024 / 1024).toFixed(2) + 'MB',
                    total: (performance.memory.totalJSHeapSize / 1024 / 1024).toFixed(2) + 'MB'
                };
            }
            return 'Not available';
        },
        
        /**
         * Clean up old cache entries
         */
        cleanupOldCache() {
            setInterval(() => {
                const now = Date.now();
                for (const [key, value] of this.ajaxCache.entries()) {
                    if (now - value.timestamp > this.settings.cacheTimeout) {
                        this.ajaxCache.delete(key);
                    }
                }
            }, 300000); // Clean up every 5 minutes
        },
        
        /**
         * Debounce utility function
         */
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        /**
         * Update stock prices in DOM
         */
        updateStockPrices(data) {
            // Update all elements with matching stock symbols
            Object.keys(data).forEach(symbol => {
                const elements = document.querySelectorAll(`[data-symbol="${symbol}"]`);
                elements.forEach(element => {
                    if (element.classList.contains('stock-widget')) {
                        this.renderStockWidget(element, data[symbol]);
                    }
                });
            });
        }
    };
    
    // Initialize when document is ready
    $(document).ready(() => {
        // Merge settings from localized script
        if (typeof stockScannerPerf !== 'undefined') {
            pluginPerf.settings = $.extend(pluginPerf.settings, {
                cacheTimeout: stockScannerPerf.cache_timeout * 1000,
                lazyLoadThreshold: stockScannerPerf.lazy_load_threshold,
                debounceDelay: stockScannerPerf.debounceDelay || 300
            });
        }
        
        pluginPerf.init();
    });
    
    // Export for global access
    window.stockScannerPluginPerf = pluginPerf;
    
})(jQuery);