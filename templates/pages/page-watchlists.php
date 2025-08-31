<?php
/**
 * Template Name: Watchlists (wired)
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">
    <a class="hover:underline" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    <span> / </span>
    <span aria-current="page"><?php esc_html_e('Watchlists', 'retail-trade-scanner'); ?></span>
  </nav>
  
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php esc_html_e('Watchlists', 'retail-trade-scanner'); ?></h1>
    <p class="mt-2 text-muted-foreground max-w-2xl"><?php esc_html_e('Create, manage and monitor your watchlists for stocks you want to track', 'retail-trade-scanner'); ?></p>
  </header>

  <section class="py-6">
    <div class="grid gap-6 lg:grid-cols-3">
      <div class="lg:col-span-2 grid gap-6">
        <h3 class="text-lg font-semibold"><?php esc_html_e('My Watchlist', 'retail-trade-scanner'); ?></h3>
        <div id="rts-watchlist" class="grid gap-2">
          <div class="text-muted-foreground"><?php esc_html_e('Loading watchlist…', 'retail-trade-scanner'); ?></div>
        </div>
      </div>
      <aside class="grid gap-6">
        <div class="card p-3">
          <h4 class="font-semibold mb-2"><?php esc_html_e('Add to Watchlist', 'retail-trade-scanner'); ?></h4>
          <form id="rts-watchlist-add" class="grid gap-2">
            <input class="border rounded px-3 py-2" type="text" name="symbol" placeholder="<?php esc_attr_e('Symbol (e.g., AAPL)', 'retail-trade-scanner'); ?>" required />
            <input class="border rounded px-3 py-2" type="text" name="watchlist_name" placeholder="<?php esc_attr_e('Watchlist name (default: My Watchlist)', 'retail-trade-scanner'); ?>" />
            <input class="border rounded px-3 py-2" type="text" name="notes" placeholder="<?php esc_attr_e('Notes (optional)', 'retail-trade-scanner'); ?>" />
            <input class="border rounded px-3 py-2" type="number" step="0.01" name="alert_price" placeholder="<?php esc_attr_e('Alert price (optional)', 'retail-trade-scanner'); ?>" />
            <button class="rounded-md bg-primary text-primary-foreground px-4 py-2" type="submit"><?php esc_html_e('Add', 'retail-trade-scanner'); ?></button>
          </form>
        </div>
      </aside>
    </div>
  </section>
</main>

<?php get_footer(); ?>