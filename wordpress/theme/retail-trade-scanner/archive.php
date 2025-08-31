<?php get_header(); ?>
<section class="section"><div class="container">
  <h1><?php echo esc_html(get_the_archive_title()); ?></h1>
  <div class="card" style="padding:16px;margin-top:12px;">
    <?php if (have_posts()) : ?>
      <ul style="margin:0;padding-left:18px;">
        <?php while (have_posts()) : the_post(); ?>
          <li><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a> <span style="color:#6b7280;">(<?php echo esc_html(get_the_date()); ?>)</span></li>
        <?php endwhile; ?>
      </ul>
      <div style="margin-top:12px;"><?php the_posts_pagination(); ?></div>
    <?php else : ?>
      <p style="color:#6b7280;">No posts found.</p>
    <?php endif; ?>
  </div>
</div></section>
<?php get_footer(); ?>