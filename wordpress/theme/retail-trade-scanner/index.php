<?php
/** Default index template */
get_header(); ?>
<section class="section">
  <div class="container">
    <h1><?php the_title(); ?></h1>
    <div class="content">
      <?php if (have_posts()) : while (have_posts()) : the_post(); the_content(); endwhile; endif; ?>
    </div>
  </div>
</section>
<?php get_footer();