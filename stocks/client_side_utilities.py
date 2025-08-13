"""
Client-Side Utilities for Frontend Processing
Comprehensive browser-based data management and UI utilities
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)

class ClientSideUtilitiesGenerator:
    """
    Generates JavaScript utilities for comprehensive frontend processing
    """
    
    def generate_pagination_system(self):
        """
        Generate client-side pagination with virtual scrolling
        """
        return '''
// Advanced Client-Side Pagination System
class ClientPagination {
    constructor(options = {}) {
        this.data = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.pageSize = options.pageSize || 50;
        this.totalPages = 0;
        this.virtualScrolling = options.virtualScrolling || true;
        this.preloadPages = options.preloadPages || 2;
        this.container = options.container;
        this.onPageChange = options.onPageChange || (() => {});
        this.cache = new Map();
        this.renderBuffer = [];
        this.visibleRange = { start: 0, end: 0 };
    }
    
    setData(data) {
        this.data = data;
        this.filteredData = [...data];
        this.totalPages = Math.ceil(this.filteredData.length / this.pageSize);
        this.goToPage(1);
    }
    
    applyFilter(filterFn) {
        this.filteredData = this.data.filter(filterFn);
        this.totalPages = Math.ceil(this.filteredData.length / this.pageSize);
        this.goToPage(1);
    }
    
    goToPage(page) {
        if (page < 1 || page > this.totalPages) return;
        
        this.currentPage = page;
        const startIndex = (page - 1) * this.pageSize;
        const endIndex = Math.min(startIndex + this.pageSize, this.filteredData.length);
        
        if (this.virtualScrolling) {
            this.updateVirtualScrolling(startIndex, endIndex);
        } else {
            this.renderPage(startIndex, endIndex);
        }
        
        this.onPageChange({
            page: this.currentPage,
            totalPages: this.totalPages,
            startIndex,
            endIndex,
            data: this.filteredData.slice(startIndex, endIndex)
        });
    }
    
    updateVirtualScrolling(startIndex, endIndex) {
        const containerHeight = this.container.clientHeight;
        const itemHeight = 50; // Estimated item height
        const visibleItems = Math.ceil(containerHeight / itemHeight);
        const bufferSize = Math.max(10, Math.floor(visibleItems / 2));
        
        const virtualStart = Math.max(0, startIndex - bufferSize);
        const virtualEnd = Math.min(this.filteredData.length, endIndex + bufferSize);
        
        this.visibleRange = { start: virtualStart, end: virtualEnd };
        this.renderVirtualItems(virtualStart, virtualEnd);
        
        // Preload adjacent pages
        this.preloadAdjacentPages();
    }
    
    renderVirtualItems(start, end) {
        const fragment = document.createDocumentFragment();
        const items = this.filteredData.slice(start, end);
        
        items.forEach((item, index) => {
            const element = this.createItemElement(item, start + index);
            fragment.appendChild(element);
        });
        
        // Update container with virtual items
        if (this.container) {
            this.container.innerHTML = '';
            this.container.appendChild(fragment);
            
            // Set container height for proper scrolling
            const totalHeight = this.filteredData.length * 50;
            this.container.style.height = totalHeight + 'px';
        }
    }
    
    renderPage(startIndex, endIndex) {
        const fragment = document.createDocumentFragment();
        const pageData = this.filteredData.slice(startIndex, endIndex);
        
        pageData.forEach((item, index) => {
            const element = this.createItemElement(item, startIndex + index);
            fragment.appendChild(element);
        });
        
        if (this.container) {
            this.container.innerHTML = '';
            this.container.appendChild(fragment);
        }
    }
    
    createItemElement(item, index) {
        // Override this method to customize item rendering
        const div = document.createElement('div');
        div.className = 'pagination-item';
        div.dataset.index = index;
        div.innerHTML = JSON.stringify(item);
        return div;
    }
    
    preloadAdjacentPages() {
        const pagesToPreload = [];
        
        for (let i = 1; i <= this.preloadPages; i++) {
            if (this.currentPage - i >= 1) {
                pagesToPreload.push(this.currentPage - i);
            }
            if (this.currentPage + i <= this.totalPages) {
                pagesToPreload.push(this.currentPage + i);
            }
        }
        
        pagesToPreload.forEach(page => {
            if (!this.cache.has(page)) {
                const startIndex = (page - 1) * this.pageSize;
                const endIndex = Math.min(startIndex + this.pageSize, this.filteredData.length);
                this.cache.set(page, this.filteredData.slice(startIndex, endIndex));
            }
        });
    }
    
    nextPage() {
        this.goToPage(this.currentPage + 1);
    }
    
    previousPage() {
        this.goToPage(this.currentPage - 1);
    }
    
    getPageInfo() {
        return {
            currentPage: this.currentPage,
            totalPages: this.totalPages,
            pageSize: this.pageSize,
            totalItems: this.filteredData.length,
            hasNext: this.currentPage < this.totalPages,
            hasPrevious: this.currentPage > 1
        };
    }
}
'''
    
    def generate_search_system(self):
        """
        Generate client-side search and indexing system
        """
        return '''
// Advanced Client-Side Search System
class ClientSearch {
    constructor(options = {}) {
        this.data = [];
        this.searchIndex = new Map();
        this.fuzzySearch = options.fuzzySearch || true;
        this.caseSensitive = options.caseSensitive || false;
        this.debounceMs = options.debounceMs || 300;
        this.searchFields = options.searchFields || [];
        this.minQueryLength = options.minQueryLength || 2;
        this.debounceTimer = null;
        this.lastQuery = '';
        this.searchResults = [];
    }
    
    setData(data, searchFields = []) {
        this.data = data;
        this.searchFields = searchFields.length ? searchFields : this.searchFields;
        this.buildSearchIndex();
    }
    
    buildSearchIndex() {
        this.searchIndex.clear();
        
        this.data.forEach((item, index) => {
            const searchableText = this.extractSearchableText(item);
            const words = this.tokenize(searchableText);
            
            words.forEach(word => {
                if (!this.searchIndex.has(word)) {
                    this.searchIndex.set(word, new Set());
                }
                this.searchIndex.get(word).add(index);
            });
            
            // Add trigrams for fuzzy search
            if (this.fuzzySearch) {
                const trigrams = this.generateTrigrams(searchableText);
                trigrams.forEach(trigram => {
                    const key = 'trigram_' + trigram;
                    if (!this.searchIndex.has(key)) {
                        this.searchIndex.set(key, new Set());
                    }
                    this.searchIndex.get(key).add(index);
                });
            }
        });
    }
    
    extractSearchableText(item) {
        if (this.searchFields.length === 0) {
            return JSON.stringify(item);
        }
        
        return this.searchFields.map(field => {
            const value = this.getNestedValue(item, field);
            return String(value || '');
        }).join(' ');
    }
    
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => {
            return current && current[key] !== undefined ? current[key] : '';
        }, obj);
    }
    
    tokenize(text) {
        const normalizedText = this.caseSensitive ? text : text.toLowerCase();
        return normalizedText
            .replace(/[^a-zA-Z0-9\\s]/g, ' ')
            .split(/\\s+/)
            .filter(word => word.length > 0);
    }
    
    generateTrigrams(text) {
        const normalizedText = this.caseSensitive ? text : text.toLowerCase();
        const trigrams = [];
        
        for (let i = 0; i <= normalizedText.length - 3; i++) {
            trigrams.push(normalizedText.substring(i, i + 3));
        }
        
        return trigrams;
    }
    
    search(query, callback) {
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        this.debounceTimer = setTimeout(() => {
            const results = this.performSearch(query);
            callback(results);
        }, this.debounceMs);
    }
    
    performSearch(query) {
        if (!query || query.length < this.minQueryLength) {
            return {
                query: query,
                results: [],
                totalResults: 0,
                searchTime: 0
            };
        }
        
        const startTime = performance.now();
        const normalizedQuery = this.caseSensitive ? query : query.toLowerCase();
        
        let matchingIndices = new Set();
        
        // Exact word matching
        const queryWords = this.tokenize(normalizedQuery);
        if (queryWords.length > 0) {
            queryWords.forEach((word, wordIndex) => {
                const wordMatches = new Set();
                
                // Direct word matches
                if (this.searchIndex.has(word)) {
                    this.searchIndex.get(word).forEach(index => wordMatches.add(index));
                }
                
                // Partial word matches
                this.searchIndex.forEach((indices, indexedWord) => {
                    if (indexedWord.includes(word) && !indexedWord.startsWith('trigram_')) {
                        indices.forEach(index => wordMatches.add(index));
                    }
                });
                
                if (wordIndex === 0) {
                    matchingIndices = wordMatches;
                } else {
                    // Intersection for multi-word queries
                    matchingIndices = new Set([...matchingIndices].filter(x => wordMatches.has(x)));
                }
            });
        }
        
        // Fuzzy search using trigrams
        if (this.fuzzySearch && matchingIndices.size === 0) {
            const queryTrigrams = this.generateTrigrams(normalizedQuery);
            const trigramMatches = new Map();
            
            queryTrigrams.forEach(trigram => {
                const key = 'trigram_' + trigram;
                if (this.searchIndex.has(key)) {
                    this.searchIndex.get(key).forEach(index => {
                        trigramMatches.set(index, (trigramMatches.get(index) || 0) + 1);
                    });
                }
            });
            
            // Sort by trigram match count (relevance)
            const sortedMatches = [...trigramMatches.entries()]
                .sort((a, b) => b[1] - a[1])
                .slice(0, 100); // Limit fuzzy results
            
            matchingIndices = new Set(sortedMatches.map(([index]) => index));
        }
        
        // Convert indices to actual results
        const results = [...matchingIndices]
            .map(index => ({
                item: this.data[index],
                index: index,
                relevance: this.calculateRelevance(this.data[index], normalizedQuery)
            }))
            .sort((a, b) => b.relevance - a.relevance);
        
        const searchTime = performance.now() - startTime;
        
        this.searchResults = results;
        this.lastQuery = query;
        
        return {
            query: query,
            results: results,
            totalResults: results.length,
            searchTime: searchTime
        };
    }
    
    calculateRelevance(item, query) {
        const searchableText = this.extractSearchableText(item).toLowerCase();
        let relevance = 0;
        
        // Exact match bonus
        if (searchableText.includes(query)) {
            relevance += 100;
        }
        
        // Word match bonus
        const queryWords = this.tokenize(query);
        queryWords.forEach(word => {
            if (searchableText.includes(word)) {
                relevance += 10;
            }
        });
        
        // Position bonus (earlier matches are more relevant)
        const firstMatchIndex = searchableText.indexOf(query);
        if (firstMatchIndex !== -1) {
            relevance += Math.max(0, 50 - firstMatchIndex);
        }
        
        return relevance;
    }
    
    getSearchSuggestions(query, maxSuggestions = 5) {
        const normalizedQuery = this.caseSensitive ? query : query.toLowerCase();
        const suggestions = new Set();
        
        // Find words that start with the query
        this.searchIndex.forEach((indices, word) => {
            if (word.startsWith(normalizedQuery) && !word.startsWith('trigram_')) {
                suggestions.add(word);
            }
        });
        
        return [...suggestions].slice(0, maxSuggestions);
    }
    
    highlightMatches(text, query) {
        if (!query) return text;
        
        const normalizedQuery = this.caseSensitive ? query : query.toLowerCase();
        const normalizedText = this.caseSensitive ? text : text.toLowerCase();
        
        let highlightedText = text;
        const queryWords = this.tokenize(normalizedQuery);
        
        queryWords.forEach(word => {
            const regex = new RegExp(`(${word})`, this.caseSensitive ? 'g' : 'gi');
            highlightedText = highlightedText.replace(regex, '<mark>$1</mark>');
        });
        
        return highlightedText;
    }
}
'''
    
    def generate_data_aggregation_system(self):
        """
        Generate client-side data aggregation and analysis
        """
        return '''
// Client-Side Data Aggregation System
class DataAggregator {
    constructor() {
        this.data = [];
        this.aggregationCache = new Map();
    }
    
    setData(data) {
        this.data = data;
        this.aggregationCache.clear();
    }
    
    groupBy(field, aggregationFn = null) {
        const cacheKey = `groupBy_${field}_${aggregationFn ? aggregationFn.name : 'count'}`;
        
        if (this.aggregationCache.has(cacheKey)) {
            return this.aggregationCache.get(cacheKey);
        }
        
        const groups = {};
        
        this.data.forEach(item => {
            const value = this.getNestedValue(item, field);
            const key = String(value);
            
            if (!groups[key]) {
                groups[key] = [];
            }
            groups[key].push(item);
        });
        
        // Apply aggregation function if provided
        if (aggregationFn) {
            Object.keys(groups).forEach(key => {
                groups[key] = aggregationFn(groups[key]);
            });
        }
        
        this.aggregationCache.set(cacheKey, groups);
        return groups;
    }
    
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => {
            return current && current[key] !== undefined ? current[key] : null;
        }, obj);
    }
    
    aggregate(field, operation = 'sum') {
        const cacheKey = `aggregate_${field}_${operation}`;
        
        if (this.aggregationCache.has(cacheKey)) {
            return this.aggregationCache.get(cacheKey);
        }
        
        let result;
        const values = this.data
            .map(item => parseFloat(this.getNestedValue(item, field)))
            .filter(value => !isNaN(value));
        
        switch (operation) {
            case 'sum':
                result = values.reduce((acc, val) => acc + val, 0);
                break;
            case 'avg':
            case 'average':
                result = values.length > 0 ? values.reduce((acc, val) => acc + val, 0) / values.length : 0;
                break;
            case 'min':
                result = values.length > 0 ? Math.min(...values) : 0;
                break;
            case 'max':
                result = values.length > 0 ? Math.max(...values) : 0;
                break;
            case 'count':
                result = values.length;
                break;
            case 'median':
                const sorted = values.sort((a, b) => a - b);
                const mid = Math.floor(sorted.length / 2);
                result = sorted.length % 2 === 0 
                    ? (sorted[mid - 1] + sorted[mid]) / 2 
                    : sorted[mid];
                break;
            default:
                result = 0;
        }
        
        this.aggregationCache.set(cacheKey, result);
        return result;
    }
    
    percentileRank(field, value) {
        const values = this.data
            .map(item => parseFloat(this.getNestedValue(item, field)))
            .filter(val => !isNaN(val))
            .sort((a, b) => a - b);
        
        const index = values.findIndex(val => val >= value);
        return index === -1 ? 100 : (index / values.length) * 100;
    }
    
    getDistribution(field, buckets = 10) {
        const values = this.data
            .map(item => parseFloat(this.getNestedValue(item, field)))
            .filter(val => !isNaN(val));
        
        if (values.length === 0) return [];
        
        const min = Math.min(...values);
        const max = Math.max(...values);
        const bucketSize = (max - min) / buckets;
        
        const distribution = Array(buckets).fill(0);
        
        values.forEach(value => {
            const bucketIndex = Math.min(Math.floor((value - min) / bucketSize), buckets - 1);
            distribution[bucketIndex]++;
        });
        
        return distribution.map((count, index) => ({
            range: {
                min: min + (index * bucketSize),
                max: min + ((index + 1) * bucketSize)
            },
            count: count,
            percentage: (count / values.length) * 100
        }));
    }
    
    correlation(field1, field2) {
        const pairs = this.data
            .map(item => [
                parseFloat(this.getNestedValue(item, field1)),
                parseFloat(this.getNestedValue(item, field2))
            ])
            .filter(([x, y]) => !isNaN(x) && !isNaN(y));
        
        if (pairs.length < 2) return 0;
        
        const n = pairs.length;
        const sumX = pairs.reduce((acc, [x]) => acc + x, 0);
        const sumY = pairs.reduce((acc, [, y]) => acc + y, 0);
        const sumXY = pairs.reduce((acc, [x, y]) => acc + (x * y), 0);
        const sumX2 = pairs.reduce((acc, [x]) => acc + (x * x), 0);
        const sumY2 = pairs.reduce((acc, [, y]) => acc + (y * y), 0);
        
        const numerator = (n * sumXY) - (sumX * sumY);
        const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
        
        return denominator === 0 ? 0 : numerator / denominator;
    }
    
    topN(field, n = 10, ascending = false) {
        const sorted = [...this.data].sort((a, b) => {
            const aVal = parseFloat(this.getNestedValue(a, field)) || 0;
            const bVal = parseFloat(this.getNestedValue(b, field)) || 0;
            return ascending ? aVal - bVal : bVal - aVal;
        });
        
        return sorted.slice(0, n);
    }
    
    movingAverage(field, period = 20) {
        const values = this.data.map(item => parseFloat(this.getNestedValue(item, field)) || 0);
        const result = [];
        
        for (let i = period - 1; i < values.length; i++) {
            const sum = values.slice(i - period + 1, i + 1).reduce((acc, val) => acc + val, 0);
            result.push({
                index: i,
                value: sum / period,
                originalValue: values[i]
            });
        }
        
        return result;
    }
    
    getStatistics(field) {
        const values = this.data
            .map(item => parseFloat(this.getNestedValue(item, field)))
            .filter(val => !isNaN(val));
        
        if (values.length === 0) {
            return { count: 0, sum: 0, average: 0, min: 0, max: 0, median: 0, standardDeviation: 0 };
        }
        
        const sorted = [...values].sort((a, b) => a - b);
        const sum = values.reduce((acc, val) => acc + val, 0);
        const average = sum / values.length;
        const median = sorted.length % 2 === 0 
            ? (sorted[Math.floor(sorted.length / 2) - 1] + sorted[Math.floor(sorted.length / 2)]) / 2
            : sorted[Math.floor(sorted.length / 2)];
        
        const variance = values.reduce((acc, val) => acc + Math.pow(val - average, 2), 0) / values.length;
        const standardDeviation = Math.sqrt(variance);
        
        return {
            count: values.length,
            sum: sum,
            average: average,
            min: Math.min(...values),
            max: Math.max(...values),
            median: median,
            standardDeviation: standardDeviation,
            variance: variance
        };
    }
}
'''
    
    def generate_progressive_loading_system(self):
        """
        Generate progressive data loading system
        """
        return '''
// Progressive Data Loading System
class ProgressiveLoader {
    constructor(options = {}) {
        this.apiEndpoint = options.apiEndpoint;
        this.batchSize = options.batchSize || 100;
        this.maxConcurrentRequests = options.maxConcurrentRequests || 3;
        this.retryAttempts = options.retryAttempts || 3;
        this.cacheEnabled = options.cacheEnabled || true;
        this.onProgress = options.onProgress || (() => {});
        this.onComplete = options.onComplete || (() => {});
        this.onError = options.onError || (() => {});
        
        this.loadedData = [];
        this.totalExpected = 0;
        this.currentOffset = 0;
        this.activeRequests = 0;
        this.cache = new Map();
        this.isLoading = false;
    }
    
    async loadData(totalItems, startOffset = 0) {
        this.totalExpected = totalItems;
        this.currentOffset = startOffset;
        this.loadedData = [];
        this.isLoading = true;
        
        try {
            await this.loadBatches();
            this.onComplete(this.loadedData);
        } catch (error) {
            this.onError(error);
        } finally {
            this.isLoading = false;
        }
    }
    
    async loadBatches() {
        const totalBatches = Math.ceil(this.totalExpected / this.batchSize);
        const promises = [];
        
        for (let batch = 0; batch < totalBatches; batch++) {
            if (this.activeRequests >= this.maxConcurrentRequests) {
                await Promise.race(promises);
            }
            
            const offset = this.currentOffset + (batch * this.batchSize);
            const limit = Math.min(this.batchSize, this.totalExpected - (batch * this.batchSize));
            
            const promise = this.loadBatch(offset, limit, batch)
                .then(data => {
                    this.activeRequests--;
                    this.processBatchData(data, batch);
                })
                .catch(error => {
                    this.activeRequests--;
                    throw error;
                });
            
            promises.push(promise);
            this.activeRequests++;
        }
        
        await Promise.all(promises);
    }
    
    async loadBatch(offset, limit, batchIndex) {
        const cacheKey = `${offset}_${limit}`;
        
        if (this.cacheEnabled && this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }
        
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const response = await fetch(`${this.apiEndpoint}?offset=${offset}&limit=${limit}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                
                if (this.cacheEnabled) {
                    this.cache.set(cacheKey, data);
                }
                
                return data;
                
            } catch (error) {
                if (attempt === this.retryAttempts) {
                    throw new Error(`Failed to load batch after ${this.retryAttempts} attempts: ${error.message}`);
                }
                
                // Exponential backoff
                await this.delay(Math.pow(2, attempt) * 1000);
            }
        }
    }
    
    processBatchData(batchData, batchIndex) {
        const data = batchData.data || batchData;
        this.loadedData = this.loadedData.concat(data);
        
        const progress = {
            loaded: this.loadedData.length,
            total: this.totalExpected,
            percentage: (this.loadedData.length / this.totalExpected) * 100,
            batchIndex: batchIndex
        };
        
        this.onProgress(progress);
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    abort() {
        this.isLoading = false;
        // Note: In a real implementation, you'd cancel active fetch requests
    }
    
    clearCache() {
        this.cache.clear();
    }
    
    getLoadedData() {
        return this.loadedData;
    }
    
    getProgress() {
        return {
            loaded: this.loadedData.length,
            total: this.totalExpected,
            percentage: this.totalExpected > 0 ? (this.loadedData.length / this.totalExpected) * 100 : 0,
            isLoading: this.isLoading
        };
    }
}

// Intersection Observer for Lazy Loading
class LazyLoader {
    constructor(options = {}) {
        this.threshold = options.threshold || 0.1;
        this.rootMargin = options.rootMargin || '100px';
        this.onIntersect = options.onIntersect || (() => {});
        
        this.observer = new IntersectionObserver(
            this.handleIntersection.bind(this),
            {
                threshold: this.threshold,
                rootMargin: this.rootMargin
            }
        );
        
        this.observedElements = new Set();
    }
    
    observe(element, data = {}) {
        if (this.observedElements.has(element)) return;
        
        element.dataset.lazyData = JSON.stringify(data);
        this.observer.observe(element);
        this.observedElements.add(element);
    }
    
    unobserve(element) {
        this.observer.unobserve(element);
        this.observedElements.delete(element);
    }
    
    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const data = JSON.parse(element.dataset.lazyData || '{}');
                
                this.onIntersect(element, data);
                this.unobserve(element);
            }
        });
    }
    
    disconnect() {
        this.observer.disconnect();
        this.observedElements.clear();
    }
}
'''

utilities_generator = ClientSideUtilitiesGenerator()

@api_view(['GET'])
@permission_classes([AllowAny])
def get_client_utilities(request):
    """
    Provide comprehensive client-side utility scripts
    """
    try:
        utility_type = request.GET.get('type', 'all')
        
        utilities = {}
        
        if utility_type in ['all', 'pagination']:
            utilities['pagination'] = utilities_generator.generate_pagination_system()
        
        if utility_type in ['all', 'search']:
            utilities['search'] = utilities_generator.generate_search_system()
        
        if utility_type in ['all', 'aggregation']:
            utilities['aggregation'] = utilities_generator.generate_data_aggregation_system()
        
        if utility_type in ['all', 'progressive']:
            utilities['progressive_loading'] = utilities_generator.generate_progressive_loading_system()
        
        return Response({
            'status': 'success',
            'utilities': utilities,
            'utility_type': utility_type,
            'features': [
                'Virtual scrolling pagination',
                'Fuzzy search with indexing',
                'Real-time data aggregation',
                'Progressive data loading',
                'Intersection Observer lazy loading',
                'Client-side caching',
                'Performance optimized'
            ],
            'usage_note': 'These utilities shift computational load from backend to frontend',
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Client utilities error: {e}")
        return Response({
            'status': 'error',
            'message': 'Failed to get client utilities',
            'timestamp': timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_performance_config(request):
    """
    Provide frontend performance optimization configuration
    """
    try:
        return Response({
            'status': 'success',
            'performance_config': {
                'data_loading': {
                    'batch_size': 100,
                    'max_concurrent_requests': 3,
                    'cache_enabled': True,
                    'cache_ttl': 300000,  # 5 minutes
                    'compression': True
                },
                'rendering': {
                    'virtual_scrolling': True,
                    'debounce_ms': 300,
                    'throttle_ms': 16,  # 60fps
                    'lazy_loading_threshold': 0.1,
                    'preload_pages': 2
                },
                'memory_management': {
                    'max_cache_size': 50 * 1024 * 1024,  # 50MB
                    'cleanup_interval': 30000,  # 30 seconds
                    'gc_threshold': 1000,  # Items
                    'compress_old_data': True
                },
                'api_optimization': {
                    'minimal_payloads': True,
                    'field_selection': True,
                    'compression': True,
                    'client_side_processing': True
                }
            },
            'browser_requirements': {
                'es6_support': True,
                'fetch_api': True,
                'intersection_observer': True,
                'web_workers': True,
                'local_storage': True
            },
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Performance config error: {e}")
        return Response({
            'status': 'error',
            'message': 'Failed to get performance configuration',
            'timestamp': timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)