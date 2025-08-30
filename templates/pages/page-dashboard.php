<?php
/**
 * Template Name: Dashboard (wired)
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">
    <a class="hover:underline" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    <span> / </span>
    <span aria-current="page"><?php esc_html_e('Dashboard', 'retail-trade-scanner'); ?></span>
  </nav>
  
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php esc_html_e('Dashboard', 'retail-trade-scanner'); ?></h1>
    <p class="mt-2 text-muted-foreground max-w-2xl"><?php esc_html_e('Live KPIs and trending market data', 'retail-trade-scanner'); ?></p>
  </header>

  <section class="py-6">
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3" id="rts-kpis">
      <div class="text-muted-foreground"><?php esc_html_e('Loading KPIs…','retail-trade-scanner'); ?></div>
    </div>
    
    <div class="grid gap-6 md:grid-cols-2 mt-8">
      <div>
        <h3 class="text-lg font-semibold mb-3"><?php esc_html_e('Top Gainers','retail-trade-scanner'); ?></h3>
        <div id="rts-trending-gainers" class="grid gap-2"></div>
      </div>
      <div>
        <h3 class="text-lg font-semibold mb-3"><?php esc_html_e('Most Active','retail-trade-scanner'); ?></h3>
        <div id="rts-trending-active" class="grid gap-2"></div>
      </div>
    </div>
  </section>
</main>

<?php get_footer(); ?>