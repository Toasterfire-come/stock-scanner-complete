<?php
/**
 * Template Name: Help
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">
    <a class="hover:underline" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    <span> / </span>
    <span aria-current="page"><?php esc_html_e('Help', 'retail-trade-scanner'); ?></span>
  </nav>
  
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php esc_html_e('Help Center', 'retail-trade-scanner'); ?></h1>
    <p class="mt-2 text-muted-foreground max-w-2xl"><?php esc_html_e('Find answers to common questions and get the support you need', 'retail-trade-scanner'); ?></p>
  </header>

  <section class="grid gap-6 lg:grid-cols-3 py-6">
    <div class="lg:col-span-2 grid gap-6">
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Frequently Asked Questions', 'retail-trade-scanner'),
        'content' => '<div class="space-y-4">'
          . '<details class="group">'
          . '<summary class="font-medium cursor-pointer list-none flex items-center justify-between">'
          . __('How do I get started with the scanner?', 'retail-trade-scanner')
          . '<span class="ml-2 group-open:rotate-180 transition-transform">▼</span></summary>'
          . '<div class="mt-2 text-sm text-muted-foreground pl-4">'
          . __('Navigate to the Scanner page and use the filters to search for stocks based on your criteria. You can filter by category, exchange, price range, volume, and more.', 'retail-trade-scanner')
          . '</div></details>'
          
          . '<details class="group">'
          . '<summary class="font-medium cursor-pointer list-none flex items-center justify-between">'
          . __('How do watchlists work?', 'retail-trade-scanner')
          . '<span class="ml-2 group-open:rotate-180 transition-transform">▼</span></summary>'
          . '<div class="mt-2 text-sm text-muted-foreground pl-4">'
          . __('Watchlists allow you to track stocks you\'re interested in. Add stocks by symbol and optionally set alert prices to get notified when they reach your target.', 'retail-trade-scanner')
          . '</div></details>'
          
          . '<details class="group">'
          . '<summary class="font-medium cursor-pointer list-none flex items-center justify-between">'
          . __('Can I track my portfolio performance?', 'retail-trade-scanner')
          . '<span class="ml-2 group-open:rotate-180 transition-transform">▼</span></summary>'
          . '<div class="mt-2 text-sm text-muted-foreground pl-4">'
          . __('Yes! Use the Portfolio section to add your holdings with purchase prices and quantities. The system will calculate your current performance automatically.', 'retail-trade-scanner')
          . '</div></details>'
          
          . '<details class="group">'
          . '<summary class="font-medium cursor-pointer list-none flex items-center justify-between">'
          . __('How do price alerts work?', 'retail-trade-scanner')
          . '<span class="ml-2 group-open:rotate-180 transition-transform">▼</span></summary>'
          . '<div class="mt-2 text-sm text-muted-foreground pl-4">'
          . __('Set up alerts for stocks to get email notifications when they reach your target price. You can set alerts for prices above or below current levels.', 'retail-trade-scanner')
          . '</div></details>'
          
          . '</div>',
      ]); ?>
    </div>
    
    <aside class="grid gap-6">
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Quick Links', 'retail-trade-scanner'),
        'content' => '<div class="space-y-2">'
          . '<a href="' . esc_url(home_url('/tutorials/')) . '" class="block text-primary hover:underline">' . __('📖 Tutorials & Guides', 'retail-trade-scanner') . '</a>'
          . '<a href="' . esc_url(home_url('/api-docs/')) . '" class="block text-primary hover:underline">' . __('🔧 API Documentation', 'retail-trade-scanner') . '</a>'
          . '<a href="' . esc_url(home_url('/endpoint-status/')) . '" class="block text-primary hover:underline">' . __('📊 System Status', 'retail-trade-scanner') . '</a>'
          . '<a href="' . esc_url(home_url('/contact/')) . '" class="block text-primary hover:underline">' . __('💬 Contact Support', 'retail-trade-scanner') . '</a>'
          . '</div>',
      ]); ?>
      
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Need More Help?', 'retail-trade-scanner'),
        'content' => '<p class="text-sm">' . __('Can\'t find what you\'re looking for? Our support team is here to help.', 'retail-trade-scanner') . '</p>'
          . '<a href="' . esc_url(home_url('/contact/')) . '" class="inline-flex items-center justify-center px-4 py-2 mt-3 rounded-md bg-primary text-primary-foreground hover:shadow-sm transition">'
          . __('Contact Support', 'retail-trade-scanner')
          . '</a>',
      ]); ?>
    </aside>
  </section>
</main>

<?php get_footer(); ?>