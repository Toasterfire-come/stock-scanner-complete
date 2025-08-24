<?php
/**
 * Stock Scanner Pro Theme Header Template v3.0.0
 * ULTRA-MODERN ENHANCED HEADER with Glassmorphism Effects
 */
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>><head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="format-detection" content="telephone=no">
<meta name="theme-color" content="#667eea">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="dns-prefetch" href="//fonts.googleapis.com">
<?php wp_head(); ?>
<?php
$schema_data = array(
  '@context' => 'https://schema.org',
  '@type' => 'WebApplication',
  'name' => get_bloginfo('name', 'display'),
  'description' => get_bloginfo('description', 'display'),
  'url' => home_url('/'),
  'applicationCategory' => 'FinanceApplication',
  'operatingSystem' => 'Web Browser',
);
?>
<script type="application/ld+json"><?php echo wp_json_encode($schema_data); ?></script>
<style>
/* Minimal critical styles */
.site-header{position:sticky;top:0;z-index:1020;backdrop-filter:blur(10px);}
.loading-skeleton{background:linear-gradient(90deg,#f0f0f0 25%,#e0e0e0 50%,#f0f0f0 75%);background-size:200% 100%;animation:shimmer 1.5s infinite}
@keyframes shimmer{0%{background-position:-200px 0}100%{background-position:calc(200px + 100%) 0}}
</style>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="skip-link screen-reader-text" href="#main" tabindex="1"><?php _e('Skip to content', 'stock-scanner'); ?></a>
<header class="site-header glass-nav" role="banner" itemscope itemtype="https://schema.org/WPHeader">
  <div class="header-container">
    <div class="site-branding" itemscope itemtype="https://schema.org/Organization">
      <a href="<?php echo esc_url(home_url('/')); ?>" class="logo-link" rel="home" aria-label="<?php echo esc_attr(get_bloginfo('name')); ?> - Home" itemprop="url">
        <div class="logo-container glass-card">
          <img src="<?php echo esc_url(get_template_directory_uri()); ?>/assets/images/logo.png" alt="<?php echo esc_attr(get_bloginfo('name')); ?> Logo" class="logo-image" width="120" height="45" loading="eager" decoding="async" itemprop="logo">
          <div class="brand-text"><span class="logo-text text-gradient" itemprop="name"><?php echo esc_html(get_bloginfo('name')); ?></span><?php $description=get_bloginfo('description','display'); if($description||is_customize_preview()): ?><span class="site-description" itemprop="description"><?php echo esc_html($description); ?></span><?php endif; ?></div>
        </div>
      </a>
    </div>

    <button class="menu-toggle btn-icon glass" aria-controls="primary-menu" aria-expanded="false" aria-label="<?php _e('Toggle navigation menu','stock-scanner'); ?>" data-mobile-menu-toggle>
      <span class="hamburger-line"></span><span class="hamburger-line"></span><span class="hamburger-line"></span>
      <span class="screen-reader-text"><?php _e('Menu','stock-scanner'); ?></span>
    </button>

    <nav class="main-navigation glass-nav" role="navigation" aria-label="<?php _e('Primary Menu','stock-scanner'); ?>" itemscope itemtype="https://schema.org/SiteNavigationElement">
      <?php
      $args = array(
        'theme_location' => 'primary',
        'menu_id'        => 'primary-menu',
        'menu_class'     => 'nav-menu enhanced-nav',
        'container'      => false,
        'fallback_cb'    => 'wp_page_menu',
        'depth'          => 2,
      );
      if (class_exists('Stock_Scanner_Nav_Walker')) {
        $args['walker'] = new Stock_Scanner_Nav_Walker();
      }
      wp_nav_menu($args);
      ?>
    </nav>

    <div class="header-actions">
      <button class="theme-toggle btn-icon glass" aria-label="<?php _e('Toggle dark mode','stock-scanner'); ?>" title="<?php _e('Toggle Theme','stock-scanner'); ?>" data-theme-toggle><span class="theme-icon light-icon">🌙</span><span class="theme-icon dark-icon">☀️</span></button>
      <button class="search-toggle btn-icon glass" aria-label="<?php _e('Toggle search','stock-scanner'); ?>" title="<?php _e('Search','stock-scanner'); ?>" data-search-toggle>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="8"></circle><path d="M21 21l-4.35-4.35"></path></svg>
      </button>
      <?php if (is_user_logged_in()) : $current_user=wp_get_current_user(); $membership_level=get_user_meta($current_user->ID,'membership_level',true)?:'free'; ?>
        <div class="user-info animate-fade-in">
          <span class="membership-badge <?php echo esc_attr($membership_level); ?> glass"><?php echo esc_html(ucfirst($membership_level)); ?></span>
          <div class="user-dropdown"><button class="user-toggle glass" aria-expanded="false" aria-haspopup="true" data-user-menu-toggle><div class="user-avatar"><?php echo get_avatar($current_user->ID,36,'','',array('class'=>'avatar-img')); ?></div><span class="user-name"><?php echo esc_html($current_user->display_name); ?></span><svg class="dropdown-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="6,9 12,15 18,9"></polyline></svg></button>
            <div class="user-menu glass-modal animate-scale-in" role="menu" data-user-menu>
              <a href="<?php echo esc_url(home_url('/dashboard/')); ?>" class="user-menu-item" role="menuitem"><?php _e('Dashboard','stock-scanner'); ?></a>
              <a href="<?php echo esc_url(home_url('/portfolio/')); ?>" class="user-menu-item" role="menuitem"><?php _e('Portfolio','stock-scanner'); ?></a>
              <a href="<?php echo esc_url(home_url('/watchlist/')); ?>" class="user-menu-item" role="menuitem"><?php _e('Watchlist','stock-scanner'); ?></a>
              <hr class="menu-divider">
              <a href="<?php echo esc_url(home_url('/account-settings/')); ?>" class="user-menu-item" role="menuitem"><?php _e('Settings','stock-scanner'); ?></a>
              <?php if ($membership_level==='free') : ?><a href="<?php echo esc_url(home_url('/premium-plans/')); ?>" class="user-menu-item premium-upgrade" role="menuitem"><?php _e('Upgrade to Premium','stock-scanner'); ?></a><?php endif; ?>
              <hr class="menu-divider">
              <a href="<?php echo esc_url(wp_logout_url(home_url('/'))); ?>" class="user-menu-item logout" role="menuitem"><?php _e('Logout','stock-scanner'); ?></a>
            </div>
          </div>
        </div>
      <?php else: ?>
        <div class="auth-actions animate-fade-in">
          <a href="<?php echo esc_url(wp_login_url()); ?>" class="btn btn-outline btn-sm glass"><?php _e('Login','stock-scanner'); ?></a>
          <a href="<?php echo esc_url(wp_registration_url()); ?>" class="btn btn-primary btn-sm gradient-primary"><?php _e('Get Started','stock-scanner'); ?></a>
        </div>
      <?php endif; ?>
    </div>
  </div>

  <div class="search-overlay glass-modal" aria-hidden="true" data-search-overlay>
    <div class="search-container glass-card animate-scale-in">
      <form role="search" method="get" class="search-form" action="<?php echo esc_url(home_url('/')); ?>">
        <div class="search-input-group">
          <label for="search-field" class="screen-reader-text"><?php _e('Search for:','stock-scanner'); ?></label>
          <input type="search" id="search-field" class="search-field" placeholder="<?php _e('Search stocks, companies, or articles...','stock-scanner'); ?>" value="<?php echo get_search_query(); ?>" name="s" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" data-advanced-search>
          <button type="submit" class="search-submit gradient-primary" aria-label="<?php _e('Search','stock-scanner'); ?>">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="8"></circle><path d="M21 21l-4.35-4.35"></path></svg>
          </button>
        </div>
        <div class="search-suggestions">
          <div class="popular-searches"><h4><?php _e('Popular Searches','stock-scanner'); ?></h4><div class="search-tags"><a href="?s=AAPL" class="search-tag glass">AAPL</a><a href="?s=TSLA" class="search-tag glass">TSLA</a><a href="?s=GOOGL" class="search-tag glass">GOOGL</a><a href="?s=MSFT" class="search-tag glass">MSFT</a><a href="?s=AMZN" class="search-tag glass">AMZN</a><a href="?s=META" class="search-tag glass">META</a></div></div>
          <div class="live-search-results" data-search-results style="display:none"><h4><?php _e('Search Results','stock-scanner'); ?></h4><div class="results-container"></div></div>
        </div>
      </form>
      <button class="search-close btn-icon glass" aria-label="<?php _e('Close search','stock-scanner'); ?>" data-search-close>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    </div>
  </div>
</header>
<div class="page-loading-bar gradient-primary" aria-hidden="true" data-loading-bar></div>
<main id="main" class="site-main" role="main" itemscope itemtype="https://schema.org/WebPageElement">