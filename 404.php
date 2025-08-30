<?php
/**
 * 404 Not Found Template
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-16 text-center">
  <h1 class="text-3xl font-bold mb-2"><?php esc_html_e('Page not found', 'retail-trade-scanner'); ?></h1>
  <p class="text-muted-foreground mb-6"><?php esc_html_e('The page you are looking for doesn’t exist or was moved.', 'retail-trade-scanner'); ?></p>
  <div class="max-w-md mx-auto mb-6"><?php get_search_form(); ?></div>
  <a class="rounded-md bg-primary text-primary-foreground px-4 py-2" href="<?php echo esc_url( home_url('/') ); ?>"><?php esc_html_e('Back to home', 'retail-trade-scanner'); ?></a>
</main>

<?php get_footer(); ?>

