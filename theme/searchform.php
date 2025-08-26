<?php
/**
 * Custom Search Form
 */
$unique_id = esc_attr( uniqid('search-form-') );
?>
<form role="search" method="get" class="search-form" action="<?php echo esc_url(home_url('/')); ?>">
  <label for="<?php echo esc_attr($unique_id); ?>" class="screen-reader-text">Search for:</label>
  <input type="search" id="<?php echo esc_attr($unique_id); ?>" class="form-control" placeholder="Search…" value="<?php echo esc_attr(get_search_query()); ?>" name="s" />
  <button type="submit" class="btn btn-primary"><span>Search</span></button>
</form>