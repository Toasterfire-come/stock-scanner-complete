<?php
/**
 * Modern Search Form Template
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
?>

<form role="search" method="get" class="modern-search-form" action="<?php echo esc_url(home_url('/')); ?>">
  <div class="search-form-wrapper">
    <div class="search-input-container">
      <label for="search-field-<?php echo uniqid(); ?>" class="sr-only">
        <?php esc_html_e('Search for:', 'retail-trade-scanner'); ?>
      </label>
      
      <div class="search-input-wrapper">
        <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="21 21l-4.35-4.35"></path>
        </svg>
        
        <input
          type="search"
          id="search-field-<?php echo uniqid(); ?>"
          class="search-field"
          placeholder="<?php esc_attr_e('Search articles, pages, tutorials...', 'retail-trade-scanner'); ?>"
          value="<?php echo get_search_query(); ?>"
          name="s"
          autocomplete="off"
          spellcheck="false"
        />
        
        <button type="submit" class="search-submit" aria-label="<?php esc_attr_e('Submit Search', 'retail-trade-scanner'); ?>">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12,5 19,12 12,19"></polyline>
          </svg>
        </button>
        
        <!-- Clear button -->
        <button type="button" class="search-clear hidden" aria-label="<?php esc_attr_e('Clear Search', 'retail-trade-scanner'); ?>">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>
    
    <!-- Search suggestions dropdown (hidden by default) -->
    <div class="search-suggestions" id="search-suggestions" style="display: none;">
      <div class="suggestions-header">
        <span class="suggestions-title"><?php esc_html_e('Quick Suggestions', 'retail-trade-scanner'); ?></span>
      </div>
      <ul class="suggestions-list" role="listbox">
        <!-- Popular search terms -->
        <li class="suggestion-item" role="option" data-query="stock scanner">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="21 21l-4.35-4.35"></path>
          </svg>
          <span><?php esc_html_e('Stock Scanner', 'retail-trade-scanner'); ?></span>
        </li>
        <li class="suggestion-item" role="option" data-query="portfolio tracking">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="20" x2="18" y2="10"></line>
            <line x1="12" y1="20" x2="12" y2="4"></line>
            <line x1="6" y1="20" x2="6" y2="14"></line>
          </svg>
          <span><?php esc_html_e('Portfolio Tracking', 'retail-trade-scanner'); ?></span>
        </li>
        <li class="suggestion-item" role="option" data-query="price alerts">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <path d="M16 10a4 4 0 0 1-8 0"></path>
          </svg>
          <span><?php esc_html_e('Price Alerts', 'retail-trade-scanner'); ?></span>
        </li>
        <li class="suggestion-item" role="option" data-query="trading tutorials">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5,3 19,12 5,21"></polygon>
          </svg>
          <span><?php esc_html_e('Trading Tutorials', 'retail-trade-scanner'); ?></span>
        </li>
        <li class="suggestion-item" role="option" data-query="market analysis">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"></polyline>
          </svg>
          <span><?php esc_html_e('Market Analysis', 'retail-trade-scanner'); ?></span>
        </li>
      </ul>
    </div>
  </div>
</form>

<style>
.modern-search-form {
  position: relative;
  width: 100%;
  max-width: 400px;
}

.search-form-wrapper {
  position: relative;
}

.search-input-container {
  position: relative;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--surface);
  border: 2px solid var(--border);
  border-radius: var(--radius-lg);
  transition: all 0.2s ease;
  overflow: hidden;
}

.search-input-wrapper:hover {
  border-color: var(--primary);
  box-shadow: 0 2px 8px rgba(55, 74, 103, 0.1);
}

.search-input-wrapper:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(55, 74, 103, 0.1);
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--muted-foreground);
  pointer-events: none;
  z-index: 2;
  transition: color 0.2s ease;
}

.search-input-wrapper:focus-within .search-icon {
  color: var(--primary);
}

.search-field {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  padding: 12px 80px 12px 44px;
  color: var(--foreground);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.search-field::placeholder {
  color: var(--muted-foreground);
  font-weight: 400;
}

.search-field:focus::placeholder {
  opacity: 0.7;
}

.search-submit {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  width: 36px;
  height: 36px;
  background: var(--primary);
  color: var(--primary-foreground);
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 3;
}

.search-submit:hover {
  background: var(--primary-hover);
  transform: translateY(-50%) scale(1.05);
}

.search-submit:active {
  transform: translateY(-50%) scale(0.95);
}

.search-clear {
  position: absolute;
  right: 48px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  background: var(--muted);
  color: var(--muted-foreground);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  opacity: 0.7;
}

.search-clear:hover {
  background: var(--accent);
  color: var(--accent-foreground);
  opacity: 1;
  transform: translateY(-50%) scale(1.1);
}

.search-clear.hidden {
  display: none;
}

/* Search Suggestions Dropdown */
.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-top: none;
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
  backdrop-filter: blur(12px);
}

.suggestions-header {
  padding: 12px 16px 8px;
  border-bottom: 1px solid var(--border);
}

.suggestions-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--muted-foreground);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid rgba(193, 189, 179, 0.1);
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover {
  background: var(--surface-hover);
  color: var(--primary);
  transform: translateX(4px);
}

.suggestion-item svg {
  flex-shrink: 0;
  opacity: 0.7;
}

.suggestion-item:hover svg {
  opacity: 1;
  color: var(--primary);
}

.suggestion-item span {
  font-size: 14px;
  font-weight: 500;
}

/* Loading state */
.search-input-wrapper.loading .search-submit {
  background: var(--muted);
  cursor: not-allowed;
}

.search-input-wrapper.loading .search-submit svg {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .modern-search-form {
    max-width: 100%;
  }
  
  .search-field {
    font-size: 16px; /* Prevents zoom on iOS */
    padding: 14px 80px 14px 44px;
  }
  
  .search-input-wrapper {
    border-radius: var(--radius);
  }
  
  .search-suggestions {
    border-radius: 0 0 var(--radius) var(--radius);
  }
}

/* Focus trap for accessibility */
.search-form-wrapper.focus-trapped .search-suggestions {
  display: block;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .search-input-wrapper {
    border-width: 3px;
  }
  
  .search-submit {
    border: 2px solid var(--primary-foreground);
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .search-input-wrapper,
  .search-submit,
  .search-clear,
  .suggestion-item {
    transition: none;
  }
  
  .search-submit:hover,
  .search-clear:hover {
    transform: none;
  }
  
  .suggestion-item:hover {
    transform: none;
  }
}
</style>

<script>
(function() {
  'use strict';
  
  document.addEventListener('DOMContentLoaded', function() {
    const searchForms = document.querySelectorAll('.modern-search-form');
    
    searchForms.forEach(function(form) {
      const searchField = form.querySelector('.search-field');
      const searchClear = form.querySelector('.search-clear');
      const searchSuggestions = form.querySelector('.search-suggestions');
      const suggestionItems = form.querySelectorAll('.suggestion-item');
      const searchWrapper = form.querySelector('.search-form-wrapper');
      
      let currentFocus = -1;
      
      // Show/hide clear button
      function toggleClearButton() {
        if (searchField.value.length > 0) {
          searchClear.classList.remove('hidden');
        } else {
          searchClear.classList.add('hidden');
        }
      }
      
      // Show suggestions
      function showSuggestions() {
        if (searchField.value.length === 0) {
          searchSuggestions.style.display = 'block';
          searchWrapper.classList.add('focus-trapped');
        }
      }
      
      // Hide suggestions
      function hideSuggestions() {
        searchSuggestions.style.display = 'none';
        searchWrapper.classList.remove('focus-trapped');
        currentFocus = -1;
      }
      
      // Handle keyboard navigation
      function handleKeyNavigation(e) {
        const items = Array.from(suggestionItems);
        
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          currentFocus = currentFocus < items.length - 1 ? currentFocus + 1 : 0;
          updateFocus(items);
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          currentFocus = currentFocus > 0 ? currentFocus - 1 : items.length - 1;
          updateFocus(items);
        } else if (e.key === 'Enter' && currentFocus >= 0) {
          e.preventDefault();
          items[currentFocus].click();
        } else if (e.key === 'Escape') {
          hideSuggestions();
          searchField.blur();
        }
      }
      
      // Update focus styling
      function updateFocus(items) {
        items.forEach((item, index) => {
          if (index === currentFocus) {
            item.style.background = 'var(--surface-hover)';
            item.style.color = 'var(--primary)';
            item.setAttribute('aria-selected', 'true');
          } else {
            item.style.background = '';
            item.style.color = '';
            item.setAttribute('aria-selected', 'false');
          }
        });
      }
      
      // Event listeners
      searchField.addEventListener('input', function() {
        toggleClearButton();
        
        // Hide suggestions when typing
        if (this.value.length > 0) {
          hideSuggestions();
        }
        
        // Debounced search suggestions (placeholder for future AJAX)
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
          // Here you could implement live search suggestions via AJAX
          console.log('Search query:', this.value);
        }, 300);
      });
      
      searchField.addEventListener('focus', function() {
        showSuggestions();
        toggleClearButton();
      });
      
      searchField.addEventListener('keydown', handleKeyNavigation);
      
      // Clear button functionality
      searchClear.addEventListener('click', function() {
        searchField.value = '';
        searchField.focus();
        toggleClearButton();
        showSuggestions();
      });
      
      // Suggestion item clicks
      suggestionItems.forEach(function(item) {
        item.addEventListener('click', function() {
          const query = this.dataset.query;
          searchField.value = query;
          hideSuggestions();
          form.submit();
        });
        
        item.addEventListener('mouseenter', function() {
          suggestionItems.forEach(i => {
            i.style.background = '';
            i.style.color = '';
            i.setAttribute('aria-selected', 'false');
          });
          this.style.background = 'var(--surface-hover)';
          this.style.color = 'var(--primary)';
          this.setAttribute('aria-selected', 'true');
          currentFocus = Array.from(suggestionItems).indexOf(this);
        });
      });
      
      // Hide suggestions when clicking outside
      document.addEventListener('click', function(e) {
        if (!form.contains(e.target)) {
          hideSuggestions();
        }
      });
      
      // Form submission with loading state
      form.addEventListener('submit', function() {
        const submitButton = this.querySelector('.search-submit');
        const inputWrapper = this.querySelector('.search-input-wrapper');
        
        if (searchField.value.trim()) {
          inputWrapper.classList.add('loading');
          submitButton.setAttribute('disabled', 'disabled');
        }
      });
      
      // Initialize
      toggleClearButton();
    });
  });
  
  // Track search analytics
  function trackSearchQuery(query) {
    if (typeof gtag !== 'undefined') {
      gtag('event', 'search', {
        search_term: query,
        engagement_time_msec: 100
      });
    }
  }
  
})();
</script>