<?php
/**
 * Table Component Template Part
 *
 * @package RetailTradeScanner
 */

$args = wp_parse_args($args, array(
    'id' => 'data-table',
    'headers' => array(),
    'data' => array(),
    'sortable' => true,
    'selectable' => false,
    'pagination' => false,
    'variant' => 'default', // default, positions, scanner
    'responsive' => true,
    'loading' => false,
    'empty_message' => __('No data available', 'retail-trade-scanner'),
    'custom_class' => ''
));

extract($args);

$table_classes = array('data-table');
$table_classes[] = 'table-' . $variant;

if ($responsive) {
    $table_classes[] = 'table-responsive';
}

if ($selectable) {
    $table_classes[] = 'table-selectable';
}

if ($custom_class) {
    $table_classes[] = $custom_class;
}

$table_id = esc_attr($id);
?>

<div class="table-container">
    
    <?php if ($loading) : ?>
        <div class="table-loading-overlay">
            <div class="loading-spinner"></div>
            <p><?php esc_html_e('Loading data...', 'retail-trade-scanner'); ?></p>
        </div>
    <?php endif; ?>
    
    <div class="table-wrapper">
        <table class="<?php echo esc_attr(implode(' ', $table_classes)); ?>" id="<?php echo $table_id; ?>">
            
            <?php if (!empty($headers)) : ?>
                <thead class="table-header">
                    <tr>
                        <?php if ($selectable) : ?>
                            <th class="select-column">
                                <input type="checkbox" class="select-all" aria-label="<?php esc_attr_e('Select all rows', 'retail-trade-scanner'); ?>">
                            </th>
                        <?php endif; ?>
                        
                        <?php foreach ($headers as $key => $label) : ?>
                            <th class="table-header-cell <?php echo $sortable ? 'sortable' : ''; ?>" 
                                data-column="<?php echo esc_attr($key); ?>"
                                <?php if ($sortable) : ?>
                                tabindex="0" 
                                role="button" 
                                aria-label="<?php echo esc_attr(sprintf(__('Sort by %s', 'retail-trade-scanner'), $label)); ?>"
                                <?php endif; ?>>
                                
                                <div class="header-content">
                                    <span class="header-label"><?php echo esc_html($label); ?></span>
                                    
                                    <?php if ($sortable) : ?>
                                        <span class="sort-indicator">
                                            <?php echo rts_get_icon('chevrons-up-down', ['width' => '14', 'height' => '14']); ?>
                                        </span>
                                    <?php endif; ?>
                                </div>
                            </th>
                        <?php endforeach; ?>
                    </tr>
                </thead>
            <?php endif; ?>
            
            <tbody class="table-body">
                <?php if (!empty($data)) : ?>
                    <?php foreach ($data as $row_index => $row) : ?>
                        <tr class="table-row" data-row="<?php echo esc_attr($row_index); ?>">
                            
                            <?php if ($selectable) : ?>
                                <td class="select-cell">
                                    <input type="checkbox" class="row-select" value="<?php echo esc_attr($row_index); ?>" aria-label="<?php esc_attr_e('Select row', 'retail-trade-scanner'); ?>">
                                </td>
                            <?php endif; ?>
                            
                            <?php foreach ($headers as $column_key => $column_label) : ?>
                                <td class="table-cell cell-<?php echo esc_attr($column_key); ?>" data-column="<?php echo esc_attr($column_key); ?>">
                                    
                                    <?php if ($column_key === 'symbol' && isset($row['symbol'])) : ?>
                                        <!-- Symbol with company name -->
                                        <div class="symbol-cell">
                                            <div class="symbol-info">
                                                <span class="symbol-ticker"><?php echo esc_html($row['symbol']); ?></span>
                                                <?php if (isset($row['company'])) : ?>
                                                    <span class="symbol-company"><?php echo esc_html($row['company']); ?></span>
                                                <?php endif; ?>
                                            </div>
                                        </div>
                                        
                                    <?php elseif ($column_key === 'change' && isset($row['type'])) : ?>
                                        <!-- Price change with badge -->
                                        <?php
                                        get_template_part('template-parts/components/badge', null, array(
                                            'value' => $row['change'],
                                            'type' => $row['type'],
                                            'size' => 'sm'
                                        ));
                                        ?>
                                        
                                    <?php elseif ($column_key === 'unrealized_pl' && isset($row['unrealized_pl_percent'])) : ?>
                                        <!-- P/L with percentage -->
                                        <div class="pl-cell">
                                            <span class="pl-amount <?php echo isset($row['type']) ? $row['type'] : ''; ?>">
                                                <?php echo esc_html($row['unrealized_pl']); ?>
                                            </span>
                                            <span class="pl-percent <?php echo isset($row['type']) ? $row['type'] : ''; ?>">
                                                <?php echo esc_html($row['unrealized_pl_percent']); ?>
                                            </span>
                                        </div>
                                        
                                    <?php elseif ($column_key === 'actions') : ?>
                                        <!-- Action buttons -->
                                        <div class="action-buttons">
                                            <?php if ($variant === 'positions') : ?>
                                                <button class="action-btn btn-ghost btn-sm" title="<?php esc_attr_e('View details', 'retail-trade-scanner'); ?>">
                                                    <?php echo rts_get_icon('eye', ['width' => '14', 'height' => '14']); ?>
                                                </button>
                                                <button class="action-btn btn-ghost btn-sm" title="<?php esc_attr_e('Add to watchlist', 'retail-trade-scanner'); ?>">
                                                    <?php echo rts_get_icon('plus', ['width' => '14', 'height' => '14']); ?>
                                                </button>
                                                <button class="action-btn btn-ghost btn-sm" title="<?php esc_attr_e('Trade', 'retail-trade-scanner'); ?>">
                                                    <?php echo rts_get_icon('trending-up', ['width' => '14', 'height' => '14']); ?>
                                                </button>
                                            <?php else : ?>
                                                <button class="action-btn btn-ghost btn-sm" title="<?php esc_attr_e('Add to watchlist', 'retail-trade-scanner'); ?>">
                                                    <?php echo rts_get_icon('bookmark', ['width' => '14', 'height' => '14']); ?>
                                                </button>
                                                <button class="action-btn btn-ghost btn-sm" title="<?php esc_attr_e('View chart', 'retail-trade-scanner'); ?>">
                                                    <?php echo rts_get_icon('bar-chart', ['width' => '14', 'height' => '14']); ?>
                                                </button>
                                            <?php endif; ?>
                                        </div>
                                        
                                    <?php else : ?>
                                        <!-- Default cell content -->
                                        <span class="cell-content">
                                            <?php echo isset($row[$column_key]) ? esc_html($row[$column_key]) : '—'; ?>
                                        </span>
                                    <?php endif; ?>
                                    
                                    <!-- Mobile label for responsive view -->
                                    <span class="mobile-label"><?php echo esc_html($column_label); ?></span>
                                </td>
                            <?php endforeach; ?>
                        </tr>
                    <?php endforeach; ?>
                    
                <?php else : ?>
                    <tr class="empty-row">
                        <td colspan="<?php echo count($headers) + ($selectable ? 1 : 0); ?>" class="empty-cell">
                            <div class="empty-state">
                                <?php echo rts_get_icon('search', ['width' => '48', 'height' => '48', 'class' => 'empty-icon']); ?>
                                <p><?php echo esc_html($empty_message); ?></p>
                            </div>
                        </td>
                    </tr>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
    
    <?php if ($pagination && !empty($data)) : ?>
        <div class="table-pagination">
            <div class="pagination-info">
                <span><?php esc_html_e('Showing', 'retail-trade-scanner'); ?> <strong>1-<?php echo count($data); ?></strong> <?php esc_html_e('of', 'retail-trade-scanner'); ?> <strong><?php echo count($data); ?></strong> <?php esc_html_e('results', 'retail-trade-scanner'); ?></span>
            </div>
            
            <div class="pagination-controls">
                <button class="pagination-btn" disabled>
                    <?php echo rts_get_icon('chevron-left', ['width' => '16', 'height' => '16']); ?>
                    <?php esc_html_e('Previous', 'retail-trade-scanner'); ?>
                </button>
                
                <div class="pagination-pages">
                    <button class="page-btn active">1</button>
                </div>
                
                <button class="pagination-btn" disabled>
                    <?php esc_html_e('Next', 'retail-trade-scanner'); ?>
                    <?php echo rts_get_icon('chevron-right', ['width' => '16', 'height' => '16']); ?>
                </button>
            </div>
        </div>
    <?php endif; ?>
    
    <?php if ($selectable) : ?>
        <div class="bulk-actions hidden">
            <div class="bulk-actions-content">
                <span class="selection-count">0 <?php esc_html_e('items selected', 'retail-trade-scanner'); ?></span>
                <div class="bulk-action-buttons">
                    <button class="btn btn-outline btn-sm bulk-action" data-action="watchlist">
                        <?php echo rts_get_icon('bookmark', ['width' => '14', 'height' => '14']); ?>
                        <?php esc_html_e('Add to Watchlist', 'retail-trade-scanner'); ?>
                    </button>
                    <button class="btn btn-outline btn-sm bulk-action" data-action="export">
                        <?php echo rts_get_icon('download', ['width' => '14', 'height' => '14']); ?>
                        <?php esc_html_e('Export', 'retail-trade-scanner'); ?>
                    </button>
                </div>
            </div>
        </div>
    <?php endif; ?>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeTable('<?php echo $table_id; ?>');
});

function initializeTable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const sortableHeaders = table.querySelectorAll('.sortable');
    const selectAllCheckbox = table.querySelector('.select-all');
    const rowCheckboxes = table.querySelectorAll('.row-select');
    const bulkActions = document.querySelector('.bulk-actions');
    
    // Sorting functionality
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            sortTable(table, this.dataset.column);
        });
        
        header.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                sortTable(table, this.dataset.column);
            }
        });
    });
    
    // Selection functionality
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            rowCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            updateBulkActions();
        });
    }
    
    rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectAllState();
            updateBulkActions();
        });
    });
    
    // Action buttons
    table.addEventListener('click', function(e) {
        if (e.target.closest('.action-btn')) {
            const btn = e.target.closest('.action-btn');
            const row = btn.closest('.table-row');
            const symbol = row.querySelector('.symbol-ticker')?.textContent;
            
            if (btn.title.includes('watchlist')) {
                handleAddToWatchlist(symbol);
            } else if (btn.title.includes('chart')) {
                handleViewChart(symbol);
            } else if (btn.title.includes('details')) {
                handleViewDetails(symbol);
            } else if (btn.title.includes('Trade')) {
                handleTrade(symbol);
            }
        }
    });
    
    function sortTable(table, column) {
        const tbody = table.querySelector('.table-body');
        const rows = Array.from(tbody.querySelectorAll('.table-row')).filter(row => !row.classList.contains('empty-row'));
        
        // Determine current sort direction
        const header = table.querySelector(`[data-column="${column}"]`);
        const currentSort = header.getAttribute('data-sort') || 'asc';
        const newSort = currentSort === 'asc' ? 'desc' : 'asc';
        
        // Clear all sort indicators
        table.querySelectorAll('.sortable').forEach(h => {
            h.removeAttribute('data-sort');
            h.querySelector('.sort-indicator').innerHTML = '<?php echo addslashes(rts_get_icon('chevrons-up-down', ['width' => '14', 'height' => '14'])); ?>';
        });
        
        // Set new sort indicator
        header.setAttribute('data-sort', newSort);
        const sortIcon = newSort === 'asc' ? 'chevron-up' : 'chevron-down';
        header.querySelector('.sort-indicator').innerHTML = `<?php echo addslashes(str_replace(['chevron-up', 'chevron-down'], ['{{ ICON }}'], rts_get_icon('{{ ICON }}', ['width' => '14', 'height' => '14']))); ?>`.replace('{{ ICON }}', sortIcon);
        
        // Sort rows
        rows.sort((a, b) => {
            const aCell = a.querySelector(`[data-column="${column}"] .cell-content, [data-column="${column}"] .symbol-ticker, [data-column="${column}"] .pl-amount`);
            const bCell = b.querySelector(`[data-column="${column}"] .cell-content, [data-column="${column}"] .symbol-ticker, [data-column="${column}"] .pl-amount`);
            
            let aValue = aCell ? aCell.textContent.trim() : '';
            let bValue = bCell ? bCell.textContent.trim() : '';
            
            // Handle numeric values
            if (column === 'price' || column === 'market_value' || column === 'shares') {
                aValue = parseFloat(aValue.replace(/[^0-9.-]+/g, '')) || 0;
                bValue = parseFloat(bValue.replace(/[^0-9.-]+/g, '')) || 0;
            }
            
            let result = 0;
            if (typeof aValue === 'number' && typeof bValue === 'number') {
                result = aValue - bValue;
            } else {
                result = aValue.localeCompare(bValue);
            }
            
            return newSort === 'desc' ? -result : result;
        });
        
        // Reorder DOM
        rows.forEach(row => tbody.appendChild(row));
    }
    
    function updateSelectAllState() {
        const checkedCount = table.querySelectorAll('.row-select:checked').length;
        const totalCount = table.querySelectorAll('.row-select').length;
        
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = checkedCount === totalCount && totalCount > 0;
            selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < totalCount;
        }
    }
    
    function updateBulkActions() {
        const checkedCount = table.querySelectorAll('.row-select:checked').length;
        
        if (bulkActions) {
            if (checkedCount > 0) {
                bulkActions.classList.remove('hidden');
                bulkActions.querySelector('.selection-count').textContent = `${checkedCount} items selected`;
            } else {
                bulkActions.classList.add('hidden');
            }
        }
    }
    
    function handleAddToWatchlist(symbol) {
        console.log('Adding to watchlist:', symbol);
        // Implement watchlist functionality
    }
    
    function handleViewChart(symbol) {
        console.log('View chart for:', symbol);
        // Implement chart view functionality
    }
    
    function handleViewDetails(symbol) {
        console.log('View details for:', symbol);
        // Implement details view functionality
    }
    
    function handleTrade(symbol) {
        console.log('Trade:', symbol);
        // Implement trade functionality
    }
}
</script>

<style>
/* Table Component Styles */
.table-container {
    position: relative;
    background: var(--surface-raised);
    border-radius: var(--radius-xl);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

.table-loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-md);
    z-index: 2;
}

.table-wrapper {
    overflow-x: auto;
    min-height: 200px;
}

.data-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
}

.table-header {
    background: var(--gray-50);
    position: sticky;
    top: 0;
    z-index: 1;
}

.table-header-cell {
    padding: var(--spacing-md) var(--spacing-lg);
    text-align: left;
    border-bottom: 1px solid var(--gray-200);
    font-weight: 600;
    font-size: var(--text-sm);
    color: var(--gray-700);
    white-space: nowrap;
}

.table-header-cell.sortable {
    cursor: pointer;
    user-select: none;
    transition: background-color var(--transition-fast) var(--easing-standard);
}

.table-header-cell.sortable:hover {
    background: var(--gray-100);
}

.header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--spacing-sm);
}

.sort-indicator {
    opacity: 0.5;
    transition: opacity var(--transition-fast) var(--easing-standard);
}

.sortable:hover .sort-indicator,
.sortable[data-sort] .sort-indicator {
    opacity: 1;
}

.table-row {
    transition: background-color var(--transition-fast) var(--easing-standard);
}

.table-row:hover {
    background: var(--gray-50);
}

.table-cell {
    padding: var(--spacing-md) var(--spacing-lg);
    border-bottom: 1px solid var(--gray-200);
    vertical-align: middle;
    position: relative;
}

.select-column,
.select-cell {
    width: 50px;
    text-align: center;
}

/* Cell-specific styles */
.symbol-cell {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.symbol-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.symbol-ticker {
    font-weight: 700;
    font-size: var(--text-sm);
    color: var(--gray-900);
}

.symbol-company {
    font-size: var(--text-xs);
    color: var(--gray-500);
    line-height: 1.2;
}

.pl-cell {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.pl-amount {
    font-weight: 600;
    font-size: var(--text-sm);
}

.pl-percent {
    font-size: var(--text-xs);
    opacity: 0.8;
}

.pl-amount.positive,
.pl-percent.positive {
    color: var(--success);
}

.pl-amount.negative,
.pl-percent.negative {
    color: var(--danger);
}

.action-buttons {
    display: flex;
    gap: var(--spacing-xs);
}

.action-btn {
    padding: var(--spacing-xs);
    min-width: 32px;
    aspect-ratio: 1;
}

/* Empty state */
.empty-cell {
    padding: var(--spacing-3xl);
    text-align: center;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-md);
    color: var(--gray-500);
}

.empty-icon {
    opacity: 0.5;
}

/* Pagination */
.table-pagination {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-lg);
    border-top: 1px solid var(--gray-200);
    background: var(--gray-50);
}

.pagination-controls {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.pagination-btn {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-sm) var(--spacing-md);
    background: transparent;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
}

.pagination-btn:hover:not(:disabled) {
    background: var(--gray-100);
}

.pagination-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.pagination-pages {
    display: flex;
    gap: var(--spacing-xs);
}

.page-btn {
    padding: var(--spacing-sm);
    min-width: 32px;
    background: transparent;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-md);
    cursor: pointer;
}

.page-btn.active {
    background: var(--primary-500);
    color: white;
    border-color: var(--primary-500);
}

/* Bulk actions */
.bulk-actions {
    position: fixed;
    bottom: var(--spacing-xl);
    left: 50%;
    transform: translateX(-50%);
    background: var(--surface-raised);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-lg);
    z-index: var(--z-sticky);
}

.bulk-actions-content {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
    padding: var(--spacing-md) var(--spacing-lg);
}

.selection-count {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--gray-700);
}

.bulk-action-buttons {
    display: flex;
    gap: var(--spacing-sm);
}

/* Mobile labels (hidden by default) */
.mobile-label {
    display: none;
}

/* Responsive design */
@media (max-width: 768px) {
    .table-responsive .table-wrapper {
        overflow: visible;
    }
    
    .table-responsive .data-table,
    .table-responsive .table-header,
    .table-responsive .table-body,
    .table-responsive .table-row,
    .table-responsive .table-header-cell,
    .table-responsive .table-cell {
        display: block;
    }
    
    .table-responsive .table-header {
        display: none;
    }
    
    .table-responsive .table-row {
        border: 1px solid var(--gray-200);
        border-radius: var(--radius-lg);
        margin-bottom: var(--spacing-md);
        padding: var(--spacing-md);
    }
    
    .table-responsive .table-cell {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--spacing-sm) 0;
        border-bottom: 1px solid var(--gray-100);
    }
    
    .table-responsive .table-cell:last-child {
        border-bottom: none;
    }
    
    .table-responsive .mobile-label {
        display: block;
        font-weight: 600;
        font-size: var(--text-sm);
        color: var(--gray-600);
    }
    
    .table-responsive .select-cell,
    .table-responsive .select-column {
        display: none;
    }
    
    .table-pagination {
        flex-direction: column;
        gap: var(--spacing-md);
        align-items: center;
    }
}

/* Dark mode adjustments */
[data-theme="dark"] .table-container {
    background: var(--gray-800);
}

[data-theme="dark"] .table-header {
    background: var(--gray-900);
}

[data-theme="dark"] .table-header-cell {
    color: var(--gray-300);
    border-color: var(--gray-700);
}

[data-theme="dark"] .table-row:hover {
    background: var(--gray-700);
}

[data-theme="dark"] .table-cell {
    border-color: var(--gray-700);
}

[data-theme="dark"] .symbol-ticker {
    color: var(--gray-100);
}

[data-theme="dark"] .symbol-company {
    color: var(--gray-400);
}

[data-theme="dark"] .table-pagination {
    background: var(--gray-900);
    border-color: var(--gray-700);
}

[data-theme="dark"] .bulk-actions {
    background: var(--gray-800);
    border-color: var(--gray-700);
}
</style>