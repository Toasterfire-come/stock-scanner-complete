<?php
/**
 * The template for displaying all pages
 *
 * @package RetailTradeScanner
 */

get_header();
?>

<div class="container">
    <?php while (have_posts()) : the_post(); ?>
        <article <?php post_class('page-content'); ?> id="post-<?php the_ID(); ?>">
            <header class="page-header animate-fade-up">
                <h1 class="page-title"><?php the_title(); ?></h1>
                <?php if (get_the_excerpt()) : ?>
                    <div class="page-description">
                        <?php the_excerpt(); ?>
                    </div>
                <?php endif; ?>
            </header>

            <div class="page-content-wrapper">
                <div class="entry-content animate-scale-in">
                    <?php
                    the_content();

                    wp_link_pages(array(
                        'before' => '<div class="page-links">' . esc_html__('Pages:', 'retail-trade-scanner'),
                        'after'  => '</div>',
                    ));
                    ?>
                </div>

                <?php if (comments_open() || get_comments_number()) : ?>
                    <div class="comments-section">
                        <?php comments_template(); ?>
                    </div>
                <?php endif; ?>
            </div>
        </article>
    <?php endwhile; ?>
</div>

<?php
get_footer();