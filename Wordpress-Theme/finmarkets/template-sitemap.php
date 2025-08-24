<?php /* Template Name: Sitemap */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <h1 style="color:var(--navy);">Sitemap</h1>
    <div class="card" style="padding:20px;">
      <ul>
        <?php wp_list_pages(['title_li' => '']); ?>
      </ul>
    </div>
  </div>
</section>
<?php get_footer(); ?>