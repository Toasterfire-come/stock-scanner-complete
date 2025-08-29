<?php
/**
 * Template Name: Filters
 * 
 * Presets list, custom builder UI, and save preset functionality
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('Filter Manager', 'retail-trade-scanner'),
    'page_description' => __('Create, manage, and apply custom filters for stock screening', 'retail-trade-scanner'),
    'page_class' => 'filters-page',
    'header_actions' => array(
        array(
            'text' => __('Import Filters', 'retail-trade-scanner'),
            'variant' => 'outline',
            'icon' => 'upload'
        ),
        array(
            'text' => __('Create New Filter', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'plus'
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

// Sample filter presets
$filter_presets = array(
    array(
        'id' => 1,
        'name' => 'High Momentum Stocks',
        'description' => 'Stocks with strong price momentum and high relative strength',
        'criteria' => array('RSI > 60', 'Price > 50-day MA', 'Volume > Average'),
        'results_count' => 234,
        'category' => 'momentum',
        'created' => '2024-01-15',
        'last_used' => '2024-01-20',
        'popularity' => 85,
        'author' => 'System'
    ),
    array(
        'id' => 2,
        'name' => 'Value Opportunities',
        'description' => 'Undervalued stocks with strong fundamentals and low P/E ratios',
        'criteria' => array('P/E < 15', 'P/B < 2', 'Debt/Equity < 0.5'),
        'results_count' => 156,
        'category' => 'value',
        'created' => '2024-01-10',
        'last_used' => '2024-01-19',
        'popularity' => 72,
        'author' => 'System'
    ),
    array(
        'id' => 3,
        'name' => 'Dividend Aristocrats',
        'description' => 'High-quality dividend stocks with consistent payout growth',
        'criteria' => array('Dividend Yield > 3%', '25+ Years Growth', 'Payout Ratio < 60%'),
        'results_count' => 67,
        'category' => 'dividend',
        'created' => '2024-01-08',
        'last_used' => '2024-01-18',
        'popularity' => 91,
        'author' => 'System'
    ),
    array(
        'id' => 4,
        'name' => 'Growth Champions',
        'description' => 'Fast-growing companies with strong revenue and earnings growth',
        'criteria' => array('Revenue Growth > 20%', 'EPS Growth > 15%', 'ROE > 15%'),
        'results_count' => 189,
        'category' => 'growth',
        'created' => '2024-01-12',
        'last_used' => '2024-01-17',
        'popularity' => 78,
        'author' => 'System'
    ),
    array(
        'id' => 5,
        'name' => 'Breakout Patterns',
        'description' => 'Stocks showing technical breakout patterns with volume confirmation',
        'criteria' => array('Price near 52W High', 'Volume Spike > 150%', 'MACD Bullish'),
        'results_count' => 98,
        'category' => 'technical',
        'created' => '2024-01-14',
        'last_used' => '2024-01-16',
        'popularity' => 63,
        'author' => 'User'
    ),
    array(
        'id' => 6,
        'name' => 'ESG Leaders',
        'description' => 'Companies with strong ESG ratings and sustainable practices',
        'criteria' => array('ESG Score > 80', 'Carbon Footprint Low', 'Governance Score > 85'),
        'results_count' => 145,
        'category' => 'esg',
        'created' => '2024-01-11',
        'last_used' => '2024-01-15',
        'popularity' => 54,
        'author' => 'System'
    )
);

$filter_categories = array(
    'all' => __('All Filters', 'retail-trade-scanner'),
    'momentum' => __('Momentum', 'retail-trade-scanner'),
    'value' => __('Value', 'retail-trade-scanner'),
    'growth' => __('Growth', 'retail-trade-scanner'),
    'dividend' => __('Dividend', 'retail-trade-scanner'),
    'technical' => __('Technical', 'retail-trade-scanner'),
    'esg' => __('ESG', 'retail-trade-scanner')
);
?>

<div class="filters-layout">
    <!-- Filter Categories -->
    <section class="filter-categories">
        <div class="categories-container">
            <div class="category-tabs">
                <?php foreach ($filter_categories as $key => $label) : ?>
                    <button class="category-tab <?php echo $key === 'all' ? 'active' : ''; ?>" 
                            data-category="<?php echo esc_attr($key); ?>">
                        <?php if ($key !== 'all') : ?>
                            <?php 
                            $icons = array(
                                'momentum' => 'trending-up',
                                'value' => 'dollar-sign',
                                'growth' => 'bar-chart',
                                'dividend' => 'percent',
                                'technical' => 'activity',
                                'esg' => 'leaf'
                            );
                            echo rts_get_icon($icons[$key], ['width' => '18', 'height' => '18']); 
                            ?>
                        <?php endif; ?>
                        <span><?php echo esc_html($label); ?></span>
                        <span class="category-count">
                            <?php echo count(array_filter($filter_presets, function($preset) use ($key) {
                                return $key === 'all' || $preset['category'] === $key;
                            })); ?>
                        </span>
                    </button>
                <?php endforeach; ?>
            </div>
            
            <div class="category-actions">
                <div class="search-filters">
                    <input type="text" 
                           class="search-input" 
                           placeholder="<?php esc_attr_e('Search filters...', 'retail-trade-scanner'); ?>">
                    <?php echo rts_get_icon('search', ['width' => '16', 'height' => '16', 'class' => 'search-icon']); ?>
                </div>
                
                <select class="sort-select form-select">
                    <option value="popularity"><?php esc_html_e('Sort by Popularity', 'retail-trade-scanner'); ?></option>
                    <option value="name"><?php esc_html_e('Name A-Z', 'retail-trade-scanner'); ?></option>
                    <option value="created"><?php esc_html_e('Recently Created', 'retail-trade-scanner'); ?></option>
                    <option value="used"><?php esc_html_e('Recently Used', 'retail-trade-scanner'); ?></option>
                    <option value="results"><?php esc_html_e('Result Count', 'retail-trade-scanner'); ?></option>
                </select>
            </div>
        </div>
    </section>

    <!-- Filter Presets Grid -->
    <section class="filter-presets">
        <div class="presets-grid" id="presets-grid">
            <?php foreach ($filter_presets as $index => $preset) : ?>
                <div class="preset-card card animate-fade-up" 
                     style="animation-delay: <?php echo $index * 0.1; ?>s;"
                     data-category="<?php echo esc_attr($preset['category']); ?>"
                     data-preset-id="<?php echo esc_attr($preset['id']); ?>">
                    
                    <div class="preset-header">
                        <div class="preset-meta">
                            <div class="preset-category">
                                <?php 
                                $category_icons = array(
                                    'momentum' => 'trending-up',
                                    'value' => 'dollar-sign',
                                    'growth' => 'bar-chart',
                                    'dividend' => 'percent',
                                    'technical' => 'activity',
                                    'esg' => 'leaf'
                                );
                                echo rts_get_icon($category_icons[$preset['category']], ['width' => '16', 'height' => '16']);
                                ?>
                                <span><?php echo esc_html(ucfirst($preset['category'])); ?></span>
                            </div>
                            <div class="preset-popularity">
                                <div class="popularity-bar">
                                    <div class="popularity-fill" style="width: <?php echo esc_attr($preset['popularity']); ?>%"></div>
                                </div>
                                <span><?php echo esc_html($preset['popularity']); ?>%</span>
                            </div>
                        </div>
                        
                        <div class="preset-actions">
                            <button class="btn btn-ghost btn-icon favorite-btn" 
                                    title="<?php esc_attr_e('Add to Favorites', 'retail-trade-scanner'); ?>">
                                <?php echo rts_get_icon('heart', ['width' => '16', 'height' => '16']); ?>
                            </button>
                            <div class="preset-menu">
                                <button class="btn btn-ghost btn-icon menu-btn">
                                    <?php echo rts_get_icon('more-horizontal', ['width' => '16', 'height' => '16']); ?>
                                </button>
                                <div class="menu-dropdown hidden">
                                    <button class="menu-item edit-preset">
                                        <?php echo rts_get_icon('edit', ['width' => '14', 'height' => '14']); ?>
                                        <?php esc_html_e('Edit', 'retail-trade-scanner'); ?>
                                    </button>
                                    <button class="menu-item duplicate-preset">
                                        <?php echo rts_get_icon('copy', ['width' => '14', 'height' => '14']); ?>
                                        <?php esc_html_e('Duplicate', 'retail-trade-scanner'); ?>
                                    </button>
                                    <button class="menu-item export-preset">
                                        <?php echo rts_get_icon('download', ['width' => '14', 'height' => '14']); ?>
                                        <?php esc_html_e('Export', 'retail-trade-scanner'); ?>
                                    </button>
                                    <button class="menu-item delete-preset text-danger">
                                        <?php echo rts_get_icon('trash', ['width' => '14', 'height' => '14']); ?>
                                        <?php esc_html_e('Delete', 'retail-trade-scanner'); ?>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="preset-content">
                        <h3 class="preset-name"><?php echo esc_html($preset['name']); ?></h3>
                        <p class="preset-description"><?php echo esc_html($preset['description']); ?></p>
                        
                        <div class="preset-criteria">
                            <?php foreach ($preset['criteria'] as $criterion) : ?>
                                <span class="criterion-tag"><?php echo esc_html($criterion); ?></span>
                            <?php endforeach; ?>
                        </div>
                    </div>
                    
                    <div class="preset-footer">
                        <div class="preset-stats">
                            <div class="stat-item">
                                <span class="stat-label"><?php esc_html_e('Results:', 'retail-trade-scanner'); ?></span>
                                <span class="stat-value"><?php echo esc_html($preset['results_count']); ?></span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label"><?php esc_html_e('Updated:', 'retail-trade-scanner'); ?></span>
                                <span class="stat-value"><?php echo esc_html(date('M j', strtotime($preset['last_used']))); ?></span>
                            </div>
                        </div>
                        
                        <div class="preset-buttons">
                            <button class="btn btn-outline btn-sm preview-preset">
                                <?php echo rts_get_icon('eye', ['width' => '14', 'height' => '14']); ?>
                                <?php esc_html_e('Preview', 'retail-trade-scanner'); ?>
                            </button>
                            <button class="btn btn-primary btn-sm apply-preset">
                                <?php echo rts_get_icon('play', ['width' => '14', 'height' => '14']); ?>
                                <?php esc_html_e('Apply', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
        
        <!-- Empty State -->
        <div class="empty-state hidden" id="empty-state">
            <div class="empty-content">
                <?php echo rts_get_icon('filter', ['width' => '48', 'height' => '48', 'class' => 'empty-icon']); ?>
                <h3><?php esc_html_e('No Filters Found', 'retail-trade-scanner'); ?></h3>
                <p><?php esc_html_e('No filters match your current search or category selection.', 'retail-trade-scanner'); ?></p>
                <button class="btn btn-primary create-filter-btn">
                    <?php echo rts_get_icon('plus', ['width' => '16', 'height' => '16']); ?>
                    <?php esc_html_e('Create New Filter', 'retail-trade-scanner'); ?>
                </button>
            </div>
        </div>
    </section>

    <!-- Filter Builder Modal -->
    <div class="filter-builder-modal modal hidden" id="filter-builder-modal">
        <div class="modal-backdrop"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title"><?php esc_html_e('Create New Filter', 'retail-trade-scanner'); ?></h3>
                <button class="modal-close">
                    <?php echo rts_get_icon('x', ['width' => '20', 'height' => '20']); ?>
                </button>
            </div>
            
            <div class="modal-body">
                <div class="builder-form">
                    <div class="form-section">
                        <h4><?php esc_html_e('Filter Information', 'retail-trade-scanner'); ?></h4>
                        <div class="form-grid">
                            <div class="form-field">
                                <label class="form-label" for="filter-name">
                                    <?php esc_html_e('Filter Name', 'retail-trade-scanner'); ?>
                                </label>
                                <input type="text" 
                                       id="filter-name" 
                                       class="form-input" 
                                       placeholder="<?php esc_attr_e('Enter filter name...', 'retail-trade-scanner'); ?>">
                            </div>
                            <div class="form-field">
                                <label class="form-label" for="filter-category">
                                    <?php esc_html_e('Category', 'retail-trade-scanner'); ?>
                                </label>
                                <select id="filter-category" class="form-select">
                                    <option value="momentum"><?php esc_html_e('Momentum', 'retail-trade-scanner'); ?></option>
                                    <option value="value"><?php esc_html_e('Value', 'retail-trade-scanner'); ?></option>
                                    <option value="growth"><?php esc_html_e('Growth', 'retail-trade-scanner'); ?></option>
                                    <option value="dividend"><?php esc_html_e('Dividend', 'retail-trade-scanner'); ?></option>
                                    <option value="technical"><?php esc_html_e('Technical', 'retail-trade-scanner'); ?></option>
                                    <option value="esg"><?php esc_html_e('ESG', 'retail-trade-scanner'); ?></option>
                                </select>
                            </div>
                        </div>
                        <div class="form-field">
                            <label class="form-label" for="filter-description">
                                <?php esc_html_e('Description', 'retail-trade-scanner'); ?>
                            </label>
                            <textarea id="filter-description" 
                                      class="form-textarea" 
                                      rows="3"
                                      placeholder="<?php esc_attr_e('Describe what this filter does...', 'retail-trade-scanner'); ?>"></textarea>
                        </div>
                    </div>
                    
                    <div class="form-section">
                        <h4><?php esc_html_e('Filter Criteria', 'retail-trade-scanner'); ?></h4>
                        <div class="criteria-builder">
                            <div class="criteria-list" id="criteria-list">
                                <!-- Dynamic criteria will be added here -->
                            </div>
                            <button class="btn btn-outline add-criterion">
                                <?php echo rts_get_icon('plus', ['width' => '16', 'height' => '16']); ?>
                                <?php esc_html_e('Add Criterion', 'retail-trade-scanner'); ?>
                            </button>
                        </div>
                    </div>
                    
                    <div class="form-section">
                        <h4><?php esc_html_e('Preview Results', 'retail-trade-scanner'); ?></h4>
                        <div class="preview-container">
                            <div class="preview-stats">
                                <div class="stat-card">
                                    <span class="stat-number" id="preview-count">--</span>
                                    <span class="stat-label"><?php esc_html_e('Matching Stocks', 'retail-trade-scanner'); ?></span>
                                </div>
                                <button class="btn btn-ghost btn-sm refresh-preview">
                                    <?php echo rts_get_icon('refresh', ['width' => '16', 'height' => '16']); ?>
                                    <?php esc_html_e('Refresh', 'retail-trade-scanner'); ?>
                                </button>
                            </div>
                            <div class="preview-chart">
                                <canvas id="preview-chart" width="300" height="150"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="modal-footer">
                <button class="btn btn-ghost cancel-filter">
                    <?php esc_html_e('Cancel', 'retail-trade-scanner'); ?>
                </button>
                <button class="btn btn-outline save-draft">
                    <?php esc_html_e('Save Draft', 'retail-trade-scanner'); ?>
                </button>
                <button class="btn btn-primary save-filter">
                    <?php echo rts_get_icon('save', ['width' => '16', 'height' => '16']); ?>
                    <?php esc_html_e('Save Filter', 'retail-trade-scanner'); ?>
                </button>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Filter page functionality
    const categoryTabs = document.querySelectorAll('.category-tab');
    const presetCards = document.querySelectorAll('.preset-card');
    const searchInput = document.querySelector('.search-input');
    const sortSelect = document.querySelector('.sort-select');
    const presetsGrid = document.getElementById('presets-grid');
    const emptyState = document.getElementById('empty-state');
    const filterBuilderModal = document.getElementById('filter-builder-modal');
    
    let currentCategory = 'all';
    let currentSearch = '';
    let currentSort = 'popularity';
    
    // Category filtering
    categoryTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            categoryTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            currentCategory = this.dataset.category;
            filterPresets();
        });
    });
    
    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            currentSearch = this.value.toLowerCase();
            filterPresets();
        });
    }
    
    // Sort functionality
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            currentSort = this.value;
            sortPresets();
        });
    }
    
    // Preset card interactions
    document.addEventListener('click', function(e) {
        // Apply preset
        if (e.target.closest('.apply-preset')) {
            const card = e.target.closest('.preset-card');
            const presetId = card.dataset.presetId;
            applyPreset(presetId);
        }
        
        // Preview preset
        if (e.target.closest('.preview-preset')) {
            const card = e.target.closest('.preset-card');
            const presetId = card.dataset.presetId;
            previewPreset(presetId);
        }
        
        // Favorite toggle
        if (e.target.closest('.favorite-btn')) {
            const btn = e.target.closest('.favorite-btn');
            toggleFavorite(btn);
        }
        
        // Menu toggle
        if (e.target.closest('.menu-btn')) {
            const menu = e.target.closest('.preset-menu').querySelector('.menu-dropdown');
            toggleMenu(menu);
        }
        
        // Create new filter
        if (e.target.closest('.create-filter-btn') || e.target.closest('[data-variant="primary"]')) {
            openFilterBuilder();
        }
        
        // Modal close
        if (e.target.closest('.modal-close') || e.target.closest('.modal-backdrop')) {
            closeModal();
        }
        
        // Add criterion
        if (e.target.closest('.add-criterion')) {
            addCriterion();
        }
    });
    
    function filterPresets() {
        let visibleCount = 0;
        
        presetCards.forEach(card => {
            const cardCategory = card.dataset.category;
            const cardName = card.querySelector('.preset-name').textContent.toLowerCase();
            const cardDescription = card.querySelector('.preset-description').textContent.toLowerCase();
            
            const matchesCategory = currentCategory === 'all' || cardCategory === currentCategory;
            const matchesSearch = currentSearch === '' || 
                                cardName.includes(currentSearch) || 
                                cardDescription.includes(currentSearch);
            
            if (matchesCategory && matchesSearch) {
                card.classList.remove('hidden');
                visibleCount++;
            } else {
                card.classList.add('hidden');
            }
        });
        
        // Show/hide empty state
        if (visibleCount === 0) {
            emptyState.classList.remove('hidden');
            presetsGrid.classList.add('hidden');
        } else {
            emptyState.classList.add('hidden');
            presetsGrid.classList.remove('hidden');
        }
    }
    
    function sortPresets() {
        const cards = Array.from(presetCards);
        const parent = cards[0].parentNode;
        
        cards.sort((a, b) => {
            const aId = parseInt(a.dataset.presetId);
            const bId = parseInt(b.dataset.presetId);
            
            // Find preset data
            const aData = getPresetData(aId);
            const bData = getPresetData(bId);
            
            switch (currentSort) {
                case 'name':
                    return aData.name.localeCompare(bData.name);
                case 'created':
                    return new Date(bData.created) - new Date(aData.created);
                case 'used':
                    return new Date(bData.last_used) - new Date(aData.last_used);
                case 'results':
                    return bData.results_count - aData.results_count;
                case 'popularity':
                default:
                    return bData.popularity - aData.popularity;
            }
        });
        
        // Re-append in sorted order
        cards.forEach(card => parent.appendChild(card));
    }
    
    function applyPreset(presetId) {
        const btn = document.querySelector(`[data-preset-id="${presetId}"] .apply-preset`);
        btn.classList.add('loading');
        btn.disabled = true;
        
        // Simulate applying preset
        setTimeout(() => {
            btn.classList.remove('loading');
            btn.disabled = false;
            
            RTS.showSuccess('Filter applied successfully!');
            
            // Redirect to scanner with applied filter
            window.location.href = '/scanner/?preset=' + presetId;
        }, 1500);
    }
    
    function previewPreset(presetId) {
        // Open preview modal or panel
        RTS.showInfo(`Previewing filter ${presetId}`);
        // Implementation would show a preview of results
    }
    
    function toggleFavorite(btn) {
        btn.classList.toggle('favorited');
        const icon = btn.querySelector('svg');
        
        if (btn.classList.contains('favorited')) {
            btn.style.color = '#ef4444';
            RTS.showSuccess('Added to favorites');
        } else {
            btn.style.color = '';
            RTS.showInfo('Removed from favorites');
        }
    }
    
    function toggleMenu(menu) {
        // Close other menus first
        document.querySelectorAll('.menu-dropdown').forEach(m => {
            if (m !== menu) m.classList.add('hidden');
        });
        
        menu.classList.toggle('hidden');
    }
    
    function openFilterBuilder() {
        filterBuilderModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        // Reset form
        resetBuilderForm();
        
        // Add initial criterion
        addCriterion();
    }
    
    function closeModal() {
        filterBuilderModal.classList.add('hidden');
        document.body.style.overflow = '';
    }
    
    function resetBuilderForm() {
        document.getElementById('filter-name').value = '';
        document.getElementById('filter-description').value = '';
        document.getElementById('filter-category').selectedIndex = 0;
        document.getElementById('criteria-list').innerHTML = '';
        document.getElementById('preview-count').textContent = '--';
    }
    
    function addCriterion() {
        const criteriaList = document.getElementById('criteria-list');
        const criterionId = 'criterion-' + Date.now();
        
        const criterion = document.createElement('div');
        criterion.className = 'criterion-item';
        criterion.innerHTML = `
            <div class="criterion-fields">
                <select class="form-select criterion-metric">
                    <option value="">Select Metric</option>
                    <option value="price">Price</option>
                    <option value="market_cap">Market Cap</option>
                    <option value="pe_ratio">P/E Ratio</option>
                    <option value="dividend_yield">Dividend Yield</option>
                    <option value="rsi">RSI</option>
                    <option value="volume">Volume</option>
                </select>
                
                <select class="form-select criterion-operator">
                    <option value="">Operator</option>
                    <option value="gt">Greater than</option>
                    <option value="lt">Less than</option>
                    <option value="eq">Equal to</option>
                    <option value="between">Between</option>
                </select>
                
                <input type="number" class="form-input criterion-value" placeholder="Value">
                
                <button class="btn btn-ghost btn-icon remove-criterion">
                    ${RTS.components.getIcon('trash', 16)}
                </button>
            </div>
        `;
        
        criteriaList.appendChild(criterion);
        
        // Add remove functionality
        criterion.querySelector('.remove-criterion').addEventListener('click', function() {
            criterion.remove();
            updatePreview();
        });
        
        // Update preview when fields change
        criterion.querySelectorAll('select, input').forEach(field => {
            field.addEventListener('change', updatePreview);
        });
    }
    
    function updatePreview() {
        const criteria = collectCriteria();
        
        // Simulate calculating matching stocks
        let count = 1247;
        criteria.forEach(criterion => {
            if (criterion.metric && criterion.operator && criterion.value) {
                count = Math.floor(count * (0.6 + Math.random() * 0.3));
            }
        });
        
        document.getElementById('preview-count').textContent = count;
    }
    
    function collectCriteria() {
        const criteriaItems = document.querySelectorAll('.criterion-item');
        const criteria = [];
        
        criteriaItems.forEach(item => {
            const metric = item.querySelector('.criterion-metric').value;
            const operator = item.querySelector('.criterion-operator').value;
            const value = item.querySelector('.criterion-value').value;
            
            if (metric || operator || value) {
                criteria.push({ metric, operator, value });
            }
        });
        
        return criteria;
    }
    
    function getPresetData(presetId) {
        // This would normally fetch from the presets array or API
        const presets = <?php echo json_encode($filter_presets); ?>;
        return presets.find(p => p.id === presetId);
    }
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.preset-menu')) {
            document.querySelectorAll('.menu-dropdown').forEach(menu => {
                menu.classList.add('hidden');
            });
        }
    });
    
    // Save filter functionality
    document.querySelector('.save-filter')?.addEventListener('click', function() {
        const name = document.getElementById('filter-name').value;
        const description = document.getElementById('filter-description').value;
        const category = document.getElementById('filter-category').value;
        const criteria = collectCriteria();
        
        if (!name || criteria.length === 0) {
            RTS.showError('Please enter a filter name and at least one criterion');
            return;
        }
        
        // Simulate saving
        this.classList.add('loading');
        
        setTimeout(() => {
            this.classList.remove('loading');
            closeModal();
            RTS.showSuccess(`Filter "${name}" saved successfully!`);
            
            // Add to grid (in real app, would refresh from server)
            addNewPresetToGrid(name, description, category, criteria);
        }, 1500);
    });
    
    function addNewPresetToGrid(name, description, category, criteria) {
        // Create new preset card and add to grid
        // This is a simplified version - real implementation would be more robust
        const newCard = document.createElement('div');
        newCard.className = 'preset-card card';
        newCard.innerHTML = `
            <div class="preset-content">
                <h3 class="preset-name">${name}</h3>
                <p class="preset-description">${description}</p>
            </div>
        `;
        
        presetsGrid.insertBefore(newCard, presetsGrid.firstChild);
    }
});
</script>

<style>
/* Filters page specific styles */
.filters-layout {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
}

/* Categories Section */
.categories-container {
    background: var(--surface-raised);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-xl);
    padding: var(--spacing-lg);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--spacing-lg);
}

.category-tabs {
    display: flex;
    gap: var(--spacing-sm);
    flex-wrap: wrap;
}

.category-tab {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    background: transparent;
    border: 2px solid transparent;
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
    font-weight: 500;
    color: var(--gray-600);
    white-space: nowrap;
}

.category-tab:hover {
    background: var(--gray-50);
    color: var(--gray-800);
}

.category-tab.active {
    background: var(--primary-500);
    color: white;
    border-color: var(--primary-500);
}

.category-count {
    background: rgba(255, 255, 255, 0.2);
    color: inherit;
    padding: 2px 6px;
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: 600;
    min-width: 20px;
    text-align: center;
}

.category-tab.active .category-count {
    background: rgba(255, 255, 255, 0.3);
}

.category-actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.search-filters {
    position: relative;
}

.search-input {
    padding: var(--spacing-sm) var(--spacing-lg) var(--spacing-sm) var(--spacing-2xl);
    border: 2px solid var(--gray-300);
    border-radius: var(--radius-lg);
    font-size: var(--text-sm);
    min-width: 200px;
}

.search-icon {
    position: absolute;
    left: var(--spacing-sm);
    top: 50%;
    transform: translateY(-50%);
    color: var(--gray-400);
}

/* Presets Grid */
.presets-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: var(--spacing-xl);
}

.preset-card {
    padding: var(--spacing-xl);
    transition: all var(--transition-normal) var(--easing-standard);
    border-radius: var(--radius-xl);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.preset-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}

.preset-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.preset-meta {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.preset-category {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: var(--text-xs);
    color: var(--gray-600);
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.05em;
}

.preset-popularity {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.popularity-bar {
    width: 60px;
    height: 4px;
    background: var(--gray-200);
    border-radius: var(--radius-full);
    overflow: hidden;
}

.popularity-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--warning) 0%, var(--success) 100%);
    transition: width var(--transition-normal);
}

.preset-actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
}

.favorite-btn.favorited {
    color: var(--danger);
}

.preset-menu {
    position: relative;
}

.menu-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    background: var(--surface-raised);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-xl);
    z-index: 100;
    min-width: 150px;
    padding: var(--spacing-sm);
}

.menu-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm);
    width: 100%;
    background: transparent;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: background var(--transition-fast);
    font-size: var(--text-sm);
    text-align: left;
}

.menu-item:hover {
    background: var(--gray-50);
}

.preset-content {
    flex: 1;
}

.preset-name {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--gray-800);
    margin: 0 0 var(--spacing-sm);
}

.preset-description {
    color: var(--gray-600);
    line-height: 1.5;
    margin-bottom: var(--spacing-md);
}

.preset-criteria {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-xs);
}

.criterion-tag {
    padding: var(--spacing-xs) var(--spacing-sm);
    background: var(--primary-100);
    color: var(--primary-700);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: 500;
}

.preset-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
    padding-top: var(--spacing-md);
    border-top: 1px solid var(--gray-100);
}

.preset-stats {
    display: flex;
    gap: var(--spacing-lg);
}

.stat-item {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.stat-label {
    font-size: var(--text-xs);
    color: var(--gray-500);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.stat-value {
    font-weight: 600;
    color: var(--gray-700);
    font-size: var(--text-sm);
}

.preset-buttons {
    display: flex;
    gap: var(--spacing-sm);
}

/* Empty State */
.empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
}

.empty-content {
    text-align: center;
    max-width: 400px;
}

.empty-icon {
    color: var(--gray-400);
    margin-bottom: var(--spacing-lg);
}

.empty-content h3 {
    color: var(--gray-700);
    margin-bottom: var(--spacing-sm);
}

.empty-content p {
    color: var(--gray-500);
    margin-bottom: var(--spacing-lg);
}

/* Filter Builder Modal */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: var(--z-modal);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-lg);
}

.modal-backdrop {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
}

.modal-content {
    background: var(--surface-raised);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-2xl);
    max-width: 800px;
    width: 100%;
    max-height: 90vh;
    overflow: hidden;
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-xl);
    border-bottom: 1px solid var(--gray-200);
}

.modal-title {
    margin: 0;
    color: var(--gray-800);
}

.modal-close {
    background: transparent;
    border: none;
    cursor: pointer;
    padding: var(--spacing-sm);
    border-radius: var(--radius-md);
    transition: background var(--transition-fast);
}

.modal-close:hover {
    background: var(--gray-100);
}

.modal-body {
    flex: 1;
    overflow-y: auto;
    padding: var(--spacing-xl);
}

.builder-form {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2xl);
}

.form-section h4 {
    margin: 0 0 var(--spacing-lg);
    color: var(--gray-800);
    font-size: var(--text-lg);
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-lg);
}

.form-field {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.form-label {
    font-weight: 600;
    color: var(--gray-700);
    font-size: var(--text-sm);
}

.form-input,
.form-select,
.form-textarea {
    padding: var(--spacing-sm) var(--spacing-md);
    border: 2px solid var(--gray-300);
    border-radius: var(--radius-lg);
    font-size: var(--text-base);
    transition: border-color var(--transition-fast);
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 4px rgba(var(--primary-500), 0.1);
}

.criteria-builder {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.criteria-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.criterion-item {
    padding: var(--spacing-lg);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    background: var(--gray-50);
}

.criterion-fields {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr auto;
    gap: var(--spacing-md);
    align-items: center;
}

.preview-container {
    display: flex;
    gap: var(--spacing-xl);
    align-items: center;
}

.preview-stats {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.stat-card {
    padding: var(--spacing-lg);
    background: var(--primary-50);
    border-radius: var(--radius-lg);
    text-align: center;
}

.stat-number {
    display: block;
    font-size: var(--text-2xl);
    font-weight: 700;
    color: var(--primary-600);
}

.stat-label {
    font-size: var(--text-sm);
    color: var(--gray-600);
    margin-top: var(--spacing-xs);
}

.preview-chart {
    flex: 1;
    min-height: 150px;
    background: var(--gray-50);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-md);
    padding: var(--spacing-xl);
    border-top: 1px solid var(--gray-200);
}

/* Loading states */
.apply-preset.loading,
.save-filter.loading {
    opacity: 0.7;
    pointer-events: none;
}

/* Mobile responsive */
@media (max-width: 1024px) {
    .categories-container {
        flex-direction: column;
        align-items: stretch;
        gap: var(--spacing-md);
    }
    
    .category-tabs {
        justify-content: center;
    }
    
    .presets-grid {
        grid-template-columns: 1fr;
    }
    
    .modal-content {
        margin: var(--spacing-md);
        max-height: calc(100vh - var(--spacing-2xl));
    }
    
    .criterion-fields {
        grid-template-columns: 1fr;
    }
    
    .preview-container {
        flex-direction: column;
    }
}

@media (max-width: 640px) {
    .category-tabs {
        flex-direction: column;
        width: 100%;
    }
    
    .category-tab {
        justify-content: center;
    }
    
    .preset-footer {
        flex-direction: column;
        gap: var(--spacing-md);
        align-items: stretch;
    }
    
    .preset-buttons {
        width: 100%;
    }
    
    .preset-buttons .btn {
        flex: 1;
    }
}
</style>

<?php get_footer(); ?>