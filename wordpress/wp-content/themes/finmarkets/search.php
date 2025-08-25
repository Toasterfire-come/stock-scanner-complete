<?php if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <h1 style="color:var(--navy); margin:0 0 12px;">Search results for “<?php echo get_search_query(); ?>”</h1>
    <?php get_search_form(); ?>
    <?php if (have_posts()) : ?>
      <ul style="padding:0; list-style:none;">
        <?php while (have_posts()) : the_post(); ?>
          <li class="card" style="padding:16px; margin:12px 0;">
            <a href="<?php the_permalink(); ?>" style="text-decoration:none; color:var(--navy); font-weight:600; "><?php the_title(); ?></a>
            <div class="muted" style="font-size:14px;"><?php echo get_the_date(); ?></div>
          </li>
        <?php endwhile; ?>
      </ul>
      <?php the_posts_pagination(); ?>
    <?php else : ?>
      <div class="card" style="padding:20px;">No results found.</div>
    <?php endif; ?>
  </div>
</section>
<?php get_footer(); ?>