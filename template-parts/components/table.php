<?php
/**
 * Table Component
 * Args:
 * - headers: [ 'Col A', 'Col B' ]
 * - rows: [ ['a','b'], ['c','d'] ]
 * - empty_text: string
 */
if (!defined('ABSPATH')) { exit; }
$defaults = [
  'headers'    => [],
  'rows'       => [],
  'empty_text' => __('No data available', 'retail-trade-scanner'),
];
$args = wp_parse_args( $args ?? [], $defaults );
?>
<div class="overflow-x-auto rounded-lg border">
  <table class="min-w-full text-sm">
    <?php if ( ! empty($args['headers']) ) : ?>
    <thead class="bg-muted/50 text-muted-foreground">
      <tr>
        <?php foreach ($args['headers'] as $h) : ?>
          <th class="px-3 py-2 text-left font-medium"><?php echo esc_html( $h ); ?></th>
        <?php endforeach; ?>
      </tr>
    </thead>
    <?php endif; ?>
    <tbody>
      <?php if ( ! empty($args['rows']) ) : ?>
        <?php foreach ($args['rows'] as $row) : ?>
          <tr class="border-t">
            <?php foreach ($row as $cell) : ?>
              <td class="px-3 py-2 align-top"><?php echo wp_kses_post( $cell ); ?></td>
            <?php endforeach; ?>
          </tr>
        <?php endforeach; ?>
      <?php else : ?>
        <tr class="border-t">
          <td class="px-3 py-6 text-center text-muted-foreground" colspan="<?php echo esc_attr( max(1, count($args['headers'])) ); ?>">
            <?php echo esc_html( $args['empty_text'] ); ?>
          </td>
        </tr>
      <?php endif; ?>
    </tbody>
  </table>
</div>