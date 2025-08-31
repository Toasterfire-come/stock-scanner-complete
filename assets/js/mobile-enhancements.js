/**
 * Mobile Enhancements & Touch Gestures
 * Modern mobile interactions for WordPress theme
 */

(function() {
  'use strict';
  
  // Touch gesture support for sidebar
  let touchStartX = 0;
  let touchStartY = 0;
  let touchEndX = 0;
  let touchEndY = 0;
  let isScrolling = false;
  
  // Initialize mobile enhancements
  document.addEventListener('DOMContentLoaded', function() {
    initTouchGestures();
    initMobileOptimizations();
    initIOSEnhancements();
    initAndroidEnhancements();
    
    console.log('📱 Mobile enhancements initialized');
  });
  
  /**
   * Touch gestures for sidebar navigation
   */
  function initTouchGestures() {
    if (!('ontouchstart' in window)) return;
    
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const body = document.body;
    
    if (!sidebar) return;
    
    // Touch event handlers
    document.addEventListener('touchstart', handleTouchStart, { passive: false });
    document.addEventListener('touchmove', handleTouchMove, { passive: false });
    document.addEventListener('touchend', handleTouchEnd, { passive: true });
    
    function handleTouchStart(e) {
      const touch = e.touches[0];
      touchStartX = touch.clientX;
      touchStartY = touch.clientY;
      isScrolling = false;
    }
    
    function handleTouchMove(e) {
      if (!touchStartX || !touchStartY) return;
      
      const touch = e.touches[0];
      const deltaX = touch.clientX - touchStartX;
      const deltaY = touch.clientY - touchStartY;
      
      // Determine if user is scrolling vertically
      if (!isScrolling) {
        isScrolling = Math.abs(deltaY) > Math.abs(deltaX);
      }
      
      // Only handle horizontal swipes
      if (isScrolling) return;
      
      // Swipe from left edge to open sidebar (mobile only)
      if (window.innerWidth <= 768) {
        if (touchStartX < 20 && deltaX > 50 && Math.abs(deltaY) < 100) {
          openMobileSidebar();
          e.preventDefault();
        }
        
        // Swipe right to close sidebar when open
        if (sidebar.classList.contains('expanded') && deltaX > 50 && Math.abs(deltaY) < 50) {
          closeMobileSidebar();
          e.preventDefault();
        }
      }
    }
    
    function handleTouchEnd(e) {
      touchStartX = 0;
      touchStartY = 0;
      isScrolling = false;
    }
    
    function openMobileSidebar() {
      sidebar.classList.add('expanded');
      if (sidebarOverlay) sidebarOverlay.classList.add('active');
      body.style.overflow = 'hidden';
      
      // Add haptic feedback if available
      if (navigator.vibrate) {
        navigator.vibrate(50);
      }
    }
    
    function closeMobileSidebar() {
      sidebar.classList.remove('expanded');
      if (sidebarOverlay) sidebarOverlay.classList.remove('active');
      body.style.overflow = '';
      
      // Add haptic feedback if available
      if (navigator.vibrate) {
        navigator.vibrate(30);
      }
    }
  }
  
  /**
   * Mobile-specific optimizations
   */
  function initMobileOptimizations() {
    // Improve touch target sizes
    const touchTargets = document.querySelectorAll('button, a, input, select, textarea');
    touchTargets.forEach(target => {
      const rect = target.getBoundingClientRect();
      if (rect.width < 44 || rect.height < 44) {
        target.style.minWidth = '44px';
        target.style.minHeight = '44px';
        target.style.display = 'inline-flex';
        target.style.alignItems = 'center';
        target.style.justifyContent = 'center';
      }
    });
    
    // Optimize images for mobile
    const images = document.querySelectorAll('img');
    images.forEach(img => {
      if (!img.srcset && window.innerWidth <= 768) {
        // Add loading="lazy" for better performance
        img.loading = 'lazy';
        
        // Add touch-friendly image zoom
        img.addEventListener('click', function() {
          if (this.classList.contains('zoomed')) {
            this.classList.remove('zoomed');
            this.style.transform = '';
            this.style.zIndex = '';
            this.style.position = '';
          } else {
            this.classList.add('zoomed');
            this.style.transform = 'scale(1.5)';
            this.style.zIndex = '1000';
            this.style.position = 'relative';
            this.style.transition = 'transform 0.3s ease';
          }
        });
      }
    });
    
    // Optimize font sizes for mobile
    if (window.innerWidth <= 768) {
      const textElements = document.querySelectorAll('p, span, div, li');
      textElements.forEach(element => {
        const fontSize = window.getComputedStyle(element).fontSize;
        const fontSizeNum = parseFloat(fontSize);
        
        if (fontSizeNum < 14) {
          element.style.fontSize = '14px';
        }
      });
    }
    
    // Add pull-to-refresh simulation
    let pullStartY = 0;
    let pullDistance = 0;
    const pullThreshold = 100;
    
    document.addEventListener('touchstart', function(e) {
      if (window.scrollY === 0) {
        pullStartY = e.touches[0].clientY;
      }
    }, { passive: true });
    
    document.addEventListener('touchmove', function(e) {
      if (window.scrollY === 0 && pullStartY > 0) {
        pullDistance = e.touches[0].clientY - pullStartY;
        
        if (pullDistance > 0 && pullDistance < pullThreshold) {
          document.body.style.transform = `translateY(${pullDistance * 0.3}px)`;
          document.body.style.opacity = `${1 - (pullDistance / pullThreshold) * 0.2}`;
        }
      }
    }, { passive: true });
    
    document.addEventListener('touchend', function() {
      if (pullDistance > pullThreshold) {
        // Trigger refresh
        showToast('Refreshing content...', 'info');
        setTimeout(() => {
          window.location.reload();
        }, 500);
      }
      
      // Reset styles
      document.body.style.transform = '';
      document.body.style.opacity = '';
      pullStartY = 0;
      pullDistance = 0;
    }, { passive: true });
  }
  
  /**
   * iOS-specific enhancements
   */
  function initIOSEnhancements() {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    if (!isIOS) return;
    
    // Add iOS-specific class
    document.body.classList.add('ios-device');
    
    // Prevent zoom on input focus
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
      if (input.type !== 'file') {
        input.style.fontSize = '16px';
      }
    });
    
    // Handle safe area insets
    const header = document.querySelector('.site-header');
    const footer = document.querySelector('.site-footer');
    
    if (header) {
      header.style.paddingTop = 'env(safe-area-inset-top)';
    }
    
    if (footer) {
      footer.style.paddingBottom = 'env(safe-area-inset-bottom)';
    }
    
    // Add momentum scrolling
    const scrollableElements = document.querySelectorAll('.sidebar-nav, .search-suggestions');
    scrollableElements.forEach(element => {
      element.style.webkitOverflowScrolling = 'touch';
    });
    
    // Handle iOS status bar
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport) {
      viewport.content = 'width=device-width, initial-scale=1, viewport-fit=cover';
    }
  }
  
  /**
   * Android-specific enhancements
   */
  function initAndroidEnhancements() {
    const isAndroid = /Android/.test(navigator.userAgent);
    if (!isAndroid) return;
    
    // Add Android-specific class
    document.body.classList.add('android-device');
    
    // Handle Android back button
    if ('navigation' in window && 'back' in window.navigation) {
      window.navigation.addEventListener('navigate', function(e) {
        const sidebar = document.getElementById('sidebar');
        if (sidebar && sidebar.classList.contains('expanded')) {
          e.preventDefault();
          sidebar.classList.remove('expanded');
          const overlay = document.getElementById('sidebar-overlay');
          if (overlay) overlay.classList.remove('active');
          document.body.style.overflow = '';
        }
      });
    }
    
    // Optimize for Android Chrome
    const chromeVersion = navigator.userAgent.match(/Chrome\/(\d+)/);
    if (chromeVersion && parseInt(chromeVersion[1]) >= 70) {
      // Enable modern scrolling
      document.documentElement.style.scrollBehavior = 'smooth';
      
      // Add theme color for Android Chrome
      let themeColorMeta = document.querySelector('meta[name="theme-color"]');
      if (!themeColorMeta) {
        themeColorMeta = document.createElement('meta');
        themeColorMeta.name = 'theme-color';
        document.head.appendChild(themeColorMeta);
      }
      themeColorMeta.content = getComputedStyle(document.documentElement)
        .getPropertyValue('--drab-dark-brown').trim();
    }
  }
  
  /**
   * Toast notification system
   */
  function showToast(message, type = 'info', duration = 3000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'toast-container';
      toastContainer.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        display: flex;
        flex-direction: column;
        gap: 8px;
        pointer-events: none;
      `;
      document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Toast styles
    const colors = {
      info: { bg: 'var(--primary)', color: 'var(--primary-foreground)' },
      success: { bg: '#22c55e', color: 'white' },
      warning: { bg: '#f59e0b', color: 'white' },
      error: { bg: 'var(--accent)', color: 'var(--accent-foreground)' }
    };
    
    const colorScheme = colors[type] || colors.info;
    
    toast.style.cssText = `
      background: ${colorScheme.bg};
      color: ${colorScheme.color};
      padding: 12px 16px;
      border-radius: var(--radius);
      font-size: 14px;
      font-weight: 500;
      box-shadow: var(--shadow-lg);
      transform: translateX(100%);
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      pointer-events: auto;
      cursor: pointer;
      max-width: 300px;
    `;
    
    toastContainer.appendChild(toast);
    
    // Animate in
    requestAnimationFrame(() => {
      toast.style.transform = 'translateX(0)';
    });
    
    // Click to dismiss
    toast.addEventListener('click', () => dismissToast(toast));
    
    // Auto dismiss
    setTimeout(() => dismissToast(toast), duration);
    
    return toast;
  }
  
  function dismissToast(toast) {
    if (!toast || !toast.parentNode) return;
    
    toast.style.transform = 'translateX(100%)';
    toast.style.opacity = '0';
    
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }
  
  // Expose toast function globally
  window.showToast = showToast;
  
  // Performance monitoring for mobile
  if ('performance' in window) {
    window.addEventListener('load', function() {
      setTimeout(() => {
        const perfData = performance.timing;
        const loadTime = perfData.loadEventEnd - perfData.navigationStart;
        
        if (loadTime > 3000 && window.innerWidth <= 768) {
          console.warn('Mobile page load time:', loadTime + 'ms');
          
          // Show optimization hint to developers
          if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            showToast('Mobile load time: ' + Math.round(loadTime / 1000) + 's', 'warning');
          }
        }
      }, 1000);
    });
  }
  
  // Handle orientation changes
  window.addEventListener('orientationchange', function() {
    // Close sidebar on orientation change
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (sidebar && sidebar.classList.contains('expanded')) {
      sidebar.classList.remove('expanded');
      if (overlay) overlay.classList.remove('active');
      document.body.style.overflow = '';
    }
    
    // Recalculate viewport height
    setTimeout(() => {
      const vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    }, 100);
  });
  
  // Set initial viewport height
  const vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty('--vh', `${vh}px`);
  
})();

// CSS for mobile enhancements
const mobileCSS = `
  /* iOS specific styles */
  .ios-device {
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -webkit-tap-highlight-color: transparent;
  }
  
  .ios-device .site-header {
    padding-top: env(safe-area-inset-top);
  }
  
  .ios-device .site-footer {
    padding-bottom: env(safe-area-inset-bottom);
  }
  
  /* Android specific styles */
  .android-device {
    overscroll-behavior: contain;
  }
  
  /* Touch target improvements */
  @media (max-width: 768px) {
    button, a, input[type="checkbox"], input[type="radio"] {
      min-width: 44px;
      min-height: 44px;
    }
    
    .nav-link {
      padding: 16px 12px;
    }
    
    .btn {
      padding: 14px 20px;
      font-size: 16px;
    }
  }
  
  /* Improved scrolling */
  .sidebar-nav,
  .search-suggestions {
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
  }
  
  /* Pull to refresh indicator */
  .pull-to-refresh {
    position: fixed;
    top: -50px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--primary);
    color: var(--primary-foreground);
    padding: 8px 16px;
    border-radius: 0 0 var(--radius) var(--radius);
    font-size: 14px;
    font-weight: 500;
    transition: top 0.3s ease;
    z-index: 1001;
  }
  
  .pull-to-refresh.active {
    top: 0;
  }
  
  /* Mobile keyboard adjustments */
  @media (max-width: 768px) {
    .search-field,
    input[type="text"],
    input[type="email"],
    textarea {
      font-size: 16px; /* Prevents zoom on iOS */
    }
  }
  
  /* Landscape mode adjustments */
  @media (max-width: 768px) and (orientation: landscape) {
    .site-header {
      height: 56px;
    }
    
    .sidebar {
      width: 240px;
    }
    
    body.sidebar-expanded {
      padding-left: 0;
    }
  }
  
  /* High DPI displays */
  @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
    .nav-icon svg,
    .btn svg {
      shape-rendering: geometricPrecision;
    }
  }
  
  /* Focus styles for touch devices */
  @media (hover: none) and (pointer: coarse) {
    button:focus,
    a:focus,
    input:focus,
    textarea:focus {
      outline: 3px solid var(--primary);
      outline-offset: 2px;
    }
  }
`;

// Inject mobile CSS
const mobileStyleElement = document.createElement('style');
mobileStyleElement.textContent = mobileCSS;
document.head.appendChild(mobileStyleElement);