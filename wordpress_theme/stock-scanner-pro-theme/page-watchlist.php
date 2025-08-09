<?php
/**
 * Template Name: Watchlist
 * Dedicated Watchlist Page Template
 */

global $post;
get_header(); ?>

<div class="watchlist-page">
    <div class="container">
        <?php echo do_shortcode('[stock_watchlist_manager]'); ?>
    </div>
</div>

<?php get_footer(); ?>