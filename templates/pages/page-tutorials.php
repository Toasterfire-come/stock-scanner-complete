<?php
/**
 * Template Name: Tutorials
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">
    <a class="hover:underline" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    <span> / </span>
    <span aria-current="page"><?php esc_html_e('Tutorials', 'retail-trade-scanner'); ?></span>
  </nav>
  
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php esc_html_e('Tutorials & Guides', 'retail-trade-scanner'); ?></h1>
    <p class="mt-2 text-muted-foreground max-w-2xl"><?php esc_html_e('Step-by-step guides to help you master the platform and make better trading decisions', 'retail-trade-scanner'); ?></p>
  </header>

  <section class="grid gap-6 lg:grid-cols-3 py-6">
    <div class="lg:col-span-2 grid gap-6">
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Getting Started Guide', 'retail-trade-scanner'),
        'subtitle' => __('Complete beginner\'s tutorial', 'retail-trade-scanner'),
        'content' => '<div class="space-y-3">'
          . '<p>' . __('Learn the basics of using Retail Trade Scanner to discover and analyze stocks. This comprehensive guide covers account setup, navigation, and your first stock scan.', 'retail-trade-scanner') . '</p>'
          . '<ul class="text-sm space-y-1 ml-4">'
          . '<li>• ' . __('Setting up your account and preferences', 'retail-trade-scanner') . '</li>'
          . '<li>• ' . __('Understanding the dashboard and KPIs', 'retail-trade-scanner') . '</li>'
          . '<li>• ' . __('Running your first stock scan', 'retail-trade-scanner') . '</li>'
          . '<li>• ' . __('Reading and interpreting results', 'retail-trade-scanner') . '</li>'
          . '</ul>'
          . '<a href="#" class="inline-flex items-center text-primary hover:underline mt-2">' . __('Read Tutorial →', 'retail-trade-scanner') . '</a>'
          . '</div>',
      ]); ?>

      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Advanced Scanning Techniques', 'retail-trade-scanner'),
        'subtitle' => __('Master the stock scanner', 'retail-trade-scanner'),
        'content' => '<div class="space-y-3">'
          . '<p>' . __('Discover advanced filtering techniques to find high-potential stocks using technical indicators, fundamental metrics, and market patterns.', 'retail-trade-scanner') . '</p>'
          . '<ul class="text-sm space-y-1 ml-4">'
          . '<li>• ' . __('Using multiple filters effectively', 'retail-trade-scanner') . '</li>'
          . '<li>• ' . __('Setting up custom scan presets', 'retail-trade-scanner') . '</li>'
          . '<li>• ' . __('Understanding P/E ratios and market cap filters', 'retail-trade-scanner') . '</li>'
          . '<li>• ' . __('Volume and momentum indicators', 'retail-trade-scanner') . '</li>'
          . '</ul>'
          . '<a href="#" class="inline-flex items-center text-primary hover:underline mt-2">' . __('Read Tutorial →', 'retail-trade-scanner') . '</a>'
          . '</div>',
      ]); ?>

      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Portfolio Management Best Practices', 'retail-trade-scanner'),
        'subtitle' => __('Track and optimize your investments', 'retail-trade-scanner'),
        'content' => '<div class="space-y-3">'
          . '<p>' . __('Learn how to effectively use the portfolio tracking features to monitor performance, manage risk, and make informed decisions about your holdings.', 'retail-trade-scanner') . '</p>'
          . '<ul class="text-sm space-y-1 ml-4">'
          . '<li>• ' . __('Adding and organizing your holdings', 'retail-trade-scanner') . '</li>'
          . '<li>• ' . __('Understanding performance metrics', 'retail-trade-scanner') . '</li>'
          . '<li>• ' . __('Setting up diversification alerts', 'retail-trade-scanner') . '</li>'
          . '<li>• ' . __('Rebalancing strategies', 'retail-trade-scanner') . '</li>'
          . '</ul>'
          . '<a href="#" class="inline-flex items-center text-primary hover:underline mt-2">' . __('Read Tutorial →', 'retail-trade-scanner') . '</a>'
          . '</div>',
      ]); ?>

      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Setting Up Effective Alerts', 'retail-trade-scanner'),
        'subtitle' => __('Never miss important price movements', 'retail-trade-scanner'),
        'content' => '<div class="space-y-3">'
          . '<p>' . __('Master the alert system to stay informed about market movements without constantly monitoring your screens. Learn to set smart, actionable alerts.', 'retail-trade-scanner') . '</p>'
          . '<ul class="text-sm space-y-1 ml-4">'
          . '<li>• ' . __('Choosing the right alert levels', 'retail-trade-scanner') . '</li>'
          . '<li>• ' . __('Setting up breakout alerts', 'retail-trade-scanner') . '</li>'
          . '<li>• ' . __('Managing alert fatigue', 'retail-trade-scanner') . '</li>'
          . '<li>• ' . __('Using alerts for risk management', 'retail-trade-scanner') . '</li>'
          . '</ul>'
          . '<a href="#" class="inline-flex items-center text-primary hover:underline mt-2">' . __('Read Tutorial →', 'retail-trade-scanner') . '</a>'
          . '</div>',
      ]); ?>
    </div>
    
    <aside class="grid gap-6">
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Video Tutorials', 'retail-trade-scanner'),
        'content' => '<div class="space-y-2">'
          . '<a href="#" class="block text-primary hover:underline">' . __('📹 Platform Overview (5 min)', 'retail-trade-scanner') . '</a>'
          . '<a href="#" class="block text-primary hover:underline">' . __('📹 First Stock Scan (8 min)', 'retail-trade-scanner') . '</a>'
          . '<a href="#" class="block text-primary hover:underline">' . __('📹 Portfolio Setup (6 min)', 'retail-trade-scanner') . '</a>'
          . '<a href="#" class="block text-primary hover:underline">' . __('📹 Advanced Filtering (12 min)', 'retail-trade-scanner') . '</a>'
          . '</div>',
      ]); ?>
      
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Quick Reference', 'retail-trade-scanner'),
        'content' => '<div class="space-y-2">'
          . '<a href="' . esc_url(home_url('/api-docs/')) . '" class="block text-primary hover:underline">' . __('📚 API Documentation', 'retail-trade-scanner') . '</a>'
          . '<a href="' . esc_url(home_url('/help/')) . '" class="block text-primary hover:underline">' . __('❓ FAQ & Help Center', 'retail-trade-scanner') . '</a>'
          . '<a href="' . esc_url(home_url('/endpoint-status/')) . '" class="block text-primary hover:underline">' . __('📊 System Status', 'retail-trade-scanner') . '</a>'
          . '<a href="' . esc_url(home_url('/contact/')) . '" class="block text-primary hover:underline">' . __('💬 Contact Support', 'retail-trade-scanner') . '</a>'
          . '</div>',
      ]); ?>
      
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Stay Updated', 'retail-trade-scanner'),
        'content' => '<p class="text-sm mb-3">' . __('Get notified when we publish new tutorials and platform updates.', 'retail-trade-scanner') . '</p>'
          . '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="flex gap-2">'
          . wp_nonce_field('rts_subscribe', 'rts_subscribe_nonce', true, false)
          . '<input type="hidden" name="action" value="rts_subscribe">'
          . '<input class="border rounded px-3 py-2 text-sm flex-1" type="email" name="email" placeholder="' . esc_attr__('Your email', 'retail-trade-scanner') . '" required>'
          . '<button class="rounded-md bg-primary text-primary-foreground px-3 py-2 text-sm" type="submit">' . __('Subscribe', 'retail-trade-scanner') . '</button>'
          . '</form>',
      ]); ?>
    </aside>
  </section>
</main>

<?php get_footer(); ?>