<?php
/**
 * Tabs Component Template Part - Keyboard Accessible Tabs
 *
 * @package RetailTradeScanner
 */

// Default tabs attributes
$defaults = array(
    'tabs' => array(), // Array of tab definitions
    'active_tab' => 0, // Index of active tab (0-based)
    'variant' => 'default', // default, pills, underline, vertical
    'size' => 'base', // sm, base, lg
    'justified' => false, // Full width tabs
    'lazy_load' => false, // Load tab content on demand
    'classes' => '',
    'attributes' => array(),
);

// Parse attributes
$args = wp_parse_args($args ?? array(), $defaults);

// Ensure we have tabs
if (empty($args['tabs'])) {
    return;
}

// Generate unique tabs ID
$tabs_id = 'tabs-' . wp_unique_id();

// Build CSS classes
$tabs_classes = array('tabs-container');
$tabs_classes[] = 'tabs-' . esc_attr($args['variant']);
$tabs_classes[] = 'tabs-' . esc_attr($args['size']);

if ($args['justified']) {
    $tabs_classes[] = 'tabs-justified';
}

if (!empty($args['classes'])) {
    $tabs_classes[] = $args['classes'];
}

// Build attributes
$attributes = array(
    'class' => implode(' ', $tabs_classes),
    'data-tabs-id' => $tabs_id,
);

// Merge custom attributes
$attributes = array_merge($attributes, $args['attributes']);

// Build attribute string
$attr_string = '';
foreach ($attributes as $attr => $value) {
    $attr_string .= ' ' . esc_attr($attr) . '="' . esc_attr($value) . '"';
}
?>

<div<?php echo $attr_string; ?>>
    <!-- Tab Navigation -->
    <div class="tabs-nav" role="tablist" aria-label="<?php esc_attr_e('Tab navigation', 'retail-trade-scanner'); ?>">
        <?php foreach ($args['tabs'] as $index => $tab) : ?>
            <?php
            $tab_id = $tabs_id . '-tab-' . $index;
            $panel_id = $tabs_id . '-panel-' . $index;
            $is_active = ($index === $args['active_tab']);
            
            $tab_text = is_array($tab) ? ($tab['title'] ?? $tab['text'] ?? 'Tab ' . ($index + 1)) : $tab;
            $tab_icon = is_array($tab) ? ($tab['icon'] ?? '') : '';
            $tab_disabled = is_array($tab) ? ($tab['disabled'] ?? false) : false;
            $tab_badge = is_array($tab) ? ($tab['badge'] ?? '') : '';
            
            $tab_classes = array('tab-nav-item');
            if ($is_active) {
                $tab_classes[] = 'active';
            }
            if ($tab_disabled) {
                $tab_classes[] = 'disabled';
            }
            ?>
            <button type="button" 
                    id="<?php echo esc_attr($tab_id); ?>"
                    class="<?php echo implode(' ', $tab_classes); ?>"
                    role="tab" 
                    aria-controls="<?php echo esc_attr($panel_id); ?>"
                    aria-selected="<?php echo $is_active ? 'true' : 'false'; ?>"
                    <?php echo $tab_disabled ? 'disabled aria-disabled="true"' : ''; ?>
                    tabindex="<?php echo $is_active ? '0' : '-1'; ?>">
                
                <?php if (!empty($tab_icon)) : ?>
                    <span class="tab-icon" aria-hidden="true">
                        <?php echo rts_get_icon($tab_icon, array('width' => '18', 'height' => '18')); ?>
                    </span>
                <?php endif; ?>
                
                <span class="tab-text"><?php echo esc_html($tab_text); ?></span>
                
                <?php if (!empty($tab_badge)) : ?>
                    <span class="tab-badge">
                        <?php
                        get_template_part('template-parts/components/badge', null, array(
                            'text' => $tab_badge,
                            'type' => 'info',
                            'size' => 'xs'
                        ));
                        ?>
                    </span>
                <?php endif; ?>
            </button>
        <?php endforeach; ?>
    </div>

    <!-- Tab Panels -->
    <div class="tabs-content">
        <?php foreach ($args['tabs'] as $index => $tab) : ?>
            <?php
            $tab_id = $tabs_id . '-tab-' . $index;
            $panel_id = $tabs_id . '-panel-' . $index;
            $is_active = ($index === $args['active_tab']);
            
            $tab_content = '';
            if (is_array($tab)) {
                $tab_content = $tab['content'] ?? $tab['html'] ?? '';
                $tab_template = $tab['template'] ?? '';
                $tab_template_args = $tab['template_args'] ?? array();
            }
            
            $panel_classes = array('tab-panel');
            if (!$is_active) {
                $panel_classes[] = 'hidden';
            }
            ?>
            <div id="<?php echo esc_attr($panel_id); ?>"
                 class="<?php echo implode(' ', $panel_classes); ?>"
                 role="tabpanel" 
                 aria-labelledby="<?php echo esc_attr($tab_id); ?>"
                 <?php echo $is_active ? '' : 'aria-hidden="true"'; ?>
                 <?php echo $args['lazy_load'] && !$is_active ? 'data-lazy-load="true"' : ''; ?>>
                
                <?php if ($args['lazy_load'] && !$is_active) : ?>
                    <div class="tab-loading-placeholder">
                        <div class="loading-spinner"></div>
                        <p><?php esc_html_e('Loading...', 'retail-trade-scanner'); ?></p>
                    </div>
                <?php else : ?>
                    <div class="tab-panel-content">
                        <?php if (!empty($tab_template)) : ?>
                            <?php get_template_part($tab_template, null, $tab_template_args); ?>
                        <?php else : ?>
                            <?php echo wp_kses_post($tab_content); ?>
                        <?php endif; ?>
                    </div>
                <?php endif; ?>
            </div>
        <?php endforeach; ?>
    </div>
</div>

<!-- Tabs JavaScript -->
<script>
(function() {
    'use strict';
    
    function initTabs(tabsContainer) {
        const tabButtons = tabsContainer.querySelectorAll('.tab-nav-item');
        const tabPanels = tabsContainer.querySelectorAll('.tab-panel');
        const lazyLoad = <?php echo $args['lazy_load'] ? 'true' : 'false'; ?>;
        
        function activateTab(targetButton, targetPanel) {
            // Deactivate all tabs
            tabButtons.forEach(button => {
                button.classList.remove('active');
                button.setAttribute('aria-selected', 'false');
                button.setAttribute('tabindex', '-1');
            });
            
            tabPanels.forEach(panel => {
                panel.classList.add('hidden');
                panel.setAttribute('aria-hidden', 'true');
            });
            
            // Activate target tab
            targetButton.classList.add('active');
            targetButton.setAttribute('aria-selected', 'true');
            targetButton.setAttribute('tabindex', '0');
            
            targetPanel.classList.remove('hidden');
            targetPanel.setAttribute('aria-hidden', 'false');
            
            // Handle lazy loading
            if (lazyLoad && targetPanel.dataset.lazyLoad === 'true') {
                loadTabContent(targetPanel);
            }
            
            // Trigger custom event
            const event = new CustomEvent('tabChange', {
                detail: {
                    tabsId: tabsContainer.dataset.tabsId,
                    activeTab: Array.from(tabButtons).indexOf(targetButton),
                    tabButton: targetButton,
                    tabPanel: targetPanel
                }
            });
            document.dispatchEvent(event);
        }
        
        function loadTabContent(panel) {
            // This would typically make an AJAX request to load content
            // For now, just remove the loading placeholder
            const placeholder = panel.querySelector('.tab-loading-placeholder');
            if (placeholder) {
                placeholder.innerHTML = '<div class="tab-panel-content"><p>Content loaded dynamically</p></div>';
                delete panel.dataset.lazyLoad;
            }
        }
        
        // Add click event listeners
        tabButtons.forEach((button, index) => {
            button.addEventListener('click', function() {
                if (!button.disabled && !button.classList.contains('disabled')) {
                    const targetPanel = tabPanels[index];
                    activateTab(button, targetPanel);
                }
            });
        });
        
        // Add keyboard navigation
        tabsContainer.querySelector('.tabs-nav').addEventListener('keydown', function(e) {
            const currentTab = document.activeElement;
            const currentIndex = Array.from(tabButtons).indexOf(currentTab);
            let targetIndex = currentIndex;
            
            switch (e.key) {
                case 'ArrowRight':
                case 'ArrowDown':
                    e.preventDefault();
                    targetIndex = (currentIndex + 1) % tabButtons.length;
                    break;
                case 'ArrowLeft':
                case 'ArrowUp':
                    e.preventDefault();
                    targetIndex = (currentIndex - 1 + tabButtons.length) % tabButtons.length;
                    break;
                case 'Home':
                    e.preventDefault();
                    targetIndex = 0;
                    break;
                case 'End':
                    e.preventDefault();
                    targetIndex = tabButtons.length - 1;
                    break;
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    if (!currentTab.disabled && !currentTab.classList.contains('disabled')) {
                        const targetPanel = tabPanels[currentIndex];
                        activateTab(currentTab, targetPanel);
                    }
                    return;
                default:
                    return;
            }
            
            // Skip disabled tabs
            while (tabButtons[targetIndex].disabled || tabButtons[targetIndex].classList.contains('disabled')) {
                if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                    targetIndex = (targetIndex + 1) % tabButtons.length;
                } else {
                    targetIndex = (targetIndex - 1 + tabButtons.length) % tabButtons.length;
                }
                
                // Prevent infinite loop if all tabs are disabled
                if (targetIndex === currentIndex) break;
            }
            
            tabButtons[targetIndex].focus();
        });
        
        // Expose public methods
        tabsContainer.activateTab = function(index) {
            if (index >= 0 && index < tabButtons.length && !tabButtons[index].disabled) {
                activateTab(tabButtons[index], tabPanels[index]);
            }
        };
        
        return tabsContainer;
    }
    
    // Initialize tabs
    const tabsContainer = document.querySelector('[data-tabs-id="<?php echo esc_js($tabs_id); ?>"]');
    if (tabsContainer) {
        initTabs(tabsContainer);
    }
    
    // Global tabs utilities
    window.RTS = window.RTS || {};
    window.RTS.activateTab = function(tabsId, tabIndex) {
        const container = document.querySelector(`[data-tabs-id="${tabsId}"]`);
        if (container && container.activateTab) {
            container.activateTab(tabIndex);
        }
    };
})();
</script>

<?php
/*
Usage examples:

// Basic tabs
$basic_tabs = array(
    'tabs' => array(
        array('title' => 'Overview', 'content' => '<p>Overview content</p>'),
        array('title' => 'Details', 'content' => '<p>Details content</p>'),
        array('title' => 'Settings', 'content' => '<p>Settings content</p>')
    )
);

get_template_part('template-parts/components/tabs', null, $basic_tabs);

// Tabs with icons and badges
$advanced_tabs = array(
    'tabs' => array(
        array(
            'title' => 'Dashboard',
            'icon' => 'dashboard',
            'content' => '<p>Dashboard content</p>'
        ),
        array(
            'title' => 'Notifications',
            'icon' => 'bell',
            'badge' => '3',
            'content' => '<p>Notifications content</p>'
        ),
        array(
            'title' => 'Settings',
            'icon' => 'settings',
            'content' => '<p>Settings content</p>'
        ),
        array(
            'title' => 'Disabled Tab',
            'disabled' => true,
            'content' => '<p>This tab is disabled</p>'
        )
    ),
    'variant' => 'pills',
    'active_tab' => 0
);

get_template_part('template-parts/components/tabs', null, $advanced_tabs);

// Tabs with template parts
$template_tabs = array(
    'tabs' => array(
        array(
            'title' => 'Stock Chart',
            'template' => 'template-parts/components/chart-shell',
            'template_args' => array(
                'title' => 'Stock Performance',
                'type' => 'line',
                'data' => $chart_data
            )
        ),
        array(
            'title' => 'Data Table',
            'template' => 'template-parts/components/table',
            'template_args' => $table_data
        )
    ),
    'lazy_load' => true
);

get_template_part('template-parts/components/tabs', null, $template_tabs);

// Vertical tabs
$vertical_tabs = array(
    'tabs' => array(
        array('title' => 'Profile', 'content' => '<p>Profile settings</p>'),
        array('title' => 'Security', 'content' => '<p>Security settings</p>'),
        array('title' => 'Notifications', 'content' => '<p>Notification settings</p>')
    ),
    'variant' => 'vertical',
    'justified' => false
);

get_template_part('template-parts/components/tabs', null, $vertical_tabs);
*/
?>

<style>
/* Tabs Component Styles */
.tabs-container {
    display: flex;
    flex-direction: column;
}

.tabs-nav {
    display: flex;
    border-bottom: 1px solid var(--gray-200);
    margin-bottom: var(--spacing-lg);
}

.tab-nav-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-md) var(--spacing-lg);
    background: none;
    border: none;
    color: var(--gray-600);
    font-size: var(--text-sm);
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast) var(--easing-standard);
    border-bottom: 2px solid transparent;
    white-space: nowrap;
}

.tab-nav-item:hover:not(.disabled) {
    color: var(--primary-600);
    background: var(--gray-50);
}

.tab-nav-item.active {
    color: var(--primary-600);
    border-bottom-color: var(--primary-600);
}

.tab-nav-item.disabled {
    color: var(--gray-400);
    cursor: not-allowed;
    opacity: 0.6;
}

.tab-nav-item:focus-visible {
    outline: 2px solid var(--primary-500);
    outline-offset: -2px;
    border-radius: var(--radius-sm);
}

.tab-icon {
    display: flex;
    align-items: center;
}

.tab-text {
    font-weight: 500;
}

.tab-badge {
    margin-left: var(--spacing-xs);
}

/* Tab Variants */
.tabs-pills .tabs-nav {
    border-bottom: none;
    gap: var(--spacing-xs);
    margin-bottom: var(--spacing-lg);
}

.tabs-pills .tab-nav-item {
    border-radius: var(--radius-full);
    border-bottom: none;
}

.tabs-pills .tab-nav-item.active {
    background: var(--primary-600);
    color: white;
}

.tabs-underline .tabs-nav {
    border-bottom: 1px solid var(--gray-200);
}

.tabs-underline .tab-nav-item {
    border-bottom: 2px solid transparent;
    border-radius: 0;
}

.tabs-underline .tab-nav-item.active {
    border-bottom-color: var(--primary-600);
}

.tabs-vertical {
    flex-direction: row;
}

.tabs-vertical .tabs-nav {
    flex-direction: column;
    border-bottom: none;
    border-right: 1px solid var(--gray-200);
    margin-bottom: 0;
    margin-right: var(--spacing-lg);
    min-width: 200px;
}

.tabs-vertical .tab-nav-item {
    justify-content: flex-start;
    text-align: left;
    border-bottom: none;
    border-right: 2px solid transparent;
}

.tabs-vertical .tab-nav-item.active {
    border-right-color: var(--primary-600);
    border-bottom-color: transparent;
}

/* Tab Sizes */
.tabs-sm .tab-nav-item {
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--text-xs);
}

.tabs-lg .tab-nav-item {
    padding: var(--spacing-lg) var(--spacing-2xl);
    font-size: var(--text-base);
}

/* Justified tabs */
.tabs-justified .tabs-nav {
    width: 100%;
}

.tabs-justified .tab-nav-item {
    flex: 1;
    justify-content: center;
}

/* Tab Panels */
.tabs-content {
    flex: 1;
}

.tab-panel {
    animation: fadeIn var(--transition-normal) var(--easing-standard);
}

.tab-panel.hidden {
    display: none;
}

.tab-panel-content {
    padding: 0;
}

.tab-loading-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-2xl);
    text-align: center;
}

/* Dark mode adjustments */
[data-theme="dark"] .tabs-nav {
    border-color: var(--gray-700);
}

[data-theme="dark"] .tab-nav-item {
    color: var(--gray-400);
}

[data-theme="dark"] .tab-nav-item:hover:not(.disabled) {
    color: var(--gray-200);
    background: var(--gray-800);
}

[data-theme="dark"] .tab-nav-item.active {
    color: var(--primary-400);
}

/* Responsive adjustments */
@media (max-width: 640px) {
    .tabs-nav {
        overflow-x: auto;
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
    
    .tabs-nav::-webkit-scrollbar {
        display: none;
    }
    
    .tabs-vertical {
        flex-direction: column;
    }
    
    .tabs-vertical .tabs-nav {
        flex-direction: row;
        border-right: none;
        border-bottom: 1px solid var(--gray-200);
        margin-right: 0;
        margin-bottom: var(--spacing-lg);
        min-width: auto;
        width: 100%;
    }
    
    .tabs-vertical .tab-nav-item {
        border-right: none;
        border-bottom: 2px solid transparent;
        justify-content: center;
    }
    
    .tabs-vertical .tab-nav-item.active {
        border-right-color: transparent;
        border-bottom-color: var(--primary-600);
    }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>