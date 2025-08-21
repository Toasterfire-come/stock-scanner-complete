/**
 * Enhanced UI Components
 * Advanced Frontend Features for Stock Scanner
 */

class EnhancedUI {
    constructor() {
        this.init();
    }

    init() {
        this.initAdvancedLoadingStates();
        this.initMicroInteractions();
        this.initAdvancedSearch();
        this.initProgressIndicators();
        this.initAdvancedCharts();
        this.initAdvancedModals();
        this.initEnhancedFormControls();
        this.initSmartNavigation();
        this.initLazyLoading();
        this.initVirtualizedLists();
        this.initParallaxEffects();
        this.initEnhancedTables();
        this.initDarkModeSupport();
    }

    // 1. Advanced Loading States
    initAdvancedLoadingStates() {
        window.showSkeleton = (element, type = 'default') => {
            this.createSkeleton(element, type);
        };

        window.hideSkeleton = (element, content) => {
            this.removeSkeleton(element, content);
        };
    }

    createSkeleton(element, type) {
        if (element.classList.contains('skeleton-loading')) return;

        element.classList.add('skeleton-loading');
        const originalContent = element.innerHTML;
        element.setAttribute('data-original-content', originalContent);

        let skeletonHTML = '';
        
        switch (type) {
            case 'table':
                skeletonHTML = this.createTableSkeleton();
                break;
            case 'card':
                skeletonHTML = this.createCardSkeleton();
                break;
            case 'chart':
                skeletonHTML = this.createChartSkeleton();
                break;
            case 'avatar':
                skeletonHTML = this.createAvatarSkeleton();
                break;
            case 'text':
                skeletonHTML = this.createTextSkeleton();
                break;
            default:
                skeletonHTML = this.createDefaultSkeleton();
        }

        element.innerHTML = skeletonHTML;
    }

    removeSkeleton(element, content) {
        if (!element.classList.contains('skeleton-loading')) return;

        element.classList.remove('skeleton-loading');
        
        if (content) {
            element.innerHTML = content;
        } else {
            const originalContent = element.getAttribute('data-original-content');
            if (originalContent) {
                element.innerHTML = originalContent;
                element.removeAttribute('data-original-content');
            }
        }

        // Add fade-in animation
        element.style.opacity = '0';
        requestAnimationFrame(() => {
            element.style.transition = 'opacity 0.3s ease';
            element.style.opacity = '1';
        });
    }

    createTableSkeleton() {
        return `
            <div class="skeleton-table">
                ${Array(5).fill().map(() => `
                    <div class="skeleton-row">
                        ${Array(4).fill().map(() => '<div class="skeleton skeleton-cell"></div>').join('')}
                    </div>
                `).join('')}
            </div>
        `;
    }

    createCardSkeleton() {
        return `
            <div class="skeleton-card">
                <div class="skeleton skeleton-avatar"></div>
                <div class="skeleton-content">
                    <div class="skeleton skeleton-title"></div>
                    <div class="skeleton skeleton-text"></div>
                    <div class="skeleton skeleton-text short"></div>
                </div>
            </div>
        `;
    }

    createChartSkeleton() {
        return `
            <div class="skeleton-chart">
                <div class="skeleton-chart-title skeleton"></div>
                <div class="skeleton-chart-content">
                    ${Array(6).fill().map((_, i) => `
                        <div class="skeleton-bar" style="height: ${20 + Math.random() * 60}%"></div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    createAvatarSkeleton() {
        return '<div class="skeleton skeleton-avatar"></div>';
    }

    createTextSkeleton() {
        return `
            <div class="skeleton-text-block">
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text short"></div>
            </div>
        `;
    }

    createDefaultSkeleton() {
        return `
            <div class="skeleton-default">
                <div class="skeleton skeleton-line"></div>
                <div class="skeleton skeleton-line"></div>
                <div class="skeleton skeleton-line short"></div>
            </div>
        `;
    }

    // 2. Micro-interactions & Animations
    initMicroInteractions() {
        this.initRippleEffects();
        this.initButtonEnhancements();
        this.initCardInteractions();
        this.initScrollAnimations();
    }

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

        ripple.classList.add('ripple-effect');
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            border-radius: 50%;
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        `;

        element.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    }

    initButtonEnhancements() {
        const enhancedButtons = document.querySelectorAll('.btn-enhanced');
        enhancedButtons.forEach(button => {
            button.addEventListener('mouseenter', () => {
                button.classList.add('btn-hover');
            });
            button.addEventListener('mouseleave', () => {
                button.classList.remove('btn-hover');
            });
        });
    }

    initCardInteractions() {
        const interactiveCards = document.querySelectorAll('.card-interactive');
        interactiveCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.classList.add('card-hover');
            });
            card.addEventListener('mouseleave', () => {
                card.classList.remove('card-hover');
            });
        });
    }

    initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add('revealed');
                    }, index * 100);
                }
            });
        }, observerOptions);

        document.querySelectorAll('.scroll-reveal').forEach(el => {
            observer.observe(el);
        });
    }

    // 3. Advanced Search with Autocomplete
    initAdvancedSearch() {
        const searchInputs = document.querySelectorAll('.search-input');
        searchInputs.forEach(input => {
            this.setupAdvancedSearch(input);
        });
    }

    setupAdvancedSearch(input) {
        const searchType = input.getAttribute('data-search-type') || 'stocks';
        const container = input.parentElement;
        
        if (!container.classList.contains('search-container')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'search-container';
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);
            container = wrapper;
        }

        // Create suggestions dropdown
        let suggestionsContainer = container.querySelector('.search-suggestions');
        if (!suggestionsContainer) {
            suggestionsContainer = document.createElement('div');
            suggestionsContainer.className = 'search-suggestions';
            container.appendChild(suggestionsContainer);
        }

        let searchTimeout;
        let currentSelection = -1;

        input.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();

            if (query.length < 2) {
                this.hideSuggestions(suggestionsContainer);
                return;
            }

            searchTimeout = setTimeout(() => {
                this.performSearch(query, searchType, suggestionsContainer, input);
            }, 300);
        });

        input.addEventListener('keydown', (e) => {
            const suggestions = suggestionsContainer.querySelectorAll('.suggestion-item');
            
            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    currentSelection = Math.min(currentSelection + 1, suggestions.length - 1);
                    this.updateSelection(suggestions, currentSelection);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    currentSelection = Math.max(currentSelection - 1, -1);
                    this.updateSelection(suggestions, currentSelection);
                    break;
                case 'Enter':
                    e.preventDefault();
                    if (currentSelection >= 0 && suggestions[currentSelection]) {
                        suggestions[currentSelection].click();
                    }
                    break;
                case 'Escape':
                    this.hideSuggestions(suggestionsContainer);
                    input.blur();
                    break;
            }
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!container.contains(e.target)) {
                this.hideSuggestions(suggestionsContainer);
            }
        });
    }

    performSearch(query, searchType, container, input) {
        // Simulate API call with mock data
        const mockResults = this.getMockSearchResults(query, searchType);
        this.displaySuggestions(mockResults, container, input);
    }

    getMockSearchResults(query, type) {
        const results = {
            stocks: [
                { symbol: 'AAPL', name: 'Apple Inc.', price: '$150.25', change: '+1.2%' },
                { symbol: 'GOOGL', name: 'Alphabet Inc.', price: '$2,750.80', change: '-0.5%' },
                { symbol: 'MSFT', name: 'Microsoft Corp.', price: '$310.50', change: '+0.8%' }
            ],
            news: [
                { title: 'Market Update: Tech Stocks Rally', source: 'Financial Times', time: '2h ago' },
                { title: 'Apple Reports Strong Q4 Earnings', source: 'Reuters', time: '4h ago' },
                { title: 'Fed Announces Rate Decision', source: 'Bloomberg', time: '6h ago' }
            ],
            sectors: [
                { name: 'Technology', performance: '+2.1%', stocks: '150 stocks' },
                { name: 'Healthcare', performance: '+0.8%', stocks: '89 stocks' },
                { name: 'Financial', performance: '-0.3%', stocks: '120 stocks' }
            ]
        };

        return results[type] || results.stocks;
    }

    displaySuggestions(results, container, input) {
        const searchType = input.getAttribute('data-search-type') || 'stocks';
        
        container.innerHTML = results.map((item, index) => {
            return this.createSuggestionItem(item, searchType, index);
        }).join('');

        this.showSuggestions(container);

        // Add click handlers
        container.querySelectorAll('.suggestion-item').forEach((item, index) => {
            item.addEventListener('click', () => {
                this.selectSuggestion(item, input, results[index]);
            });
        });
    }

    createSuggestionItem(item, type, index) {
        switch (type) {
            case 'stocks':
                return `
                    <div class="suggestion-item" data-index="${index}">
                        <div class="suggestion-icon"></div>
                        <div class="suggestion-content">
                            <div class="suggestion-title">${item.symbol} - ${item.name}</div>
                            <div class="suggestion-meta">${item.price} <span class="${item.change.startsWith('+') ? 'positive' : 'negative'}">${item.change}</span></div>
                        </div>
                    </div>
                `;
            case 'news':
                return `
                    <div class="suggestion-item" data-index="${index}">
                        <div class="suggestion-icon">📰</div>
                        <div class="suggestion-content">
                            <div class="suggestion-title">${item.title}</div>
                            <div class="suggestion-meta">${item.source} • ${item.time}</div>
                        </div>
                    </div>
                `;
            case 'sectors':
                return `
                    <div class="suggestion-item" data-index="${index}">
                        <div class="suggestion-icon">🏢</div>
                        <div class="suggestion-content">
                            <div class="suggestion-title">${item.name}</div>
                            <div class="suggestion-meta">${item.performance} • ${item.stocks}</div>
                        </div>
                    </div>
                `;
            default:
                return `
                    <div class="suggestion-item" data-index="${index}">
                        <div class="suggestion-content">
                            <div class="suggestion-title">${item.name || item.title}</div>
                        </div>
                    </div>
                `;
        }
    }

    selectSuggestion(element, input, data) {
        input.value = data.symbol || data.name || data.title;
        this.hideSuggestions(element.closest('.search-suggestions'));
        
        // Dispatch custom event
        input.dispatchEvent(new CustomEvent('suggestionSelected', {
            detail: { data, element }
        }));
    }

    showSuggestions(container) {
        container.classList.add('suggestions-visible');
    }

    hideSuggestions(container) {
        container.classList.remove('suggestions-visible');
    }

    updateSelection(suggestions, currentSelection) {
        suggestions.forEach((item, index) => {
            item.classList.toggle('selected', index === currentSelection);
        });
    }

    // 6. Enhanced Progress Indicators
    initProgressIndicators() {
        window.updateProgress = (element, percentage) => {
            const circle = element.querySelector('.progress-ring-progress');
            const text = element.querySelector('.progress-ring-text');
            
            if (circle && text) {
                const circumference = 2 * Math.PI * 40;
                const strokeDasharray = `${percentage / 100 * circumference} ${circumference}`;
                circle.style.strokeDasharray = strokeDasharray;
                text.textContent = `${Math.round(percentage)}%`;
            }
        };

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
        const increment = targetPercentage / 60;
        
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

    // 7. Advanced Charts Integration
    initAdvancedCharts() {
        window.createAdvancedChart = (canvas, config) => {
            const ctx = canvas.getContext('2d');
            
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

            const mergedConfig = this.deepMerge(defaultConfig, config);
            return new Chart(ctx, mergedConfig);
        };
    }

    // 8. Advanced Modal System
    initAdvancedModals() {
        window.showModal = (content, options = {}) => {
            const modal = document.createElement('div');
            modal.className = 'modal-enhanced';
            modal.innerHTML = `
                <div class="modal-backdrop"></div>
                <div class="modal-content-enhanced" style="max-width: ${options.maxWidth || '600px'}">
                    ${options.showClose !== false ? '<button class="modal-close" aria-label="Close modal">&times;</button>' : ''}
                    <div class="modal-body">
                        ${content}
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
            document.body.style.overflow = 'hidden';

            // Show with animation
            requestAnimationFrame(() => {
                modal.classList.add('modal-show');
            });

            // Event handlers
            const closeModal = () => {
                modal.classList.remove('modal-show');
                setTimeout(() => {
                    modal.remove();
                    document.body.style.overflow = '';
                }, 300);
            };

            modal.querySelector('.modal-close')?.addEventListener('click', closeModal);
            modal.querySelector('.modal-backdrop')?.addEventListener('click', closeModal);

            // Keyboard support
            const handleKeydown = (e) => {
                if (e.key === 'Escape') {
                    closeModal();
                    document.removeEventListener('keydown', handleKeydown);
                }
            };
            document.addEventListener('keydown', handleKeydown);

            return modal;
        };
    }

    // 9. Enhanced Form Controls
    initEnhancedFormControls() {
        this.initFloatingLabels();
        this.initFormValidation();
    }

    initFloatingLabels() {
        const inputs = document.querySelectorAll('.form-control-enhanced');
        
        inputs.forEach(input => {
            const wrapper = input.closest('.form-group-enhanced') || input.parentElement;
            
            if (!wrapper.querySelector('.floating-label')) {
                const label = document.createElement('label');
                label.className = 'floating-label';
                label.textContent = input.placeholder || input.getAttribute('data-label') || 'Enter value';
                wrapper.appendChild(label);
            }

            // Set placeholder to space for CSS to work
            if (!input.placeholder || input.placeholder === label.textContent) {
                input.placeholder = ' ';
            }

            // Add focus/blur handlers
            input.addEventListener('focus', () => {
                wrapper.classList.add('focused');
            });

            input.addEventListener('blur', () => {
                wrapper.classList.remove('focused');
                wrapper.classList.toggle('filled', input.value.length > 0);
            });

            // Initial state
            wrapper.classList.toggle('filled', input.value.length > 0);
        });
    }

    initFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const isValid = this.validateForm(form);
                if (!isValid) {
                    e.preventDefault();
                }
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            const isFieldValid = this.validateField(input);
            if (!isFieldValid) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(input) {
        const value = input.value.trim();
        const wrapper = input.closest('.form-group-enhanced') || input.parentElement;
        
        // Remove previous validation states
        wrapper.classList.remove('invalid', 'valid');
        
        let isValid = true;
        let message = '';

        if (input.hasAttribute('required') && !value) {
            isValid = false;
            message = 'This field is required';
        } else if (input.type === 'email' && value && !this.isValidEmail(value)) {
            isValid = false;
            message = 'Please enter a valid email address';
        }

        // Apply validation state
        wrapper.classList.add(isValid ? 'valid' : 'invalid');
        
        // Show/hide error message
        let errorElement = wrapper.querySelector('.error-message');
        if (!isValid && message) {
            if (!errorElement) {
                errorElement = document.createElement('div');
                errorElement.className = 'error-message';
                wrapper.appendChild(errorElement);
            }
            errorElement.textContent = message;
        } else if (errorElement) {
            errorElement.remove();
        }

        return isValid;
    }

    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // 10. Smart Navigation
    initSmartNavigation() {
        this.initScrollAwareHeader();
        this.initSmoothScrolling();
        this.initActiveSectionHighlighting();
    }

    initScrollAwareHeader() {
        const header = document.querySelector('.nav-enhanced, header, .navbar');
        if (!header) return;

        let lastScrollTop = 0;
        let scrollTimeout;

        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                // Add scrolled class
                header.classList.toggle('scrolled', scrollTop > 100);
                
                // Hide/show header based on scroll direction
                if (scrollTop > 200) {
                    if (scrollTop > lastScrollTop) {
                        header.classList.add('header-hidden');
                    } else {
                        header.classList.remove('header-hidden');
                    }
                }
                
                lastScrollTop = scrollTop;
            }, 10);
        });
    }

    initSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
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
    }

    initActiveSectionHighlighting() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('nav a[href^="#"]');

        if (sections.length === 0 || navLinks.length === 0) return;

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

    // 11. Lazy Loading System
    initLazyLoading() {
        this.initImageLazyLoading();
        this.initContentLazyLoading();
    }

    initImageLazyLoading() {
        const lazyImages = document.querySelectorAll('img[data-lazy]');
        
        if (lazyImages.length === 0) return;

        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.lazy;
                    img.classList.add('lazy-loaded');
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => imageObserver.observe(img));
    }

    initContentLazyLoading() {
        const lazyContent = document.querySelectorAll('[data-lazy-content]');
        
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
        element.classList.add('loading');
        
        fetch(url)
            .then(response => response.text())
            .then(html => {
                element.innerHTML = html;
                element.classList.remove('loading');
                element.classList.add('lazy-loaded');
            })
            .catch(error => {
                element.innerHTML = '<p>Failed to load content</p>';
                element.classList.remove('loading');
                element.classList.add('lazy-error');
            });
    }

    // 12. Virtualized Lists
    initVirtualizedLists() {
        const virtualLists = document.querySelectorAll('[data-virtual-list]');
        virtualLists.forEach(list => this.createVirtualList(list));
    }

    createVirtualList(container) {
        const itemHeight = parseInt(container.dataset.itemHeight) || 50;
        const containerHeight = parseInt(container.dataset.height) || 400;
        const buffer = 5;
        let scrollTop = 0;
        let data = [];

        // Try to parse data from attribute or fetch from URL
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

    // 15. Parallax Effects
    initParallaxEffects() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        
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
        });
    }

    // 15. Enhanced Tables
    initEnhancedTables() {
        const tables = document.querySelectorAll('.table-enhanced');
        
        tables.forEach(table => {
            this.setupTableSorting(table);
            this.setupTableSelection(table);
            this.setupStickyHeaders(table);
        });
    }

    setupTableSorting(table) {
        const headers = table.querySelectorAll('th[data-sortable]');
        
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.classList.add('sortable-header');
            
            // Add sort indicator
            if (!header.querySelector('.sort-indicator')) {
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
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const columnIndex = Array.from(header.parentNode.children).indexOf(header);
        const isAscending = !header.classList.contains('sorted-asc');

        // Clear all sort indicators
        table.querySelectorAll('th').forEach(h => {
            h.classList.remove('sorted-asc', 'sorted-desc');
            const indicator = h.querySelector('.sort-indicator');
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
        header.classList.add(isAscending ? 'sorted-asc' : 'sorted-desc');
        const indicator = header.querySelector('.sort-indicator');
        if (indicator) {
            indicator.innerHTML = isAscending ? '↑' : '↓';
        }

        // Re-append sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }

    setupTableSelection(table) {
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            row.addEventListener('click', () => {
                // Allow multiple selection with Ctrl/Cmd
                if (!event.ctrlKey && !event.metaKey) {
                    rows.forEach(r => r.classList.remove('selected'));
                }
                row.classList.toggle('selected');
                
                // Dispatch selection event
                table.dispatchEvent(new CustomEvent('rowSelection', {
                    detail: {
                        selectedRows: Array.from(table.querySelectorAll('tbody tr.selected'))
                    }
                }));
            });
        });
    }

    setupStickyHeaders(table) {
        const header = table.querySelector('thead');
        if (!header) return;

        const observer = new IntersectionObserver(
            ([entry]) => {
                table.classList.toggle('sticky-header', !entry.isIntersecting);
            },
            { threshold: 1 }
        );

        observer.observe(header);
    }

    // 16. Dark Mode Support
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
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', theme === 'dark' ? '#1a1a1a' : '#ffffff');
        }
    }

    // Utility Methods
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

// Initialize Enhanced UI
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedUI = new EnhancedUI();
});

// Add required CSS styles
const style = document.createElement('style');
style.textContent = `
    /* 1. Advanced Loading States */
    .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 4px;
    }

    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    .skeleton-table {
        width: 100%;
    }

    .skeleton-row {
        display: flex;
        gap: 15px;
        margin-bottom: 10px;
    }

    .skeleton-cell {
        flex: 1;
        height: 20px;
    }

    .skeleton-card {
        display: flex;
        gap: 15px;
        padding: 20px;
    }

    .skeleton-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
    }

    .skeleton-content {
        flex: 1;
    }

    .skeleton-title {
        height: 24px;
        margin-bottom: 10px;
        width: 70%;
    }

    .skeleton-text {
        height: 16px;
        margin-bottom: 8px;
        width: 100%;
    }

    .skeleton-text.short {
        width: 60%;
    }

    .skeleton-chart {
        padding: 20px;
    }

    .skeleton-chart-title {
        height: 24px;
        width: 40%;
        margin-bottom: 20px;
    }

    .skeleton-chart-content {
        display: flex;
        align-items: end;
        gap: 8px;
        height: 200px;
    }

    .skeleton-bar {
        flex: 1;
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 4px 4px 0 0;
    }

    /* 2. Micro-interactions & Animations */
    .ripple {
        position: relative;
        overflow: hidden;
    }

    .ripple-effect {
        background: rgba(255, 255, 255, 0.3);
    }

    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .btn-enhanced {
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        transform: translateY(0);
    }

    .btn-enhanced:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }

    .btn-enhanced.btn-hover::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer-btn 0.6s;
    }

    @keyframes shimmer-btn {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    .card-interactive {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        transform-style: preserve-3d;
    }

    .card-interactive.card-hover {
        transform: translateY(-5px) rotateX(5deg);
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }

    .card-interactive.card-hover::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border-radius: inherit;
        pointer-events: none;
    }

    .scroll-reveal {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .scroll-reveal.revealed {
        opacity: 1;
        transform: translateY(0);
    }

    /* 3. Advanced Search */
    .search-container {
        position: relative;
        width: 100%;
    }

    .search-input {
        width: 100%;
        padding: 12px 16px;
        border: 2px solid #e1e5e9;
        border-radius: 8px;
        font-size: 16px;
        transition: all 0.3s ease;
    }

    .search-input:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        outline: none;
    }

    .search-suggestions {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        max-height: 300px;
        overflow-y: auto;
        z-index: 1000;
        opacity: 0;
        transform: translateY(-10px);
        visibility: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .search-suggestions.suggestions-visible {
        opacity: 1;
        transform: translateY(0);
        visibility: visible;
    }

    .suggestion-item {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        cursor: pointer;
        transition: background-color 0.2s ease;
        border-bottom: 1px solid #f5f5f5;
    }

    .suggestion-item:hover,
    .suggestion-item.selected {
        background-color: #f8f9fa;
    }

    .suggestion-item:last-child {
        border-bottom: none;
    }

    .suggestion-icon {
        margin-right: 12px;
        font-size: 18px;
    }

    .suggestion-content {
        flex: 1;
    }

    .suggestion-title {
        font-weight: 500;
        color: #2c3e50;
        margin-bottom: 2px;
    }

    .suggestion-meta {
        font-size: 12px;
        color: #6c757d;
    }

    .suggestion-meta .positive {
        color: #27ae60;
    }

    .suggestion-meta .negative {
        color: #e74c3c;
    }

    /* 6. Enhanced Progress Indicators */
    .progress-ring {
        position: relative;
        display: inline-block;
    }

    .progress-ring svg {
        width: 100px;
        height: 100px;
        transform: rotate(-90deg);
    }

    .progress-ring-progress {
        fill: none;
        stroke: #3498db;
        stroke-width: 4;
        stroke-linecap: round;
        stroke-dasharray: 251.2;
        stroke-dashoffset: 251.2;
        transition: stroke-dashoffset 0.5s ease;
    }

    .progress-ring-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-weight: bold;
        font-size: 16px;
        color: #2c3e50;
    }

    /* 8. Advanced Modal System */
    .modal-enhanced {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .modal-enhanced.modal-show {
        opacity: 1;
        visibility: visible;
    }

    .modal-backdrop {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(5px);
    }

    .modal-content-enhanced {
        position: relative;
        background: white;
        border-radius: 12px;
        max-height: 90vh;
        overflow-y: auto;
        transform: scale(0.9);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 25px 50px rgba(0,0,0,0.2);
    }

    .modal-enhanced.modal-show .modal-content-enhanced {
        transform: scale(1);
    }

    .modal-close {
        position: absolute;
        top: 15px;
        right: 15px;
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #6c757d;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: all 0.3s ease;
    }

    .modal-close:hover {
        background: #f8f9fa;
        color: #2c3e50;
    }

    .modal-body {
        padding: 30px;
    }

    /* 9. Enhanced Form Controls */
    .form-group-enhanced {
        position: relative;
        margin-bottom: 20px;
    }

    .form-control-enhanced {
        width: 100%;
        padding: 16px 12px 8px 12px;
        border: 2px solid #e1e5e9;
        border-radius: 8px;
        font-size: 16px;
        background: white;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .form-control-enhanced:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        outline: none;
    }

    .floating-label {
        position: absolute;
        left: 12px;
        top: 16px;
        font-size: 16px;
        color: #6c757d;
        pointer-events: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: white;
        padding: 0 4px;
    }

    .form-group-enhanced.focused .floating-label,
    .form-group-enhanced.filled .floating-label {
        top: -8px;
        font-size: 12px;
        color: #3498db;
    }

    .form-group-enhanced.invalid .form-control-enhanced {
        border-color: #e74c3c;
    }

    .form-group-enhanced.invalid .floating-label {
        color: #e74c3c;
    }

    .form-group-enhanced.valid .form-control-enhanced {
        border-color: #27ae60;
    }

    .error-message {
        color: #e74c3c;
        font-size: 12px;
        margin-top: 4px;
    }

    /* 10. Smart Navigation */
    .nav-enhanced {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        transform: translateY(0);
    }

    .nav-enhanced.scrolled {
        backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 2px 20px rgba(0,0,0,0.1);
    }

    .nav-enhanced.header-hidden {
        transform: translateY(-100%);
    }

    /* 11. Lazy Loading */
    img[data-lazy] {
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    img.lazy-loaded {
        opacity: 1;
    }

    [data-lazy-content].loading::before {
        content: 'Loading...';
        display: block;
        text-align: center;
        padding: 20px;
        color: #6c757d;
    }

    /* 12. Virtualized Lists */
    .virtual-list-viewport {
        border: 1px solid #e1e5e9;
        border-radius: 8px;
    }

    .virtual-list-item {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        border-bottom: 1px solid #f5f5f5;
        transition: background-color 0.2s ease;
    }

    .virtual-list-item:hover {
        background-color: #f8f9fa;
    }

    .virtual-item-content {
        flex: 1;
    }

    .virtual-item-title {
        font-weight: 500;
        color: #2c3e50;
        margin-bottom: 2px;
    }

    .virtual-item-subtitle {
        font-size: 12px;
        color: #6c757d;
    }

    /* 15. Enhanced Tables */
    .table-enhanced {
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .table-enhanced th {
        background: #f8f9fa;
        padding: 12px 16px;
        text-align: left;
        font-weight: 600;
        color: #2c3e50;
        border-bottom: 2px solid #e1e5e9;
    }

    .table-enhanced td {
        padding: 12px 16px;
        border-bottom: 1px solid #f5f5f5;
    }

    .table-enhanced tbody tr {
        transition: background-color 0.2s ease;
    }

    .table-enhanced tbody tr:hover {
        background-color: #f8f9fa;
    }

    .table-enhanced tbody tr.selected {
        background-color: rgba(52, 152, 219, 0.1);
    }

    .sortable-header {
        position: relative;
        user-select: none;
    }

    .sort-indicator {
        margin-left: 8px;
        color: #6c757d;
        font-size: 12px;
    }

    .sortable-header.sorted-asc .sort-indicator,
    .sortable-header.sorted-desc .sort-indicator {
        color: #3498db;
    }

    .table-enhanced.sticky-header th {
        position: sticky;
        top: 0;
        z-index: 10;
    }

    /* 16. Dark Mode Support */
    [data-theme="dark"] {
        --bg-color: #1a1a1a;
        --text-color: #e1e1e1;
        --border-color: #333;
        --card-bg: #2d2d2d;
    }

    [data-theme="dark"] body {
        background-color: var(--bg-color);
        color: var(--text-color);
    }

    [data-theme="dark"] .card,
    [data-theme="dark"] .modal-content-enhanced,
    [data-theme="dark"] .table-enhanced {
        background-color: var(--card-bg);
        color: var(--text-color);
    }

    [data-theme="dark"] .form-control-enhanced,
    [data-theme="dark"] .search-input {
        background-color: var(--card-bg);
        border-color: var(--border-color);
        color: var(--text-color);
    }

    [data-theme="dark"] .skeleton {
        background: linear-gradient(90deg, #333 25%, #444 50%, #333 75%);
        background-size: 200% 100%;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .modal-content-enhanced {
            margin: 20px;
            max-width: none;
        }
        
        .search-suggestions {
            max-height: 200px;
        }
        
        .virtual-list-viewport {
            height: 300px !important;
        }
    }

    /* Print Styles */
    @media print {
        .nav-enhanced,
        .modal-enhanced,
        .search-suggestions,
        .btn-enhanced {
            display: none !important;
        }
        
        .table-enhanced {
            box-shadow: none;
            border: 1px solid #ccc;
        }
    }
`;
document.head.appendChild(style);

(function(){
  if (typeof window === 'undefined') return;

  const THEME = window.ssTheme || window.stock_scanner_theme || {};
  const settings = (THEME && THEME.settings) || {};
  const enableSkeletons = !!settings.feature_skeletons;
  const enableCmdPalette = !!settings.feature_command_palette;

  // Offline indicator
  function updateOnlineStatus(){
    let bar = document.getElementById('offline-indicator');
    if (!bar){
      bar = document.createElement('div');
      bar.id = 'offline-indicator';
      bar.setAttribute('role','status');
      bar.style.cssText = 'position:fixed;bottom:10px;left:50%;transform:translateX(-50%);padding:8px 12px;border-radius:6px;background:#b91c1c;color:#fff;font-weight:600;box-shadow:0 4px 12px rgba(0,0,0,.2);z-index:9999;display:none';
      bar.textContent = 'You are offline';
      document.body.appendChild(bar);
    }
    bar.style.display = navigator.onLine ? 'none' : 'block';
  }
  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  if (document.readyState === 'complete') { updateOnlineStatus(); } else { window.addEventListener('load', updateOnlineStatus); }

  // Fetch with retry/backoff
  window.fetchWithRetry = async function(url, opts = {}, retries = 2){
    const baseDelay = 500;
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const res = await fetch(url, opts);
        if (!res.ok) throw new Error('HTTP '+res.status);
        return res;
      } catch (e) {
        if (attempt === retries) throw e;
        const delay = baseDelay * Math.pow(2, attempt);
        await new Promise(r=>setTimeout(r, delay));
      }
    }
  };

  // Skeleton helpers
  if (enableSkeletons) {
    const style = document.createElement('style');
    style.innerHTML = `
      .skeleton{position:relative;overflow:hidden;background:#e5e7eb;border-radius:8px}
      .skeleton::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.6),rgba(255,255,255,0));transform:translateX(-100%);animation:sk 1.2s infinite}
      @keyframes sk{100%{transform:translateX(100%)}}
    `;
    document.head.appendChild(style);

    window.showSkeletons = function(selector, count = 3, height = 80){
      const el = document.querySelector(selector);
      if (!el) return;
      el.innerHTML = Array.from({length:count}).map(()=>`<div class="skeleton" style="height:${height}px;margin:10px 0"></div>`).join('');
    };
  }

  // Command Palette
  if (enableCmdPalette) {
    const palette = document.createElement('div');
    palette.id = 'command-palette';
    palette.setAttribute('role', 'dialog');
    palette.setAttribute('aria-modal', 'true');
    palette.setAttribute('aria-label', 'Command Palette');
    palette.style.cssText = 'position:fixed;inset:0;display:none;align-items:flex-start;justify-content:center;background:rgba(0,0,0,.4);z-index:10000;padding-top:10vh';
    palette.innerHTML = `
      <div style="width:min(700px,92vw);background:#fff;border-radius:12px;box-shadow:0 20px 40px rgba(0,0,0,.25);">
        <div style="padding:12px 14px;border-bottom:1px solid #e5e7eb;display:flex;gap:8px;align-items:center">
          <span>⌘K</span>
          <input id="cmdk-input" aria-label="Search commands" placeholder="Type a command or page..." style="flex:1;border:none;outline:none;font-size:16px" />
          <button id="cmdk-close" aria-label="Close" style="background:none;border:none;font-size:20px">×</button>
        </div>
        <div id="cmdk-list" role="listbox" style="max-height:50vh;overflow:auto;padding:8px 0"></div>
      </div>`;
    document.body.appendChild(palette);

    const input = palette.querySelector('#cmdk-input');
    const list  = palette.querySelector('#cmdk-list');
    const close = palette.querySelector('#cmdk-close');

    const commands = [
      {label:'Dashboard', href:'/dashboard/'},
      {label:'Stock Lookup', href:'/stock-lookup/'},
      {label:'Stock News', href:'/stock-news/'},
      {label:'Stock Screener', href:'/stock-screener/'},
      {label:'Watchlist', href:'/watchlist/'},
      {label:'Market Overview', href:'/market-overview/'},
      {label:'Premium Plans', href:'/premium-plans/'},
    ];

    function renderCommands(q=''){
      const norm = q.trim().toLowerCase();
      const items = commands.filter(c=>!norm || c.label.toLowerCase().includes(norm));
      list.innerHTML = items.map((c,i)=>`<div role="option" tabindex="0" data-idx="${i}" style="padding:10px 14px;cursor:pointer" class="cmdk-item">${c.label}</div>`).join('');
      list.querySelectorAll('.cmdk-item').forEach((el, i)=>{
        el.addEventListener('click', ()=>{ window.location.href = items[i].href; hide(); });
        el.addEventListener('keydown', (e)=>{ if (e.key==='Enter') { window.location.href = items[i].href; } });
      });
    }

    function show(){ palette.style.display='flex'; renderCommands(); input.value=''; input.focus(); }
    function hide(){ palette.style.display='none'; }

    document.addEventListener('keydown', (e)=>{
      const metaK = (e.ctrlKey || e.metaKey) && e.key.toLowerCase()==='k';
      if (metaK){ e.preventDefault(); show(); }
      if (e.key==='Escape' && palette.style.display==='flex'){ hide(); }
    });
    input.addEventListener('input', ()=>renderCommands(input.value));
    close.addEventListener('click', hide);
  }
})();