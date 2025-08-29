<?php
/**
 * Chart Shell Placeholder
 * Args: title, description
 */
if (!defined('ABSPATH')) { exit; }
$defaults = [ 'title' => '', 'description' => '' ];
$args = wp_parse_args( $args ?? [], $defaults );
?>
<section class="rounded-xl border p-5">
  <?php if ($args['title']) : ?>
    <h3 class="text-lg font-semibold"><?php echo esc_html($args['title']); ?></h3>
  <?php endif; ?>
  <?php if ($args['description']) : ?>
    <p class="text-sm text-muted-foreground mt-1"><?php echo esc_html($args['description']); ?></p>
  <?php endif; ?>
  <div class="mt-4 h-48 w-full rounded-md bg-muted"></div>
</section>