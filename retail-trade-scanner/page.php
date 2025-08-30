<?php
/**
 * Default Page Template
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
      </header>
      <div class="entry-content">
        <?php the_content(); ?>
      </div>
    </article>
  <?php endwhile; endif; ?>
  <?php if ( is_page_template('page-templates/page-paypal-checkout.php') ) : ?>
    <section class="mt-10">
      <a class="btn btn-primary rounded-md px-3 py-2" href="<?php echo esc_url( home_url('/payment-success/') ); ?>">Proceed to PayPal</a>
    </section>
  <?php endif; ?>
</main>

<?php get_footer(); ?>

