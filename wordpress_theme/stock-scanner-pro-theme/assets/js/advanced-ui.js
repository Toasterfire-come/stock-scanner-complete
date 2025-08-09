/**
 * Advanced UI Enhancement JavaScript
 * Improves user experience with modern interactions and animations
 */

class AdvancedUI {
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
        this.initAdvancedCharts();
    }

    // Advanced Notification System
    initNotificationSystem() {
        // Create notification container if it doesn't exist
        if (!document.querySelector('.notification-container')) {
            const container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }

        // Global notification function
        window.showNotification = (message, type = 'info', duration = 5000) => {
            const container = document.querySelector('.notification-container');
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
            setTimeout(() => notification.classList.add('show'), 100);

            // Auto remove
            if (duration > 0) {
                setTimeout(() => {
                    notification.classList.remove('show');
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
            element.classList.add('skeleton-container');
        };

        window.hideSkeleton = (element, content) => {
            element.classList.remove('skeleton-container');
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
        const searchInputs = document.querySelectorAll('.search-input');
        
        searchInputs.forEach(input => {
            const container = input.closest('.search-container');
            let suggestionsContainer = container.querySelector('.search-suggestions');
            
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
                if (!suggestionsContainer.classList.contains('show')) return;

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
                { symbol: 'AAPL', name: 'Apple Inc.', type: 'stock' },
                { symbol: 'GOOGL', name: 'Alphabet Inc.', type: 'stock' },
                { symbol: 'MSFT', name: 'Microsoft Corporation', type: 'stock' },
                { symbol: 'TSLA', name: 'Tesla, Inc.', type: 'stock' },
                { symbol: 'AMZN', name: 'Amazon.com Inc.', type: 'stock' }
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
                <div>
                    <strong>${suggestion.symbol || suggestion.title}</strong>
                    ${suggestion.name ? `<br><small>${suggestion.name}</small>` : ''}
                </div>
            </div>
        `).join('');

        container.classList.add('show');

        // Add click handlers
        container.querySelectorAll('.suggestion-item').forEach((item, index) => {
            item.addEventListener('click', () => {
                const input = container.parentElement.querySelector('.search-input');
                this.selectSuggestion(input, suggestions[index]);
                this.hideSuggestions(container);
            });
        });
    }

    hideSuggestions(container) {
        container.classList.remove('show');
    }

    highlightSuggestion(container, index) {
        container.querySelectorAll('.suggestion-item').forEach((item, i) => {
            item.classList.toggle('highlighted', i === index);
        });
    }

    selectSuggestion(input, suggestion) {
        input.value = suggestion.symbol || suggestion.title;
        input.dispatchEvent(new Event('suggestionSelected', { 
            detail: suggestion 
        }));
    }

    getSuggestionIcon(type) {
        const icons = {
            stock: '📈',
            news: '📰',
            sector: '🏢'
        };
        return icons[type] || '🔍';
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
                    entry.target.classList.add('revealed');
                }
            });
        }, observerOptions);

        // Observe elements with scroll-reveal class
        document.querySelectorAll('.scroll-reveal').forEach(el => {
            observer.observe(el);
        });

        // Add scroll-based navigation styling
        let lastScrollTop = 0;
        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const nav = document.querySelector('.nav-enhanced');
            
            if (nav) {
                if (scrollTop > 100) {
                    nav.classList.add('scrolled');
                } else {
                    nav.classList.remove('scrolled');
                }

                // Hide/show nav on scroll
                if (scrollTop > lastScrollTop && scrollTop > 200) {
                    nav.style.transform = 'translateY(-100%)';
                } else {
                    nav.style.transform = 'translateY(0)';
                }
            }
            
            lastScrollTop = scrollTop;
        });
    }

    // Enhanced Tooltips
    initTooltips() {
        document.addEventListener('mouseenter', (e) => {
            if (e.target.hasAttribute('data-tooltip')) {
                this.showTooltip(e.target, e.target.getAttribute('data-tooltip'));
            }
        }, true);

        document.addEventListener('mouseleave', (e) => {
            if (e.target.hasAttribute('data-tooltip')) {
                this.hideTooltip(e.target);
            }
        }, true);
    }

    showTooltip(element, text) {
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
            const circle = element.querySelector('.progress-ring-progress');
            const text = element.querySelector('.progress-ring-text');
            
            if (circle && text) {
                const circumference = 2 * Math.PI * 40; // radius = 40
                const strokeDasharray = `${percentage / 100 * circumference} ${circumference}`;
                circle.style.strokeDasharray = strokeDasharray;
                text.textContent = `${Math.round(percentage)}%`;
            }
        };

        // Animate progress rings on scroll
        const progressRings = document.querySelectorAll('.progress-ring');
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
                <div class="modal-content-enhanced" style="max-width: ${options.maxWidth || '600px'}">
                    ${options.showClose !== false ? '<button class="modal-close" onclick="this.closest(\'.modal-enhanced\').remove()">&times;</button>' : ''}
                    ${content}
                </div>
            `;

            document.body.appendChild(modal);
            
            // Show modal with animation
            setTimeout(() => modal.classList.add('show'), 10);

            // Close on backdrop click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
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
        modal.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
    }

    // Parallax Effects
    initParallaxEffects() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        
        if (parallaxElements.length === 0) return;

        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const speed = element.dataset.parallax || 0.5;
                const yPos = -(scrolled * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        });
    }

    // Advanced Navigation
    initAdvancedNavigation() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Active section highlighting
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('nav a[href^="#"]');

        if (sections.length > 0 && navLinks.length > 0) {
            const sectionObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        navLinks.forEach(link => {
                            link.classList.remove('active');
                            if (link.getAttribute('href') === `#${entry.target.id}`) {
                                link.classList.add('active');
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
            if (e.target.classList.contains('ripple')) {
                this.createRipple(e.target, e);
            }
        });
    }

    createRipple(element, event) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

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

        element.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }

    // Floating Labels
    initFloatingLabels() {
        const inputs = document.querySelectorAll('.form-control-enhanced');
        
        inputs.forEach(input => {
            // Create floating label if it doesn't exist
            if (!input.nextElementSibling?.classList.contains('floating-label')) {
                const label = document.createElement('label');
                label.className = 'floating-label';
                label.textContent = input.placeholder || 'Enter value';
                input.parentNode.insertBefore(label, input.nextSibling);
            }

            // Add required placeholder for CSS selector
            if (!input.placeholder) {
                input.placeholder = ' ';
            }
        });
    }

    // Advanced Tables
    initAdvancedTables() {
        const tables = document.querySelectorAll('.table-enhanced');
        
        tables.forEach(table => {
            // Add sorting functionality
            const headers = table.querySelectorAll('th[data-sortable]');
            headers.forEach(header => {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    this.sortTable(table, header);
                });
            });

            // Add row selection
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                row.addEventListener('click', () => {
                    rows.forEach(r => r.classList.remove('selected'));
                    row.classList.add('selected');
                });
            });
        });
    }

    sortTable(table, header) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const columnIndex = Array.from(header.parentNode.children).indexOf(header);
        const isAscending = !header.classList.contains('sorted-asc');

        rows.sort((a, b) => {
            const aValue = a.children[columnIndex].textContent.trim();
            const bValue = b.children[columnIndex].textContent.trim();
            
            const comparison = isNaN(aValue) ? 
                aValue.localeCompare(bValue) : 
                parseFloat(aValue) - parseFloat(bValue);
            
            return isAscending ? comparison : -comparison;
        });

        // Clear previous sort indicators
        header.parentNode.querySelectorAll('th').forEach(h => {
            h.classList.remove('sorted-asc', 'sorted-desc');
        });

        // Add sort indicator
        header.classList.add(isAscending ? 'sorted-asc' : 'sorted-desc');

        // Reorder rows
        rows.forEach(row => tbody.appendChild(row));
    }

    // Lazy Loading
    initLazyLoading() {
        const lazyElements = document.querySelectorAll('[data-lazy]');
        
        if (lazyElements.length === 0) return;

        const lazyObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadLazyElement(entry.target);
                    lazyObserver.unobserve(entry.target);
                }
            });
        });

        lazyElements.forEach(element => lazyObserver.observe(element));
    }

    loadLazyElement(element) {
        const src = element.dataset.lazy;
        
        if (element.tagName === 'IMG') {
            element.src = src;
        } else {
            // Load content via AJAX
            fetch(src)
                .then(response => response.text())
                .then(html => {
                    element.innerHTML = html;
                    element.classList.add('lazy-loaded');
                });
        }
    }

    // Keyboard Shortcuts
    initKeyboardShortcuts() {
        const shortcuts = {
            'ctrl+k': () => {
                const searchInput = document.querySelector('.search-input');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            },
            'escape': () => {
                // Close any open modals
                const modals = document.querySelectorAll('.modal-enhanced.show');
                modals.forEach(modal => this.closeModal(modal));
                
                // Clear search
                const searchInputs = document.querySelectorAll('.search-input');
                searchInputs.forEach(input => {
                    input.blur();
                    const container = input.closest('.search-container');
                    const suggestions = container?.querySelector('.search-suggestions');
                    if (suggestions) this.hideSuggestions(suggestions);
                });
            },
            'ctrl+s': (e) => {
                e.preventDefault();
                const saveBtn = document.querySelector('[data-action="save"]');
                if (saveBtn) saveBtn.click();
            }
        };

        document.addEventListener('keydown', (e) => {
            const key = e.key.toLowerCase();
            const combo = [];
            
            if (e.ctrlKey) combo.push('ctrl');
            if (e.altKey) combo.push('alt');
            if (e.shiftKey) combo.push('shift');
            combo.push(key);
            
            const shortcut = combo.join('+');
            
            if (shortcuts[shortcut]) {
                shortcuts[shortcut](e);
            }
        });
    }

    // Virtualized Lists (for large datasets)
    initVirtualizedLists() {
        const virtualLists = document.querySelectorAll('[data-virtual-list]');
        
        virtualLists.forEach(list => {
            this.createVirtualList(list);
        });
    }

    createVirtualList(container) {
        const itemHeight = parseInt(container.dataset.itemHeight) || 50;
        const buffer = 5; // Extra items to render for smooth scrolling
        let scrollTop = 0;
        let data = JSON.parse(container.dataset.items || '[]');

        const viewport = document.createElement('div');
        viewport.style.cssText = `
            height: ${container.dataset.height || '400px'};
            overflow-y: auto;
            position: relative;
        `;

        const content = document.createElement('div');
        content.style.height = `${data.length * itemHeight}px`;

        const visibleItems = document.createElement('div');
        visibleItems.style.position = 'absolute';
        visibleItems.style.top = '0';
        visibleItems.style.width = '100%';

        content.appendChild(visibleItems);
        viewport.appendChild(content);
        container.appendChild(viewport);

        const updateVisibleItems = () => {
            const containerHeight = viewport.clientHeight;
            const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - buffer);
            const endIndex = Math.min(data.length, Math.ceil((scrollTop + containerHeight) / itemHeight) + buffer);

            visibleItems.innerHTML = '';
            visibleItems.style.transform = `translateY(${startIndex * itemHeight}px)`;

            for (let i = startIndex; i < endIndex; i++) {
                const item = document.createElement('div');
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
    }

    renderVirtualListItem(item, index) {
        // Override this method for custom item rendering
        return `<div class="virtual-list-item">${item.name || item.title || `Item ${index}`}</div>`;
    }

    // Advanced Charts Integration
    initAdvancedCharts() {
        window.createAdvancedChart = (canvas, config) => {
            const ctx = canvas.getContext('2d');
            
            // Enhanced default configuration
            const defaultConfig = {
                type: 'line',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    },
                    plugins: {
                        tooltip: {
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: '#3498db',
                            borderWidth: 1,
                            cornerRadius: 8,
                            displayColors: false
                        },
                        legend: {
                            position: 'top',
                            labels: {
                                usePointStyle: true,
                                padding: 20
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { color: '#6c757d' }
                        },
                        y: {
                            grid: { color: 'rgba(0,0,0,0.1)' },
                            ticks: { color: '#6c757d' }
                        }
                    },
                    animation: {
                        duration: 2000,
                        easing: 'easeInOutQuart'
                    }
                }
            };

            // Merge configurations
            const mergedConfig = this.deepMerge(defaultConfig, config);
            
            return new Chart(ctx, mergedConfig);
        };
    }

    deepMerge(target, source) {
        const output = Object.assign({}, target);
        if (this.isObject(target) && this.isObject(source)) {
            Object.keys(source).forEach(key => {
                if (this.isObject(source[key])) {
                    if (!(key in target))
                        Object.assign(output, { [key]: source[key] });
                    else
                        output[key] = this.deepMerge(target[key], source[key]);
                } else {
                    Object.assign(output, { [key]: source[key] });
                }
            });
        }
        return output;
    }

    isObject(item) {
        return item && typeof item === 'object' && !Array.isArray(item);
    }
}

// Initialize Advanced UI
document.addEventListener('DOMContentLoaded', () => {
    window.advancedUI = new AdvancedUI();
});

// Add CSS animation for ripple effect
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .virtual-list-item {
        padding: 10px;
        border-bottom: 1px solid #eee;
        display: flex;
        align-items: center;
    }
    
    .notification-close {
        position: absolute;
        top: 10px;
        right: 10px;
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        opacity: 0.7;
    }
    
    .notification-close:hover {
        opacity: 1;
    }
    
    .dynamic-tooltip {
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .table-enhanced th.sorted-asc:after {
        content: ' ↑';
        color: #3498db;
    }
    
    .table-enhanced th.sorted-desc:after {
        content: ' ↓';
        color: #3498db;
    }
    
    .table-enhanced tbody tr.selected {
        background: rgba(52, 152, 219, 0.1) !important;
    }
    
    .lazy-loaded {
        animation: fadeIn 0.5s ease-in-out;
    }
`;
document.head.appendChild(style);