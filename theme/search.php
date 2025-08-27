<?php
/**
 * Search pages only (no posts)
 */
get_header();
?>
<main id="main-content" class="site-main">
  <div class="container">
    <?php get_template_part('template-parts/breadcrumbs'); ?>
    <div class="page-header">
      <h1 class="page-title">Search pages for “<?php echo esc_html(get_search_query()); ?>”</h1>
      <div class="search-container"><?php get_search_form(); ?></div>
    </div>

    <?php if (have_posts()): ?>
      <div class="pricing-table" style="grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));">
        <?php while (have_posts()): the_post(); ?>
          <article <?php post_class('card'); ?> >
            <div class="card-header">
              <h2 class="card-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
            </div>
            <div class="card-body"><?php the_excerpt(); ?></div>
            <div class="card-footer"><a class="btn btn-primary" href="<?php the_permalink(); ?>"><span>Open Page</span></a></div>
          </article>
        <?php endwhile; ?>
      </div>
      <div class="d-flex justify-content-center"><?php the_posts_pagination(); ?></div>
    <?php else: ?>
      <div class="card"><div class="card-body">No pages found. Try another search.</div></div>
    <?php endif; ?>
  </div>
</main>
<?php get_footer(); ?>