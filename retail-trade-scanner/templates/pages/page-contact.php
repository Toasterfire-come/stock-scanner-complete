<?php
/**
 * Template Name: Contact
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();

$layout_args = array(
  'page_title'       => __('Contact', 'retail-trade-scanner'),
  'page_description' => __('Get in touch with our team.', 'retail-trade-scanner'),
  'page_class'       => 'page-contact',
);
?>
<section class="container mx-auto px-4 py-10 grid gap-6 lg:grid-cols-3">
  <div class="lg:col-span-2">
    <?php get_template_part('template-parts/components/card', null, [
      'title' => __('Send a Message', 'retail-trade-scanner'),
      'content' => '<form class="grid gap-3">'
        . '<input class="border rounded px-3 py-2" type="text" placeholder="Name" />'
        . '<input class="border rounded px-3 py-2" type="email" placeholder="Email" />'
        . '<textarea class="border rounded px-3 py-2" rows="4" placeholder="Message"></textarea>'
        . '<button class="rounded-md bg-primary text-primary-foreground px-4 py-2" type="button">' . esc_html__('Send', 'retail-trade-scanner') . '</button>'
        . '</form>',
    ]); ?>
  </div>
  <aside class="grid gap-6">
    <?php get_template_part('template-parts/components/card', null, [
      'title' => __('Contact Info', 'retail-trade-scanner'),
      'content' => __('Email: support@example.com', 'retail-trade-scanner'),
    ]); ?>
  </aside>
</section>
<?php
get_template_part('template-parts/layout/main-shell', null, $layout_args);
get_footer();