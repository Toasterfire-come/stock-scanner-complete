<?php
/** Template Name: Endpoint Status */
if (!defined('ABSPATH')) { exit; }
get_header();
$layout_args = ['page_title'=>__('Endpoint Status','retail-trade-scanner'),'page_description'=>__('Live uptime and latency for backend endpoints','retail-trade-scanner'),'page_class'=>'page-endpoint-status'];
?>
<section class="container mx-auto px-4 py-10">
  <div id="rts-endpoint-status" class="grid gap-2">
    <div class="text-muted-foreground"><?php esc_html_e('Checking endpoints…','retail-trade-scanner'); ?></div>
  </div>
</section>
<?php get_template_part('template-parts/layout/main-shell', null, $layout_args); get_footer(); ?>