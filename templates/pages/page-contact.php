<?php
/**
 * Template Name: Contact
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">
    <a class="hover:underline" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    <span> / </span>
    <span aria-current="page"><?php esc_html_e('Contact', 'retail-trade-scanner'); ?></span>
  </nav>
  
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php esc_html_e('Contact', 'retail-trade-scanner'); ?></h1>
    <p class="mt-2 text-muted-foreground max-w-2xl"><?php esc_html_e('Get in touch with our team for support, feedback, or partnership inquiries', 'retail-trade-scanner'); ?></p>
  </header>

  <section class="grid gap-6 lg:grid-cols-3 py-6">
    <div class="lg:col-span-2">
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Send a Message', 'retail-trade-scanner'),
        'content' => '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="grid gap-3">'
          . wp_nonce_field('rts_contact', 'rts_contact_nonce', true, false)
          . '<input type="hidden" name="action" value="rts_contact">'
          . '<input class="border rounded px-3 py-2" type="text" name="name" placeholder="' . esc_attr__('Full Name', 'retail-trade-scanner') . '" required />'
          . '<input class="border rounded px-3 py-2" type="email" name="email" placeholder="' . esc_attr__('Email Address', 'retail-trade-scanner') . '" required />'
          . '<textarea class="border rounded px-3 py-2" name="message" rows="4" placeholder="' . esc_attr__('Your Message', 'retail-trade-scanner') . '" required></textarea>'
          . '<button class="rounded-md bg-primary text-primary-foreground px-4 py-2" type="submit">' . esc_html__('Send Message', 'retail-trade-scanner') . '</button>'
          . '</form>',
      ]); ?>
      
      <?php if (isset($_GET['contact']) && $_GET['contact'] === 'sent') : ?>
        <div class="notice notice-success mt-4 p-3 rounded-md bg-green-50 border border-green-200">
          <p class="text-green-800"><?php esc_html_e('Thank you! Your message has been sent successfully.', 'retail-trade-scanner'); ?></p>
        </div>
      <?php elseif (isset($_GET['contact']) && $_GET['contact'] === 'error') : ?>
        <div class="notice notice-error mt-4 p-3 rounded-md bg-red-50 border border-red-200">
          <p class="text-red-800"><?php esc_html_e('Sorry, there was an error sending your message. Please try again.', 'retail-trade-scanner'); ?></p>
        </div>
      <?php endif; ?>
    </div>
    
    <aside class="grid gap-6">
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Contact Information', 'retail-trade-scanner'),
        'content' => '<div class="space-y-3">'
          . '<div><strong>' . __('Email:', 'retail-trade-scanner') . '</strong><br>support@retailtradescanner.com</div>'
          . '<div><strong>' . __('Support Hours:', 'retail-trade-scanner') . '</strong><br>' . __('Monday - Friday, 9 AM - 6 PM EST', 'retail-trade-scanner') . '</div>'
          . '<div><strong>' . __('Response Time:', 'retail-trade-scanner') . '</strong><br>' . __('Within 24 hours', 'retail-trade-scanner') . '</div>'
          . '</div>',
      ]); ?>
      
      <?php get_template_part('template-parts/components/card', null, [
        'title' => __('Other Ways to Reach Us', 'retail-trade-scanner'),
        'content' => '<div class="space-y-2">'
          . '<a href="' . esc_url(home_url('/help/')) . '" class="block text-primary hover:underline">' . __('Help Center', 'retail-trade-scanner') . '</a>'
          . '<a href="' . esc_url(home_url('/tutorials/')) . '" class="block text-primary hover:underline">' . __('Tutorials', 'retail-trade-scanner') . '</a>'
          . '<a href="' . esc_url(home_url('/api-docs/')) . '" class="block text-primary hover:underline">' . __('API Documentation', 'retail-trade-scanner') . '</a>'
          . '</div>',
      ]); ?>
    </aside>
  </section>
</main>

<?php get_footer(); ?>