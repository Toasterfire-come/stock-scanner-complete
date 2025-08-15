<?php
/**
 * Functions and definitions
 *
 *
 */
 function zatra_setup() {
	// Add default posts and comments RSS feed links to head.
	add_theme_support( 'automatic-feed-links' );

	// Let WordPress manage the document title.
	add_theme_support( 'title-tag' );

	// Enable support for Post Thumbnails.
	add_theme_support( 'post-thumbnails' );
    
    // Make theme available for translation.
	load_theme_textdomain( 'zatra' );

	// Admin editor styles.
	add_theme_support( 'editor-styles' );

	// Switch default core markup for different forms to output valid HTML5.
	add_theme_support( 'html5', array( 'comment-form', 'comment-list' ) );

	// Add support for responsive embeds.
	add_theme_support( 'responsive-embeds' );

	// Add theme support for selective refresh for widgets.
	add_theme_support( 'customize-selective-refresh-widgets' );

	// Enable block styles.
	add_theme_support( 'wp-block-styles' );

	// Enqueue editor styles.
	add_editor_style();
}
add_action( 'after_setup_theme', 'zatra_setup' );

/**
 * Enqueue scripts and styles.
 *
 * @since 1.0.0
 */
function zatra_scripts() {
	wp_enqueue_style('font-awesome', get_template_directory_uri() . '/assets/framework/font-awesome-6/css/all.css', array());
	wp_enqueue_style('font-awesome-min', get_template_directory_uri() . '/assets/framework/font-awesome-6/css/all.min.css', array());
	wp_enqueue_style( 'zatra-style', get_stylesheet_uri(), array());
}
add_action( 'wp_enqueue_scripts', 'zatra_scripts' );

/**
 * Register block patterns category.
 *
 * @since 1.0.0
 */
function zatra_register_block_patterns_category() {
	register_block_pattern_category(
		'zatra',
		array(
			'label' => esc_html__( 'Zatra', 'zatra' ),
		)
	);
}
add_action( 'init', 'zatra_register_block_patterns_category', 9 );
