<?php
/**
 * Simple Breadcrumbs
 */
if (is_front_page()) return;
?>
<nav class="breadcrumbs" aria-label="Breadcrumb" style="margin: 1rem 0 1.25rem; font-size: 0.95rem;">
  <a href="<?php echo esc_url(home_url('/')); ?>">Home</a>
  <?php if (is_home()): ?>
    <span> / Blog</span>
  <?php elseif (is_category() || is_tag()): ?>
    <span> / <?php single_term_title(); ?></span>
  <?php elseif (is_search()): ?>
    <span> / Search</span>
  <?php elseif (is_singular('post')): ?>
    <span> / <a href="<?php echo esc_url(get_permalink( get_option('page_for_posts') )); ?>">Blog</a> / <?php the_title(); ?></span>
  <?php elseif (is_page()): ?>
    <span> / <?php the_title(); ?></span>
  <?php elseif (is_archive()): ?>
    <span> / <?php the_archive_title(); ?></span>
  <?php else: ?>
    <span> / <?php echo esc_html(get_the_title()); ?></span>
  <?php endif; ?>
</nav>
<style>
  .breadcrumbs a { color: var(--text-secondary); text-decoration: none; position: relative; }
  .breadcrumbs a::after { content:''; position:absolute; bottom:-2px; left:0; width:0; height:2px; background: var(--primary-gradient); transition: width .2s ease; }
  .breadcrumbs a:hover { color: var(--text-primary); }
  .breadcrumbs a:hover::after { width: 100%; }
</style>