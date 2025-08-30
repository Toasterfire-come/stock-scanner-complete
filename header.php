<?php
/** 
 * Modern Header with Expandable Sidebar Navigation
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<a class="skip-link" href="#primary"><?php esc_html_e('Skip to content','retail-trade-scanner'); ?></a>

<!-- Mobile Sidebar Overlay -->
<div class="sidebar-overlay" id="sidebar-overlay"></div>

<!-- Expandable Sidebar Navigation -->
<nav class="sidebar" id="sidebar" role="navigation" aria-label="Main Navigation">
  <div class="sidebar-header">
    <button class="sidebar-toggle" id="sidebar-toggle" aria-label="Toggle Navigation">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </button>
    <div class="sidebar-logo">
      <?php bloginfo('name'); ?>
    </div>
  </div>
  
  <div class="sidebar-nav">
    <?php
    // Define navigation items with SVG icons
    $nav_items = [
      [
        'title' => __('Dashboard', 'retail-trade-scanner'),
        'url' => home_url('/dashboard/'),
        'icon' => '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>'
      ],
      [
        'title' => __('Stock Scanner', 'retail-trade-scanner'),
        'url' => home_url('/scanner/'),
        'icon' => '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><path d="21 21l-4.35-4.35"></path></svg>'
      ],
      [
        'title' => __('Portfolio', 'retail-trade-scanner'),
        'url' => home_url('/portfolio/'),
        'icon' => '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>'
      ],
      [
        'title' => __('Watchlists', 'retail-trade-scanner'),
        'url' => home_url('/watchlists/'),
        'icon' => '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>'
      ],
      [
        'title' => __('Price Alerts', 'retail-trade-scanner'),
        'url' => home_url('/alerts/'),
        'icon' => '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><bell></bell><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>'
      ],
      [
        'title' => __('Market News', 'retail-trade-scanner'),
        'url' => home_url('/news/'),
        'icon' => '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"></path><path d="M18 14h-8"></path><path d="M15 18h-5"></path><path d="M10 6h8v4h-8V6Z"></path></svg>'
      ],
      [
        'title' => __('Tutorials', 'retail-trade-scanner'),
        'url' => home_url('/tutorials/'),
        'icon' => '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5,3 19,12 5,21"></polygon></svg>'
      ],
      [
        'title' => __('Help Center', 'retail-trade-scanner'),
        'url' => home_url('/help/'),
        'icon' => '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
      ],
      [
        'title' => __('Contact', 'retail-trade-scanner'),
        'url' => home_url('/contact/'),
        'icon' => '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>'
      ]
    ];

    // Get current page URL for active state
    $current_url = home_url(add_query_arg(array()));
    
    foreach ($nav_items as $item) :
      $is_active = (strpos($current_url, $item['url']) !== false) ? 'active' : '';
    ?>
      <div class="nav-item">
        <a href="<?php echo esc_url($item['url']); ?>" class="nav-link <?php echo $is_active; ?>">
          <span class="nav-icon"><?php echo $item['icon']; ?></span>
          <span class="nav-text"><?php echo esc_html($item['title']); ?></span>
        </a>
      </div>
    <?php endforeach; ?>
  </div>
</nav>

<!-- Modern Header -->
<header class="site-header" role="banner">
  <div class="header-content">
    <div class="header-left">
      <button class="mobile-sidebar-toggle" id="mobile-sidebar-toggle" aria-label="Toggle Mobile Menu">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      </button>
      
      <h1 class="header-title">
        <?php 
        if (is_front_page()) {
          echo esc_html(get_bloginfo('name'));
        } else {
          echo esc_html(get_the_title());
        }
        ?>
      </h1>
    </div>
    
    <div class="header-right">
      <!-- Home Button -->
      <a href="<?php echo esc_url(home_url('/')); ?>" class="home-btn" aria-label="Go to Home">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
          <polyline points="9,22 9,12 15,12 15,22"></polyline>
        </svg>
      </a>
      
      <!-- Sign In/Out or Upgrade Button -->
      <?php if (is_user_logged_in()) : ?>
        <a href="<?php echo wp_logout_url(home_url()); ?>" class="auth-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16,17 21,12 16,7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
          <?php esc_html_e('Sign Out', 'retail-trade-scanner'); ?>
        </a>
      <?php else : ?>
        <a href="<?php echo wp_login_url(); ?>" class="auth-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
            <polyline points="10,17 15,12 10,7"></polyline>
            <line x1="15" y1="12" x2="3" y2="12"></line>
          </svg>
          <?php esc_html_e('Sign In', 'retail-trade-scanner'); ?>
        </a>
      <?php endif; ?>
      
      <!-- Upgrade Button (for premium features) -->
      <a href="<?php echo esc_url(home_url('/upgrade/')); ?>" class="auth-btn" style="background: var(--accent);">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="13,2 3,14 12,14 11,22 21,10 12,10"></polygon>
        </svg>
        <?php esc_html_e('Upgrade', 'retail-trade-scanner'); ?>
      </a>
    </div>
  </div>
</header>

<script>
(function() {
  'use strict';
  
  // Sidebar functionality
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');
  const sidebarOverlay = document.getElementById('sidebar-overlay');
  const body = document.body;
  
  // Check if sidebar should be expanded by default (desktop)
  const isDesktop = window.innerWidth > 768;
  const savedState = localStorage.getItem('sidebar-expanded');
  const shouldExpand = isDesktop && (savedState === null || savedState === 'true');
  
  if (shouldExpand) {
    sidebar.classList.add('expanded');
    body.classList.add('sidebar-expanded');
  }
  
  // Desktop sidebar toggle
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function() {
      const isExpanded = sidebar.classList.contains('expanded');
      
      if (isExpanded) {
        sidebar.classList.remove('expanded');
        body.classList.remove('sidebar-expanded');
        localStorage.setItem('sidebar-expanded', 'false');
      } else {
        sidebar.classList.add('expanded');
        body.classList.add('sidebar-expanded');
        localStorage.setItem('sidebar-expanded', 'true');
      }
    });
  }
  
  // Mobile sidebar toggle
  if (mobileSidebarToggle) {
    mobileSidebarToggle.addEventListener('click', function() {
      sidebar.classList.add('expanded');
      sidebarOverlay.classList.add('active');
      body.style.overflow = 'hidden';
    });
  }
  
  // Close mobile sidebar
  function closeMobileSidebar() {
    if (window.innerWidth <= 768) {
      sidebar.classList.remove('expanded');
      sidebarOverlay.classList.remove('active');
      body.style.overflow = '';
    }
  }
  
  // Overlay click
  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', closeMobileSidebar);
  }
  
  // ESC key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeMobileSidebar();
    }
  });
  
  // Handle window resize
  window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
      // Desktop: restore saved state
      const savedState = localStorage.getItem('sidebar-expanded');
      if (savedState === 'true' || savedState === null) {
        sidebar.classList.add('expanded');
        body.classList.add('sidebar-expanded');
      }
      sidebarOverlay.classList.remove('active');
      body.style.overflow = '';
    } else {
      // Mobile: collapse sidebar
      sidebar.classList.remove('expanded');
      body.classList.remove('sidebar-expanded');
    }
  });
  
  // Set active nav item based on current page
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.nav-link');
  
  navLinks.forEach(function(link) {
    const linkPath = new URL(link.href).pathname;
    if (currentPath === linkPath || (linkPath !== '/' && currentPath.includes(linkPath.replace('/', '')))) {
      link.classList.add('active');
    }
  });
  
  // Smooth animations
  sidebar.style.transition = 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
  body.style.transition = 'padding-left 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
  
})();
</script>