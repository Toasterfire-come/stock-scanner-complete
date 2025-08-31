/**
 * WordPress Customizer Preview JavaScript
 * Live preview for theme customizer settings
 */

(function($) {
    'use strict';
    
    // Primary color changes
    wp.customize('rts_primary_color', function(value) {
        value.bind(function(newval) {
            document.documentElement.style.setProperty('--primary', newval);
            document.documentElement.style.setProperty('--yinmn-blue', newval);
        });
    });
    
    // Accent color changes
    wp.customize('rts_accent_color', function(value) {
        value.bind(function(newval) {
            document.documentElement.style.setProperty('--accent', newval);
            document.documentElement.style.setProperty('--indian-red', newval);
        });
    });
    
    // Font size changes
    wp.customize('rts_font_size', function(value) {
        value.bind(function(newval) {
            document.documentElement.style.fontSize = newval + 'px';
        });
    });
    
    // Container width changes
    wp.customize('rts_container_width', function(value) {
        value.bind(function(newval) {
            var style = document.getElementById('customizer-container-width');
            if (!style) {
                style = document.createElement('style');
                style.id = 'customizer-container-width';
                document.head.appendChild(style);
            }
            style.textContent = '.container, .site-main { max-width: ' + newval + 'px; }';
        });
    });
    
    // Sidebar position changes
    wp.customize('rts_sidebar_position', function(value) {
        value.bind(function(newval) {
            document.body.classList.remove('sidebar-left', 'sidebar-right');
            document.body.classList.add('sidebar-' + newval);
        });
    });
    
    // Site title changes
    wp.customize('blogname', function(value) {
        value.bind(function(newval) {
            $('.site-title, .sidebar-logo').text(newval);
        });
    });
    
    // Site tagline changes
    wp.customize('blogdescription', function(value) {
        value.bind(function(newval) {
            $('.site-description').text(newval);
        });
    });
    
    // Header text color
    wp.customize('header_textcolor', function(value) {
        value.bind(function(newval) {
            if ('blank' === newval) {
                $('.site-title, .site-description').css({
                    'clip': 'rect(1px, 1px, 1px, 1px)',
                    'position': 'absolute'
                });
            } else {
                $('.site-title, .site-description').css({
                    'clip': 'auto',
                    'position': 'relative',
                    'color': newval
                });
            }
        });
    });
    
})(jQuery);