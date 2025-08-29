<?php
/**
 * Table Component Template Part - Data Tables with Sorting and Responsive Behavior
 *
 * @package RetailTradeScanner
 */

// Default table attributes
$defaults = array(
    'headers' => array(), // Array of header definitions
    'rows' => array(), // Array of row data
    'sortable' => true,
    'responsive' => true,
    'striped' => true,
    'hover' => true,
    'sticky_header' => false,
    'pagination' => false,
    'per_page' => 10,
    'current_page' => 1,
    'search' => false,
    'actions' => false, // Show action column
    'variant' => 'default', // default, minimal, bordered, glass
    'size' => 'base', // sm, base, lg
    'classes' => '',
    'attributes' => array(),
    'empty_message' => '',
    'loading' => false,
);

// Parse attributes
$args = wp_parse_args($args ?? array(), $defaults);

// Ensure we have data
if (empty($args['headers']) && empty($args['rows'])) {
    return;
}

// Build CSS classes
$table_classes = array('data-table');
$table_classes[] = 'table-' . esc_attr($args['variant']);
$table_classes[] = 'table-' . esc_attr($args['size']);

if ($args['sortable']) {
    $table_classes[] = 'sortable';
}

if ($args['responsive']) {
    $table_classes[] = 'responsive';
}

if ($args['striped']) {
    $table_classes[] = 'table-striped';
}

if ($args['hover']) {
    $table_classes[] = 'table-hover';
}

if ($args['sticky_header']) {
    $table_classes[] = 'table-sticky';
}

if (!empty($args['classes'])) {
    $table_classes[] = $args['classes'];
}

// Build attributes
$attributes = array(
    'class' => implode(' ', $table_classes),
    'role' => 'table',
    'aria-label' => __('Data table', 'retail-trade-scanner')
);

// Merge custom attributes
$attributes = array_merge($attributes, $args['attributes']);

// Build attribute string
$attr_string = '';
foreach ($attributes as $attr => $value) {
    $attr_string .= ' ' . esc_attr($attr) . '="' . esc_attr($value) . '"';
}

// Generate unique table ID
$table_id = 'table-' . wp_unique_id();

// Paginate rows if needed
$total_rows = count($args['rows']);
$paginated_rows = $args['rows'];
$total_pages = 1;

if ($args['pagination'] && $total_rows > $args['per_page']) {
    $total_pages = ceil($total_rows / $args['per_page']);
    $offset = ($args['current_page'] - 1) * $args['per_page'];
    $paginated_rows = array_slice($args['rows'], $offset, $args['per_page']);
}
?>

<div class="table-container" data-table-id="<?php echo esc_attr($table_id); ?>">
    <?php if ($args['search']) : ?>
        <div class="table-search">
            <div class="search-field-wrapper">
                <input type="search" 
                       id="<?php echo esc_attr($table_id); ?>-search"
                       class="table-search-input form-input" 
                       placeholder="<?php esc_attr_e('Search table data...', 'retail-trade-scanner'); ?>"
                       aria-label="<?php esc_attr_e('Search table', 'retail-trade-scanner'); ?>">
                <label for="<?php echo esc_attr($table_id); ?>-search" class="sr-only">
                    <?php esc_html_e('Search', 'retail-trade-scanner'); ?>
                </label>
            </div>
        </div>
    <?php endif; ?>

    <?php if ($args['loading']) : ?>
        <div class="table-loading">
            <div class="loading-spinner"></div>
            <p><?php esc_html_e('Loading data...', 'retail-trade-scanner'); ?></p>
        </div>
    <?php else : ?>
        <div class="table-responsive">
            <table id="<?php echo esc_attr($table_id); ?>" <?php echo $attr_string; ?>>
                <?php if (!empty($args['headers'])) : ?>
                    <thead>
                        <tr>
                            <?php foreach ($args['headers'] as $index => $header) : ?>
                                <?php
                                $header_classes = array('table-header');
                                $header_attrs = array();
                                
                                if (is_array($header)) {
                                    $header_text = $header['text'] ?? '';
                                    $header_key = $header['key'] ?? $index;
                                    $sortable = $header['sortable'] ?? $args['sortable'];
                                    $width = $header['width'] ?? '';
                                    $align = $header['align'] ?? 'left';
                                    
                                    if ($sortable) {
                                        $header_classes[] = 'sortable';
                                        $header_attrs['data-sort'] = $header_key;
                                        $header_attrs['tabindex'] = '0';
                                        $header_attrs['role'] = 'button';
                                        $header_attrs['aria-label'] = sprintf(__('Sort by %s', 'retail-trade-scanner'), $header_text);
                                    }
                                    
                                    if ($width) {
                                        $header_attrs['style'] = 'width: ' . esc_attr($width);
                                    }
                                    
                                    $header_attrs['class'] = implode(' ', $header_classes) . ' text-' . $align;
                                } else {
                                    $header_text = $header;
                                    $header_key = $index;
                                    
                                    if ($args['sortable']) {
                                        $header_classes[] = 'sortable';
                                        $header_attrs['data-sort'] = $header_key;
                                        $header_attrs['tabindex'] = '0';
                                        $header_attrs['role'] = 'button';
                                        $header_attrs['aria-label'] = sprintf(__('Sort by %s', 'retail-trade-scanner'), $header_text);
                                    }
                                    
                                    $header_attrs['class'] = implode(' ', $header_classes);
                                }
                                
                                $header_attr_string = '';
                                foreach ($header_attrs as $attr => $value) {
                                    $header_attr_string .= ' ' . esc_attr($attr) . '="' . esc_attr($value) . '"';
                                }
                                ?>
                                <th<?php echo $header_attr_string; ?>>
                                    <span class="header-content">
                                        <?php echo esc_html($header_text); ?>
                                        <?php if (isset($header_attrs['data-sort'])) : ?>
                                            <span class="sort-indicator" aria-hidden="true">
                                                <?php echo rts_get_icon('chevron-up-down', array('width' => '14', 'height' => '14')); ?>
                                            </span>
                                        <?php endif; ?>
                                    </span>
                                </th>
                            <?php endforeach; ?>
                            
                            <?php if ($args['actions']) : ?>
                                <th class="table-header actions-header">
                                    <?php esc_html_e('Actions', 'retail-trade-scanner'); ?>
                                </th>
                            <?php endif; ?>
                        </tr>
                    </thead>
                <?php endif; ?>

                <tbody>
                    <?php if (!empty($paginated_rows)) : ?>
                        <?php foreach ($paginated_rows as $row_index => $row) : ?>
                            <tr class="table-row" <?php echo is_array($row) && isset($row['_attributes']) ? $row['_attributes'] : ''; ?>>
                                <?php 
                                $row_data = is_array($row) && isset($row['data']) ? $row['data'] : $row;
                                
                                foreach ($args['headers'] as $header_index => $header) :
                                    $header_key = is_array($header) ? ($header['key'] ?? $header_index) : $header_index;
                                    $cell_value = is_array($row_data) ? ($row_data[$header_key] ?? '') : '';
                                    $cell_classes = array('table-cell');
                                    
                                    // Add alignment class
                                    if (is_array($header) && isset($header['align'])) {
                                        $cell_classes[] = 'text-' . $header['align'];
                                    }
                                    
                                    // Add data attribute for responsive view
                                    $data_label = is_array($header) ? ($header['text'] ?? $header_key) : $header;
                                ?>
                                    <td class="<?php echo implode(' ', $cell_classes); ?>" 
                                        data-label="<?php echo esc_attr($data_label); ?>"
                                        data-sort="<?php echo esc_attr($header_key); ?>">
                                        <?php
                                        if (is_array($cell_value) && isset($cell_value['html'])) {
                                            echo wp_kses_post($cell_value['html']);
                                        } else {
                                            echo esc_html($cell_value);
                                        }
                                        ?>
                                    </td>
                                <?php endforeach; ?>
                                
                                <?php if ($args['actions']) : ?>
                                    <td class="table-cell actions-cell">
                                        <div class="table-actions">
                                            <?php
                                            $row_actions = is_array($row) && isset($row['actions']) ? $row['actions'] : array();
                                            foreach ($row_actions as $action) :
                                                if (is_array($action)) {
                                                    echo '<a href="' . esc_url($action['url'] ?? '#') . '" class="action-link ' . esc_attr($action['class'] ?? '') . '">';
                                                    if (isset($action['icon'])) {
                                                        echo rts_get_icon($action['icon'], array('width' => '16', 'height' => '16'));
                                                    }
                                                    echo esc_html($action['text'] ?? '');
                                                    echo '</a>';
                                                }
                                            endforeach;
                                            ?>
                                        </div>
                                    </td>
                                <?php endif; ?>
                            </tr>
                        <?php endforeach; ?>
                    <?php else : ?>
                        <tr class="table-empty">
                            <td colspan="<?php echo count($args['headers']) + ($args['actions'] ? 1 : 0); ?>" class="table-cell text-center">
                                <div class="empty-state">
                                    <?php echo rts_get_icon('database', array('width' => '48', 'height' => '48', 'class' => 'empty-icon')); ?>
                                    <p><?php echo esc_html($args['empty_message'] ?: __('No data available', 'retail-trade-scanner')); ?></p>
                                </div>
                            </td>
                        </tr>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>

        <?php if ($args['pagination'] && $total_pages > 1) : ?>
            <div class="table-pagination">
                <div class="pagination-info">
                    <?php
                    $start = ($args['current_page'] - 1) * $args['per_page'] + 1;
                    $end = min($args['current_page'] * $args['per_page'], $total_rows);
                    printf(
                        __('Showing %d to %d of %d entries', 'retail-trade-scanner'),
                        $start,
                        $end,
                        $total_rows
                    );
                    ?>
                </div>
                
                <nav class="pagination-nav" aria-label="<?php esc_attr_e('Table pagination', 'retail-trade-scanner'); ?>">
                    <?php
                    // Simple pagination implementation
                    $prev_page = max(1, $args['current_page'] - 1);
                    $next_page = min($total_pages, $args['current_page'] + 1);
                    ?>
                    
                    <?php if ($args['current_page'] > 1) : ?>
                        <button class="pagination-btn btn btn-outline btn-sm" data-page="<?php echo $prev_page; ?>">
                            <?php echo rts_get_icon('chevron-left', array('width' => '16', 'height' => '16')); ?>
                            <?php esc_html_e('Previous', 'retail-trade-scanner'); ?>
                        </button>
                    <?php endif; ?>
                    
                    <span class="pagination-current">
                        <?php printf(__('Page %d of %d', 'retail-trade-scanner'), $args['current_page'], $total_pages); ?>
                    </span>
                    
                    <?php if ($args['current_page'] < $total_pages) : ?>
                        <button class="pagination-btn btn btn-outline btn-sm" data-page="<?php echo $next_page; ?>">
                            <?php esc_html_e('Next', 'retail-trade-scanner'); ?>
                            <?php echo rts_get_icon('chevron-right', array('width' => '16', 'height' => '16')); ?>
                        </button>
                    <?php endif; ?>
                </nav>
            </div>
        <?php endif; ?>
    <?php endif; ?>
</div>

<?php
/*
Usage example:

$stock_data = array(
    'headers' => array(
        array('text' => 'Symbol', 'key' => 'symbol', 'sortable' => true, 'width' => '100px'),
        array('text' => 'Company', 'key' => 'company', 'sortable' => true),
        array('text' => 'Price', 'key' => 'price', 'sortable' => true, 'align' => 'right'),
        array('text' => 'Change', 'key' => 'change', 'sortable' => true, 'align' => 'right'),
        array('text' => 'Volume', 'key' => 'volume', 'sortable' => true, 'align' => 'right'),
    ),
    'rows' => array(
        array(
            'data' => array(
                'symbol' => 'AAPL',
                'company' => 'Apple Inc.',
                'price' => '$182.34',
                'change' => array('html' => '<span class="text-success">+2.45%</span>'),
                'volume' => '89.2M'
            ),
            'actions' => array(
                array('text' => 'View', 'url' => '/stock/aapl/', 'icon' => 'eye', 'class' => 'btn-sm'),
                array('text' => 'Add to Watchlist', 'url' => '/watchlist/add/aapl/', 'icon' => 'plus', 'class' => 'btn-sm')
            )
        ),
        // ... more rows
    ),
    'sortable' => true,
    'responsive' => true,
    'pagination' => true,
    'per_page' => 25,
    'search' => true,
    'actions' => true,
    'variant' => 'default'
);

get_template_part('template-parts/components/table', null, $stock_data);
*/