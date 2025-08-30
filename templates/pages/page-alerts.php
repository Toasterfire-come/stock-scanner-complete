<?php
/**
 * Template Name: Alerts (wired)
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">
    <a class="hover:underline" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    <span> / </span>
    <span aria-current="page"><?php esc_html_e('Alerts', 'retail-trade-scanner'); ?></span>
  </nav>
  
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php esc_html_e('Alerts', 'retail-trade-scanner'); ?></h1>
    <p class="mt-2 text-muted-foreground max-w-2xl"><?php esc_html_e('Create and manage price alerts to stay informed about market movements', 'retail-trade-scanner'); ?></p>
  </header>

  <section class="py-6">
    <div class="grid gap-6 lg:grid-cols-3">
      <div class="lg:col-span-2 grid gap-4">
        <h3 class="text-lg font-semibold"><?php esc_html_e('Active Alerts', 'retail-trade-scanner'); ?></h3>
        <div id="rts-alerts-list" class="grid gap-2">
          <div class="text-muted-foreground"><?php esc_html_e('Loading alerts…', 'retail-trade-scanner'); ?></div>
        </div>
      </div>
      <aside class="grid gap-4">
        <div class="card p-3">
          <h4 class="font-semibold mb-2"><?php esc_html_e('Create Alert', 'retail-trade-scanner'); ?></h4>
          <div id="rts-alert-descriptor" class="text-sm text-muted-foreground mb-2"></div>
          <form id="rts-alert-form" class="grid gap-2">
            <input class="border rounded px-3 py-2" type="text" name="ticker" placeholder="<?php esc_attr_e('Ticker (e.g., AAPL)', 'retail-trade-scanner'); ?>" required />
            <input class="border rounded px-3 py-2" type="number" step="0.01" name="target_price" placeholder="<?php esc_attr_e('Target Price', 'retail-trade-scanner'); ?>" required />
            <select class="border rounded px-3 py-2" name="condition" required>
              <option value="above"><?php esc_html_e('Above', 'retail-trade-scanner'); ?></option>
              <option value="below"><?php esc_html_e('Below', 'retail-trade-scanner'); ?></option>
            </select>
            <input class="border rounded px-3 py-2" type="email" name="email" placeholder="<?php esc_attr_e('Your Email', 'retail-trade-scanner'); ?>" required />
            <button class="rounded-md bg-primary text-primary-foreground px-4 py-2" type="submit"><?php esc_html_e('Create', 'retail-trade-scanner'); ?></button>
          </form>
          <div id="rts-alert-msg" class="notice mt-2" aria-live="polite"></div>
          <details class="mt-3">
            <summary class="text-sm text-muted-foreground cursor-pointer"><?php esc_html_e('Show required fields and usage','retail-trade-scanner'); ?></summary>
            <div class="text-xs text-muted-foreground mt-2">
              <div><?php esc_html_e('POST /api/alerts/create/','retail-trade-scanner'); ?></div>
              <div><?php esc_html_e('ticker: string (required)','retail-trade-scanner'); ?></div>
              <div><?php esc_html_e('target_price: number (required)','retail-trade-scanner'); ?></div>
              <div><?php esc_html_e('condition: above|below (required)','retail-trade-scanner'); ?></div>
              <div><?php esc_html_e('email: string (required)','retail-trade-scanner'); ?></div>
            </div>
          </details>
        </div>
      </aside>
    </div>
  </section>
</main>

<?php get_footer(); ?>