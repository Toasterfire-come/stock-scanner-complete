<?php get_header(); ?>
<section class="section"><div class="container">
  <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
    <article class="card" style="padding:24px;">
      <h1><?php the_title(); ?></h1>
      <div style="color:#6b7280;font-size:14px;margin-bottom:12px;">Published <?php echo esc_html(get_the_date()); ?> by <?php the_author(); ?></div>
      <div class="content"><?php the_content(); ?></div>
    </article>
  <?php endwhile; endif; ?>
</div></section>
<?php get_footer(); ?>