<?php
/**
 * Toast Component Template Part - Notification Toasts
 *
 * @package RetailTradeScanner
 */

// Default toast attributes
$defaults = array(
    'message' => '',
    'title' => '',
    'type' => 'info', // success, error, warning, info
    'duration' => 5000, // Auto-hide duration in milliseconds (0 = no auto-hide)
    'closable' => true,
    'icon' => 'auto', // 'auto' uses type-based icons, or specify custom icon
    'position' => 'top-right', // top-right, top-left, bottom-right, bottom-left, top-center, bottom-center
    'show_progress' => true, // Show progress bar for auto-hide
    'classes' => '',
    'attributes' => array(),
);

// Parse attributes
$args = wp_parse_args($args ?? array(), $defaults);

// Ensure we have a message
if (empty($args['message'])) {
    return;
}

// Generate unique toast ID
$toast_id = 'toast-' . wp_unique_id();

// Auto-determine icon based on type
if ($args['icon'] === 'auto') {
    $icon_map = array(
        'success' => 'check-circle',
        'error' => 'x-circle',
        'warning' => 'alert-triangle',
        'info' => 'info-circle',
    );
    $args['icon'] = $icon_map[$args['type']] ?? 'info-circle';
}

// Build CSS classes
$toast_classes = array('toast');
$toast_classes[] = 'toast-' . esc_attr($args['type']);

if (!empty($args['classes'])) {
    $toast_classes[] = $args['classes'];
}

// Build attributes
$attributes = array(
    'id' => $toast_id,
    'class' => implode(' ', $toast_classes),
    'role' => 'alert',
    'aria-live' => 'polite',
    'aria-atomic' => 'true',
    'data-toast-type' => $args['type'],
    'data-toast-duration' => $args['duration'],
    'data-toast-position' => $args['position'],
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
    <div class="toast-content">
        <?php if (!empty($args['icon'])) : ?>
            <div class="toast-icon" aria-hidden="true">
                <?php echo rts_get_icon($args['icon'], array('width' => '20', 'height' => '20')); ?>
            </div>
        <?php endif; ?>
        
        <div class="toast-body">
            <?php if (!empty($args['title'])) : ?>
                <div class="toast-title"><?php echo esc_html($args['title']); ?></div>
            <?php endif; ?>
            <div class="toast-message"><?php echo esc_html($args['message']); ?></div>
        </div>
        
        <?php if ($args['closable']) : ?>
            <button type="button" 
                    class="toast-close" 
                    data-dismiss="toast" 
                    aria-label="<?php esc_attr_e('Close notification', 'retail-trade-scanner'); ?>">
                <?php echo rts_get_icon('x', array('width' => '16', 'height' => '16')); ?>
            </button>
        <?php endif; ?>
    </div>
    
    <?php if ($args['show_progress'] && $args['duration'] > 0) : ?>
        <div class="toast-progress" aria-hidden="true">
            <div class="toast-progress-bar"></div>
        </div>
    <?php endif; ?>
</div>

<!-- Toast JavaScript -->
<script>
(function() {
    'use strict';
    
    function initToast(toastElement) {
        const toast = toastElement;
        const duration = parseInt(toast.dataset.toastDuration) || 0;
        const position = toast.dataset.toastPosition || 'top-right';
        const progressBar = toast.querySelector('.toast-progress-bar');
        
        let autoHideTimer = null;
        let progressTimer = null;
        let startTime = null;
        
        function showToast() {
            // Ensure toast container exists
            let container = document.querySelector('.toast-container[data-position="' + position + '"]');
            if (!container) {
                container = createToastContainer(position);
            }
            
            // Add toast to container
            container.appendChild(toast);
            
            // Trigger show animation
            setTimeout(() => {
                toast.classList.add('show');
                
                // Start auto-hide timer
                if (duration > 0) {
                    startAutoHide();
                }
                
                // Trigger show event
                const showEvent = new CustomEvent('toastShow', {
                    detail: { toast: toast, toastId: toast.id }
                });
                document.dispatchEvent(showEvent);
            }, 50);
        }
        
        function hideToast() {
            clearTimers();
            
            toast.classList.remove('show');
            toast.classList.add('hiding');
            
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
                
                // Trigger hide event
                const hideEvent = new CustomEvent('toastHide', {
                    detail: { toast: toast, toastId: toast.id }
                });
                document.dispatchEvent(hideEvent);
            }, 300);
        }
        
        function startAutoHide() {
            if (duration <= 0) return;
            
            startTime = Date.now();
            
            autoHideTimer = setTimeout(() => {
                hideToast();
            }, duration);
            
            // Animate progress bar
            if (progressBar) {
                progressBar.style.transition = `width ${duration}ms linear`;
                progressBar.style.width = '0%';
            }
        }
        
        function pauseAutoHide() {
            if (autoHideTimer) {
                clearTimeout(autoHideTimer);
                
                if (progressBar && startTime) {
                    const elapsed = Date.now() - startTime;
                    const remaining = Math.max(0, duration - elapsed);
                    const progress = Math.max(0, (elapsed / duration) * 100);
                    
                    progressBar.style.transition = 'none';
                    progressBar.style.width = progress + '%';
                }
            }
        }
        
        function resumeAutoHide() {
            if (duration > 0 && startTime) {
                const elapsed = Date.now() - startTime;
                const remaining = Math.max(0, duration - elapsed);
                
                if (remaining > 0) {
                    autoHideTimer = setTimeout(() => {
                        hideToast();
                    }, remaining);
                    
                    if (progressBar) {
                        progressBar.style.transition = `width ${remaining}ms linear`;
                        progressBar.style.width = '0%';
                    }
                }
            }
        }
        
        function clearTimers() {
            if (autoHideTimer) {
                clearTimeout(autoHideTimer);
                autoHideTimer = null;
            }
            if (progressTimer) {
                clearInterval(progressTimer);
                progressTimer = null;
            }
        }
        
        // Add event listeners
        toast.addEventListener('mouseenter', pauseAutoHide);
        toast.addEventListener('mouseleave', resumeAutoHide);
        toast.addEventListener('focusin', pauseAutoHide);
        toast.addEventListener('focusout', resumeAutoHide);
        
        // Close button functionality
        const closeButton = toast.querySelector('[data-dismiss="toast"]');
        if (closeButton) {
            closeButton.addEventListener('click', hideToast);
        }
        
        // Expose public methods
        toast.show = showToast;
        toast.hide = hideToast;
        
        return toast;
    }
    
    function createToastContainer(position) {
        const container = document.createElement('div');
        container.className = 'toast-container';
        container.setAttribute('data-position', position);
        container.setAttribute('aria-live', 'polite');
        container.setAttribute('aria-atomic', 'true');
        
        // Position the container
        const positionClasses = {
            'top-right': 'toast-container-top-right',
            'top-left': 'toast-container-top-left',
            'bottom-right': 'toast-container-bottom-right',
            'bottom-left': 'toast-container-bottom-left',
            'top-center': 'toast-container-top-center',
            'bottom-center': 'toast-container-bottom-center'
        };
        
        container.classList.add(positionClasses[position] || 'toast-container-top-right');
        
        document.body.appendChild(container);
        return container;
    }
    
    // Initialize this toast
    const toast = document.getElementById('<?php echo esc_js($toast_id); ?>');
    if (toast) {
        const toastInstance = initToast(toast);
        
        // Auto-show toast (remove this if you want to show manually)
        toastInstance.show();
    }
    
    // Global toast utilities
    window.RTS = window.RTS || {};
    window.RTS.showToast = function(message, options = {}) {
        const defaults = {
            type: 'info',
            title: '',
            duration: 5000,
            closable: true,
            icon: 'auto',
            position: 'top-right',
            showProgress: true
        };
        
        const settings = Object.assign(defaults, options);
        const toastId = 'dynamic-toast-' + Date.now();
        
        // Auto-determine icon
        if (settings.icon === 'auto') {
            const iconMap = {
                'success': 'check-circle',
                'error': 'x-circle',
                'warning': 'alert-triangle',
                'info': 'info-circle'
            };
            settings.icon = iconMap[settings.type] || 'info-circle';
        }
        
        // Create toast HTML
        const toastHTML = `
            <div id="${toastId}" 
                 class="toast toast-${settings.type}" 
                 role="alert" 
                 aria-live="polite" 
                 aria-atomic="true"
                 data-toast-type="${settings.type}"
                 data-toast-duration="${settings.duration}"
                 data-toast-position="${settings.position}">
                <div class="toast-content">
                    ${settings.icon ? `
                        <div class="toast-icon" aria-hidden="true">
                            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                ${getIconPath(settings.icon)}
                            </svg>
                        </div>
                    ` : ''}
                    <div class="toast-body">
                        ${settings.title ? `<div class="toast-title">${settings.title}</div>` : ''}
                        <div class="toast-message">${message}</div>
                    </div>
                    ${settings.closable ? `
                        <button type="button" class="toast-close" data-dismiss="toast" aria-label="Close notification">
                            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    ` : ''}
                </div>
                ${settings.showProgress && settings.duration > 0 ? `
                    <div class="toast-progress" aria-hidden="true">
                        <div class="toast-progress-bar"></div>
                    </div>
                ` : ''}
            </div>
        `;
        
        // Create temporary container and parse HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = toastHTML;
        const toastElement = tempDiv.firstElementChild;
        
        // Initialize and show toast
        const toastInstance = initToast(toastElement);
        toastInstance.show();
        
        return toastInstance;
    };
    
    function getIconPath(iconName) {
        const icons = {
            'check-circle': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>',
            'x-circle': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>',
            'alert-triangle': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"></path>',
            'info-circle': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>',
            'x': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>'
        };
        return icons[iconName] || icons['info-circle'];
    }
    
    // Convenience methods
    window.RTS.showSuccess = function(message, options = {}) {
        return window.RTS.showToast(message, Object.assign({ type: 'success' }, options));
    };
    
    window.RTS.showError = function(message, options = {}) {
        return window.RTS.showToast(message, Object.assign({ type: 'error' }, options));
    };
    
    window.RTS.showWarning = function(message, options = {}) {
        return window.RTS.showToast(message, Object.assign({ type: 'warning' }, options));
    };
    
    window.RTS.showInfo = function(message, options = {}) {
        return window.RTS.showToast(message, Object.assign({ type: 'info' }, options));
    };
})();
</script>

<?php
/*
Usage examples:

// Basic success toast
get_template_part('template-parts/components/toast', null, array(
    'message' => 'Data saved successfully!',
    'type' => 'success'
));

// Error toast with title
get_template_part('template-parts/components/toast', null, array(
    'title' => 'Error',
    'message' => 'Failed to save data. Please try again.',
    'type' => 'error',
    'duration' => 0 // Don't auto-hide
));

// Warning toast with custom position
get_template_part('template-parts/components/toast', null, array(
    'message' => 'Your session will expire in 5 minutes',
    'type' => 'warning',
    'position' => 'top-center',
    'duration' => 10000
));

// JavaScript usage:
// RTS.showSuccess('Operation completed successfully!');
// RTS.showError('Something went wrong!');
// RTS.showWarning('Please check your input');
// RTS.showInfo('New data available');
//
// RTS.showToast('Custom message', {
//     type: 'info',
//     title: 'Information',
//     duration: 3000,
//     position: 'bottom-right'
// });
*/
?>

<style>
/* Toast Container Positioning */
.toast-container {
    position: fixed;
    z-index: var(--z-tooltip);
    pointer-events: none;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
    max-width: 400px;
}

.toast-container-top-right {
    top: var(--spacing-xl);
    right: var(--spacing-xl);
}

.toast-container-top-left {
    top: var(--spacing-xl);
    left: var(--spacing-xl);
}

.toast-container-bottom-right {
    bottom: var(--spacing-xl);
    right: var(--spacing-xl);
}

.toast-container-bottom-left {
    bottom: var(--spacing-xl);
    left: var(--spacing-xl);
}

.toast-container-top-center {
    top: var(--spacing-xl);
    left: 50%;
    transform: translateX(-50%);
}

.toast-container-bottom-center {
    bottom: var(--spacing-xl);
    left: 50%;
    transform: translateX(-50%);
}

/* Toast Base Styles */
.toast {
    background: var(--surface-raised);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--gray-200);
    overflow: hidden;
    pointer-events: auto;
    opacity: 0;
    transform: translateX(100%);
    transition: all var(--transition-normal) var(--easing-standard);
    position: relative;
    max-width: 400px;
    min-width: 300px;
}

.toast.show {
    opacity: 1;
    transform: translateX(0);
}

.toast.hiding {
    opacity: 0;
    transform: translateX(100%);
}

/* Toast Content */
.toast-content {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-md);
    padding: var(--spacing-lg);
}

.toast-icon {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: var(--radius-full);
    margin-top: 2px;
}

.toast-body {
    flex: 1;
    min-width: 0;
}

.toast-title {
    font-weight: 600;
    font-size: var(--text-sm);
    margin-bottom: var(--spacing-xs);
    color: var(--gray-900);
}

.toast-message {
    font-size: var(--text-sm);
    color: var(--gray-700);
    line-height: 1.4;
    word-wrap: break-word;
}

.toast-close {
    flex-shrink: 0;
    background: none;
    border: none;
    color: var(--gray-500);
    cursor: pointer;
    padding: var(--spacing-xs);
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast) var(--easing-standard);
    margin-top: -2px;
}

.toast-close:hover {
    color: var(--gray-700);
    background: var(--gray-100);
}

/* Toast Types */
.toast-success {
    border-left: 4px solid var(--success);
}

.toast-success .toast-icon {
    background: rgba(22, 163, 74, 0.1);
    color: var(--success);
}

.toast-error {
    border-left: 4px solid var(--danger);
}

.toast-error .toast-icon {
    background: rgba(220, 38, 38, 0.1);
    color: var(--danger);
}

.toast-warning {
    border-left: 4px solid var(--warning);
}

.toast-warning .toast-icon {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning);
}

.toast-info {
    border-left: 4px solid var(--info);
}

.toast-info .toast-icon {
    background: rgba(14, 165, 233, 0.1);
    color: var(--info);
}

/* Progress Bar */
.toast-progress {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--gray-200);
}

.toast-progress-bar {
    height: 100%;
    width: 100%;
    background: var(--primary-500);
    transition: width 0ms linear;
}

.toast-success .toast-progress-bar {
    background: var(--success);
}

.toast-error .toast-progress-bar {
    background: var(--danger);
}

.toast-warning .toast-progress-bar {
    background: var(--warning);
}

.toast-info .toast-progress-bar {
    background: var(--info);
}

/* Dark mode adjustments */
[data-theme="dark"] .toast {
    background: var(--gray-800);
    border-color: var(--gray-700);
}

[data-theme="dark"] .toast-title {
    color: var(--gray-100);
}

[data-theme="dark"] .toast-message {
    color: var(--gray-300);
}

[data-theme="dark"] .toast-close {
    color: var(--gray-400);
}

[data-theme="dark"] .toast-close:hover {
    color: var(--gray-200);
    background: var(--gray-700);
}

/* Left-positioned toasts */
.toast-container-top-left .toast,
.toast-container-bottom-left .toast {
    transform: translateX(-100%);
}

.toast-container-top-left .toast.show,
.toast-container-bottom-left .toast.show {
    transform: translateX(0);
}

.toast-container-top-left .toast.hiding,
.toast-container-bottom-left .toast.hiding {
    transform: translateX(-100%);
}

/* Center-positioned toasts */
.toast-container-top-center .toast,
.toast-container-bottom-center .toast {
    transform: translateY(-100%);
}

.toast-container-bottom-center .toast {
    transform: translateY(100%);
}

.toast-container-top-center .toast.show,
.toast-container-bottom-center .toast.show {
    transform: translateY(0);
}

.toast-container-top-center .toast.hiding {
    transform: translateY(-100%);
}

.toast-container-bottom-center .toast.hiding {
    transform: translateY(100%);
}

/* Responsive adjustments */
@media (max-width: 640px) {
    .toast-container {
        left: var(--spacing-md) !important;
        right: var(--spacing-md) !important;
        max-width: none;
    }
    
    .toast-container-top-center,
    .toast-container-bottom-center {
        transform: none;
    }
    
    .toast {
        min-width: auto;
        width: 100%;
    }
}
</style>