<?php
/**
 * Template Name: News (wired)
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">
    <a class="hover:underline" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    <span> / </span>
    <span aria-current="page"><?php esc_html_e('News', 'retail-trade-scanner'); ?></span>
  </nav>
  
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php esc_html_e('News', 'retail-trade-scanner'); ?></h1>
    <p class="mt-2 text-muted-foreground max-w-2xl"><?php esc_html_e('Live market news with sentiment analysis and advanced filters', 'retail-trade-scanner'); ?></p>
  </header>

  <section class="py-6">
    <form id="rts-news-filters" class="grid gap-3 md:grid-cols-4">
      <input class="border rounded px-3 py-2" type="number" name="limit" placeholder="<?php esc_attr_e('Limit (<=50)','retail-trade-scanner'); ?>" />
      <select class="border rounded px-3 py-2" name="sentiment">
        <option value=""><?php esc_html_e('Any Sentiment','retail-trade-scanner'); ?></option>
        <option value="positive"><?php esc_html_e('Positive','retail-trade-scanner'); ?></option>
        <option value="negative"><?php esc_html_e('Negative','retail-trade-scanner'); ?></option>
        <option value="neutral"><?php esc_html_e('Neutral','retail-trade-scanner'); ?></option>
      </select>
      <input class="border rounded px-3 py-2" type="text" name="ticker" placeholder="<?php esc_attr_e('Ticker (optional)','retail-trade-scanner'); ?>" />
      <button class="rounded-md bg-primary text-primary-foreground px-4 py-2" type="submit"><?php esc_html_e('Apply','retail-trade-scanner'); ?></button>
    </form>
    
    <div id="rts-news" class="grid gap-3 mt-6">
      <div class="text-muted-foreground"><?php esc_html_e('Loading news…','retail-trade-scanner'); ?></div>
    </div>
  </section>
</main>

<?php get_footer(); ?>