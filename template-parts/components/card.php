<?php
/**
 * Reusable Card Component
 * Args:
 * - title (string)
 * - subtitle (string)
 * - meta (string|array)
 * - content (callable|string)
 * - footer (callable|string)
 * - class (string)
 */
if (!defined('ABSPATH')) { exit; }

$defaults = [
  'title'    => '',
  'subtitle' => '',
  'meta'     => '',
  'content'  => '',
  'footer'   => '',
  'class'    => '',
];
$args = wp_parse_args( $args ?? [], $defaults );
?>

<article class="rounded-xl border bg-card text-card-foreground p-5 shadow-sm <?php echo esc_attr($args['class']); ?>">
  <?php if ( $args['title'] || $args['subtitle'] || $args['meta'] ) : ?>
    <header class="mb-3">
      <?php if ( $args['title'] ) : ?>
        <h3 class="text-lg font-semibold leading-snug"><?php echo esc_html( $args['title'] ); ?></h3>
      <?php endif; ?>
      <?php if ( $args['subtitle'] ) : ?>
        <p class="text-sm text-muted-foreground mt-0.5"><?php echo esc_html( $args['subtitle'] ); ?></p>
      <?php endif; ?>
      <?php if ( $args['meta'] ) : ?>
        <div class="mt-1 text-xs text-muted-foreground">
          <?php echo is_array($args['meta']) ? wp_kses_post( implode(' · ', array_map('esc_html', $args['meta'])) ) : wp_kses_post( $args['meta'] ); ?>
        </div>
      <?php endif; ?>
    </header>
  <?php endif; ?>

  <div class="text-sm leading-relaxed">
    <?php
      if ( is_callable( $args['content'] ) ) { call_user_func( $args['content'] ); }
      else { echo wp_kses_post( $args['content'] ); }
    ?>
  </div>

  <?php if ( $args['footer'] ) : ?>
    <footer class="mt-4">
      <?php
        if ( is_callable( $args['footer'] ) ) { call_user_func( $args['footer'] ); }
        else { echo wp_kses_post( $args['footer'] ); }
      ?>
    </footer>
  <?php endif; ?>
</article>