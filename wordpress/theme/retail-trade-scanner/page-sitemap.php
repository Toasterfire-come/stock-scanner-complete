<?php /* Template Name: Sitemap */ get_header(); ?>
<section class="section"><div class="container">
  <h1>Sitemap</h1>
  <div class="grid" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;">
    <div class="card" style="padding:16px;">
      <h3>Pages</h3>
      <ul style="margin:0;padding-left:18px;">
        <?php $pages = get_pages(['sort_column' => 'post_title']); foreach ($pages as $p): ?>
          <li><a href="<?php echo esc_url(get_permalink($p->ID)); ?>"><?php echo esc_html($p->post_title); ?></a></li>
        <?php endforeach; ?>
      </ul>
    </div>
    <div class="card" style="padding:16px;">
      <h3>Posts</h3>
      <ul style="margin:0;padding-left:18px;">
        <?php $posts = get_posts(['numberposts' => 20]); foreach ($posts as $po): ?>
          <li><a href="<?php echo esc_url(get_permalink($po->ID)); ?>"><?php echo esc_html(get_the_title($po->ID)); ?></a></li>
        <?php endforeach; ?>
      </ul>
    </div>
    <div class="card" style="padding:16px;">
      <h3>Categories</h3>
      <ul style="margin:0;padding-left:18px;">
        <?php foreach (get_categories() as $cat): ?>
          <li><a href="<?php echo esc_url(get_category_link($cat->term_id)); ?>"><?php echo esc_html($cat->name); ?></a></li>
        <?php endforeach; ?>
      </ul>
    </div>
  </div>
</div></section>
<?php get_footer(); ?>