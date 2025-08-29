<?php
/**
 * Template Name: Finder
 * 
 * Sector grid, factor tiles, and screen results for stock discovery
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('Stock Finder', 'retail-trade-scanner'),
    'page_description' => __('Discover stocks by sector, factors, and custom screening criteria', 'retail-trade-scanner'),
    'page_class' => 'finder-page',
    'header_actions' => array(
        array(
            'text' => __('Save Screen', 'retail-trade-scanner'),
            'variant' => 'outline',
            'icon' => 'save'
        ),
        array(
            'text' => __('Run Screen', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'search'
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);

// Sector data
$sectors = array(
    array('name' => 'Technology', 'count' => 342, 'change' => '+2.3%', 'type' => 'positive', 'icon' => 'cpu'),
    array('name' => 'Healthcare', 'count' => 198, 'change' => '+1.8%', 'type' => 'positive', 'icon' => 'heart'),
    array('name' => 'Financial', 'count' => 267, 'change' => '-0.5%', 'type' => 'negative', 'icon' => 'dollar-sign'),
    array('name' => 'Consumer Disc.', 'count' => 156, 'change' => '+0.9%', 'type' => 'positive', 'icon' => 'shopping-cart'),
    array('name' => 'Industrial', 'count' => 203, 'change' => '+1.2%', 'type' => 'positive', 'icon' => 'settings'),
    array('name' => 'Energy', 'count' => 89, 'change' => '-1.4%', 'type' => 'negative', 'icon' => 'zap'),
    array('name' => 'Real Estate', 'count' => 76, 'change' => '+0.3%', 'type' => 'positive', 'icon' => 'home'),
    array('name' => 'Utilities', 'count' => 45, 'change' => '-0.2%', 'type' => 'negative', 'icon' => 'activity'),
    array('name' => 'Materials', 'count' => 134, 'change' => '+2.1%', 'type' => 'positive', 'icon' => 'layers'),
    array('name' => 'Telecom', 'count' => 67, 'change' => '+0.7%', 'type' => 'positive', 'icon' => 'phone'),
    array('name' => 'Consumer Staples', 'count' => 98, 'change' => '-0.8%', 'type' => 'negative', 'icon' => 'package'),
    array('name' => 'Aerospace', 'count' => 54, 'change' => '+1.5%', 'type' => 'positive', 'icon' => 'plane')
);

// Factor data
$factors = array(
    array('name' => 'Momentum', 'description' => 'Price trending upward', 'count' => 234, 'icon' => 'trending-up'),
    array('name' => 'Value', 'description' => 'Low P/E, P/B ratios', 'count' => 189, 'icon' => 'dollar-sign'),
    array('name' => 'Growth', 'description' => 'High revenue/earnings growth', 'count' => 156, 'icon' => 'bar-chart'),
    array('name' => 'Quality', 'description' => 'Strong financials, low debt', 'count' => 203, 'icon' => 'shield'),
    array('name' => 'Dividend', 'description' => 'High dividend yield', 'count' => 134, 'icon' => 'percent'),
    array('name' => 'Size', 'description' => 'Small/mid-cap stocks', 'count' => 287, 'icon' => 'circle'),
    array('name' => 'Volatility', 'description' => 'Low volatility stocks', 'count' => 98, 'icon' => 'activity'),
    array('name' => 'ESG', 'description' => 'Environmental, Social, Governance', 'count' => 167, 'icon' => 'leaf')
);
?>

<div class="finder-layout">
    <!-- Search Bar -->
    <section class="finder-search">
        <div class="search-container card glass-card">
            <div class="search-header">
                <h2><?php esc_html_e('Find Your Perfect Stocks', 'retail-trade-scanner'); ?></h2>
                <p><?php esc_html_e('Use our advanced screening tools to discover investment opportunities across sectors and factors.', 'retail-trade-scanner'); ?></p>
            </div>
            
            <div class="quick-search">
                <div class="search-input-wrapper">
                    <input type="text" 
                           class="search-input" 
                           placeholder="<?php esc_attr_e('Search by company name, ticker, or keyword...', 'retail-trade-scanner'); ?>">
                    <button class="search-btn">
                        <?php echo rts_get_icon('search', ['width' => '20', 'height' => '20']); ?>
                    </button>
                </div>
                
                <div class="search-suggestions">
                    <span class="suggestion-label"><?php esc_html_e('Popular:', 'retail-trade-scanner'); ?></span>
                    <div class="suggestion-tags">
                        <button class="suggestion-tag">AI Stocks</button>
                        <button class="suggestion-tag">Dividend Aristocrats</button>
                        <button class="suggestion-tag">Small Cap Growth</button>
                        <button class="suggestion-tag">ESG Leaders</button>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Sector Grid -->
    <section class="sector-explorer">
        <div class="section-header">
            <h3><?php esc_html_e('Explore by Sector', 'retail-trade-scanner'); ?></h3>
            <p><?php esc_html_e('Browse stocks organized by industry sectors', 'retail-trade-scanner'); ?></p>
        </div>
        
        <div class="sector-grid">
            <?php foreach ($sectors as $index => $sector) : ?>
                <div class="sector-card glass-card animate-scale-in" 
                     style="animation-delay: <?php echo $index * 0.1; ?>s;"
                     data-sector="<?php echo esc_attr(strtolower(str_replace([' ', '.'], ['_', ''], $sector['name']))); ?>">
                    <div class="sector-icon">
                        <?php echo rts_get_icon($sector['icon'], ['width' => '32', 'height' => '32']); ?>
                    </div>
                    <div class="sector-info">
                        <h4 class="sector-name"><?php echo esc_html($sector['name']); ?></h4>
                        <div class="sector-stats">
                            <span class="stock-count"><?php echo esc_html($sector['count']); ?> <?php esc_html_e('stocks', 'retail-trade-scanner'); ?></span>
                            <span class="sector-change <?php echo $sector['type'] === 'positive' ? 'text-success' : 'text-danger'; ?>">
                                <?php echo esc_html($sector['change']); ?>
                            </span>
                        </div>
                    </div>
                    <div class="sector-action">
                        <button class="btn btn-ghost btn-sm explore-sector">
                            <?php esc_html_e('Explore', 'retail-trade-scanner'); ?>
                            <?php echo rts_get_icon('arrow-right', ['width' => '16', 'height' => '16']); ?>
                        </button>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    </section>

    <!-- Factor Tiles -->
    <section class="factor-explorer">
        <div class="section-header">
            <h3><?php esc_html_e('Screen by Investment Factors', 'retail-trade-scanner'); ?></h3>
            <p><?php esc_html_e('Find stocks based on proven investment factors and strategies', 'retail-trade-scanner'); ?></p>
        </div>
        
        <div class="factor-grid">
            <?php foreach ($factors as $index => $factor) : ?>
                <div class="factor-card card animate-fade-up" 
                     style="animation-delay: <?php echo $index * 0.1; ?>s;"
                     data-factor="<?php echo esc_attr(strtolower($factor['name'])); ?>">
                    <div class="factor-header">
                        <div class="factor-icon">
                            <?php echo rts_get_icon($factor['icon'], ['width' => '24', 'height' => '24']); ?>
                        </div>
                        <h4 class="factor-name"><?php echo esc_html($factor['name']); ?></h4>
                    </div>
                    <div class="factor-content">
                        <p class="factor-description"><?php echo esc_html($factor['description']); ?></p>
                        <div class="factor-stats">
                            <span class="factor-count"><?php echo esc_html($factor['count']); ?> <?php esc_html_e('matches', 'retail-trade-scanner'); ?></span>
                        </div>
                    </div>
                    <div class="factor-action">
                        <button class="btn btn-outline btn-sm screen-factor">
                            <?php esc_html_e('Screen', 'retail-trade-scanner'); ?>
                        </button>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    </section>

    <!-- Custom Screen Builder -->
    <section class="screen-builder">
        <div class="builder-container card glass-card">
            <div class="builder-header">
                <h3><?php esc_html_e('Custom Screen Builder', 'retail-trade-scanner'); ?></h3>
                <p><?php esc_html_e('Create your own screening criteria with multiple filters and conditions', 'retail-trade-scanner'); ?></p>
            </div>
            
            <div class="builder-content">
                <div class="screen-criteria">
                    <div class="criteria-group">
                        <h4><?php esc_html_e('Market Cap', 'retail-trade-scanner'); ?></h4>
                        <div class="criteria-options">
                            <label class="criteria-checkbox">
                                <input type="checkbox" value="mega"> 
                                <span><?php esc_html_e('Mega Cap (>$200B)', 'retail-trade-scanner'); ?></span>
                            </label>
                            <label class="criteria-checkbox">
                                <input type="checkbox" value="large"> 
                                <span><?php esc_html_e('Large Cap ($10B-$200B)', 'retail-trade-scanner'); ?></span>
                            </label>
                            <label class="criteria-checkbox">
                                <input type="checkbox" value="mid"> 
                                <span><?php esc_html_e('Mid Cap ($2B-$10B)', 'retail-trade-scanner'); ?></span>
                            </label>
                            <label class="criteria-checkbox">
                                <input type="checkbox" value="small"> 
                                <span><?php esc_html_e('Small Cap (<$2B)', 'retail-trade-scanner'); ?></span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="criteria-group">
                        <h4><?php esc_html_e('Performance', 'retail-trade-scanner'); ?></h4>
                        <div class="criteria-ranges">
                            <div class="range-input">
                                <label><?php esc_html_e('1 Year Return (%)', 'retail-trade-scanner'); ?></label>
                                <div class="range-wrapper">
                                    <input type="range" min="-50" max="200" value="0" class="range-slider" data-metric="1y-return">
                                    <span class="range-value">0%</span>
                                </div>
                            </div>
                            <div class="range-input">
                                <label><?php esc_html_e('Revenue Growth (%)', 'retail-trade-scanner'); ?></label>
                                <div class="range-wrapper">
                                    <input type="range" min="-20" max="100" value="0" class="range-slider" data-metric="revenue-growth">
                                    <span class="range-value">0%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="criteria-group">
                        <h4><?php esc_html_e('Valuation', 'retail-trade-scanner'); ?></h4>
                        <div class="criteria-ranges">
                            <div class="range-input">
                                <label><?php esc_html_e('P/E Ratio', 'retail-trade-scanner'); ?></label>
                                <div class="range-wrapper">
                                    <input type="range" min="0" max="100" value="25" class="range-slider" data-metric="pe-ratio">
                                    <span class="range-value">25</span>
                                </div>
                            </div>
                            <div class="range-input">
                                <label><?php esc_html_e('Dividend Yield (%)', 'retail-trade-scanner'); ?></label>
                                <div class="range-wrapper">
                                    <input type="range" min="0" max="10" value="2" step="0.1" class="range-slider" data-metric="dividend-yield">
                                    <span class="range-value">2.0%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="criteria-group">
                        <h4><?php esc_html_e('Technical Indicators', 'retail-trade-scanner'); ?></h4>
                        <div class="criteria-options">
                            <select class="form-select" data-metric="rsi">
                                <option value=""><?php esc_html_e('RSI Condition', 'retail-trade-scanner'); ?></option>
                                <option value="oversold"><?php esc_html_e('Oversold (RSI < 30)', 'retail-trade-scanner'); ?></option>
                                <option value="neutral"><?php esc_html_e('Neutral (30-70)', 'retail-trade-scanner'); ?></option>
                                <option value="overbought"><?php esc_html_e('Overbought (RSI > 70)', 'retail-trade-scanner'); ?></option>
                            </select>
                            <select class="form-select" data-metric="sma">
                                <option value=""><?php esc_html_e('Moving Average', 'retail-trade-scanner'); ?></option>
                                <option value="above_20"><?php esc_html_e('Above 20-day SMA', 'retail-trade-scanner'); ?></option>
                                <option value="above_50"><?php esc_html_e('Above 50-day SMA', 'retail-trade-scanner'); ?></option>
                                <option value="above_200"><?php esc_html_e('Above 200-day SMA', 'retail-trade-scanner'); ?></option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <div class="builder-actions">
                    <div class="action-buttons">
                        <button class="btn btn-ghost clear-criteria">
                            <?php esc_html_e('Clear All', 'retail-trade-scanner'); ?>
                        </button>
                        <button class="btn btn-outline save-screen">
                            <?php echo rts_get_icon('save', ['width' => '16', 'height' => '16']); ?>
                            <?php esc_html_e('Save Screen', 'retail-trade-scanner'); ?>
                        </button>
                        <button class="btn btn-primary run-screen">
                            <?php echo rts_get_icon('search', ['width' => '16', 'height' => '16']); ?>
                            <?php esc_html_e('Run Screen', 'retail-trade-scanner'); ?>
                        </button>
                    </div>
                    <div class="screen-summary">
                        <span class="estimated-results"><?php esc_html_e('Estimated results:', 'retail-trade-scanner'); ?> <strong id="estimated-count">1,247</strong></span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Results Section -->
    <section class="screen-results hidden" id="screen-results">
        <div class="results-container">
            <div class="results-header">
                <h3><?php esc_html_e('Screen Results', 'retail-trade-scanner'); ?></h3>
                <div class="results-actions">
                    <select class="form-select sort-select">
                        <option value="relevance"><?php esc_html_e('Sort by Relevance', 'retail-trade-scanner'); ?></option>
                        <option value="market_cap"><?php esc_html_e('Market Cap', 'retail-trade-scanner'); ?></option>
                        <option value="price_change"><?php esc_html_e('Price Change', 'retail-trade-scanner'); ?></option>
                        <option value="volume"><?php esc_html_e('Volume', 'retail-trade-scanner'); ?></option>
                    </select>
                    <button class="btn btn-outline btn-sm export-results">
                        <?php echo rts_get_icon('download', ['width' => '16', 'height' => '16']); ?>
                        <?php esc_html_e('Export', 'retail-trade-scanner'); ?>
                    </button>
                </div>
            </div>
            
            <div class="results-table-container">
                <?php
                get_template_part('template-parts/components/table', null, array(
                    'id' => 'screen-results-table',
                    'headers' => array(
                        'symbol' => __('Symbol', 'retail-trade-scanner'),
                        'name' => __('Company', 'retail-trade-scanner'),
                        'price' => __('Price', 'retail-trade-scanner'),
                        'change' => __('Change', 'retail-trade-scanner'),
                        'market_cap' => __('Market Cap', 'retail-trade-scanner'),
                        'pe_ratio' => __('P/E', 'retail-trade-scanner'),
                        'actions' => __('Actions', 'retail-trade-scanner')
                    ),
                    'data' => array(),
                    'sortable' => true,
                    'pagination' => true,
                    'loading' => true
                ));
                ?>
            </div>
        </div>
    </section>

    <!-- Saved Screens -->
    <section class="saved-screens">
        <div class="saved-container card">
            <div class="saved-header">
                <h3><?php esc_html_e('Saved Screens', 'retail-trade-scanner'); ?></h3>
                <button class="btn btn-ghost btn-sm manage-screens">
                    <?php esc_html_e('Manage All', 'retail-trade-scanner'); ?>
                </button>
            </div>
            
            <div class="saved-list">
                <div class="saved-item">
                    <div class="saved-info">
                        <h4><?php esc_html_e('High Growth Tech', 'retail-trade-scanner'); ?></h4>
                        <p><?php esc_html_e('Technology stocks with >20% revenue growth', 'retail-trade-scanner'); ?></p>
                        <span class="saved-meta"><?php esc_html_e('Created 3 days ago • 45 results', 'retail-trade-scanner'); ?></span>
                    </div>
                    <div class="saved-actions">
                        <button class="btn btn-ghost btn-sm run-saved">
                            <?php esc_html_e('Run', 'retail-trade-scanner'); ?>
                        </button>
                        <button class="btn btn-ghost btn-icon edit-saved">
                            <?php echo rts_get_icon('edit', ['width' => '16', 'height' => '16']); ?>
                        </button>
                    </div>
                </div>
                
                <div class="saved-item">
                    <div class="saved-info">
                        <h4><?php esc_html_e('Dividend Champions', 'retail-trade-scanner'); ?></h4>
                        <p><?php esc_html_e('Stocks with consistent dividend increases', 'retail-trade-scanner'); ?></p>
                        <span class="saved-meta"><?php esc_html_e('Created 1 week ago • 67 results', 'retail-trade-scanner'); ?></span>
                    </div>
                    <div class="saved-actions">
                        <button class="btn btn-ghost btn-sm run-saved">
                            <?php esc_html_e('Run', 'retail-trade-scanner'); ?>
                        </button>
                        <button class="btn btn-ghost btn-icon edit-saved">
                            <?php echo rts_get_icon('edit', ['width' => '16', 'height' => '16']); ?>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </section>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Finder functionality
    const sectorCards = document.querySelectorAll('.sector-card');
    const factorCards = document.querySelectorAll('.factor-card');
    const rangeSliders = document.querySelectorAll('.range-slider');
    const runScreenBtn = document.querySelector('.run-screen');
    const clearBtn = document.querySelector('.clear-criteria');
    const saveScreenBtn = document.querySelector('.save-screen');
    
    // Sector exploration
    sectorCards.forEach(card => {
        card.addEventListener('click', function() {
            const sector = this.dataset.sector;
            exploreSector(sector);
        });
    });
    
    // Factor screening
    factorCards.forEach(card => {
        const screenBtn = card.querySelector('.screen-factor');
        screenBtn.addEventListener('click', function() {
            const factor = card.dataset.factor;
            screenByFactor(factor);
        });
    });
    
    // Range sliders
    rangeSliders.forEach(slider => {
        slider.addEventListener('input', function() {
            const valueSpan = this.parentElement.querySelector('.range-value');
            const metric = this.dataset.metric;
            let value = this.value;
            
            // Format value based on metric
            if (metric.includes('yield') || metric.includes('return')) {
                value += '%';
            }
            
            valueSpan.textContent = value;
            updateEstimatedResults();
        });
    });
    
    // Screen builder actions
    if (runScreenBtn) {
        runScreenBtn.addEventListener('click', function() {
            runCustomScreen();
        });
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            clearAllCriteria();
        });
    }
    
    if (saveScreenBtn) {
        saveScreenBtn.addEventListener('click', function() {
            saveCustomScreen();
        });
    }
    
    // Suggestion tags
    document.querySelectorAll('.suggestion-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            const query = this.textContent;
            searchByQuery(query);
        });
    });
    
    function exploreSector(sector) {
        // Add loading state to sector card
        const sectorCard = document.querySelector(`[data-sector="${sector}"]`);
        sectorCard.classList.add('loading');
        
        // Simulate API call
        setTimeout(() => {
            sectorCard.classList.remove('loading');
            showSectorResults(sector);
            RTS.showSuccess(`Exploring ${sector} sector`);
        }, 1500);
    }
    
    function screenByFactor(factor) {
        // Show loading state
        const factorCard = document.querySelector(`[data-factor="${factor}"]`);
        const screenBtn = factorCard.querySelector('.screen-factor');
        screenBtn.classList.add('loading');
        screenBtn.textContent = 'Screening...';
        
        // Simulate API call
        setTimeout(() => {
            screenBtn.classList.remove('loading');
            screenBtn.textContent = 'Screen';
            showFactorResults(factor);
            RTS.showSuccess(`Screening by ${factor} factor`);
        }, 2000);
    }
    
    function runCustomScreen() {
        const criteria = collectCriteria();
        
        runScreenBtn.classList.add('loading');
        runScreenBtn.disabled = true;
        
        // Show results section
        const resultsSection = document.getElementById('screen-results');
        resultsSection.classList.remove('hidden');
        
        // Simulate screening
        setTimeout(() => {
            loadScreenResults(criteria);
            runScreenBtn.classList.remove('loading');
            runScreenBtn.disabled = false;
            
            // Scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth' });
            
            RTS.showSuccess('Screen completed successfully!');
        }, 3000);
    }
    
    function collectCriteria() {
        const criteria = {};
        
        // Market cap checkboxes
        const marketCapChecked = document.querySelectorAll('input[type="checkbox"]:checked');
        criteria.marketCap = Array.from(marketCapChecked).map(cb => cb.value);
        
        // Range sliders
        rangeSliders.forEach(slider => {
            criteria[slider.dataset.metric] = slider.value;
        });
        
        // Select dropdowns
        const selects = document.querySelectorAll('select[data-metric]');
        selects.forEach(select => {
            if (select.value) {
                criteria[select.dataset.metric] = select.value;
            }
        });
        
        return criteria;
    }
    
    function clearAllCriteria() {
        // Reset checkboxes
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        
        // Reset range sliders
        rangeSliders.forEach(slider => {
            slider.value = slider.defaultValue || slider.min;
            const valueSpan = slider.parentElement.querySelector('.range-value');
            valueSpan.textContent = slider.value;
        });
        
        // Reset selects
        document.querySelectorAll('select[data-metric]').forEach(select => {
            select.selectedIndex = 0;
        });
        
        updateEstimatedResults();
        
        RTS.showInfo('All criteria cleared');
    }
    
    function updateEstimatedResults() {
        // Simulate dynamic result count based on criteria
        const criteria = collectCriteria();
        let count = 1247; // Base count
        
        // Adjust count based on criteria
        if (criteria.marketCap && criteria.marketCap.length > 0) {
            count = Math.floor(count * 0.7);
        }
        
        rangeSliders.forEach(slider => {
            const value = parseFloat(slider.value);
            const min = parseFloat(slider.min);
            const max = parseFloat(slider.max);
            const normalizedValue = (value - min) / (max - min);
            
            // Reduce count based on how restrictive the criteria is
            if (normalizedValue > 0.5) {
                count = Math.floor(count * 0.8);
            }
        });
        
        const estimatedCountEl = document.getElementById('estimated-count');
        if (estimatedCountEl) {
            estimatedCountEl.textContent = count.toLocaleString();
        }
    }
    
    function saveCustomScreen() {
        const criteria = collectCriteria();
        
        // Simulate save operation
        saveScreenBtn.classList.add('loading');
        
        setTimeout(() => {
            saveScreenBtn.classList.remove('loading');
            
            // Show success message with modal or prompt for name
            const screenName = prompt('Enter a name for this screen:');
            if (screenName) {
                RTS.showSuccess(`Screen "${screenName}" saved successfully!`);
                addToSavedScreens(screenName, criteria);
            }
        }, 1000);
    }
    
    function addToSavedScreens(name, criteria) {
        const savedList = document.querySelector('.saved-list');
        const criteriaCount = Object.keys(criteria).length;
        
        const savedItem = document.createElement('div');
        savedItem.className = 'saved-item';
        savedItem.innerHTML = `
            <div class="saved-info">
                <h4>${name}</h4>
                <p>Custom screen with ${criteriaCount} criteria</p>
                <span class="saved-meta">Created just now • Estimated ${document.getElementById('estimated-count').textContent} results</span>
            </div>
            <div class="saved-actions">
                <button class="btn btn-ghost btn-sm run-saved">Run</button>
                <button class="btn btn-ghost btn-icon edit-saved">
                    ${RTS.components.getIcon('edit', 16)}
                </button>
            </div>
        `;
        
        savedList.insertBefore(savedItem, savedList.firstChild);
    }
    
    function showSectorResults(sector) {
        // This would show results for the selected sector
        console.log(`Showing results for sector: ${sector}`);
    }
    
    function showFactorResults(factor) {
        // This would show results for the selected factor
        console.log(`Showing results for factor: ${factor}`);
    }
    
    function loadScreenResults(criteria) {
        // Simulate loading screen results
        const mockResults = [
            { symbol: 'AAPL', name: 'Apple Inc.', price: '182.34', change: '+2.45%', market_cap: '2.84T', pe_ratio: '28.5' },
            { symbol: 'MSFT', name: 'Microsoft Corp', price: '334.89', change: '+1.23%', market_cap: '2.48T', pe_ratio: '32.1' },
            { symbol: 'GOOGL', name: 'Alphabet Inc.', price: '128.76', change: '+0.89%', market_cap: '1.62T', pe_ratio: '25.3' }
        ];
        
        // Update results table (this would integrate with the table component)
        console.log('Loading screen results:', criteria);
        
        // Hide loading state
        const resultsTable = document.getElementById('screen-results-table');
        if (resultsTable) {
            // Update table with results
        }
    }
    
    function searchByQuery(query) {
        // Handle suggestion tag clicks
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.value = query;
            searchInput.focus();
        }
        
        RTS.showInfo(`Searching for: ${query}`);
    }
    
    // Initialize estimated results
    updateEstimatedResults();
});
</script>

<style>
/* Finder page specific styles */
.finder-layout {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2xl);
}

/* Search Section */
.finder-search {
    margin-bottom: var(--spacing-xl);
}

.search-container {
    max-width: 900px;
    margin: 0 auto;
    padding: var(--spacing-2xl);
    text-align: center;
}

.search-header h2 {
    margin-bottom: var(--spacing-sm);
    color: var(--gray-800);
}

.search-header p {
    color: var(--gray-600);
    margin-bottom: var(--spacing-xl);
    font-size: var(--text-lg);
}

.search-input-wrapper {
    display: flex;
    max-width: 600px;
    margin: 0 auto var(--spacing-lg);
    border: 2px solid var(--gray-300);
    border-radius: var(--radius-xl);
    overflow: hidden;
    transition: border-color var(--transition-fast);
}

.search-input-wrapper:focus-within {
    border-color: var(--primary-500);
    box-shadow: 0 0 0 4px rgba(var(--primary-500), 0.1);
}

.search-input {
    flex: 1;
    padding: var(--spacing-lg);
    border: none;
    font-size: var(--text-lg);
    background: transparent;
}

.search-input:focus {
    outline: none;
}

.search-btn {
    padding: var(--spacing-lg) var(--spacing-xl);
    background: var(--primary-500);
    color: white;
    border: none;
    cursor: pointer;
    transition: background var(--transition-fast);
}

.search-btn:hover {
    background: var(--primary-600);
}

.search-suggestions {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    flex-wrap: wrap;
    justify-content: center;
}

.suggestion-label {
    color: var(--gray-600);
    font-size: var(--text-sm);
    font-weight: 500;
}

.suggestion-tags {
    display: flex;
    gap: var(--spacing-sm);
    flex-wrap: wrap;
}

.suggestion-tag {
    padding: var(--spacing-xs) var(--spacing-sm);
    background: var(--gray-100);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-full);
    font-size: var(--text-sm);
    color: var(--gray-700);
    cursor: pointer;
    transition: all var(--transition-fast);
}

.suggestion-tag:hover {
    background: var(--primary-500);
    color: white;
    border-color: var(--primary-500);
}

/* Section Headers */
.section-header {
    text-align: center;
    margin-bottom: var(--spacing-2xl);
}

.section-header h3 {
    color: var(--gray-800);
    margin-bottom: var(--spacing-sm);
}

.section-header p {
    color: var(--gray-600);
    font-size: var(--text-lg);
}

/* Sector Grid */
.sector-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-lg);
}

.sector-card {
    padding: var(--spacing-xl);
    cursor: pointer;
    transition: all var(--transition-normal) var(--easing-standard);
    border-radius: var(--radius-xl);
}

.sector-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}

.sector-card.loading {
    opacity: 0.7;
    pointer-events: none;
}

.sector-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 60px;
    background: var(--primary-100);
    border-radius: var(--radius-lg);
    margin-bottom: var(--spacing-md);
    color: var(--primary-600);
}

.sector-name {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--gray-800);
    margin: 0 0 var(--spacing-sm);
}

.sector-stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-md);
}

.stock-count {
    font-size: var(--text-sm);
    color: var(--gray-600);
}

.sector-change {
    font-weight: 600;
    font-size: var(--text-sm);
}

.sector-action {
    margin-top: var(--spacing-md);
}

.explore-sector {
    width: 100%;
    justify-content: space-between;
}

/* Factor Grid */
.factor-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--spacing-lg);
}

.factor-card {
    padding: var(--spacing-xl);
    transition: all var(--transition-normal) var(--easing-standard);
}

.factor-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.factor-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-md);
}

.factor-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background: var(--secondary-100);
    border-radius: var(--radius-lg);
    color: var(--secondary-600);
}

.factor-name {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--gray-800);
    margin: 0;
}

.factor-description {
    color: var(--gray-600);
    margin-bottom: var(--spacing-md);
    line-height: 1.5;
}

.factor-stats {
    margin-bottom: var(--spacing-md);
}

.factor-count {
    font-size: var(--text-sm);
    color: var(--gray-600);
    font-weight: 500;
}

.factor-action {
    margin-top: auto;
}

.screen-factor {
    width: 100%;
}

/* Screen Builder */
.builder-container {
    padding: var(--spacing-2xl);
}

.builder-header {
    text-align: center;
    margin-bottom: var(--spacing-2xl);
}

.builder-header h3 {
    color: var(--gray-800);
    margin-bottom: var(--spacing-sm);
}

.builder-header p {
    color: var(--gray-600);
    font-size: var(--text-lg);
}

.screen-criteria {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--spacing-2xl);
    margin-bottom: var(--spacing-2xl);
}

.criteria-group {
    background: var(--gray-50);
    padding: var(--spacing-xl);
    border-radius: var(--radius-lg);
    border: 1px solid var(--gray-200);
}

.criteria-group h4 {
    color: var(--gray-800);
    margin: 0 0 var(--spacing-lg);
    font-size: var(--text-lg);
}

.criteria-options {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.criteria-checkbox {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
    transition: color var(--transition-fast);
}

.criteria-checkbox:hover {
    color: var(--primary-600);
}

.criteria-checkbox input[type="checkbox"] {
    width: 18px;
    height: 18px;
    border: 2px solid var(--gray-300);
    border-radius: var(--radius-sm);
    margin: 0;
}

.criteria-ranges {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.range-input {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.range-input label {
    font-weight: 500;
    color: var(--gray-700);
    font-size: var(--text-sm);
}

.range-wrapper {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.range-slider {
    flex: 1;
    height: 6px;
    background: var(--gray-200);
    border-radius: var(--radius-full);
    outline: none;
    -webkit-appearance: none;
}

.range-slider::-webkit-slider-thumb {
    appearance: none;
    width: 20px;
    height: 20px;
    background: var(--primary-500);
    border-radius: 50%;
    cursor: pointer;
}

.range-value {
    font-weight: 600;
    color: var(--primary-600);
    min-width: 50px;
    text-align: center;
    font-size: var(--text-sm);
}

.builder-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: var(--spacing-xl);
    border-top: 1px solid var(--gray-200);
}

.action-buttons {
    display: flex;
    gap: var(--spacing-md);
}

.screen-summary {
    color: var(--gray-600);
    font-size: var(--text-sm);
}

.estimated-results strong {
    color: var(--primary-600);
}

/* Results Section */
.screen-results {
    margin-top: var(--spacing-2xl);
}

.results-container {
    background: var(--surface-raised);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xl);
}

.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
}

.results-header h3 {
    margin: 0;
    color: var(--gray-800);
}

.results-actions {
    display: flex;
    gap: var(--spacing-md);
    align-items: center;
}

/* Saved Screens */
.saved-container {
    padding: var(--spacing-xl);
}

.saved-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
}

.saved-header h3 {
    margin: 0;
    color: var(--gray-800);
}

.saved-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.saved-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    transition: all var(--transition-fast);
}

.saved-item:hover {
    background: var(--gray-50);
    border-color: var(--primary-200);
}

.saved-info h4 {
    margin: 0 0 var(--spacing-xs);
    color: var(--gray-800);
    font-size: var(--text-base);
}

.saved-info p {
    margin: 0 0 var(--spacing-xs);
    color: var(--gray-600);
    font-size: var(--text-sm);
}

.saved-meta {
    font-size: var(--text-xs);
    color: var(--gray-500);
}

.saved-actions {
    display: flex;
    gap: var(--spacing-sm);
    align-items: center;
}

/* Loading states */
.screen-factor.loading,
.run-screen.loading {
    opacity: 0.7;
    pointer-events: none;
}

/* Mobile responsive */
@media (max-width: 1024px) {
    .sector-grid,
    .factor-grid {
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    }
    
    .screen-criteria {
        grid-template-columns: 1fr;
    }
    
    .builder-actions {
        flex-direction: column;
        gap: var(--spacing-md);
        align-items: stretch;
    }
    
    .action-buttons {
        justify-content: center;
    }
}

@media (max-width: 640px) {
    .search-suggestions {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .suggestion-tags {
        width: 100%;
    }
    
    .suggestion-tag {
        flex: 1;
        text-align: center;
    }
    
    .saved-item {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--spacing-md);
    }
    
    .saved-actions {
        width: 100%;
        justify-content: flex-end;
    }
}
</style>

<?php get_footer(); ?>