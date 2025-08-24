<?php if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <h1 style="color:var(--navy); margin:0 0 12px;">Archive</h1>
    <?php if (have_posts()) : ?>
      <div class="grid cols-3">
        <?php while (have_posts()) : the_post(); ?>
          <article class="card" style="padding:16px;">
            <h3 style="margin:0 0 6px; color:var(--navy);"><a href="<?php the_permalink(); ?>" style="text-decoration:none; color:inherit;"><?php the_title(); ?></a></h3>
            <div class="muted" style="font-size:14px; margin-bottom:8px;">By <?php the_author(); ?> · <?php echo get_the_date(); ?></div>
            <div><?php the_excerpt(); ?></div>
            <a class="btn btn-ghost" style="margin-top:10px;" href="<?php the_permalink(); ?>">Read more</a>
          </article>
        <?php endwhile; ?>
      </div>
      <div style="margin-top:16px;"><?php the_posts_pagination(); ?></div>
    <?php else : ?>
      <div class="card" style="padding:20px;">No posts found.</div>
    <?php endif; ?>
  </div>
</section>
<?php get_footer(); ?>