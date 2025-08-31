<?php
/**
 * Template Name: Portfolio (wired)
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">
    <a class="hover:underline" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    <span> / </span>
    <span aria-current="page"><?php esc_html_e('Portfolio', 'retail-trade-scanner'); ?></span>
  </nav>
  
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php esc_html_e('Portfolio', 'retail-trade-scanner'); ?></h1>
    <p class="mt-2 text-muted-foreground max-w-2xl"><?php esc_html_e('Track positions and performance across your investment portfolio', 'retail-trade-scanner'); ?></p>
  </header>

  <section class="py-6">
    <div class="grid gap-6 lg:grid-cols-3">
      <div class="lg:col-span-2">
        <h3 class="text-lg font-semibold mb-2"><?php esc_html_e('Holdings', 'retail-trade-scanner'); ?></h3>
        <div id="rts-portfolio" class="grid gap-2">
          <div class="text-muted-foreground"><?php esc_html_e('Loading holdings…', 'retail-trade-scanner'); ?></div>
        </div>
      </div>
      <aside>
        <div class="card p-3">
          <h4 class="font-semibold mb-2"><?php esc_html_e('Add Holding', 'retail-trade-scanner'); ?></h4>
          <form id="rts-portfolio-add" class="grid gap-2">
            <input class="border rounded px-3 py-2" type="text" name="symbol" placeholder="<?php esc_attr_e('Symbol (e.g., AAPL)', 'retail-trade-scanner'); ?>" required />
            <input class="border rounded px-3 py-2" type="number" step="0.0001" name="shares" placeholder="<?php esc_attr_e('Shares', 'retail-trade-scanner'); ?>" required />
            <input class="border rounded px-3 py-2" type="number" step="0.01" name="avg_cost" placeholder="<?php esc_attr_e('Average Cost', 'retail-trade-scanner'); ?>" required />
            <input class="border rounded px-3 py-2" type="text" name="portfolio_name" placeholder="<?php esc_attr_e('Portfolio name (default: My Portfolio)', 'retail-trade-scanner'); ?>" />
            <button class="rounded-md bg-primary text-primary-foreground px-4 py-2" type="submit"><?php esc_html_e('Add', 'retail-trade-scanner'); ?></button>
          </form>
        </div>
      </aside>
    </div>
  </section>
</main>

<?php get_footer(); ?>