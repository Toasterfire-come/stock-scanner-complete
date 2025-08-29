<?php
/**
 * Template for displaying search forms
 *
 * @package RetailTradeScanner
 */

$unique_id = esc_attr(wp_unique_id('search-form-'));
?>

<form role="search" method="get" class="search-form" action="<?php echo esc_url(home_url('/')); ?>">
    <div class="search-field-wrapper floating-label">
        <input 
            type="search" 
            id="<?php echo $unique_id; ?>"
            class="search-field form-input" 
            placeholder="<?php echo esc_attr_x('Search stocks, companies, or symbols...', 'placeholder', 'retail-trade-scanner'); ?>"
            value="<?php echo get_search_query(); ?>" 
            name="s"
            autocomplete="off"
            aria-describedby="<?php echo $unique_id; ?>-description"
        />
        <label class="search-label form-label" for="<?php echo $unique_id; ?>">
            <?php echo rts_get_icon('search', ['width' => '20', 'height' => '20']); ?>
            <?php _x('Search', 'label', 'retail-trade-scanner'); ?>
        </label>
    </div>
    
    <button type="submit" class="search-submit btn btn-primary">
        <?php echo rts_get_icon('search', ['width' => '20', 'height' => '20']); ?>
        <span class="sr-only"><?php echo _x('Search', 'submit button', 'retail-trade-scanner'); ?></span>
    </button>
    
    <div id="<?php echo $unique_id; ?>-description" class="sr-only">
        <?php esc_html_e('Search for stocks, companies, or stock symbols', 'retail-trade-scanner'); ?>
    </div>
</form>

<!-- Quick Search Suggestions -->
<div class="search-suggestions">
    <div class="popular-searches">
        <h4><?php esc_html_e('Popular Searches', 'retail-trade-scanner'); ?></h4>
        <div class="search-tags">
            <button type="button" class="search-tag" data-search="AAPL">AAPL</button>
            <button type="button" class="search-tag" data-search="TSLA">TSLA</button>
            <button type="button" class="search-tag" data-search="NVDA">NVDA</button>
            <button type="button" class="search-tag" data-search="AMZN">AMZN</button>
            <button type="button" class="search-tag" data-search="GOOGL">GOOGL</button>
            <button type="button" class="search-tag" data-search="MSFT">MSFT</button>
        </div>
    </div>
    
    <div class="recent-searches hidden">
        <h4><?php esc_html_e('Recent Searches', 'retail-trade-scanner'); ?></h4>
        <div class="recent-search-list">
            <!-- Populated by JavaScript -->
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const searchTags = document.querySelectorAll('.search-tag[data-search]');
    const searchField = document.getElementById('<?php echo $unique_id; ?>');
    
    searchTags.forEach(tag => {
        tag.addEventListener('click', function() {
            const searchTerm = this.getAttribute('data-search');
            if (searchField) {
                searchField.value = searchTerm;
                searchField.focus();
            }
        });
    });
    
    // Save recent searches to localStorage
    if (searchField) {
        searchField.addEventListener('input', function() {
            const value = this.value.trim();
            if (value.length >= 2) {
                // Implement autocomplete functionality here
                console.log('Searching for:', value);
            }
        });
    }
});
</script>