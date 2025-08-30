<?php
/**
 * Single Post Template
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <?php if ( have_posts() ) : while ( have_posts() ) : the_post(); ?>
    <article id="post-<?php the_ID(); ?>" <?php post_class('prose dark:prose-invert max-w-none'); ?>>
      <header class="mb-6">
        <h1 class="text-3xl font-bold leading-tight"><?php the_title(); ?></h1>
        <div class="mt-2 text-sm text-muted-foreground">
          <time datetime="<?php echo esc_attr( get_the_date('c') ); ?>"><?php echo esc_html( get_the_date() ); ?></time>
          <span>•</span>
          <span><?php echo esc_html( get_the_author() ); ?></span>
        </div>
      </header>
      <div class="entry-content">
        <?php the_content(); ?>
      </div>
      <footer class="mt-8">
        <?php the_tags('<div class="text-sm text-muted-foreground">', ', ', '</div>'); ?>
      </footer>
    </article>
    <?php comments_template(); ?>
  <?php endwhile; endif; ?>
</main>

<?php get_footer(); ?>

