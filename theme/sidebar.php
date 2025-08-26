<?php
/** Sidebar template */
if (!is_active_sidebar('primary-sidebar')) { return; }
?>
<aside class="site-sidebar" role="complementary" aria-label="Sidebar Widgets">
  <?php dynamic_sidebar('primary-sidebar'); ?>
</aside>