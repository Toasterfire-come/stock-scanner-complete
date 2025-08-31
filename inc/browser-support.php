<?php
/**
 * Browser Support & Progressive Enhancement
 * Cross-browser compatibility and progressive enhancement features
 */
if (!defined('ABSPATH')) { exit; }

/**
 * Browser Support Class
 */
class RTS_Browser_Support {
    
    private $supported_browsers;
    private $user_agent;
    private $browser_info;
    
    public function __construct() {
        $this->user_agent = $_SERVER['HTTP_USER_AGENT'] ?? '';
        $this->browser_info = $this->detect_browser();
        
        // Define supported browsers
        $this->supported_browsers = array(
            'chrome' => 80,
            'firefox' => 75,
            'safari' => 13,
            'edge' => 80,
            'opera' => 67,
            'ie' => 11, // Minimum support
        );
        
        add_action('wp_head', array($this, 'add_browser_detection'), 1);
        add_action('wp_head', array($this, 'add_polyfills'), 2);
        add_action('wp_enqueue_scripts', array($this, 'enqueue_browser_specific_assets'));
        add_action('wp_footer', array($this, 'add_browser_upgrade_notice'), 999);
        
        // Progressive enhancement
        add_action('wp_footer', array($this, 'add_progressive_enhancement'));
        
        // Feature detection
        add_action('wp_head', array($this, 'add_feature_detection'));
        
        // CSS custom properties fallbacks
        add_action('wp_head', array($this, 'add_css_fallbacks'));
    }
    
    /**
     * Detect browser and version
     */
    private function detect_browser() {
        $browser = array(
            'name' => 'unknown',
            'version' => 0,
            'is_mobile' => false,
            'is_tablet' => false,
            'supports_webp' => false,
            'supports_avif' => false,
        );
        
        $ua = $this->user_agent;
        
        // Mobile detection
        $browser['is_mobile'] = wp_is_mobile();
        $browser['is_tablet'] = preg_match('/(tablet|ipad|playbook)|(android(?!.*(mobi|opera mini)))/i', $ua);
        
        // Browser detection
        if (preg_match('/Chrome\/(\d+)/', $ua, $matches)) {
            $browser['name'] = 'chrome';
            $browser['version'] = intval($matches[1]);
        } elseif (preg_match('/Firefox\/(\d+)/', $ua, $matches)) {
            $browser['name'] = 'firefox';
            $browser['version'] = intval($matches[1]);
        } elseif (preg_match('/Safari\/(\d+)/', $ua, $matches) && !preg_match('/Chrome/', $ua)) {
            $browser['name'] = 'safari';
            // Safari version detection is complex, use a simplified approach
            if (preg_match('/Version\/(\d+)/', $ua, $version_matches)) {
                $browser['version'] = intval($version_matches[1]);
            }
        } elseif (preg_match('/Edge\/(\d+)/', $ua, $matches)) {
            $browser['name'] = 'edge';
            $browser['version'] = intval($matches[1]);
        } elseif (preg_match('/OPR\/(\d+)/', $ua, $matches)) {
            $browser['name'] = 'opera';
            $browser['version'] = intval($matches[1]);
        } elseif (preg_match('/MSIE (\d+)/', $ua, $matches) || preg_match('/Trident.*rv:(\d+)/', $ua, $matches)) {
            $browser['name'] = 'ie';
            $browser['version'] = intval($matches[1]);
        }
        
        // Feature support detection
        $browser['supports_webp'] = $this->supports_webp();
        $browser['supports_avif'] = $this->supports_avif();
        
        return $browser;
    }
    
    /**
     * Check WebP support
     */
    private function supports_webp() {
        return isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'image/webp') !== false;
    }
    
    /**
     * Check AVIF support
     */
    private function supports_avif() {
        return isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'image/avif') !== false;
    }
    
    /**
     * Add browser detection to head
     */
    public function add_browser_detection() {
        $browser = $this->browser_info;
        
        // Add browser classes to html element
        ?>
        <script>
        (function() {
            var html = document.documentElement;
            var browser = <?php echo json_encode($browser); ?>;
            
            // Add browser classes
            html.className += ' browser-' + browser.name;
            html.className += ' browser-version-' + browser.version;
            
            if (browser.is_mobile) {
                html.className += ' is-mobile';
            }
            
            if (browser.is_tablet) {
                html.className += ' is-tablet';
            }
            
            // Feature detection classes
            if (browser.supports_webp) {
                html.className += ' supports-webp';
            } else {
                html.className += ' no-webp';
            }
            
            if (browser.supports_avif) {
                html.className += ' supports-avif';
            } else {
                html.className += ' no-avif';
            }
            
            // Touch support
            if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
                html.className += ' touch';
            } else {
                html.className += ' no-touch';
            }
            
            // Retina display
            if (window.devicePixelRatio && window.devicePixelRatio > 1) {
                html.className += ' retina';
            }
        })();
        </script>
        <?php
    }
    
    /**
     * Add polyfills for older browsers
     */
    public function add_polyfills() {
        $browser = $this->browser_info;
        
        // IE11 and older browsers need polyfills
        if ($browser['name'] === 'ie' || 
            ($browser['name'] === 'chrome' && $browser['version'] < 60) ||
            ($browser['name'] === 'firefox' && $browser['version'] < 55) ||
            ($browser['name'] === 'safari' && $browser['version'] < 10)) {
            
            ?>
            <!-- Polyfills for older browsers -->
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6,Array.prototype.includes,CustomEvent,Element.prototype.closest,Element.prototype.matches,fetch,Promise,IntersectionObserver"></script>
            
            <script>
            // CSS Custom Properties polyfill for IE11
            if (!window.CSS || !CSS.supports || !CSS.supports('color', 'var(--fake-var)')) {
                var link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = 'https://cdn.jsdelivr.net/npm/css-vars-ponyfill@2/dist/css-vars-ponyfill.min.css';
                document.head.appendChild(link);
                
                var script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/css-vars-ponyfill@2/dist/css-vars-ponyfill.min.js';
                script.onload = function() {
                    cssVars({
                        include: 'style,link[rel="stylesheet"]',
                        onlyLegacy: true,
                        watch: true
                    });
                };
                document.head.appendChild(script);
            }
            
            // Object.assign polyfill for IE11
            if (typeof Object.assign !== 'function') {
                Object.assign = function(target) {
                    'use strict';
                    if (target == null) {
                        throw new TypeError('Cannot convert undefined or null to object');
                    }
                    
                    var to = Object(target);
                    
                    for (var index = 1; index < arguments.length; index++) {
                        var nextSource = arguments[index];
                        
                        if (nextSource != null) {
                            for (var nextKey in nextSource) {
                                if (Object.prototype.hasOwnProperty.call(nextSource, nextKey)) {
                                    to[nextKey] = nextSource[nextKey];
                                }
                            }
                        }
                    }
                    return to;
                };
            }
            
            // Array.from polyfill
            if (!Array.from) {
                Array.from = function(object) {
                    return [].slice.call(object);
                };
            }
            
            // NodeList.forEach polyfill for IE11
            if (window.NodeList && !NodeList.prototype.forEach) {
                NodeList.prototype.forEach = Array.prototype.forEach;
            }
            </script>
            <?php
        }
        
        // Add Intersection Observer polyfill for older browsers
        if ($this->needs_intersection_observer_polyfill()) {
            ?>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=IntersectionObserver"></script>
            <?php
        }
    }
    
    /**
     * Check if Intersection Observer polyfill is needed
     */
    private function needs_intersection_observer_polyfill() {
        $browser = $this->browser_info;
        
        return (
            $browser['name'] === 'ie' ||
            ($browser['name'] === 'safari' && $browser['version'] < 12) ||
            ($browser['name'] === 'chrome' && $browser['version'] < 51) ||
            ($browser['name'] === 'firefox' && $browser['version'] < 55)
        );
    }
    
    /**
     * Enqueue browser-specific assets
     */
    public function enqueue_browser_specific_assets() {
        $browser = $this->browser_info;
        
        // IE11 specific styles
        if ($browser['name'] === 'ie') {
            wp_enqueue_style('rts-ie11', get_template_directory_uri() . '/assets/css/ie11.css', array(), wp_get_theme()->get('Version'));
        }
        
        // Safari specific fixes
        if ($browser['name'] === 'safari') {
            wp_add_inline_style('rts-style', '
                /* Safari fixes */
                .sidebar {
                    -webkit-backdrop-filter: blur(12px);
                }
                
                input, textarea, select {
                    -webkit-appearance: none;
                    border-radius: 0;
                }
                
                button {
                    -webkit-appearance: none;
                }
            ');
        }
        
        // Firefox specific fixes
        if ($browser['name'] === 'firefox') {
            wp_add_inline_style('rts-style', '
                /* Firefox fixes */
                .sidebar {
                    scrollbar-width: thin;
                    scrollbar-color: var(--davys-gray) transparent;
                }
                
                input[type="number"] {
                    -moz-appearance: textfield;
                }
                
                input[type="number"]::-webkit-outer-spin-button,
                input[type="number"]::-webkit-inner-spin-button {
                    -webkit-appearance: none;
                    margin: 0;
                }
            ');
        }
        
        // Chrome specific optimizations
        if ($browser['name'] === 'chrome') {
            wp_add_inline_style('rts-style', '
                /* Chrome optimizations */
                .sidebar {
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                }
                
                body {
                    text-rendering: optimizeLegibility;
                }
            ');
        }
        
        // Mobile specific styles
        if ($browser['is_mobile']) {
            wp_add_inline_style('rts-style', '
                /* Mobile optimizations */
                body {
                    -webkit-text-size-adjust: 100%;
                    -ms-text-size-adjust: 100%;
                }
                
                input, textarea, select {
                    font-size: 16px; /* Prevent zoom on iOS */
                }
                
                .sidebar {
                    -webkit-overflow-scrolling: touch;
                }
            ');
        }
    }
    
    /**
     * Add browser upgrade notice
     */
    public function add_browser_upgrade_notice() {
        $browser = $this->browser_info;
        
        // Show upgrade notice for unsupported browsers
        if ($this->is_unsupported_browser()) {
            ?>
            <div id="browser-upgrade-notice" style="
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: #e15554;
                color: white;
                padding: 12px;
                text-align: center;
                z-index: 10000;
                font-size: 14px;
                line-height: 1.4;
            ">
                <p style="margin: 0;">
                    <?php 
                    printf(
                        esc_html__('You are using an outdated browser (%s %d). Please upgrade your browser for the best experience.', 'retail-trade-scanner'),
                        ucfirst($browser['name']),
                        $browser['version']
                    ); 
                    ?>
                    <a href="https://browsehappy.com/" target="_blank" style="color: white; text-decoration: underline;">
                        <?php esc_html_e('Upgrade Now', 'retail-trade-scanner'); ?>
                    </a>
                    <button onclick="this.parentNode.parentNode.style.display='none'" style="
                        background: none;
                        border: none;
                        color: white;
                        font-size: 18px;
                        margin-left: 15px;
                        cursor: pointer;
                        padding: 0;
                    ">&times;</button>
                </p>
            </div>
            
            <script>
            // Adjust body padding to account for notice
            document.body.style.paddingTop = (document.getElementById('browser-upgrade-notice').offsetHeight) + 'px';
            </script>
            <?php
        }
    }
    
    /**
     * Check if browser is unsupported
     */
    private function is_unsupported_browser() {
        $browser = $this->browser_info;
        
        if (!isset($this->supported_browsers[$browser['name']])) {
            return true;
        }
        
        return $browser['version'] < $this->supported_browsers[$browser['name']];
    }
    
    /**
     * Add progressive enhancement features
     */
    public function add_progressive_enhancement() {
        ?>
        <script>
        (function() {
            'use strict';
            
            // Progressive enhancement for modern browsers
            if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                    // Service worker registration placeholder
                    console.log('Service Worker ready for implementation');
                });
            }
            
            // Enhanced functionality for modern browsers
            if ('IntersectionObserver' in window) {
                // Lazy loading improvements
                var lazyImages = document.querySelectorAll('img[loading="lazy"]');
                if (lazyImages.length > 0) {
                    var imageObserver = new IntersectionObserver(function(entries) {
                        entries.forEach(function(entry) {
                            if (entry.isIntersecting) {
                                var img = entry.target;
                                img.classList.add('loaded');
                                imageObserver.unobserve(img);
                            }
                        });
                    });
                    
                    lazyImages.forEach(function(img) {
                        imageObserver.observe(img);
                    });
                }
            }
            
            // WebP support enhancement
            if (document.documentElement.classList.contains('supports-webp')) {
                var images = document.querySelectorAll('img[data-webp]');
                images.forEach(function(img) {
                    img.src = img.dataset.webp;
                });
            }
            
            // Touch enhancements
            if (document.documentElement.classList.contains('touch')) {
                // Add touch-specific optimizations
                var cards = document.querySelectorAll('.card, .btn');
                cards.forEach(function(card) {
                    card.addEventListener('touchstart', function() {
                        this.classList.add('touch-active');
                    });
                    
                    card.addEventListener('touchend', function() {
                        var self = this;
                        setTimeout(function() {
                            self.classList.remove('touch-active');
                        }, 150);
                    });
                });
            }
            
            // Reduced motion preference
            if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                var style = document.createElement('style');
                style.textContent = `
                    *, *::before, *::after {
                        animation-duration: 0.01ms !important;
                        animation-iteration-count: 1 !important;
                        transition-duration: 0.01ms !important;
                        scroll-behavior: auto !important;
                    }
                `;
                document.head.appendChild(style);
            }
            
            // High contrast mode support
            if (window.matchMedia && window.matchMedia('(prefers-contrast: high)').matches) {
                document.documentElement.classList.add('high-contrast');
            }
            
            // Connection-aware features
            if ('connection' in navigator) {
                var connection = navigator.connection;
                
                if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                    document.documentElement.classList.add('slow-connection');
                    
                    // Disable non-essential animations on slow connections
                    var style = document.createElement('style');
                    style.textContent = `
                        .slow-connection * {
                            animation: none !important;
                            transition: none !important;
                        }
                    `;
                    document.head.appendChild(style);
                }
            }
            
        })();
        </script>
        <?php
    }
    
    /**
     * Add feature detection
     */
    public function add_feature_detection() {
        ?>
        <script>
        // Modernizr-style feature detection
        (function() {
            var html = document.documentElement;
            var tests = {
                // CSS Features
                'flexbox': function() {
                    return 'flexWrap' in document.createElement('div').style;
                },
                'grid': function() {
                    return 'grid' in document.createElement('div').style;
                },
                'customproperties': function() {
                    return window.CSS && CSS.supports && CSS.supports('color', 'var(--fake-var)');
                },
                'objectfit': function() {
                    return 'objectFit' in document.createElement('div').style;
                },
                
                // JavaScript Features
                'promises': function() {
                    return 'Promise' in window;
                },
                'fetch': function() {
                    return 'fetch' in window;
                },
                'arrow-functions': function() {
                    try {
                        // Arrow functions supported in ES6+
                        return true;
                    } catch(e) {
                        return false;
                    }
                },
                
                // Browser APIs
                'localstorage': function() {
                    try {
                        localStorage.setItem('test', 'test');
                        localStorage.removeItem('test');
                        return true;
                    } catch(e) {
                        return false;
                    }
                },
                'geolocation': function() {
                    return 'geolocation' in navigator;
                },
                'websockets': function() {
                    return 'WebSocket' in window;
                }
            };
            
            // Run tests and add classes
            Object.keys(tests).forEach(function(test) {
                if (tests[test]()) {
                    html.classList.add(test);
                } else {
                    html.classList.add('no-' + test);
                }
            });
        })();
        </script>
        <?php
    }
    
    /**
     * Add CSS fallbacks
     */
    public function add_css_fallbacks() {
        ?>
        <style>
        /* CSS Fallbacks for older browsers */
        
        /* Flexbox fallbacks */
        .no-flexbox .flex {
            display: table;
            width: 100%;
        }
        
        .no-flexbox .flex > * {
            display: table-cell;
            vertical-align: middle;
        }
        
        .no-flexbox .flex-center {
            text-align: center;
        }
        
        /* Grid fallbacks */
        .no-grid .grid {
            display: block;
        }
        
        .no-grid .grid > * {
            display: inline-block;
            vertical-align: top;
            width: 48%;
            margin-right: 2%;
        }
        
        .no-grid .grid-3 > * {
            width: 31.33%;
        }
        
        .no-grid .grid-4 > * {
            width: 23%;
        }
        
        /* Custom properties fallbacks */
        .no-customproperties {
            background: #433e0e; /* fallback for var(--background) */
            color: #c1bdb3; /* fallback for var(--foreground) */
        }
        
        .no-customproperties .btn-primary {
            background: #374a67; /* fallback for var(--primary) */
            color: #ffffff;
        }
        
        .no-customproperties .btn-accent {
            background: #e15554; /* fallback for var(--accent) */
            color: #ffffff;
        }
        
        .no-customproperties .card {
            background: #2a2506; /* fallback for var(--surface) */
            border: 1px solid rgba(193, 189, 179, 0.2);
        }
        
        /* Object-fit fallbacks */
        .no-objectfit img {
            width: 100%;
            height: auto;
        }
        
        /* Browser-specific fixes */
        
        /* Internet Explorer fixes */
        .browser-ie .sidebar {
            position: absolute; /* IE11 doesn't support sticky properly */
        }
        
        .browser-ie .grid {
            display: -ms-grid;
        }
        
        .browser-ie input,
        .browser-ie textarea,
        .browser-ie select {
            border: 1px solid #ccc; /* IE11 needs explicit borders */
        }
        
        /* Safari fixes */
        .browser-safari input[type="search"] {
            -webkit-appearance: none;
        }
        
        .browser-safari .sidebar {
            -webkit-transform: translateZ(0); /* Force hardware acceleration */
        }
        
        /* Touch device optimizations */
        .touch .nav-link {
            padding: 16px 12px; /* Larger touch targets */
        }
        
        .touch .btn {
            min-height: 44px; /* iOS recommended minimum */
            min-width: 44px;
        }
        
        .touch .card:hover {
            transform: none; /* Disable hover effects on touch */
        }
        
        .touch .card.touch-active {
            transform: scale(0.98);
            transition: transform 0.1s ease;
        }
        
        /* High contrast mode */
        .high-contrast {
            filter: contrast(1.5);
        }
        
        .high-contrast .card {
            border: 2px solid currentColor;
        }
        
        .high-contrast .btn {
            border: 2px solid currentColor;
        }
        
        /* Slow connection optimizations */
        .slow-connection img {
            background: #f0f0f0; /* Placeholder while loading */
        }
        
        .slow-connection .card {
            box-shadow: none; /* Remove shadows to improve performance */
        }
        
        /* Print styles */
        @media print {
            .sidebar,
            .site-header,
            .btn,
            .mobile-sidebar-toggle {
                display: none !important;
            }
            
            body {
                padding-left: 0 !important;
                background: white !important;
                color: black !important;
                font-size: 12pt;
                line-height: 1.4;
            }
            
            .site-main {
                padding-top: 0 !important;
                max-width: none !important;
            }
            
            .card {
                border: 1px solid #000 !important;
                break-inside: avoid;
                page-break-inside: avoid;
            }
            
            a[href]:after {
                content: " (" attr(href) ")";
            }
            
            a[href^="#"]:after,
            a[href^="javascript:"]:after {
                content: "";
            }
        }
        
        /* Reduced motion */
        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
        }
        </style>
        <?php
    }
    
    /**
     * Get browser information
     */
    public function get_browser_info() {
        return $this->browser_info;
    }
    
    /**
     * Check if specific feature is supported
     */
    public function supports_feature($feature) {
        switch ($feature) {
            case 'webp':
                return $this->browser_info['supports_webp'];
            case 'avif':
                return $this->browser_info['supports_avif'];
            case 'flexbox':
                return !($this->browser_info['name'] === 'ie' && $this->browser_info['version'] < 11);
            case 'grid':
                return !($this->browser_info['name'] === 'ie');
            case 'custom_properties':
                return !($this->browser_info['name'] === 'ie');
            default:
                return false;
        }
    }
}

// Initialize Browser Support
new RTS_Browser_Support();

/**
 * Browser Support Utility Functions
 */

/**
 * Get optimized image source based on browser support
 */
function rts_get_optimized_image_src($attachment_id, $size = 'medium') {
    $browser_support = new RTS_Browser_Support();
    $browser_info = $browser_support->get_browser_info();
    
    $image_url = wp_get_attachment_image_url($attachment_id, $size);
    
    // Return AVIF if supported
    if ($browser_info['supports_avif']) {
        $avif_url = preg_replace('/\.(jpg|jpeg|png)$/i', '.avif', $image_url);
        if (file_exists(str_replace(home_url(), ABSPATH, $avif_url))) {
            return $avif_url;
        }
    }
    
    // Return WebP if supported
    if ($browser_info['supports_webp']) {
        $webp_url = preg_replace('/\.(jpg|jpeg|png)$/i', '.webp', $image_url);
        if (file_exists(str_replace(home_url(), ABSPATH, $webp_url))) {
            return $webp_url;
        }
    }
    
    return $image_url;
}

/**
 * Output responsive image with fallbacks
 */
function rts_responsive_image($attachment_id, $size = 'medium', $attr = array()) {
    $browser_support = new RTS_Browser_Support();
    $browser_info = $browser_support->get_browser_info();
    
    $image = wp_get_attachment_image_src($attachment_id, $size);
    if (!$image) {
        return '';
    }
    
    $alt = get_post_meta($attachment_id, '_wp_attachment_image_alt', true);
    $title = get_the_title($attachment_id);
    
    $default_attr = array(
        'src' => $image[0],
        'width' => $image[1],
        'height' => $image[2],
        'alt' => $alt ?: $title,
        'loading' => 'lazy',
    );
    
    $attr = array_merge($default_attr, $attr);
    
    // Add WebP source if supported
    $picture_html = '';
    if ($browser_info['supports_webp'] || $browser_info['supports_avif']) {
        $picture_html = '<picture>';
        
        if ($browser_info['supports_avif']) {
            $avif_url = preg_replace('/\.(jpg|jpeg|png)$/i', '.avif', $image[0]);
            $picture_html .= '<source srcset="' . esc_url($avif_url) . '" type="image/avif">';
        }
        
        if ($browser_info['supports_webp']) {
            $webp_url = preg_replace('/\.(jpg|jpeg|png)$/i', '.webp', $image[0]);
            $picture_html .= '<source srcset="' . esc_url($webp_url) . '" type="image/webp">';
        }
    }
    
    // Build img tag
    $img_html = '<img';
    foreach ($attr as $key => $value) {
        $img_html .= ' ' . $key . '="' . esc_attr($value) . '"';
    }
    $img_html .= '>';
    
    if ($picture_html) {
        return $picture_html . $img_html . '</picture>';
    }
    
    return $img_html;
}

/**
 * Check if browser needs polyfill
 */
function rts_needs_polyfill($feature) {
    $browser_support = new RTS_Browser_Support();
    return !$browser_support->supports_feature($feature);
}

/**
 * Add browser-specific CSS class
 */
function rts_browser_body_class($classes) {
    $browser_support = new RTS_Browser_Support();
    $browser_info = $browser_support->get_browser_info();
    
    $classes[] = 'browser-' . $browser_info['name'];
    $classes[] = 'browser-version-' . $browser_info['version'];
    
    if ($browser_info['is_mobile']) {
        $classes[] = 'is-mobile';
    }
    
    if ($browser_info['is_tablet']) {
        $classes[] = 'is-tablet';
    }
    
    return $classes;
}
add_filter('body_class', 'rts_browser_body_class');