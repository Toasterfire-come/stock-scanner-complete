<?php if (!defined('ABSPATH')) { exit; } ?>
<form role="search" method="get" class="toolbar" style="margin:8px 0 16px;" action="<?php echo esc_url(home_url('/')); ?>">
  <label for="s" class="screen-reader-text">Search for:</label>
  <input type="search" id="s" class="input" placeholder="Search…" value="<?php echo esc_attr(get_search_query()); ?>" name="s" />
  <button type="submit" class="btn">Search</button>
</form>