<?php
/**
 * Default Page Template
 * Ensures each page displays its own content
 */

get_header(); ?>

<div class="page-wrapper">
    <div class="container">
        <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
            <header class="page-header">
                <h1 class="page-title"><?php the_title(); ?></h1>
            </header>
            <div class="page-content">
                <?php the_content(); ?>
            </div>
        <?php endwhile; endif; ?>
    </div>
</div>

<?php get_footer(); ?>