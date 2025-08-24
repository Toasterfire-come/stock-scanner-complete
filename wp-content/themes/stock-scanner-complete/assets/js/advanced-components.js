/**
 * Stock Scanner Pro - Advanced Components v3.0.0
 * ENTERPRISE-GRADE BROWSER-SIDE FEATURES
 * Advanced pagination, data tables, infinite scroll, search, and premium UI components
 */

(function() {
    'use strict';

    // ===== ADVANCED DATA TABLE COMPONENT =====
    class AdvancedDataTable {
        constructor(container, options = {}) {
            this.container = typeof container === 'string' ? document.querySelector(container) : container;
            this.options = {
                sortable: true,
                filterable: true,
                exportable: true,
                selectable: false,
                pageSize: 10,
                ...options
            };
            
            this.data = [];
            this.filteredData = [];
            this.currentSort = { column: null, direction: 'asc' };
            this.selectedRows = new Set();
            this.filters = new Map();
            
            this.init();
        }

        init() {
            if (!this.container) return;
            
            this.createTableStructure();
            this.setupEventListeners();
            this.render();
        }

        createTableStructure() {
            this.container.innerHTML = `
                <div class="advanced-table-wrapper">
                    <div class="table-controls">
                        <div class="table-search">
                            <input type="search" class="table-search-input" placeholder="Search table...">
                        </div>
                        <div class="table-actions">
                            ${this.options.exportable ? `
                                <div class="export-dropdown">
                                    <button class="btn btn-outline btn-sm export-toggle">Export ⋮</button>
                                    <div class="export-menu">
                                        <button class="export-csv">Export CSV</button>
                                        <button class="export-json">Export JSON</button>
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    <div class="table-container">
                        <table class="advanced-table">
                            <thead class="table-header"></thead>
                            <tbody class="table-body"></tbody>
                        </table>
                    </div>
                    <div class="table-footer">
                        <div class="table-info"></div>
                        <div class="table-pagination"></div>
                    </div>
                </div>
            `;
        }

        setupEventListeners() {
            // Search functionality
            const searchInput = this.container.querySelector('.table-search-input');
            if (searchInput) {
                searchInput.addEventListener('input', this.debounce((e) => {
                    this.search(e.target.value);
                }, 300));
            }

            // Export functionality
            const exportToggle = this.container.querySelector('.export-toggle');
            const exportMenu = this.container.querySelector('.export-menu');
            
            if (exportToggle && exportMenu) {
                exportToggle.addEventListener('click', (e) => {
                    e.stopPropagation();
                    exportMenu.classList.toggle('show');
                });

                document.addEventListener('click', () => {
                    exportMenu.classList.remove('show');
                });

                this.container.querySelector('.export-csv')?.addEventListener('click', () => {
                    this.exportCSV();
                });

                this.container.querySelector('.export-json')?.addEventListener('click', () => {
                    this.exportJSON();
                });
            }

            // Table sorting
            if (this.options.sortable) {
                this.container.addEventListener('click', (e) => {
                    const th = e.target.closest('th[data-sortable]');
                    if (th) {
                        this.sort(th.dataset.column);
                    }
                });
            }
        }

        setData(data) {
            this.data = [...data];
            this.filteredData = [...data];
            this.render();
        }

        search(query) {
            if (!query.trim()) {
                this.filteredData = [...this.data];
            } else {
                const searchTerm = query.toLowerCase();
                this.filteredData = this.data.filter(row => {
                    return Object.values(row).some(value => 
                        String(value).toLowerCase().includes(searchTerm)
                    );
                });
            }
            this.render();
        }

        sort(column) {
            if (this.currentSort.column === column) {
                this.currentSort.direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
            } else {
                this.currentSort.column = column;
                this.currentSort.direction = 'asc';
            }

            this.filteredData.sort((a, b) => {
                const aVal = a[column];
                const bVal = b[column];
                
                let comparison = 0;
                if (typeof aVal === 'number' && typeof bVal === 'number') {
                    comparison = aVal - bVal;
                } else {
                    comparison = String(aVal).localeCompare(String(bVal));
                }
                
                return this.currentSort.direction === 'asc' ? comparison : -comparison;
            });

            this.render();
        }

        render() {
            this.renderHeaders();
            this.renderBody();
            this.renderFooter();
        }

        renderHeaders() {
            const thead = this.container.querySelector('.table-header');
            if (!thead || !this.data.length) return;

            const headers = Object.keys(this.data[0]);
            thead.innerHTML = `
                <tr>
                    ${this.options.selectable ? '<th class="select-col"><input type="checkbox" class="select-all"></th>' : ''}
                    ${headers.map(header => `
                        <th data-column="${header}" ${this.options.sortable ? 'data-sortable' : ''} 
                            class="${this.currentSort.column === header ? 'sorted ' + this.currentSort.direction : ''}">
                            ${this.formatHeader(header)}
                            ${this.options.sortable ? '<span class="sort-indicator">⇅</span>' : ''}
                        </th>
                    `).join('')}
                </tr>
            `;
        }

        renderBody() {
            const tbody = this.container.querySelector('.table-body');
            if (!tbody) return;

            if (!this.filteredData.length) {
                tbody.innerHTML = '<tr><td colspan="100%" class="no-data">No data available</td></tr>';
                return;
            }

            const headers = Object.keys(this.filteredData[0]);
            tbody.innerHTML = this.filteredData.map((row, index) => `
                <tr data-index="${index}" class="${this.selectedRows.has(index) ? 'selected' : ''}">
                    ${this.options.selectable ? `<td><input type="checkbox" class="row-select" ${this.selectedRows.has(index) ? 'checked' : ''}></td>` : ''}
                    ${headers.map(header => `
                        <td class="cell-${header}">${this.formatCell(row[header], header)}</td>
                    `).join('')}
                </tr>
            `).join('');

            // Add selection event listeners
            if (this.options.selectable) {
                this.setupSelectionListeners();
            }
        }

        renderFooter() {
            const info = this.container.querySelector('.table-info');
            if (info) {
                const showing = this.filteredData.length;
                const total = this.data.length;
                info.textContent = `Showing ${showing} of ${total} entries`;
            }
        }

        formatHeader(header) {
            return header.charAt(0).toUpperCase() + header.slice(1).replace(/([A-Z])/g, ' $1');
        }

        formatCell(value, column) {
            if (column.includes('price') || column.includes('amount')) {
                return typeof value === 'number' ? `$${value.toFixed(2)}` : value;
            }
            if (column.includes('change') && typeof value === 'string' && value.includes('%')) {
                const isPositive = !value.includes('-');
                return `<span class="change ${isPositive ? 'positive' : 'negative'}">${value}</span>`;
            }
            return value;
        }

        setupSelectionListeners() {
            // Select all checkbox
            const selectAll = this.container.querySelector('.select-all');
            if (selectAll) {
                selectAll.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        this.filteredData.forEach((_, index) => this.selectedRows.add(index));
                    } else {
                        this.selectedRows.clear();
                    }
                    this.render();
                });
            }

            // Individual row checkboxes
            const rowSelects = this.container.querySelectorAll('.row-select');
            rowSelects.forEach((checkbox, index) => {
                checkbox.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        this.selectedRows.add(index);
                    } else {
                        this.selectedRows.delete(index);
                    }
                });
            });
        }

        exportCSV() {
            const headers = Object.keys(this.filteredData[0] || {});
            const csvContent = [
                headers.join(','),
                ...this.filteredData.map(row => 
                    headers.map(header => `"${String(row[header]).replace(/"/g, '""')}"`).join(',')
                )
            ].join('\n');

            this.downloadFile(csvContent, 'table-export.csv', 'text/csv');
        }

        exportJSON() {
            const jsonContent = JSON.stringify(this.filteredData, null, 2);
            this.downloadFile(jsonContent, 'table-export.json', 'application/json');
        }

        downloadFile(content, filename, mimeType) {
            const blob = new Blob([content], { type: mimeType });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }

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
        }
    }

    // ===== ADVANCED PAGINATION COMPONENT =====
    class AdvancedPagination {
        constructor(container, options = {}) {
            this.container = typeof container === 'string' ? document.querySelector(container) : container;
            this.options = {
                currentPage: 1,
                totalItems: 0,
                itemsPerPage: 10,
                maxVisiblePages: 5,
                showPageSizer: true,
                showPageJumper: true,
                pageSizeOptions: [5, 10, 25, 50, 100],
                ...options
            };
            
            this.currentPage = this.options.currentPage;
            this.itemsPerPage = this.options.itemsPerPage;
            this.totalPages = Math.ceil(this.options.totalItems / this.itemsPerPage);
            
            this.callbacks = {
                onPageChange: this.options.onPageChange || (() => {}),
                onPageSizeChange: this.options.onPageSizeChange || (() => {})
            };
            
            this.init();
        }

        init() {
            if (!this.container) return;
            this.render();
            this.setupEventListeners();
        }

        render() {
            const startItem = ((this.currentPage - 1) * this.itemsPerPage) + 1;
            const endItem = Math.min(this.currentPage * this.itemsPerPage, this.options.totalItems);
            
            this.container.innerHTML = `
                <div class="pagination-wrapper">
                    <div class="pagination-info">
                        Showing ${startItem}-${endItem} of ${this.options.totalItems} items
                    </div>
                    
                    <div class="pagination-controls">
                        ${this.renderPageSizer()}
                        ${this.renderPagination()}
                        ${this.renderPageJumper()}
                    </div>
                </div>
            `;
        }

        renderPageSizer() {
            if (!this.options.showPageSizer) return '';
            
            return `
                <div class="page-sizer">
                    <label for="page-size">Show:</label>
                    <select id="page-size" class="page-size-select">
                        ${this.options.pageSizeOptions.map(size => 
                            `<option value="${size}" ${size === this.itemsPerPage ? 'selected' : ''}>${size}</option>`
                        ).join('')}
                    </select>
                </div>
            `;
        }

        renderPagination() {
            if (this.totalPages <= 1) return '';
            
            const pages = this.getVisiblePages();
            
            return `
                <div class="pagination-nav">
                    <button class="page-btn prev-btn" ${this.currentPage === 1 ? 'disabled' : ''}>
                        ← Previous
                    </button>
                    
                    ${pages.map(page => {
                        if (page === '...') {
                            return '<span class="page-ellipsis">...</span>';
                        }
                        return `
                            <button class="page-btn page-number ${page === this.currentPage ? 'active' : ''}" 
                                    data-page="${page}">
                                ${page}
                            </button>
                        `;
                    }).join('')}
                    
                    <button class="page-btn next-btn" ${this.currentPage === this.totalPages ? 'disabled' : ''}>
                        Next →
                    </button>
                </div>
            `;
        }

        renderPageJumper() {
            if (!this.options.showPageJumper || this.totalPages <= 1) return '';
            
            return `
                <div class="page-jumper">
                    <label for="page-jump">Go to:</label>
                    <input type="number" id="page-jump" class="page-jump-input" 
                           min="1" max="${this.totalPages}" placeholder="${this.currentPage}">
                    <button class="page-jump-btn">Go</button>
                </div>
            `;
        }

        getVisiblePages() {
            const delta = Math.floor(this.options.maxVisiblePages / 2);
            const range = [];
            const rangeWithDots = [];
            
            for (let i = Math.max(2, this.currentPage - delta); 
                 i <= Math.min(this.totalPages - 1, this.currentPage + delta); 
                 i++) {
                range.push(i);
            }
            
            if (this.currentPage - delta > 2) {
                rangeWithDots.push(1, '...');
            } else {
                rangeWithDots.push(1);
            }
            
            rangeWithDots.push(...range);
            
            if (this.currentPage + delta < this.totalPages - 1) {
                rangeWithDots.push('...', this.totalPages);
            } else {
                if (this.totalPages > 1) {
                    rangeWithDots.push(this.totalPages);
                }
            }
            
            return rangeWithDots;
        }

        setupEventListeners() {
            // Page navigation
            this.container.addEventListener('click', (e) => {
                if (e.target.classList.contains('prev-btn') && this.currentPage > 1) {
                    this.goToPage(this.currentPage - 1);
                } else if (e.target.classList.contains('next-btn') && this.currentPage < this.totalPages) {
                    this.goToPage(this.currentPage + 1);
                } else if (e.target.classList.contains('page-number')) {
                    const page = parseInt(e.target.dataset.page);
                    if (page !== this.currentPage) {
                        this.goToPage(page);
                    }
                } else if (e.target.classList.contains('page-jump-btn')) {
                    const input = this.container.querySelector('.page-jump-input');
                    const page = parseInt(input.value);
                    if (page >= 1 && page <= this.totalPages) {
                        this.goToPage(page);
                    }
                }
            });

            // Page size change
            const pageSizeSelect = this.container.querySelector('.page-size-select');
            if (pageSizeSelect) {
                pageSizeSelect.addEventListener('change', (e) => {
                    this.changePageSize(parseInt(e.target.value));
                });
            }

            // Page jumper enter key
            const pageJumpInput = this.container.querySelector('.page-jump-input');
            if (pageJumpInput) {
                pageJumpInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        const page = parseInt(e.target.value);
                        if (page >= 1 && page <= this.totalPages) {
                            this.goToPage(page);
                        }
                    }
                });
            }
        }

        goToPage(page) {
            if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
                this.currentPage = page;
                this.render();
                this.setupEventListeners();
                this.callbacks.onPageChange(page, this.itemsPerPage);
            }
        }

        changePageSize(newSize) {
            this.itemsPerPage = newSize;
            this.totalPages = Math.ceil(this.options.totalItems / this.itemsPerPage);
            this.currentPage = 1; // Reset to first page
            this.render();
            this.setupEventListeners();
            this.callbacks.onPageSizeChange(newSize, this.currentPage);
        }

        updateTotalItems(totalItems) {
            this.options.totalItems = totalItems;
            this.totalPages = Math.ceil(totalItems / this.itemsPerPage);
            
            // Adjust current page if necessary
            if (this.currentPage > this.totalPages) {
                this.currentPage = Math.max(1, this.totalPages);
            }
            
            this.render();
            this.setupEventListeners();
        }
    }

    // ===== INFINITE SCROLL COMPONENT =====
    class InfiniteScroll {
        constructor(container, options = {}) {
            this.container = typeof container === 'string' ? document.querySelector(container) : container;
            this.options = {
                threshold: 100,
                batchSize: 20,
                loadingTemplate: '<div class="loading-spinner">Loading...</div>',
                enableManualLoad: true,
                debounceDelay: 100,
                ...options
            };
            
            this.isLoading = false;
            this.hasMore = true;
            this.currentPage = 1;
            this.loadCallback = this.options.onLoad || (() => Promise.resolve([]));
            
            this.init();
        }

        init() {
            if (!this.container) return;
            
            this.setupIntersectionObserver();
            this.createManualLoadButton();
            this.loadInitialContent();
        }

        setupIntersectionObserver() {
            const options = {
                root: null,
                rootMargin: `${this.options.threshold}px`,
                threshold: 0.1
            };

            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !this.isLoading && this.hasMore) {
                        this.loadMore();
                    }
                });
            }, options);

            // Create sentinel element
            this.sentinel = document.createElement('div');
            this.sentinel.className = 'infinite-scroll-sentinel';
            this.sentinel.style.height = '1px';
            this.container.appendChild(this.sentinel);
            
            this.observer.observe(this.sentinel);
        }

        createManualLoadButton() {
            if (!this.options.enableManualLoad) return;
            
            this.loadButton = document.createElement('button');
            this.loadButton.className = 'btn btn-outline load-more-btn';
            this.loadButton.textContent = 'Load More';
            this.loadButton.style.display = 'none';
            
            this.loadButton.addEventListener('click', () => {
                this.loadMore();
            });
            
            this.container.appendChild(this.loadButton);
        }

        async loadInitialContent() {
            await this.loadMore();
        }

        async loadMore() {
            if (this.isLoading || !this.hasMore) return;
            
            this.isLoading = true;
            this.showLoading();
            
            try {
                const data = await this.loadCallback(this.currentPage, this.options.batchSize);
                
                if (data && data.length > 0) {
                    this.renderItems(data);
                    this.currentPage++;
                    
                    if (data.length < this.options.batchSize) {
                        this.hasMore = false;
                        this.showEndMessage();
                    }
                } else {
                    this.hasMore = false;
                    this.showEndMessage();
                }
            } catch (error) {
                console.error('Error loading more content:', error);
                this.showError();
            } finally {
                this.isLoading = false;
                this.hideLoading();
            }
        }

        renderItems(items) {
            const fragment = document.createDocumentFragment();
            
            items.forEach((item, index) => {
                const element = this.createItemElement(item);
                element.style.opacity = '0';
                element.style.transform = 'translateY(20px)';
                fragment.appendChild(element);
                
                // Staggered animation
                setTimeout(() => {
                    element.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                    element.style.opacity = '1';
                    element.style.transform = 'translateY(0)';
                }, index * 100);
            });
            
            // Insert before sentinel
            this.container.insertBefore(fragment, this.sentinel);
        }

        createItemElement(item) {
            const element = document.createElement('div');
            element.className = 'infinite-scroll-item';
            
            if (this.options.itemTemplate) {
                element.innerHTML = this.options.itemTemplate(item);
            } else {
                element.innerHTML = `
                    <div class="item-content">
                        <h3>${item.title || item.name || 'Item'}</h3>
                        <p>${item.description || item.content || ''}</p>
                    </div>
                `;
            }
            
            return element;
        }

        showLoading() {
            if (!this.loadingElement) {
                this.loadingElement = document.createElement('div');
                this.loadingElement.className = 'infinite-scroll-loading';
                this.loadingElement.innerHTML = this.options.loadingTemplate;
            }
            
            this.container.insertBefore(this.loadingElement, this.sentinel);
            
            if (this.loadButton) {
                this.loadButton.style.display = 'none';
            }
        }

        hideLoading() {
            if (this.loadingElement && this.loadingElement.parentNode) {
                this.loadingElement.parentNode.removeChild(this.loadingElement);
            }
        }

        showEndMessage() {
            if (this.sentinel) {
                this.observer.unobserve(this.sentinel);
                this.sentinel.style.display = 'none';
            }
            
            if (this.loadButton) {
                this.loadButton.style.display = 'none';
            }
            
            const endMessage = document.createElement('div');
            endMessage.className = 'infinite-scroll-end';
            endMessage.innerHTML = '<p>No more items to load</p>';
            this.container.appendChild(endMessage);
        }

        showError() {
            const errorElement = document.createElement('div');
            errorElement.className = 'infinite-scroll-error';
            errorElement.innerHTML = `
                <p>Error loading content. <button class="retry-btn">Retry</button></p>
            `;
            
            errorElement.querySelector('.retry-btn').addEventListener('click', () => {
                errorElement.remove();
                this.loadMore();
            });
            
            this.container.insertBefore(errorElement, this.sentinel);
            
            if (this.loadButton) {
                this.loadButton.style.display = 'block';
            }
        }

        reset() {
            // Clear all items except controls
            const items = this.container.querySelectorAll('.infinite-scroll-item');
            items.forEach(item => item.remove());
            
            // Reset state
            this.currentPage = 1;
            this.hasMore = true;
            this.isLoading = false;
            
            // Show sentinel again
            if (this.sentinel) {
                this.sentinel.style.display = 'block';
                this.observer.observe(this.sentinel);
            }
            
            // Load initial content
            this.loadInitialContent();
        }

        destroy() {
            if (this.observer) {
                this.observer.disconnect();
            }
            
            if (this.loadButton) {
                this.loadButton.remove();
            }
            
            if (this.sentinel) {
                this.sentinel.remove();
            }
        }
    }

    // ===== ADVANCED SEARCH COMPONENT =====
    class AdvancedSearch {
        constructor(input, options = {}) {
            this.input = typeof input === 'string' ? document.querySelector(input) : input;
            this.options = {
                minLength: 2,
                debounceDelay: 300,
                maxResults: 10,
                cacheResults: true,
                showSuggestions: true,
                highlightMatches: true,
                searchEndpoint: null,
                ...options
            };
            
            this.cache = new Map();
            this.currentRequest = null;
            this.suggestions = [];
            this.selectedIndex = -1;
            
            this.init();
        }

        init() {
            if (!this.input) return;
            
            this.createSuggestionsContainer();
            this.setupEventListeners();
        }

        createSuggestionsContainer() {
            this.suggestionsContainer = document.createElement('div');
            this.suggestionsContainer.className = 'search-suggestions-dropdown';
            this.suggestionsContainer.style.display = 'none';
            
            // Position relative to input
            this.input.parentNode.style.position = 'relative';
            this.input.parentNode.appendChild(this.suggestionsContainer);
        }

        setupEventListeners() {
            // Input events
            this.input.addEventListener('input', this.debounce((e) => {
                this.handleInput(e.target.value);
            }, this.options.debounceDelay));

            // Keyboard navigation
            this.input.addEventListener('keydown', (e) => {
                this.handleKeydown(e);
            });

            // Focus events
            this.input.addEventListener('focus', () => {
                if (this.suggestions.length > 0) {
                    this.showSuggestions();
                }
            });

            this.input.addEventListener('blur', () => {
                // Delay hiding to allow clicking on suggestions
                setTimeout(() => {
                    this.hideSuggestions();
                }, 150);
            });

            // Click outside to close
            document.addEventListener('click', (e) => {
                if (!this.input.contains(e.target) && !this.suggestionsContainer.contains(e.target)) {
                    this.hideSuggestions();
                }
            });
        }

        async handleInput(query) {
            if (query.length < this.options.minLength) {
                this.hideSuggestions();
                return;
            }

            // Cancel previous request
            if (this.currentRequest) {
                this.currentRequest.abort();
            }

            // Check cache
            if (this.options.cacheResults && this.cache.has(query)) {
                this.suggestions = this.cache.get(query);
                this.renderSuggestions(query);
                return;
            }

            // Show loading state
            this.showLoading();

            try {
                const results = await this.performSearch(query);
                this.suggestions = results.slice(0, this.options.maxResults);
                
                if (this.options.cacheResults) {
                    this.cache.set(query, this.suggestions);
                }
                
                this.renderSuggestions(query);
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.error('Search error:', error);
                    this.showError();
                }
            }
        }

        async performSearch(query) {
            if (this.options.onSearch) {
                return this.options.onSearch(query);
            }
            
            if (this.options.searchEndpoint) {
                const controller = new AbortController();
                this.currentRequest = controller;
                
                const response = await fetch(`${this.options.searchEndpoint}?q=${encodeURIComponent(query)}`, {
                    signal: controller.signal
                });
                
                if (!response.ok) {
                    throw new Error('Search request failed');
                }
                
                return response.json();
            }
            
            // Return empty results if no search implementation
            return [];
        }

        renderSuggestions(query) {
            if (this.suggestions.length === 0) {
                this.showNoResults();
                return;
            }

            const html = this.suggestions.map((suggestion, index) => `
                <div class="search-suggestion ${index === this.selectedIndex ? 'selected' : ''}" 
                     data-index="${index}" data-id="${suggestion.id}">
                    <div class="suggestion-content">
                        <div class="suggestion-title">
                            ${this.options.highlightMatches ? this.highlightMatch(suggestion.title, query) : suggestion.title}
                        </div>
                        ${suggestion.description ? `<div class="suggestion-description">${suggestion.description}</div>` : ''}
                    </div>
                    <div class="suggestion-type">${suggestion.type || ''}</div>
                </div>
            `).join('');

            this.suggestionsContainer.innerHTML = html;
            this.showSuggestions();
            this.setupSuggestionListeners();
        }

        highlightMatch(text, query) {
            const regex = new RegExp(`(${query})`, 'gi');
            return text.replace(regex, '<mark>$1</mark>');
        }

        setupSuggestionListeners() {
            const suggestionElements = this.suggestionsContainer.querySelectorAll('.search-suggestion');
            
            suggestionElements.forEach((element, index) => {
                element.addEventListener('click', () => {
                    this.selectSuggestion(index);
                });
                
                element.addEventListener('mouseenter', () => {
                    this.selectedIndex = index;
                    this.updateSelection();
                });
            });
        }

        handleKeydown(e) {
            if (!this.suggestionsContainer.style.display || this.suggestionsContainer.style.display === 'none') {
                return;
            }

            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    this.selectedIndex = Math.min(this.selectedIndex + 1, this.suggestions.length - 1);
                    this.updateSelection();
                    break;
                    
                case 'ArrowUp':
                    e.preventDefault();
                    this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                    this.updateSelection();
                    break;
                    
                case 'Enter':
                    e.preventDefault();
                    if (this.selectedIndex >= 0) {
                        this.selectSuggestion(this.selectedIndex);
                    }
                    break;
                    
                case 'Escape':
                    this.hideSuggestions();
                    this.input.blur();
                    break;
            }
        }

        updateSelection() {
            const suggestions = this.suggestionsContainer.querySelectorAll('.search-suggestion');
            suggestions.forEach((el, index) => {
                el.classList.toggle('selected', index === this.selectedIndex);
            });
        }

        selectSuggestion(index) {
            const suggestion = this.suggestions[index];
            if (suggestion) {
                this.input.value = suggestion.title;
                this.hideSuggestions();
                
                if (this.options.onSelect) {
                    this.options.onSelect(suggestion);
                }
            }
        }

        showSuggestions() {
            this.suggestionsContainer.style.display = 'block';
        }

        hideSuggestions() {
            this.suggestionsContainer.style.display = 'none';
            this.selectedIndex = -1;
        }

        showLoading() {
            this.suggestionsContainer.innerHTML = '<div class="search-loading">Searching...</div>';
            this.showSuggestions();
        }

        showError() {
            this.suggestionsContainer.innerHTML = '<div class="search-error">Search failed. Please try again.</div>';
            this.showSuggestions();
        }

        showNoResults() {
            this.suggestionsContainer.innerHTML = '<div class="search-no-results">No results found</div>';
            this.showSuggestions();
        }

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
        }

        clearCache() {
            this.cache.clear();
        }

        destroy() {
            if (this.currentRequest) {
                this.currentRequest.abort();
            }
            
            if (this.suggestionsContainer) {
                this.suggestionsContainer.remove();
            }
        }
    }

    // ===== GLOBAL API EXPOSURE =====
    window.StockScannerComponents = {
        AdvancedDataTable,
        AdvancedPagination,
        InfiniteScroll,
        AdvancedSearch
    };

    // ===== AUTO-INITIALIZATION FOR DEMOS (DISABLED) =====
    document.addEventListener('DOMContentLoaded', () => {
        // Auto-initialization is disabled to prevent loading fake data
        // Initialize components manually when needed with real data
        console.log('Stock Scanner Advanced Components v3.0.0 loaded - Initialize manually with real data');
    });

})();