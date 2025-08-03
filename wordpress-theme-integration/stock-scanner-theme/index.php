<?php
/**
 * The main template file
 */

get_header(); ?>

<div id="primary" class="content-area">
    <main id="main" class="site-main">
        
        <?php if (have_posts()) : ?>
            
            <header class="page-header">
                <h1 class="page-title"><?php bloginfo('name'); ?></h1>
                <p class="page-description"><?php bloginfo('description'); ?></p>
            </header>
            
            <!-- Stock Ticker Section -->
            <section class="stock-ticker-section">
                <h2>Live Stock Ticker</h2>
                <?php echo do_shortcode('[stock_ticker limit="10" category="gainers"]'); ?>
            </section>
            
            <!-- Stock News Section -->
            <section class="stock-news-section">
                <h2>Latest Market News</h2>
                <?php echo do_shortcode('[stock_news limit="5" show_sentiment="true"]'); ?>
            </section>
            
            <!-- Regular Posts -->
            <div class="posts-grid">
                <?php while (have_posts()) : the_post(); ?>
                    <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                        <header class="entry-header">
                            <?php the_title(sprintf('<h2 class="entry-title"><a href="%s" rel="bookmark">', esc_url(get_permalink())), '</a></h2>'); ?>
                        </header>
                        
                        <div class="entry-content">
                            <?php the_excerpt(); ?>
                        </div>
                        
                        <footer class="entry-footer">
                            <span class="posted-on">
                                <?php echo get_the_date(); ?>
                            </span>
                        </footer>
                    </article>
                <?php endwhile; ?>
            </div>
            
            <?php the_posts_navigation(); ?>
            
        <?php else : ?>
            <p><?php _e('No posts found.', 'stock-scanner'); ?></p>
        <?php endif; ?>
        
    </main>
</div>

<?php get_sidebar(); ?>
<?php get_footer(); ?>