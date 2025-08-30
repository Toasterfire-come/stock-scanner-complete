/**
 * Enhanced Theme Integration JavaScript
 * Modern interactions, animations, and functionality
 */

(function() {
  'use strict';
  
  // Wait for DOM to be ready
  document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all features
    initSmoothScrolling();
    initScrollAnimations();
    initLoadingStates();
    initTooltips();
    initSearchEnhancements();
    initFormValidation();
    initPerformanceOptimizations();
    initMobileEnhancements();
    initToastNotifications();
    
    console.log('🚀 Retail Trade Scanner Theme initialized');
  });
  
  /**
   * Smooth scrolling for anchor links
   */
  function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
      link.addEventListener('click', function(e) {
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
          e.preventDefault();
          
          const headerHeight = document.querySelector('.site-header')?.offsetHeight || 0;
          const targetPosition = targetElement.offsetTop - headerHeight - 20;
          
          window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
          });
        }
      });
    });
  }
  
  /**
   * Scroll-triggered animations
   */
  function initScrollAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('fade-in');
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);
    
    // Observe cards and content sections
    const animatedElements = document.querySelectorAll('.card, .footer-section, article');
    animatedElements.forEach(el => {
      if (!el.classList.contains('fade-in')) {
        observer.observe(el);
      }
    });
  }
  
  /**
   * Loading states for buttons and forms
   */
  function initLoadingStates() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
      form.addEventListener('submit', function() {
        const submitButton = this.querySelector('button[type="submit"], input[type="submit"]');
        
        if (submitButton && !submitButton.disabled) {
          submitButton.classList.add('loading');
          submitButton.disabled = true;
          
          // Reset after 5 seconds if no redirect occurs
          setTimeout(() => {
            submitButton.classList.remove('loading');
            submitButton.disabled = false;
          }, 5000);
        }
      });
    });
    
    // Loading states for navigation links
    const navLinks = document.querySelectorAll('.nav-link, .btn');
    navLinks.forEach(link => {
      link.addEventListener('click', function(e) {
        if (this.href && this.href !== window.location.href && !this.target) {
          this.style.opacity = '0.7';
          this.style.transform = 'scale(0.98)';
        }
      });
    });
  }
  
  /**
   * Enhanced tooltips for interactive elements
   */
  function initTooltips() {
    const tooltipElements = document.querySelectorAll('[title], [aria-label]');
    
    tooltipElements.forEach(element => {
      const tooltipText = element.getAttribute('title') || element.getAttribute('aria-label');
      
      if (tooltipText && tooltipText.length > 0) {
        element.addEventListener('mouseenter', function() {
          showTooltip(this, tooltipText);
        });
        
        element.addEventListener('mouseleave', function() {
          hideTooltip();
        });
      }
    });
  }
  
  function showTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
      position: absolute;
      background: var(--yinmn-blue);
      color: white;
      padding: 8px 12px;
      border-radius: var(--radius);
      font-size: 12px;
      font-weight: 500;
      z-index: 1000;
      pointer-events: none;
      opacity: 0;
      transform: translateY(5px);
      transition: all 0.2s ease;
      box-shadow: var(--shadow-lg);
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
    
    // Animate in
    requestAnimationFrame(() => {
      tooltip.style.opacity = '1';
      tooltip.style.transform = 'translateY(0)';
    });
  }
  
  function hideTooltip() {
    const tooltip = document.querySelector('.custom-tooltip');
    if (tooltip) {
      tooltip.style.opacity = '0';
      tooltip.style.transform = 'translateY(5px)';
      setTimeout(() => tooltip.remove(), 200);
    }
  }
  
  /**
   * Enhanced search functionality
   */
  function initSearchEnhancements() {
    const searchForms = document.querySelectorAll('.search-form, form[role="search"]');
    
    searchForms.forEach(form => {
      const searchInput = form.querySelector('input[type="search"], input[name="s"]');
      
      if (searchInput) {
        // Add search suggestions (placeholder for future enhancement)
        searchInput.addEventListener('input', debounce(function() {
          const query = this.value.trim();
          if (query.length > 2) {
            // Here you could implement search suggestions
            console.log('Search query:', query);
          }
        }, 300));
        
        // Enhanced placeholder animation
        searchInput.addEventListener('focus', function() {
          this.parentElement.classList.add('search-focused');
        });
        
        searchInput.addEventListener('blur', function() {
          this.parentElement.classList.remove('search-focused');
        });
      }
    });
  }
  
  /**
   * Form validation enhancements
   */
  function initFormValidation() {
    const emailInputs = document.querySelectorAll('input[type="email"]');
    
    emailInputs.forEach(input => {
      input.addEventListener('blur', function() {
        validateEmail(this);
      });
      
      input.addEventListener('input', function() {
        if (this.classList.contains('error')) {
          validateEmail(this);
        }
      });
    });
  }
  
  function validateEmail(input) {
    const email = input.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
      input.classList.add('error');
      showFieldError(input, 'Please enter a valid email address');
    } else {
      input.classList.remove('error');
      hideFieldError(input);
    }
  }
  
  function showFieldError(input, message) {
    let errorElement = input.parentElement.querySelector('.field-error');
    
    if (!errorElement) {
      errorElement = document.createElement('div');
      errorElement.className = 'field-error';
      errorElement.style.cssText = `
        color: var(--indian-red);
        font-size: 12px;
        margin-top: 4px;
        opacity: 0;
        transform: translateY(-5px);
        transition: all 0.2s ease;
      `;
      input.parentElement.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    requestAnimationFrame(() => {
      errorElement.style.opacity = '1';
      errorElement.style.transform = 'translateY(0)';
    });
  }
  
  function hideFieldError(input) {
    const errorElement = input.parentElement.querySelector('.field-error');
    if (errorElement) {
      errorElement.style.opacity = '0';
      errorElement.style.transform = 'translateY(-5px)';
      setTimeout(() => errorElement.remove(), 200);
    }
  }
  
  /**
   * Performance optimizations
   */
  function initPerformanceOptimizations() {
    // Lazy load images
    if ('IntersectionObserver' in window) {
      const lazyImages = document.querySelectorAll('img[data-src]');
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            imageObserver.unobserve(img);
          }
        });
      });
      
      lazyImages.forEach(img => imageObserver.observe(img));
    }
    
    // Preload critical resources
    const criticalLinks = document.querySelectorAll('a[href^="/dashboard"], a[href^="/scanner"]');
    criticalLinks.forEach(link => {
      link.addEventListener('mouseenter', function() {
        const linkElement = document.createElement('link');
        linkElement.rel = 'prefetch';
        linkElement.href = this.href;
        document.head.appendChild(linkElement);
      }, { once: true });
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
  
  function throttle(func, wait) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, wait);
      }
    };
  }
  
  /**
   * Theme customization based on user preferences
   */
  function initThemeCustomization() {
    // Respect user's motion preferences
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.documentElement.style.setProperty('--animation-duration', '0.01ms');
    }
    
    // Add high contrast mode support
    const highContrastQuery = window.matchMedia('(prefers-contrast: high)');
    
    function handleHighContrast(e) {
      if (e.matches) {
        document.body.classList.add('high-contrast');
      } else {
        document.body.classList.remove('high-contrast');
      }
    }
    
    highContrastQuery.addListener(handleHighContrast);
    handleHighContrast(highContrastQuery);
  }
  
  // Initialize theme customizations
  initThemeCustomization();
  
  // Expose utilities to global scope for other scripts
  window.RTSTheme = {
    debounce,
    throttle,
    showTooltip,
    hideTooltip
  };
  
})();

/**
 * Service Worker Registration (for future PWA features)
 */
if ('serviceWorker' in navigator && 'caches' in window) {
  window.addEventListener('load', function() {
    // Future: Register service worker for offline functionality
    console.log('Service Worker ready for future implementation');
  });
}

/**
 * Error handling and logging
 */
window.addEventListener('error', function(e) {
  console.error('Theme JavaScript Error:', e.error);
  
  // Future: Send errors to analytics or logging service
  if (window.gtag) {
    gtag('event', 'exception', {
      description: e.error.toString(),
      fatal: false
    });
  }
});

/**
 * API Health Check (if configured)
 */
document.addEventListener('DOMContentLoaded', function() {
  const healthDot = document.getElementById('rts-health-dot');
  
  if (healthDot && window.rtsConfig && window.rtsConfig.apiBase) {
    checkAPIHealth();
    
    // Check every 5 minutes
    setInterval(checkAPIHealth, 5 * 60 * 1000);
  }
  
  function checkAPIHealth() {
    const healthDot = document.getElementById('rts-health-dot');
    if (!healthDot) return;
    
    fetch(window.rtsConfig.apiBase + 'health', {
      method: 'GET',
      timeout: 5000
    })
    .then(response => {
      if (response.ok) {
        healthDot.style.backgroundColor = '#22c55e'; // Green
        healthDot.setAttribute('aria-label', 'API Online');
      } else {
        healthDot.style.backgroundColor = '#eab308'; // Yellow
        healthDot.setAttribute('aria-label', 'API Issues');
      }
    })
    .catch(() => {
      healthDot.style.backgroundColor = '#ef4444'; // Red
      healthDot.setAttribute('aria-label', 'API Offline');
    });
  }
});