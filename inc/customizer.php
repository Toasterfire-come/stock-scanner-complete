<?php
/**
 * WordPress Customizer Integration for Production
 * @package RetailTradeScanner
 */

if (!defined('ABSPATH')) { exit; }

/**
 * Theme Customizer class
 */
class RTS_Customizer {
    
    public function __construct() {
        add_action('customize_register', [$this, 'register_customizer_settings']);
        add_action('customize_preview_init', [$this, 'customize_preview_js']);
        add_action('wp_head', [$this, 'output_customizer_css']);
    }
    
    /**
     * Register customizer settings
     */
    public function register_customizer_settings($wp_customize) {
        
        // Site Identity Section (extend existing)
        $wp_customize->add_setting('rts_logo_width', [
            'default' => 200,
            'sanitize_callback' => 'absint',
            'transport' => 'postMessage'
        ]);
        
        $wp_customize->add_control('rts_logo_width', [
            'type' => 'range',
            'section' => 'title_tagline',
            'label' => __('Logo Width (px)', 'retail-trade-scanner'),
            'input_attrs' => [
                'min' => 100,
                'max' => 400,
                'step' => 10
            ]
        ]);
        
        // Colors Section (extend existing)
        $wp_customize->add_section('rts_colors', [
            'title' => __('Theme Colors', 'retail-trade-scanner'),
            'priority' => 40,
            'description' => __('Customize the color scheme of your theme', 'retail-trade-scanner')
        ]);
        
        // Primary Color
        $wp_customize->add_setting('rts_primary_color', [
            'default' => '#374a67',
            'sanitize_callback' => 'sanitize_hex_color',
            'transport' => 'postMessage'
        ]);
        
        $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'rts_primary_color', [
            'label' => __('Primary Color', 'retail-trade-scanner'),
            'section' => 'rts_colors'
        ]));
        
        // Accent Color
        $wp_customize->add_setting('rts_accent_color', [
            'default' => '#e15554',
            'sanitize_callback' => 'sanitize_hex_color',
            'transport' => 'postMessage'
        ]);
        
        $wp_customize->add_control(new WP_Customize_Color_Control($wp_customize, 'rts_accent_color', [
            'label' => __('Accent Color', 'retail-trade-scanner'),
            'section' => 'rts_colors'
        ]));
        
        // Typography Section
        $wp_customize->add_section('rts_typography', [
            'title' => __('Typography', 'retail-trade-scanner'),
            'priority' => 50,
            'description' => __('Customize fonts and typography settings', 'retail-trade-scanner')
        ]);
        
        // Heading Font
        $wp_customize->add_setting('rts_heading_font', [
            'default' => 'Inter',
            'sanitize_callback' => 'sanitize_text_field'
        ]);
        
        $wp_customize->add_control('rts_heading_font', [
            'type' => 'select',
            'section' => 'rts_typography',
            'label' => __('Heading Font', 'retail-trade-scanner'),
            'choices' => $this->get_google_fonts()
        ]);
        
        // Body Font
        $wp_customize->add_setting('rts_body_font', [
            'default' => 'Inter',
            'sanitize_callback' => 'sanitize_text_field'
        ]);
        
        $wp_customize->add_control('rts_body_font', [
            'type' => 'select',
            'section' => 'rts_typography',
            'label' => __('Body Font', 'retail-trade-scanner'),
            'choices' => $this->get_google_fonts()
        ]);
        
        // Font Size
        $wp_customize->add_setting('rts_base_font_size', [
            'default' => 16,
            'sanitize_callback' => 'absint',
            'transport' => 'postMessage'
        ]);
        
        $wp_customize->add_control('rts_base_font_size', [
            'type' => 'range',
            'section' => 'rts_typography',
            'label' => __('Base Font Size (px)', 'retail-trade-scanner'),
            'input_attrs' => [
                'min' => 14,
                'max' => 20,
                'step' => 1
            ]
        ]);
        
        // Layout Section
        $wp_customize->add_section('rts_layout', [
            'title' => __('Layout Options', 'retail-trade-scanner'),
            'priority' => 60,
            'description' => __('Customize layout and spacing options', 'retail-trade-scanner')
        ]);
        
        // Sidebar Default State
        $wp_customize->add_setting('rts_sidebar_default', [
            'default' => 'expanded',
            'sanitize_callback' => 'sanitize_text_field'
        ]);
        
        $wp_customize->add_control('rts_sidebar_default', [
            'type' => 'radio',
            'section' => 'rts_layout',
            'label' => __('Default Sidebar State', 'retail-trade-scanner'),
            'choices' => [
                'expanded' => __('Expanded', 'retail-trade-scanner'),
                'collapsed' => __('Collapsed', 'retail-trade-scanner')
            ]
        ]);
        
        // Container Width
        $wp_customize->add_setting('rts_container_width', [
            'default' => 1200,
            'sanitize_callback' => 'absint',
            'transport' => 'postMessage'
        ]);
        
        $wp_customize->add_control('rts_container_width', [
            'type' => 'range',
            'section' => 'rts_layout',
            'label' => __('Container Max Width (px)', 'retail-trade-scanner'),
            'input_attrs' => [
                'min' => 960,
                'max' => 1400,
                'step' => 20
            ]
        ]);
        
        // Social Media Section
        $wp_customize->add_section('rts_social', [
            'title' => __('Social Media', 'retail-trade-scanner'),
            'priority' => 70,
            'description' => __('Add your social media profiles', 'retail-trade-scanner')
        ]);
        
        $social_networks = [
            'twitter' => __('Twitter', 'retail-trade-scanner'),
            'linkedin' => __('LinkedIn', 'retail-trade-scanner'),
            'facebook' => __('Facebook', 'retail-trade-scanner'),
            'youtube' => __('YouTube', 'retail-trade-scanner'),
            'github' => __('GitHub', 'retail-trade-scanner')
        ];
        
        foreach ($social_networks as $network => $label) {
            $wp_customize->add_setting("rts_social_{$network}", [
                'default' => '',
                'sanitize_callback' => 'esc_url_raw'
            ]);
            
            $wp_customize->add_control("rts_social_{$network}", [
                'type' => 'url',
                'section' => 'rts_social',
                'label' => $label . ' ' . __('URL', 'retail-trade-scanner')
            ]);
        }
        
        // SEO Section
        $wp_customize->add_section('rts_seo', [
            'title' => __('SEO Settings', 'retail-trade-scanner'),
            'priority' => 80,
            'description' => __('Basic SEO configuration', 'retail-trade-scanner')
        ]);
        
        // Google Analytics ID
        $wp_customize->add_setting('rts_google_analytics_id', [
            'default' => '',
            'sanitize_callback' => 'sanitize_text_field'
        ]);
        
        $wp_customize->add_control('rts_google_analytics_id', [
            'type' => 'text',
            'section' => 'rts_seo',
            'label' => __('Google Analytics ID', 'retail-trade-scanner'),
            'description' => __('Enter your GA4 Measurement ID (e.g., G-XXXXXXXXXX)', 'retail-trade-scanner')
        ]);
        
        // Site Keywords
        $wp_customize->add_setting('rts_site_keywords', [
            'default' => 'stock trading, market analysis, portfolio tracking',
            'sanitize_callback' => 'sanitize_text_field'
        ]);
        
        $wp_customize->add_control('rts_site_keywords', [
            'type' => 'text',
            'section' => 'rts_seo',
            'label' => __('Site Keywords', 'retail-trade-scanner'),
            'description' => __('Comma-separated keywords for your site', 'retail-trade-scanner')
        ]);
        
        // Twitter Handle
        $wp_customize->add_setting('rts_twitter_handle', [
            'default' => '',
            'sanitize_callback' => 'sanitize_text_field'
        ]);
        
        $wp_customize->add_control('rts_twitter_handle', [
            'type' => 'text',
            'section' => 'rts_seo',
            'label' => __('Twitter Handle', 'retail-trade-scanner'),
            'description' => __('Without the @ symbol', 'retail-trade-scanner')
        ]);
        
        // Performance Section
        $wp_customize->add_section('rts_performance', [
            'title' => __('Performance', 'retail-trade-scanner'),
            'priority' => 90,
            'description' => __('Performance optimization settings', 'retail-trade-scanner')
        ]);
        
        // Enable Lazy Loading
        $wp_customize->add_setting('rts_lazy_loading', [
            'default' => true,
            'sanitize_callback' => 'rest_sanitize_boolean'
        ]);
        
        $wp_customize->add_control('rts_lazy_loading', [
            'type' => 'checkbox',
            'section' => 'rts_performance',
            'label' => __('Enable Lazy Loading', 'retail-trade-scanner'),
            'description' => __('Improve page load times by lazy loading images', 'retail-trade-scanner')
        ]);
        
        // Minify CSS/JS
        $wp_customize->add_setting('rts_minify_assets', [
            'default' => false,
            'sanitize_callback' => 'rest_sanitize_boolean'
        ]);
        
        $wp_customize->add_control('rts_minify_assets', [
            'type' => 'checkbox',
            'section' => 'rts_performance',
            'label' => __('Minify CSS/JS', 'retail-trade-scanner'),
            'description' => __('Reduce file sizes for better performance', 'retail-trade-scanner')
        ]);
    }
    
    /**
     * Get Google Fonts list
     */
    private function get_google_fonts() {
        return [
            'Inter' => 'Inter',
            'Roboto' => 'Roboto',
            'Open Sans' => 'Open Sans',
            'Lato' => 'Lato',
            'Montserrat' => 'Montserrat',
            'Poppins' => 'Poppins',
            'Source Sans Pro' => 'Source Sans Pro',
            'Nunito' => 'Nunito',
            'Raleway' => 'Raleway',
            'Playfair Display' => 'Playfair Display'
        ];
    }
    
    /**
     * Enqueue customizer preview JavaScript
     */
    public function customize_preview_js() {
        wp_enqueue_script(
            'rts-customizer-preview',
            get_template_directory_uri() . '/assets/js/customizer-preview.js',
            ['customize-preview'],
            wp_get_theme()->get('Version'),
            true
        );
    }
    
    /**
     * Output customizer CSS
     */
    public function output_customizer_css() {
        $primary_color = get_theme_mod('rts_primary_color', '#374a67');
        $accent_color = get_theme_mod('rts_accent_color', '#e15554');
        $heading_font = get_theme_mod('rts_heading_font', 'Inter');
        $body_font = get_theme_mod('rts_body_font', 'Inter');
        $base_font_size = get_theme_mod('rts_base_font_size', 16);
        $container_width = get_theme_mod('rts_container_width', 1200);
        $logo_width = get_theme_mod('rts_logo_width', 200);
        
        $custom_css = "
        <style type='text/css'>
            :root {
                --primary: {$primary_color};
                --primary-hover: " . $this->adjust_brightness($primary_color, -20) . ";
                --accent: {$accent_color};
                --accent-hover: " . $this->adjust_brightness($accent_color, -20) . ";
            }
            
            body {
                font-family: '{$body_font}', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                font-size: {$base_font_size}px;
            }
            
            h1, h2, h3, h4, h5, h6 {
                font-family: '{$heading_font}', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            }
            
            .container,
            .site-main {
                max-width: {$container_width}px;
            }
            
            .custom-logo {
                max-width: {$logo_width}px;
                height: auto;
            }
        </style>";
        
        // Load Google Fonts if needed
        if ($heading_font !== 'Inter' || $body_font !== 'Inter') {
            $fonts_to_load = array_unique([$heading_font, $body_font]);
            $font_families = implode('|', array_map(function($font) {
                return str_replace(' ', '+', $font) . ':300,400,500,600,700';
            }, $fonts_to_load));
            
            $custom_css .= "\n<link href='https://fonts.googleapis.com/css?family={$font_families}&display=swap' rel='stylesheet'>";
        }
        
        echo $custom_css;
    }
    
    /**
     * Adjust color brightness
     */
    private function adjust_brightness($hex, $percent) {
        $hex = ltrim($hex, '#');
        
        if (strlen($hex) == 3) {
            $hex = $hex[0] . $hex[0] . $hex[1] . $hex[1] . $hex[2] . $hex[2];
        }
        
        $hex = array_map('hexdec', str_split($hex, 2));
        
        foreach ($hex as &$color) {
            $adjustableLimit = $percent < 0 ? $color : 255 - $color;
            $adjustAmount = ceil($adjustableLimit * $percent / 100);
            $color = str_pad(dechex($color + $adjustAmount), 2, '0', STR_PAD_LEFT);
        }
        
        return '#' . implode($hex);
    }
}

// Initialize Customizer
new RTS_Customizer();

/**
 * Save customizer settings to options for performance
 */
function rts_save_customizer_settings() {
    $settings = [
        'primary_color' => get_theme_mod('rts_primary_color', '#374a67'),
        'accent_color' => get_theme_mod('rts_accent_color', '#e15554'),
        'heading_font' => get_theme_mod('rts_heading_font', 'Inter'),
        'body_font' => get_theme_mod('rts_body_font', 'Inter'),
        'base_font_size' => get_theme_mod('rts_base_font_size', 16),
        'container_width' => get_theme_mod('rts_container_width', 1200),
        'sidebar_default' => get_theme_mod('rts_sidebar_default', 'expanded'),
        'google_analytics_id' => get_theme_mod('rts_google_analytics_id', ''),
        'lazy_loading' => get_theme_mod('rts_lazy_loading', true),
        'minify_assets' => get_theme_mod('rts_minify_assets', false)
    ];
    
    update_option('rts_theme_settings', $settings);
}
add_action('customize_save_after', 'rts_save_customizer_settings');

/**
 * Get theme setting with fallback
 */
function rts_get_theme_setting($setting, $default = '') {
    $settings = get_option('rts_theme_settings', []);
    return isset($settings[$setting]) ? $settings[$setting] : get_theme_mod("rts_{$setting}", $default);
}