<?php if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <h1 style="color:var(--navy); margin:0 0 12px;"><?php the_title(); ?></h1>
    <div class="card" style="padding:20px;">
      <?php if (have_posts()) : while (have_posts()) : the_post(); the_content(); endwhile; endif; ?>
    </div>
  </div>
</section>
<?php get_footer(); ?>