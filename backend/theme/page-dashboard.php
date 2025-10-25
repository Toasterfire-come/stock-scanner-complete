<?php
/**
 * Template Name: Dashboard
 * Dedicated Dashboard Page Template
 */

global $post;
get_header(); ?>

<div class="dashboard-page">
    <div class="container">
        <?php echo do_shortcode('[stock_scanner_dashboard]'); ?>
    </div>
</div>

<?php get_footer(); ?>