<?php
/**
 * Main Shell Layout
 *
 * Provides a consistent page shell with header area, description and content slot.
 * Used by page templates referenced in activation routine.
 *
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

$defaults = [
  'page_title'       => get_the_title(),
  'page_description' => '',
  'page_class'       => '',
];
$args = wp_parse_args( $args ?? [], $defaults );
?>

<section class="container mx-auto px-4 py-10 <?php echo esc_attr($args['page_class']); ?>">
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php echo esc_html( $args['page_title'] ); ?></h1>
    <?php if ( ! empty( $args['page_description'] ) ) : ?>
      <p class="mt-2 text-muted-foreground max-w-2xl"><?php echo esc_html( $args['page_description'] ); ?></p>
    <?php endif; ?>
  </header>

  <div class="grid gap-6">
    <?php
      // Slot for page content (templates can output additional markup before/after including this shell)
      if ( have_posts() ) {
        while ( have_posts() ) { the_post(); the_content(); }
      }
    ?>
  </div>
</section>