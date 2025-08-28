<?php
/**
 * Simple Breadcrumbs
 */
if (is_front_page()) {
    return;
}
?>
<nav class="breadcrumbs" aria-label="<?php esc_attr_e('Breadcrumb', 'retail-trade-scanner'); ?>">
  <ul class="breadcrumb-list">
    <li class="breadcrumb-item">
      <a href="<?php echo esc_url(home_url('/')); ?>" class="breadcrumb-link"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    </li>
    <?php if (is_home()): ?>
      <li class="breadcrumb-item">
        <span class="breadcrumb-current"><?php esc_html_e('Blog', 'retail-trade-scanner'); ?></span>
      </li>
    <?php elseif (is_category() || is_tag()): ?>
      <li class="breadcrumb-item">
        <span class="breadcrumb-current"><?php single_term_title(); ?></span>
      </li>
    <?php elseif (is_search()): ?>
      <li class="breadcrumb-item">
        <span class="breadcrumb-current"><?php esc_html_e('Search', 'retail-trade-scanner'); ?></span>
      </li>
    <?php elseif (is_singular('post')): ?>
      <li class="breadcrumb-item">
        <a href="<?php echo esc_url(get_permalink( get_option('page_for_posts') )); ?>" class="breadcrumb-link"><?php esc_html_e('Blog', 'retail-trade-scanner'); ?></a>
      </li>
      <li class="breadcrumb-item">
        <span class="breadcrumb-current"><?php the_title(); ?></span>
      </li>
    <?php elseif (is_page()): ?>
      <li class="breadcrumb-item">
        <span class="breadcrumb-current"><?php the_title(); ?></span>
      </li>
    <?php elseif (is_archive()): ?>
      <li class="breadcrumb-item">
        <span class="breadcrumb-current"><?php the_archive_title(); ?></span>
      </li>
    <?php else: ?>
      <li class="breadcrumb-item">
        <span class="breadcrumb-current"><?php echo esc_html(get_the_title()); ?></span>
      </li>
    <?php endif; ?>
  </ul>
</nav>