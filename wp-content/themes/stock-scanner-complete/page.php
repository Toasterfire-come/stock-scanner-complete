<?php
/**
 * Default Page Template (Modernized for v3 styles)
 */
get_header(); ?>

<section class="glass-section">
  <div class="container">
    <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
      <header class="section-intro">
        <h1 class="section-title text-gradient"><?php the_title(); ?></h1>
      </header>
      <div class="card glass-card">
        <div class="card-body page-content">
          <?php the_content(); ?>
        </div>
      </div>
    <?php endwhile; endif; ?>
  </div>
</section>

<?php get_footer(); ?>