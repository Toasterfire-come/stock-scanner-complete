<?php if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
      <article class="card" style="padding:24px;">
        <h1 style="margin:0 0 10px; color:var(--navy);"><?php the_title(); ?></h1>
        <div class="muted" style="font-size:14px; margin-bottom:16px;">By <?php the_author(); ?> · <?php echo get_the_date(); ?></div>
        <div><?php the_content(); ?></div>
      </article>
      <?php comments_template(); ?>
    <?php endwhile; endif; ?>
  </div>
</section>
<?php get_footer(); ?>