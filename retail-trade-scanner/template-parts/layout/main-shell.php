<?php
/**
 * Main Shell Layout with Breadcrumbs
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

if (!function_exists('retail_trade_scanner_breadcrumbs')) {
  function retail_trade_scanner_breadcrumbs() {
    echo '<nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">';
    echo '<a class="hover:underline" href="' . esc_url(home_url('/')) . '">' . esc_html__('Home', 'retail-trade-scanner') . '</a>';
    if (is_page()) {
      $ancestors = array_reverse(get_post_ancestors(get_queried_object_id()));
      foreach ($ancestors as $ancestor) {
        echo ' / <a class="hover:underline" href="' . esc_url(get_permalink($ancestor)) . '">' . esc_html(get_the_title($ancestor)) . '</a>';
      }
      echo ' / <span aria-current="page">' . esc_html(get_the_title()) . '</span>';
    }
    echo '</nav>';
  }
}

$defaults = [ 'page_title' => get_the_title(), 'page_description' => '', 'page_class' => '' ];
$args = wp_parse_args( $args ?? [], $defaults );
?>
<section class="container mx-auto px-4 py-10 <?php echo esc_attr($args['page_class']); ?>">
  <?php retail_trade_scanner_breadcrumbs(); ?>
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php echo esc_html( $args['page_title'] ); ?></h1>
    <?php if (!empty($args['page_description'])) : ?>
      <p class="mt-2 text-muted-foreground max-w-2xl"><?php echo esc_html( $args['page_description'] ); ?></p>
    <?php endif; ?>
  </header>
  <div class="grid gap-6 cv-auto">
    <?php if (have_posts()) { while (have_posts()) { the_post(); the_content(); } } ?>
  </div>
</section>