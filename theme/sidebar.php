<?php
/** Sidebar template */
if (!is_active_sidebar('primary-sidebar')) { 
    return; 
}
?>
<aside class="site-sidebar" role="complementary" aria-label="<?php esc_attr_e('Sidebar Widgets', 'retail-trade-scanner'); ?>">
  <?php dynamic_sidebar('primary-sidebar'); ?>
</aside>