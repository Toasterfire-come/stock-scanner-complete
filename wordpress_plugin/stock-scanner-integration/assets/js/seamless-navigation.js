/**
 * Stock Scanner Professional - Seamless Navigation
 * Version: 3.0.0
 * 
 * Provides smooth, AJAX-powered navigation between plugin pages
 * with loading animations and professional transitions
 */

(function($) {
    'use strict';

    /**
     * Seamless Navigation Manager
     */
    const StockScannerNavigation = {
        
        // Configuration
        config: {
            loadingClass: 'stock-scanner-loading',
            contentClass: 'stock-scanner-page-content',
            navActiveClass: 'active',
            animationDuration: 300,
            cacheTimeout: 300000, // 5 minutes
            maxCacheSize: 10
        },
        
        // Cache for storing page content
        cache: new Map(),
        
        // Current page state
        currentPage: null,
        isLoading: false,
        
        /**
         * Initialize navigation system
         */
        init() {
            this.bindEvents();
            this.createLoadingOverlay();
            this.setupPageTransitions();
            this.initializeCurrentPage();
            
            // Initialize browser history
            window.addEventListener('popstate', (e) => {
                if (e.state && e.state.stockScannerPage) {
                    this.loadPage(e.state.url, false);
                }
            });
            
            console.log('Stock Scanner Navigation initialized');
        },
        
        /**
         * Bind navigation events
         */
        bindEvents() {
            // Navigation links
            $(document).on('click', '.stock-scanner-nav-link', (e) => {
                e.preventDefault();
                const url = $(e.currentTarget).attr('href');
                this.navigateToPage(url);
            });
            
            // Mobile navigation toggle
            $(document).on('click', '.stock-scanner-nav-toggle', () => {
                $('.stock-scanner-nav-menu').toggleClass('active');
            });
            
            // Handle form submissions with AJAX
            $(document).on('submit', '.stock-scanner-form[data-ajax="true"]', (e) => {
                e.preventDefault();
                this.handleFormSubmission($(e.currentTarget));
            });
            
            // Handle back/forward browser buttons
            $(window).on('resize', () => {
                this.handleResize();
            });
        },
        
        /**
         * Create loading overlay
         */
        createLoadingOverlay() {
            if ($('.stock-scanner-loading').length === 0) {
                $('body').append(`
                    <div class="stock-scanner-loading">
                        <div class="stock-scanner-spinner"></div>
                    </div>
                `);
            }
        },
        
        /**
         * Setup page transition animations
         */
        setupPageTransitions() {
            // Add transition classes to content areas
            $('.stock-scanner-page-content').addClass('stock-scanner-page-content');
        },
        
        /**
         * Initialize current page state
         */
        initializeCurrentPage() {
            const currentUrl = window.location.href;
            this.currentPage = currentUrl;
            
            // Cache current page
            const currentContent = $('.stock-scanner-page-content').html();
            if (currentContent) {
                this.addToCache(currentUrl, currentContent);
            }
            
            // Set active navigation
            this.updateActiveNavigation(currentUrl);
        },
        
        /**
         * Navigate to a new page
         */
        navigateToPage(url) {
            if (this.isLoading || url === this.currentPage) {
                return;
            }
            
            // Update browser history
            if (url !== window.location.href) {
                history.pushState(
                    { stockScannerPage: true, url: url },
                    '',
                    url
                );
            }
            
            this.loadPage(url, true);
        },
        
        /**
         * Load page content via AJAX
         */
        async loadPage(url, updateHistory = true) {
            if (this.isLoading) {
                return;
            }
            
            this.isLoading = true;
            this.showLoading();
            
            try {
                // Check cache first
                const cachedContent = this.getFromCache(url);
                if (cachedContent) {
                    await this.displayContent(cachedContent, url);
                    return;
                }
                
                // Load content via AJAX
                const response = await $.ajax({
                    url: stockScannerPro.ajaxUrl,
                    method: 'POST',
                    data: {
                        action: 'stock_scanner_load_page',
                        nonce: stockScannerPro.nonce,
                        page_url: url
                    },
                    timeout: 10000
                });
                
                if (response.success) {
                    await this.displayContent(response.data.content, url);
                    this.addToCache(url, response.data.content);
                } else {
                    throw new Error(response.data.message || 'Failed to load page');
                }
                
            } catch (error) {
                console.error('Navigation error:', error);
                this.showError('Failed to load page. Please try again.');
            } finally {
                this.isLoading = false;
                this.hideLoading();
            }
        },
        
        /**
         * Display content with smooth transition
         */
        async displayContent(content, url) {
            const $content = $('.stock-scanner-page-content');
            
            // Fade out current content
            $content.addClass('loading');
            
            await this.delay(this.config.animationDuration);
            
            // Update content
            $content.html(content);
            
            // Update navigation
            this.updateActiveNavigation(url);
            this.currentPage = url;
            
            // Trigger content loaded event
            $(document).trigger('stockScannerContentLoaded', [url, content]);
            
            // Fade in new content
            await this.delay(50); // Small delay for DOM update
            $content.removeClass('loading');
            
            // Scroll to top smoothly
            $('html, body').animate({ scrollTop: 0 }, 300);
            
            // Re-initialize any widgets or components
            this.reinitializeComponents();
        },
        
        /**
         * Update active navigation state
         */
        updateActiveNavigation(url) {
            $('.stock-scanner-nav-link').removeClass(this.config.navActiveClass);
            
            // Find matching navigation link
            $('.stock-scanner-nav-link').each(function() {
                const linkUrl = $(this).attr('href');
                if (linkUrl === url || url.includes(linkUrl)) {
                    $(this).addClass('active');
                }
            });
        },
        
        /**
         * Show loading state
         */
        showLoading() {
            $('.stock-scanner-loading').addClass('active');
            $('body').addClass('loading');
        },
        
        /**
         * Hide loading state
         */
        hideLoading() {
            $('.stock-scanner-loading').removeClass('active');
            $('body').removeClass('loading');
        },
        
        /**
         * Show error message
         */
        showError(message) {
            // Create or update error notification
            let $errorNotice = $('.stock-scanner-error-notice');
            
            if ($errorNotice.length === 0) {
                $errorNotice = $(`
                    <div class="stock-scanner-error-notice" style="
                        position: fixed;
                        top: 50px;
                        right: 20px;
                        background: var(--wp-error);
                        color: white;
                        padding: 15px 20px;
                        border-radius: 6px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                        z-index: 10000;
                        max-width: 400px;
                        opacity: 0;
                        transform: translateX(100%);
                        transition: all 0.3s ease;
                    ">
                        <div class="error-message"></div>
                        <button class="error-close" style="
                            background: none;
                            border: none;
                            color: white;
                            float: right;
                            font-size: 18px;
                            margin-top: -5px;
                            cursor: pointer;
                        ">&times;</button>
                    </div>
                `);
                $('body').append($errorNotice);
            }
            
            $errorNotice.find('.error-message').text(message);
            
            // Show with animation
            setTimeout(() => {
                $errorNotice.css({
                    opacity: 1,
                    transform: 'translateX(0)'
                });
            }, 100);
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                this.hideError();
            }, 5000);
            
            // Bind close button
            $errorNotice.find('.error-close').off('click').on('click', () => {
                this.hideError();
            });
        },
        
        /**
         * Hide error message
         */
        hideError() {
            $('.stock-scanner-error-notice').css({
                opacity: 0,
                transform: 'translateX(100%)'
            });
        },
        
        /**
         * Handle form submissions
         */
        async handleFormSubmission($form) {
            if (this.isLoading) {
                return;
            }
            
            this.isLoading = true;
            
            const formData = new FormData($form[0]);
            formData.append('action', 'stock_scanner_form_submit');
            formData.append('nonce', stockScannerPro.nonce);
            
            try {
                const response = await $.ajax({
                    url: stockScannerPro.ajaxUrl,
                    method: 'POST',
                    data: formData,
                    processData: false,
                    contentType: false
                });
                
                if (response.success) {
                    if (response.data.redirect) {
                        this.navigateToPage(response.data.redirect);
                    } else if (response.data.content) {
                        await this.displayContent(response.data.content, this.currentPage);
                    }
                } else {
                    throw new Error(response.data.message || 'Form submission failed');
                }
                
            } catch (error) {
                console.error('Form submission error:', error);
                this.showError('Form submission failed. Please try again.');
            } finally {
                this.isLoading = false;
            }
        },
        
        /**
         * Cache management
         */
        addToCache(url, content) {
            // Remove oldest entry if cache is full
            if (this.cache.size >= this.config.maxCacheSize) {
                const firstKey = this.cache.keys().next().value;
                this.cache.delete(firstKey);
            }
            
            this.cache.set(url, {
                content: content,
                timestamp: Date.now()
            });
        },
        
        /**
         * Get content from cache
         */
        getFromCache(url) {
            const cached = this.cache.get(url);
            
            if (!cached) {
                return null;
            }
            
            // Check if cache is expired
            if (Date.now() - cached.timestamp > this.config.cacheTimeout) {
                this.cache.delete(url);
                return null;
            }
            
            return cached.content;
        },
        
        /**
         * Clear cache
         */
        clearCache() {
            this.cache.clear();
        },
        
        /**
         * Re-initialize components after content change
         */
        reinitializeComponents() {
            // Re-initialize stock widgets
            if (typeof window.StockScannerPro !== 'undefined') {
                window.StockScannerPro.initializeWidgets();
            }
            
            // Re-initialize any third-party components
            $(document).trigger('stockScannerReinitialize');
            
            // Update mobile navigation
            $('.stock-scanner-nav-menu').removeClass('active');
        },
        
        /**
         * Handle window resize
         */
        handleResize() {
            // Close mobile menu on resize to desktop
            if ($(window).width() > 782) {
                $('.stock-scanner-nav-menu').removeClass('active');
            }
        },
        
        /**
         * Utility: Create delay
         */
        delay(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        },
        
        /**
         * Get current page URL
         */
        getCurrentPage() {
            return this.currentPage;
        },
        
        /**
         * Check if navigation is loading
         */
        isNavigationLoading() {
            return this.isLoading;
        }
    };
    
    /**
     * Progress Bar for page loading
     */
    const ProgressBar = {
        $element: null,
        
        init() {
            this.createElement();
            this.bindEvents();
        },
        
        createElement() {
            this.$element = $(`
                <div class="stock-scanner-progress-bar" style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 0%;
                    height: 3px;
                    background: var(--wp-primary);
                    z-index: 10001;
                    transition: width 0.3s ease;
                    opacity: 0;
                "></div>
            `);
            $('body').append(this.$element);
        },
        
        bindEvents() {
            $(document).on('stockScannerNavigationStart', () => {
                this.start();
            });
            
            $(document).on('stockScannerNavigationComplete', () => {
                this.complete();
            });
        },
        
        start() {
            this.$element.css({
                opacity: 1,
                width: '0%'
            });
            
            // Animate to 30%
            setTimeout(() => {
                this.$element.css('width', '30%');
            }, 100);
            
            // Slowly progress to 70%
            setTimeout(() => {
                this.$element.css('width', '70%');
            }, 500);
        },
        
        complete() {
            this.$element.css('width', '100%');
            
            setTimeout(() => {
                this.$element.css({
                    opacity: 0,
                    width: '0%'
                });
            }, 300);
        }
    };
    
    /**
     * Initialize when document is ready
     */
    $(document).ready(function() {
        // Only initialize on Stock Scanner pages
        if ($('.stock-scanner-pro').length > 0 || $('.stock-scanner-nav').length > 0) {
            StockScannerNavigation.init();
            ProgressBar.init();
            
            // Make navigation available globally
            window.StockScannerNavigation = StockScannerNavigation;
        }
    });
    
})(jQuery);