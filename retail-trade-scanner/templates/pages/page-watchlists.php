<?php
/**
 * Template Name: Watchlists
 * 
 * Create and organize stock watchlists with quick actions and alert integration
 *
 * @package RetailTradeScanner
 */

// Restrict to logged-in users
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header();

// Sample watchlists and items (placeholder data for UI)
$watchlists = array(
    array(
        'id' => 'wl-1',
        'name' => 'Momentum Plays',
        'description' => 'High RSI, strong volume, near breakout levels',
        'count' => 8,
        'last_updated' => 'Today 2:10 PM'
    ),
    array(
        'id' => 'wl-2',
        'name' => 'Dividend Kings',
        'description' => 'Reliable dividend payers with low volatility',
        'count' => 12,
        'last_updated' => 'Yesterday 5:42 PM'
    ),
    array(
        'id' => 'wl-3',
        'name' => 'AI & Chips',
        'description' => 'Semiconductors and AI leaders',
        'count' => 6,
        'last_updated' => 'Today 12:03 PM'
    )
);

$selected_watchlist = 'wl-3';

$watchlist_items = array(
    array(
        'symbol' => 'NVDA',
        'company' => 'NVIDIA Corporation',
        'price' => '$456.78',
        'change' => '+3.67%',
        'volume' => '35.7M',
        'market_cap' => '1.12T',
        'rsi' => '72.5',
        'type' => 'positive'
    ),
    array(
        'symbol' => 'AMD',
        'company' => 'Advanced Micro Devices, Inc.',
        'price' => '$168.24',
        'change' => '+1.12%',
        'volume' => '21.4M',
        'market_cap' => '270.3B',
        'rsi' => '64.1',
        'type' => 'positive'
    ),
    array(
        'symbol' => 'TSM',
        'company' => 'Taiwan Semiconductor MFG',
        'price' => '$152.19',
        'change' => '-0.58%',
        'volume' => '9.2M',
        'market_cap' => '790.6B',
        'rsi' => '58.9',
        'type' => 'negative'
    )
);

$layout_args = array(
    'page_title' => __('Watchlists', 'retail-trade-scanner'),
    'page_description' => __('Track symbols you care about and get notified on key moves', 'retail-trade-scanner'),
    'page_class' => 'watchlists-page',
    'header_actions' => array(
        array(
            'text' => __('New Watchlist', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'plus'
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<!-- Overview Cards -->
<div class="grid grid-4 gap-lg mb-2xl">
    <div class="glass-card dashboard-widget">
        <div class="widget-header">
            <h3 class="widget-title"><?php esc_html_e('Total Watchlists', 'retail-trade-scanner'); ?></h3>
            <div class="widget-actions">
                <button class="btn btn-ghost btn-sm create-watchlist">
                    <?php echo rts_get_icon('plus', ['width' => '16', 'height' => '16']); ?>
                </button>
            </div>
        </div>
        <div class="widget-content">
            <div class="kpi-value"><?php echo count($watchlists); ?></div>
            <div class="kpi-meta"><?php esc_html_e('Manage lists for different strategies', 'retail-trade-scanner'); ?></div>
        </div>
    </div>

    <div class="glass-card dashboard-widget">
        <div class="widget-header">
            <h3 class="widget-title"><?php esc_html_e('Tracked Symbols', 'retail-trade-scanner'); ?></h3>
        </div>
        <div class="widget-content">
            <div class="kpi-value">26</div>
            <div class="kpi-meta"><?php esc_html_e('Across all watchlists', 'retail-trade-scanner'); ?></div>
        </div>
    </div>

    <div class="glass-card dashboard-widget">
        <div class="widget-header">
            <h3 class="widget-title"><?php esc_html_e('Active Alerts', 'retail-trade-scanner'); ?></h3>
            <div class="widget-actions">
                <a class="btn btn-outline btn-sm" href="<?php echo esc_url(home_url('/alerts/')); ?>">
                    <?php echo rts_get_icon('bell', ['width' => '14', 'height' => '14']); ?>
                    <?php esc_html_e('Manage', 'retail-trade-scanner'); ?>
                </a>
            </div>
        </div>
        <div class="widget-content">
            <div class="kpi-value">12</div>
            <div class="kpi-meta"><?php esc_html_e('Linked to watchlist items', 'retail-trade-scanner'); ?></div>
        </div>
    </div>

    <div class="glass-card dashboard-widget">
        <div class="widget-header">
            <h3 class="widget-title"><?php esc_html_e('Today\'s Movers', 'retail-trade-scanner'); ?></h3>
        </div>
        <div class="widget-content">
            <div class="kpi-value">5</div>
            <div class="kpi-meta">
                <span class="status-indicator status-online"><?php esc_html_e('Market Open', 'retail-trade-scanner'); ?></span>
            </div>
        </div>
    </div>
</div>

<div class="grid grid-cols-12 gap-lg">
    <!-- Watchlists Sidebar -->
    <aside class="col-span-3">
        <div class="card glass-card">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Your Watchlists', 'retail-trade-scanner'); ?></h3>
                <button class="btn btn-ghost btn-sm create-watchlist">
                    <?php echo rts_get_icon('plus', ['width' => '16', 'height' => '16']); ?>
                    <?php esc_html_e('New', 'retail-trade-scanner'); ?>
                </button>
            </div>
            <div class="card-body">
                <ul class="watchlist-list">
                    <?php foreach ($watchlists as $wl) : ?>
                        <li class="watchlist-item <?php echo $selected_watchlist === $wl['id'] ? 'active' : ''; ?>" data-id="<?php echo esc_attr($wl['id']); ?>">
                            <button class="watchlist-link">
                                <div class="wl-info">
                                    <div class="wl-name"><?php echo esc_html($wl['name']); ?></div>
                                    <div class="wl-desc text-sm text-muted"><?php echo esc_html($wl['description']); ?></div>
                                </div>
                                <div class="wl-meta">
                                    <span class="wl-count badge"><?php echo esc_html($wl['count']); ?></span>
                                    <span class="wl-updated text-xs text-muted"><?php echo esc_html($wl['last_updated']); ?></span>
                                </div>
                            </button>
                            <div class="wl-actions">
                                <button class="btn btn-ghost btn-xs rename-wl" title="<?php esc_attr_e('Rename', 'retail-trade-scanner'); ?>"><?php echo rts_get_icon('edit', ['width' => '14', 'height' => '14']); ?></button>
                                <button class="btn btn-ghost btn-xs delete-wl" title="<?php esc_attr_e('Delete', 'retail-trade-scanner'); ?>"><?php echo rts_get_icon('trash', ['width' => '14', 'height' => '14']); ?></button>
                            </div>
                        </li>
                    <?php endforeach; ?>
                </ul>
            </div>
        </div>

        <!-- Quick Add Symbol -->
        <div class="card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('Quick Add', 'retail-trade-scanner'); ?></h3>
            </div>
            <div class="card-body">
                <form class="quick-add-form">
                    <label class="form-label" for="quick-symbol"><?php esc_html_e('Symbol', 'retail-trade-scanner'); ?></label>
                    <input id="quick-symbol" class="form-input" type="text" placeholder="<?php esc_attr_e('e.g., AAPL', 'retail-trade-scanner'); ?>" autocomplete="off">
                    <div class="symbol-suggestions hidden"></div>
                    <button type="button" class="btn btn-primary mt-md add-symbol-btn">
                        <?php echo rts_get_icon('plus', ['width' => '16', 'height' => '16']); ?>
                        <?php esc_html_e('Add to Current List', 'retail-trade-scanner'); ?>
                    </button>
                </form>
            </div>
        </div>
    </aside>

    <!-- Watchlist Details -->
    <section class="col-span-9">
        <div class="card glass-card">
            <div class="card-header">
                <div class="card-title with-sub">
                    <h3 class="m-0"><?php esc_html_e('AI & Chips', 'retail-trade-scanner'); ?></h3>
                    <p class="text-sm text-muted m-0"><?php esc_html_e('Semiconductors and AI leaders', 'retail-trade-scanner'); ?></p>
                </div>
                <div class="card-actions">
                    <button class="btn btn-ghost btn-sm">
                        <?php echo rts_get_icon('refresh', ['width' => '16', 'height' => '16']); ?>
                        <?php esc_html_e('Refresh', 'retail-trade-scanner'); ?>
                    </button>
                    <button class="btn btn-outline btn-sm">
                        <?php echo rts_get_icon('download', ['width' => '16', 'height' => '16']); ?>
                        <?php esc_html_e('Export', 'retail-trade-scanner'); ?>
                    </button>
                    <button class="btn btn-primary btn-sm set-alerts">
                        <?php echo rts_get_icon('bell', ['width' => '16', 'height' => '16']); ?>
                        <?php esc_html_e('Set Alerts', 'retail-trade-scanner'); ?>
                    </button>
                </div>
            </div>

            <div class="card-body">
                <?php
                get_template_part('template-parts/components/table', null, array(
                    'id' => 'watchlist-table',
                    'headers' => array(
                        'symbol' => __('Symbol', 'retail-trade-scanner'),
                        'price' => __('Price', 'retail-trade-scanner'),
                        'change' => __('Change', 'retail-trade-scanner'),
                        'volume' => __('Volume', 'retail-trade-scanner'),
                        'market_cap' => __('Market Cap', 'retail-trade-scanner'),
                        'rsi' => __('RSI', 'retail-trade-scanner'),
                        'actions' => __('Actions', 'retail-trade-scanner')
                    ),
                    'data' => $watchlist_items,
                    'sortable' => true,
                    'selectable' => true,
                    'pagination' => false,
                    'variant' => 'scanner',
                    'empty_message' => __('No symbols in this watchlist yet', 'retail-trade-scanner')
                ));
                ?>
            </div>
        </div>

        <!-- Bulk Actions Bar -->
        <div class="bulk-actions glass-card mt-lg">
            <div class="bulk-info">
                <span class="selected-count">0</span>
                <span class="text-muted"><?php esc_html_e('selected', 'retail-trade-scanner'); ?></span>
            </div>
            <div class="bulk-buttons">
                <button class="btn btn-ghost btn-sm"><?php echo rts_get_icon('bookmark', ['width' => '14', 'height' => '14']); ?> <?php esc_html_e('Move to...', 'retail-trade-scanner'); ?></button>
                <button class="btn btn-ghost btn-sm"><?php echo rts_get_icon('bell', ['width' => '14', 'height' => '14']); ?> <?php esc_html_e('Create Alerts', 'retail-trade-scanner'); ?></button>
                <button class="btn btn-danger btn-sm"><?php echo rts_get_icon('trash', ['width' => '14', 'height' => '14']); ?> <?php esc_html_e('Remove', 'retail-trade-scanner'); ?></button>
            </div>
        </div>
    </section>
</div>

<!-- Create/Rename Watchlist Modal (structure only) -->
<div class="modal-overlay hidden" data-modal="watchlist-modal" aria-hidden="true">
    <div class="modal glass-card" role="dialog" aria-modal="true">
        <div class="modal-header">
            <h3 class="modal-title"><?php esc_html_e('New Watchlist', 'retail-trade-scanner'); ?></h3>
            <button class="btn btn-ghost btn-sm close-modal" aria-label="<?php esc_attr_e('Close', 'retail-trade-scanner'); ?>">
                <?php echo rts_get_icon('close', ['width' => '16', 'height' => '16']); ?>
            </button>
        </div>
        <div class="modal-body">
            <div class="form-group">
                <label class="form-label" for="wl-name"><?php esc_html_e('Name', 'retail-trade-scanner'); ?></label>
                <input id="wl-name" type="text" class="form-input" placeholder="<?php esc_attr_e('e.g., Growth Stocks', 'retail-trade-scanner'); ?>">
            </div>
            <div class="form-group">
                <label class="form-label" for="wl-desc"><?php esc_html_e('Description (optional)', 'retail-trade-scanner'); ?></label>
                <textarea id="wl-desc" class="form-textarea" rows="3" placeholder="<?php esc_attr_e('Short description', 'retail-trade-scanner'); ?>"></textarea>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-ghost close-modal"><?php esc_html_e('Cancel', 'retail-trade-scanner'); ?></button>
            <button class="btn btn-primary save-watchlist"><?php esc_html_e('Create', 'retail-trade-scanner'); ?></button>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Toggle active watchlist selection
    document.querySelectorAll('.watchlist-item .watchlist-link').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.watchlist-item').forEach(i => i.classList.remove('active'));
            this.closest('.watchlist-item').classList.add('active');
        });
    });

    // Bulk selection count (demo)
    const table = document.getElementById('watchlist-table');
    if (table) {
        table.addEventListener('change', function(e) {
            if (e.target.classList.contains('row-select') || e.target.classList.contains('select-all')) {
                updateSelectedCount();
            }
        });
    }

    function updateSelectedCount() {
        const selected = document.querySelectorAll('#watchlist-table .row-select:checked').length;
        const countEl = document.querySelector('.bulk-actions .selected-count');
        if (countEl) countEl.textContent = selected;
    }

    // Modal controls (lightweight demo)
    document.querySelectorAll('.create-watchlist').forEach(btn => btn.addEventListener('click', openModal));
    document.querySelectorAll('.close-modal').forEach(btn => btn.addEventListener('click', closeModal));
    document.querySelector('[data-modal="watchlist-modal"]').addEventListener('click', function(e) {
        if (e.target === this) closeModal();
    });

    function openModal() {
        const modal = document.querySelector('[data-modal="watchlist-modal"]');
        if (!modal) return;
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        modal.querySelector('#wl-name')?.focus();
    }
    function closeModal() {
        const modal = document.querySelector('[data-modal="watchlist-modal"]');
        if (!modal) return;
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
});
</script>

<style>
/* Watchlists page styles */
.watchlist-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: var(--spacing-sm); }
.watchlist-item { position: relative; border: 1px solid var(--gray-200); border-radius: var(--radius-xl); overflow: hidden; background: var(--surface-raised); }
.watchlist-item.active { outline: 2px solid var(--primary-300); box-shadow: var(--shadow-md); }
.watchlist-link { width: 100%; display: flex; align-items: flex-start; justify-content: space-between; gap: var(--spacing-md); text-align: left; padding: var(--spacing-md); border: 0; background: transparent; cursor: pointer; }
.wl-info { display: flex; flex-direction: column; gap: 4px; }
.wl-name { font-weight: 700; color: var(--gray-900); }
.wl-meta { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.wl-actions { position: absolute; right: var(--spacing-sm); bottom: var(--spacing-sm); display: flex; gap: var(--spacing-xs); }

.bulk-actions { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-md) var(--spacing-lg); }
.badge { background: var(--gray-100); color: var(--gray-700); padding: 2px 8px; border-radius: var(--radius-full); font-size: var(--text-xs); font-weight: 700; }

/* Dark mode */
[data-theme="dark"] .watchlist-item { background: var(--gray-800); border-color: var(--gray-700); }
[data-theme="dark"] .badge { background: var(--gray-700); color: var(--gray-200); }
</style>

<?php get_template_part('template-parts/layout/main-shell-end'); ?>

<?php get_footer(); ?>