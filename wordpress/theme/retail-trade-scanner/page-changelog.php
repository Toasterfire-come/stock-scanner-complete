<?php /* Template Name: Changelog */ get_header(); ?>
<section class="section"><div class="container">
  <h1>Changelog</h1>
  <div class="card" style="padding:16px;">
    <ul style="margin:0;padding-left:18px;">
      <?php $posts = get_posts(['numberposts'=>10, 'category_name'=>'changelog']); if (!$posts) { echo '<li style="color:#6b7280;">No changelog entries yet.</li>'; } else { foreach($posts as $po) { echo '<li><a href="'.esc_url(get_permalink($po->ID)).'">'.esc_html(get_the_title($po->ID)).'</a> <span style="color:#6b7280;">('.esc_html(get_the_date('', $po->ID)).')</span></li>'; } } ?>
    </ul>
  </div>
</div></section>
<?php get_footer(); ?>