/**
 * Advanced UI Enhancement - Pure Vanilla JavaScript
 * Production-ready user experience enhancements without dependencies
 */

class AdvancedUIVanilla {
    constructor() {
        this.init();
    }

    init() {
        this.initNotificationSystem();
        this.initSkeletonLoaders();
        this.initAdvancedSearch();
        this.initScrollAnimations();
        this.initTooltips();
        this.initProgressIndicators();
        this.initAdvancedModals();
        this.initParallaxEffects();
        this.initAdvancedNavigation();
        this.initRippleEffects();
        this.initFloatingLabels();
        this.initAdvancedTables();
        this.initLazyLoading();
        this.initKeyboardShortcuts();
        this.initVirtualizedLists();
        this.initDarkModeSupport();
    }

    // Utility methods
    select(selector, context = document) {
        return context.querySelector(selector);
    }

    selectAll(selector, context = document) {
        return context.querySelectorAll(selector);
    }

    addClass(element, className) {
        if (element) element.classList.add(className);
    }

    removeClass(element, className) {
        if (element) element.classList.remove(className);
    }

    toggleClass(element, className) {
        if (element) element.classList.toggle(className);
    }

    // Advanced Notification System
    initNotificationSystem() {
        // Create notification container if it doesn't exist
        if (!this.select('.notification-container')) {
            const container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }

        // Global notification function
        window.showNotification = (message, type = 'info', duration = 5000) => {
            const container = this.select('.notification-container');
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            
            const icon = this.getNotificationIcon(type);
            notification.innerHTML = `
                <div class="notification-icon">${icon}</div>
                <div class="notification-content">
                    <strong>${this.getNotificationTitle(type)}</strong>
                    <p>${message}</p>
                </div>
                <button class="notification-close" onclick="this.parentElement.remove()">&times;</button>
            `;

            container.appendChild(notification);

            // Trigger animation
            setTimeout(() => this.addClass(notification, 'show'), 100);

            // Auto remove
            if (duration > 0) {
                setTimeout(() => {
                    this.removeClass(notification, 'show');
                    setTimeout(() => notification.remove(), 500);
                }, duration);
            }
        };
    }

    getNotificationIcon(type) {
        const icons = {
            success: '✓',
            error: '✗',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }

    getNotificationTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information'
        };
        return titles[type] || titles.info;
    }

    // Skeleton Loading System
    initSkeletonLoaders() {
        window.showSkeleton = (element, type = 'default') => {
            const skeletonHTML = this.generateSkeletonHTML(type);
            element.innerHTML = skeletonHTML;
            this.addClass(element, 'skeleton-container');
        };

        window.hideSkeleton = (element, content) => {
            this.removeClass(element, 'skeleton-container');
            element.innerHTML = content;
        };
    }

    generateSkeletonHTML(type) {
        const skeletons = {
            default: `
                <div class="skeleton-card">
                    <div class="skeleton skeleton-text large wide"></div>
                    <div class="skeleton skeleton-text medium"></div>
                    <div class="skeleton skeleton-text narrow"></div>
                </div>
            `,
            table: `
                <div class="skeleton-card">
                    ${Array(5).fill().map(() => `
                        <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                            <div class="skeleton skeleton-avatar"></div>
                            <div style="flex: 1;">
                                <div class="skeleton skeleton-text medium"></div>
                                <div class="skeleton skeleton-text small narrow"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `,
            chart: `<div class="skeleton skeleton-chart"></div>`
        };
        return skeletons[type] || skeletons.default;
    }

    // Advanced Search with Autocomplete
    initAdvancedSearch() {
        const searchInputs = this.selectAll('.search-input');
        
        searchInputs.forEach(input => {
            const container = input.closest('.search-container');
            let suggestionsContainer = this.select('.search-suggestions', container);
            
            if (!suggestionsContainer) {
                suggestionsContainer = document.createElement('div');
                suggestionsContainer.className = 'search-suggestions';
                container.appendChild(suggestionsContainer);
            }

            let searchTimeout;
            let currentSuggestions = [];
            let selectedIndex = -1;

            input.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const query = e.target.value.trim();

                if (query.length < 2) {
                    this.hideSuggestions(suggestionsContainer);
                    return;
                }

                searchTimeout = setTimeout(() => {
                    this.fetchSuggestions(query, input.dataset.searchType || 'stocks')
                        .then(suggestions => {
                            currentSuggestions = suggestions;
                            selectedIndex = -1;
                            this.displaySuggestions(suggestionsContainer, suggestions);
                        });
                }, 300);
            });

            input.addEventListener('keydown', (e) => {
                if (!suggestionsContainer.classList.contains('suggestions-visible')) return;

                switch (e.key) {
                    case 'ArrowDown':
                        e.preventDefault();
                        selectedIndex = Math.min(selectedIndex + 1, currentSuggestions.length - 1);
                        this.highlightSuggestion(suggestionsContainer, selectedIndex);
                        break;
                    case 'ArrowUp':
                        e.preventDefault();
                        selectedIndex = Math.max(selectedIndex - 1, -1);
                        this.highlightSuggestion(suggestionsContainer, selectedIndex);
                        break;
                    case 'Enter':
                        e.preventDefault();
                        if (selectedIndex >= 0 && currentSuggestions[selectedIndex]) {
                            this.selectSuggestion(input, currentSuggestions[selectedIndex]);
                            this.hideSuggestions(suggestionsContainer);
                        }
                        break;
                    case 'Escape':
                        this.hideSuggestions(suggestionsContainer);
                        break;
                }
            });

            // Hide suggestions when clicking outside
            document.addEventListener('click', (e) => {
                if (!container.contains(e.target)) {
                    this.hideSuggestions(suggestionsContainer);
                }
            });
        });
    }

    async fetchSuggestions(query, type) {
        // Simulate API call - replace with actual implementation
        const mockSuggestions = {
            stocks: [
                { symbol: 'AAPL', name: 'Apple Inc.', type: 'stock', price: 150.25 },
                { symbol: 'GOOGL', name: 'Alphabet Inc.', type: 'stock', price: 2800.50 },
                { symbol: 'MSFT', name: 'Microsoft Corporation', type: 'stock', price: 310.75 },
                { symbol: 'TSLA', name: 'Tesla, Inc.', type: 'stock', price: 800.15 },
                { symbol: 'AMZN', name: 'Amazon.com Inc.', type: 'stock', price: 3200.40 }
            ].filter(item => 
                item.symbol.toLowerCase().includes(query.toLowerCase()) ||
                item.name.toLowerCase().includes(query.toLowerCase())
            ),
            news: [
                { title: 'Market Update', category: 'market', type: 'news' },
                { title: 'Earnings Report', category: 'earnings', type: 'news' }
            ]
        };

        return new Promise(resolve => {
            setTimeout(() => resolve(mockSuggestions[type] || []), 150);
        });
    }

    displaySuggestions(container, suggestions) {
        if (suggestions.length === 0) {
            this.hideSuggestions(container);
            return;
        }

        container.innerHTML = suggestions.map((suggestion, index) => `
            <div class="suggestion-item" data-index="${index}">
                <span class="suggestion-icon">${this.getSuggestionIcon(suggestion.type)}</span>
                <div class="suggestion-content">
                    <div class="suggestion-title">${suggestion.symbol || suggestion.title}</div>
                    ${suggestion.name ? `<div class="suggestion-meta">${suggestion.name}</div>` : ''}
                    ${suggestion.price ? `<div class="suggestion-price">$${suggestion.price}</div>` : ''}
                </div>
            </div>
        `).join('');

        this.addClass(container, 'suggestions-visible');

        // Add click handlers
        this.selectAll('.suggestion-item', container).forEach((item, index) => {
            item.addEventListener('click', () => {
                const input = container.parentElement.querySelector('.search-input');
                this.selectSuggestion(input, suggestions[index]);
                this.hideSuggestions(container);
            });
        });
    }

    hideSuggestions(container) {
        this.removeClass(container, 'suggestions-visible');
    }

    highlightSuggestion(container, index) {
        this.selectAll('.suggestion-item', container).forEach((item, i) => {
            this.toggleClass(item, 'highlighted', i === index);
        });
    }

    selectSuggestion(input, suggestion) {
        input.value = suggestion.symbol || suggestion.title;
        const event = new CustomEvent('suggestionSelected', { 
            detail: suggestion 
        });
        input.dispatchEvent(event);
    }

    getSuggestionIcon(type) {
        const icons = {
            stock: '📈',
            news: '📰',
            sector: '🏢'
        };
        return icons[type] || '';
    }

    // Scroll Animations
    initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.addClass(entry.target, 'revealed');
                }
            });
        }, observerOptions);

        // Observe elements with scroll-reveal class
        this.selectAll('.scroll-reveal').forEach(el => {
            observer.observe(el);
        });

        // Add scroll-based navigation styling
        let lastScrollTop = 0;
        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const nav = this.select('.nav-enhanced');
            
            if (nav) {
                if (scrollTop > 100) {
                    this.addClass(nav, 'scrolled');
                } else {
                    this.removeClass(nav, 'scrolled');
                }

                // Hide/show nav on scroll
                if (scrollTop > lastScrollTop && scrollTop > 200) {
                    nav.style.transform = 'translateY(-100%)';
                } else {
                    nav.style.transform = 'translateY(0)';
                }
            }
            
            lastScrollTop = scrollTop;
        }, { passive: true });
    }

    // Enhanced Tooltips
    initTooltips() {
        document.addEventListener('mouseenter', (e) => {
            const target = e.target.closest('[data-tooltip]');
            if (target) {
                this.showTooltip(target, target.getAttribute('data-tooltip'));
            }
        }, true);

        document.addEventListener('mouseleave', (e) => {
            const target = e.target.closest('[data-tooltip]');
            if (target) {
                this.hideTooltip(target);
            }
        }, true);
    }

    showTooltip(element, text) {
        if (element._tooltip) return;

        const tooltip = document.createElement('div');
        tooltip.className = 'dynamic-tooltip';
        tooltip.textContent = text;
        document.body.appendChild(tooltip);

        const rect = element.getBoundingClientRect();
        tooltip.style.cssText = `
            position: fixed;
            background: #2c3e50;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            z-index: 10000;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
            white-space: nowrap;
        `;

        // Position tooltip
        const tooltipRect = tooltip.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2 - tooltipRect.width / 2}px`;
        tooltip.style.top = `${rect.top - tooltipRect.height - 5}px`;

        // Show tooltip
        setTimeout(() => tooltip.style.opacity = '1', 10);

        element._tooltip = tooltip;
    }

    hideTooltip(element) {
        if (element._tooltip) {
            element._tooltip.remove();
            delete element._tooltip;
        }
    }

    // Progress Indicators
    initProgressIndicators() {
        window.updateProgress = (element, percentage) => {
            const circle = this.select('.progress-ring-progress', element);
            const text = this.select('.progress-ring-text', element);
            
            if (circle && text) {
                const circumference = 2 * Math.PI * 40; // radius = 40
                const strokeDasharray = `${percentage / 100 * circumference} ${circumference}`;
                circle.style.strokeDasharray = strokeDasharray;
                text.textContent = `${Math.round(percentage)}%`;
            }
        };

        // Animate progress rings on scroll
        const progressRings = this.selectAll('.progress-ring');
        const progressObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const targetPercentage = entry.target.dataset.percentage || 75;
                    this.animateProgress(entry.target, targetPercentage);
                }
            });
        });

        progressRings.forEach(ring => progressObserver.observe(ring));
    }

    animateProgress(element, targetPercentage) {
        let current = 0;
        const increment = targetPercentage / 60; // 60 frames for 1 second animation
        
        const animate = () => {
            current += increment;
            if (current <= targetPercentage) {
                window.updateProgress(element, current);
                requestAnimationFrame(animate);
            } else {
                window.updateProgress(element, targetPercentage);
            }
        };
        
        animate();
    }

    // Advanced Modals
    initAdvancedModals() {
        window.showModal = (content, options = {}) => {
            const modal = document.createElement('div');
            modal.className = 'modal-enhanced';
            modal.innerHTML = `
                <div class="modal-backdrop"></div>
                <div class="modal-content-enhanced" style="max-width: ${options.maxWidth || '600px'}">
                    ${options.showClose !== false ? '<button class="modal-close" onclick="this.closest(\'.modal-enhanced\').remove()">&times;</button>' : ''}
                    <div class="modal-body">${content}</div>
                </div>
            `;

            document.body.appendChild(modal);
            
            // Show modal with animation
            setTimeout(() => this.addClass(modal, 'modal-show'), 10);

            // Close on backdrop click
            const backdrop = this.select('.modal-backdrop', modal);
            backdrop.addEventListener('click', () => {
                this.closeModal(modal);
            });

            // Close on escape key
            const escapeHandler = (e) => {
                if (e.key === 'Escape') {
                    this.closeModal(modal);
                    document.removeEventListener('keydown', escapeHandler);
                }
            };
            document.addEventListener('keydown', escapeHandler);

            return modal;
        };
    }

    closeModal(modal) {
        this.removeClass(modal, 'modal-show');
        setTimeout(() => modal.remove(), 300);
    }

    // Parallax Effects
    initParallaxEffects() {
        const parallaxElements = this.selectAll('[data-parallax]');
        
        if (parallaxElements.length === 0) return;

        let ticking = false;

        const updateParallax = () => {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const speed = parseFloat(element.dataset.parallax) || 0.5;
                const yPos = -(scrolled * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
            
            ticking = false;
        };

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateParallax);
                ticking = true;
            }
        }, { passive: true });
    }

    // Advanced Navigation
    initAdvancedNavigation() {
        // Smooth scrolling for anchor links
        this.selectAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href === '#') return;
                
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Active section highlighting
        const sections = this.selectAll('section[id]');
        const navLinks = this.selectAll('nav a[href^="#"]');

        if (sections.length > 0 && navLinks.length > 0) {
            const sectionObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        navLinks.forEach(link => {
                            this.removeClass(link, 'active');
                            if (link.getAttribute('href') === `#${entry.target.id}`) {
                                this.addClass(link, 'active');
                            }
                        });
                    }
                });
            }, { threshold: 0.3 });

            sections.forEach(section => sectionObserver.observe(section));
        }
    }

    // Ripple Effects
    initRippleEffects() {
        document.addEventListener('click', (e) => {
            const target = e.target.closest('.ripple');
            if (target) {
                this.createRipple(target, e);
            }
        });
    }

    createRipple(element, event) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.className = 'ripple-effect';
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        `;

        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }

    // Floating Labels
    initFloatingLabels() {
        const inputs = this.selectAll('.form-control-enhanced');
        
        inputs.forEach(input => {
            const wrapper = input.parentElement;
            
            // Create floating label if it doesn't exist
            if (!this.select('.floating-label', wrapper)) {
                const label = document.createElement('label');
                label.className = 'floating-label';
                label.textContent = input.placeholder || 'Enter value';
                wrapper.appendChild(label);
            }

            // Add required placeholder for CSS selector
            if (!input.placeholder) {
                input.placeholder = ' ';
            }

            // Handle focus and blur events
            input.addEventListener('focus', () => {
                this.addClass(wrapper, 'focused');
            });

            input.addEventListener('blur', () => {
                this.removeClass(wrapper, 'focused');
                this.toggleClass(wrapper, 'filled', input.value.trim() !== '');
            });

            // Initial state
            this.toggleClass(wrapper, 'filled', input.value.trim() !== '');
        });
    }

    // Advanced Tables
    initAdvancedTables() {
        const tables = this.selectAll('.table-enhanced');
        
        tables.forEach(table => {
            this.setupTableSorting(table);
            this.setupTableSelection(table);
            this.setupStickyHeaders(table);
        });
    }

    setupTableSorting(table) {
        const headers = this.selectAll('th[data-sortable]', table);
        
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            this.addClass(header, 'sortable-header');
            
            // Add sort indicator
            if (!this.select('.sort-indicator', header)) {
                const indicator = document.createElement('span');
                indicator.className = 'sort-indicator';
                indicator.innerHTML = '⇅';
                header.appendChild(indicator);
            }
            
            header.addEventListener('click', () => {
                this.sortTable(table, header);
            });
        });
    }

    sortTable(table, header) {
        const tbody = this.select('tbody', table);
        const rows = Array.from(this.selectAll('tr', tbody));
        const columnIndex = Array.from(header.parentNode.children).indexOf(header);
        const isAscending = !header.classList.contains('sorted-asc');

        // Clear all sort indicators
        this.selectAll('th', table).forEach(h => {
            this.removeClass(h, 'sorted-asc');
            this.removeClass(h, 'sorted-desc');
            const indicator = this.select('.sort-indicator', h);
            if (indicator) indicator.innerHTML = '⇅';
        });

        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.children[columnIndex].textContent.trim();
            const bValue = b.children[columnIndex].textContent.trim();
            
            // Try to parse as numbers
            const aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
            const bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));
            
            let comparison;
            if (!isNaN(aNum) && !isNaN(bNum)) {
                comparison = aNum - bNum;
            } else {
                comparison = aValue.localeCompare(bValue);
            }
            
            return isAscending ? comparison : -comparison;
        });

        // Update header class and indicator
        this.addClass(header, isAscending ? 'sorted-asc' : 'sorted-desc');
        const indicator = this.select('.sort-indicator', header);
        if (indicator) {
            indicator.innerHTML = isAscending ? '↑' : '↓';
        }

        // Re-append sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }

    setupTableSelection(table) {
        const rows = this.selectAll('tbody tr', table);
        
        rows.forEach(row => {
            row.addEventListener('click', (event) => {
                // Allow multiple selection with Ctrl/Cmd
                if (!event.ctrlKey && !event.metaKey) {
                    rows.forEach(r => this.removeClass(r, 'selected'));
                }
                this.toggleClass(row, 'selected');
                
                // Dispatch selection event
                const selectionEvent = new CustomEvent('rowSelection', {
                    detail: {
                        selectedRows: Array.from(this.selectAll('tbody tr.selected', table))
                    }
                });
                table.dispatchEvent(selectionEvent);
            });
        });
    }

    setupStickyHeaders(table) {
        const header = this.select('thead', table);
        if (!header) return;

        const observer = new IntersectionObserver(
            ([entry]) => {
                this.toggleClass(table, 'sticky-header', !entry.isIntersecting);
            },
            { threshold: 1 }
        );

        observer.observe(header);
    }

    // Lazy Loading System
    initLazyLoading() {
        this.initImageLazyLoading();
        this.initContentLazyLoading();
    }

    initImageLazyLoading() {
        const lazyImages = this.selectAll('img[data-lazy]');
        
        if (lazyImages.length === 0) return;

        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.lazy;
                    this.addClass(img, 'lazy-loaded');
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => imageObserver.observe(img));
    }

    initContentLazyLoading() {
        const lazyContent = this.selectAll('[data-lazy-content]');
        
        if (lazyContent.length === 0) return;

        const contentObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadLazyContent(entry.target);
                    contentObserver.unobserve(entry.target);
                }
            });
        });

        lazyContent.forEach(element => contentObserver.observe(element));
    }

    loadLazyContent(element) {
        const url = element.dataset.lazyContent;
        this.addClass(element, 'loading');
        
        fetch(url)
            .then(response => response.text())
            .then(html => {
                element.innerHTML = html;
                this.removeClass(element, 'loading');
                this.addClass(element, 'lazy-loaded');
            })
            .catch(error => {
                element.innerHTML = '<p>Failed to load content</p>';
                this.removeClass(element, 'loading');
                this.addClass(element, 'lazy-error');
            });
    }

    // Keyboard Shortcuts
    initKeyboardShortcuts() {
        const shortcuts = {
            'ctrl+k': () => this.openCommandPalette(),
            'ctrl+/': () => this.showShortcuts(),
            'escape': () => this.closeModals()
        };

        document.addEventListener('keydown', (e) => {
            const key = [];
            if (e.ctrlKey) key.push('ctrl');
            if (e.metaKey) key.push('cmd');
            if (e.shiftKey) key.push('shift');
            if (e.altKey) key.push('alt');
            key.push(e.key.toLowerCase());

            const combination = key.join('+');
            if (shortcuts[combination]) {
                e.preventDefault();
                shortcuts[combination]();
            }
        });
    }

    openCommandPalette() {
        // Command palette implementation
        console.log('Command palette opened');
    }

    showShortcuts() {
        const shortcutsModal = `
            <h3>Keyboard Shortcuts</h3>
            <div class="shortcuts-list">
                <div class="shortcut-item">
                    <kbd>Ctrl+K</kbd>
                    <span>Open command palette</span>
                </div>
                <div class="shortcut-item">
                    <kbd>Ctrl+/</kbd>
                    <span>Show shortcuts</span>
                </div>
                <div class="shortcut-item">
                    <kbd>Escape</kbd>
                    <span>Close modals</span>
                </div>
            </div>
        `;
        window.showModal(shortcutsModal, { maxWidth: '400px' });
    }

    closeModals() {
        const activeModals = this.selectAll('.modal-enhanced.modal-show');
        activeModals.forEach(modal => this.closeModal(modal));
    }

    // Virtualized Lists
    initVirtualizedLists() {
        const virtualLists = this.selectAll('[data-virtual-list]');
        virtualLists.forEach(list => this.createVirtualList(list));
    }

    createVirtualList(container) {
        const itemHeight = parseInt(container.dataset.itemHeight) || 50;
        const containerHeight = parseInt(container.dataset.height) || 400;
        const buffer = 5;
        let scrollTop = 0;
        let data = [];

        // Try to parse data from attribute
        if (container.dataset.items) {
            try {
                data = JSON.parse(container.dataset.items);
            } catch (e) {
                console.error('Invalid JSON in data-items:', e);
            }
        }

        const viewport = document.createElement('div');
        viewport.className = 'virtual-list-viewport';
        viewport.style.cssText = `
            height: ${containerHeight}px;
            overflow-y: auto;
            position: relative;
        `;

        const content = document.createElement('div');
        content.className = 'virtual-list-content';
        content.style.height = `${data.length * itemHeight}px`;

        const visibleItems = document.createElement('div');
        visibleItems.className = 'virtual-list-items';
        visibleItems.style.cssText = `
            position: absolute;
            top: 0;
            width: 100%;
        `;

        content.appendChild(visibleItems);
        viewport.appendChild(content);
        container.appendChild(viewport);

        const updateVisibleItems = () => {
            const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - buffer);
            const endIndex = Math.min(data.length, Math.ceil((scrollTop + containerHeight) / itemHeight) + buffer);

            visibleItems.innerHTML = '';
            visibleItems.style.transform = `translateY(${startIndex * itemHeight}px)`;

            for (let i = startIndex; i < endIndex; i++) {
                const item = document.createElement('div');
                item.className = 'virtual-list-item';
                item.style.height = `${itemHeight}px`;
                item.innerHTML = this.renderVirtualListItem(data[i], i);
                visibleItems.appendChild(item);
            }
        };

        viewport.addEventListener('scroll', () => {
            scrollTop = viewport.scrollTop;
            updateVisibleItems();
        });

        updateVisibleItems();

        // Expose method to update data
        container.updateVirtualListData = (newData) => {
            data = newData;
            content.style.height = `${data.length * itemHeight}px`;
            updateVisibleItems();
        };
    }

    renderVirtualListItem(item, index) {
        if (typeof item === 'string') {
            return `<div class="virtual-item-content">${item}</div>`;
        }
        
        return `
            <div class="virtual-item-content">
                <div class="virtual-item-title">${item.name || item.title || `Item ${index + 1}`}</div>
                ${item.subtitle ? `<div class="virtual-item-subtitle">${item.subtitle}</div>` : ''}
            </div>
        `;
    }

    // Dark Mode Support
    initDarkModeSupport() {
        // Check for saved preference or system preference
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        const isDark = savedTheme === 'dark' || (!savedTheme && systemPrefersDark);
        
        this.setTheme(isDark ? 'dark' : 'light');
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });

        // Add theme toggle function
        window.toggleTheme = () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            this.setTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        };
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update meta theme color for mobile browsers
        const metaThemeColor = this.select('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', theme === 'dark' ? '#1a1a1a' : '#ffffff');
        }
    }
}

// Initialize Enhanced UI
document.addEventListener('DOMContentLoaded', () => {
    window.advancedUIVanilla = new AdvancedUIVanilla();
});

// Export for global use
window.AdvancedUIVanilla = AdvancedUIVanilla;