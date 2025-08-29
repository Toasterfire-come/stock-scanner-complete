<?php
/** Template Name: API Docs (wired) */
if (!defined('ABSPATH')) { exit; }
get_header();
$layout_args = ['page_title'=>__('API Documentation','retail-trade-scanner'),'page_description'=>__('Live endpoints and examples','retail-trade-scanner'),'page_class'=>'page-api-docs'];
?>
<section class="container mx-auto px-4 py-10">
  <div id="rts-api-docs" class="grid gap-3">
    <div class="text-muted-foreground"><?php esc_html_e('Loading API docs…','retail-trade-scanner'); ?></div>
  </div>
</section>
<?php get_template_part('template-parts/layout/main-shell', null, $layout_args); get_footer(); ?>