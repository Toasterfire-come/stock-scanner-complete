<?php
/**
 * Template Name: Endpoint Status
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">
    <a class="hover:underline" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    <span> / </span>
    <span aria-current="page"><?php esc_html_e('Endpoint Status', 'retail-trade-scanner'); ?></span>
  </nav>
  
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php esc_html_e('Endpoint Status', 'retail-trade-scanner'); ?></h1>
    <p class="mt-2 text-muted-foreground max-w-2xl"><?php esc_html_e('Live uptime and latency monitoring for all backend API endpoints', 'retail-trade-scanner'); ?></p>
  </header>

  <section class="py-6">
    <div id="rts-endpoint-status" class="grid gap-2">
      <div class="text-muted-foreground"><?php esc_html_e('Checking endpoints…','retail-trade-scanner'); ?></div>
    </div>
  </section>
</main>

<?php get_footer(); ?>