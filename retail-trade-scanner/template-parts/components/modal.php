<?php
/**
 * Modal Component Template Part - Accessible Modal Dialogs
 *
 * @package RetailTradeScanner
 */

// Default modal attributes
$defaults = array(
    'id' => '',
    'title' => '',
    'content' => '',
    'size' => 'medium', // small, medium, large, full
    'type' => 'default', // default, alert, confirm
    'show_header' => true,
    'show_footer' => true,
    'show_close' => true,
    'closable' => true, // Can be closed by clicking outside or pressing ESC
    'primary_button' => array(),
    'secondary_button' => array(),
    'classes' => '',
    'attributes' => array(),
    'backdrop' => true,
    'focus_trap' => true,
);

// Parse attributes
$args = wp_parse_args($args ?? array(), $defaults);

// Generate unique modal ID if not provided
if (empty($args['id'])) {
    $args['id'] = 'modal-' . wp_unique_id();
}

// Build CSS classes
$modal_classes = array('modal');
$modal_classes[] = 'modal-' . esc_attr($args['size']);
$modal_classes[] = 'modal-' . esc_attr($args['type']);

if (!empty($args['classes'])) {
    $modal_classes[] = $args['classes'];
}

// Build attributes
$attributes = array(
    'id' => $args['id'],
    'class' => implode(' ', $modal_classes),
    'role' => 'dialog',
    'aria-modal' => 'true',
    'aria-hidden' => 'true',
    'tabindex' => '-1',
);

if (!empty($args['title'])) {
    $attributes['aria-labelledby'] = $args['id'] . '-title';
}

// Merge custom attributes
$attributes = array_merge($attributes, $args['attributes']);

// Build attribute string
$attr_string = '';
foreach ($attributes as $attr => $value) {
    $attr_string .= ' ' . esc_attr($attr) . '="' . esc_attr($value) . '"';
}
?>

<div<?php echo $attr_string; ?>>
    <?php if ($args['backdrop']) : ?>
        <div class="modal-backdrop" <?php echo $args['closable'] ? 'data-dismiss="modal"' : ''; ?>></div>
    <?php endif; ?>
    
    <div class="modal-dialog" role="document">
        <div class="modal-content glass-card">
            <?php if ($args['show_header']) : ?>
                <div class="modal-header">
                    <?php if (!empty($args['title'])) : ?>
                        <h2 class="modal-title" id="<?php echo esc_attr($args['id']); ?>-title">
                            <?php echo esc_html($args['title']); ?>
                        </h2>
                    <?php endif; ?>
                    
                    <?php if ($args['show_close'] && $args['closable']) : ?>
                        <button type="button" 
                                class="modal-close btn-icon btn-ghost" 
                                data-dismiss="modal" 
                                aria-label="<?php esc_attr_e('Close modal', 'retail-trade-scanner'); ?>">
                            <?php echo rts_get_icon('x', array('width' => '20', 'height' => '20')); ?>
                        </button>
                    <?php endif; ?>
                </div>
            <?php endif; ?>

            <div class="modal-body">
                <?php if (!empty($args['content'])) : ?>
                    <?php echo wp_kses_post($args['content']); ?>
                <?php else : ?>
                    <!-- Content will be inserted dynamically -->
                    <div class="modal-content-placeholder"></div>
                <?php endif; ?>
            </div>

            <?php if ($args['show_footer'] && (!empty($args['primary_button']) || !empty($args['secondary_button']))) : ?>
                <div class="modal-footer">
                    <div class="modal-actions">
                        <?php if (!empty($args['secondary_button'])) : ?>
                            <?php
                            $secondary_defaults = array(
                                'text' => __('Cancel', 'retail-trade-scanner'),
                                'variant' => 'secondary',
                                'type' => 'button',
                                'classes' => 'modal-secondary-btn',
                                'attributes' => array('data-dismiss' => 'modal')
                            );
                            $secondary_args = wp_parse_args($args['secondary_button'], $secondary_defaults);
                            
                            get_template_part('template-parts/components/button', null, $secondary_args);
                            ?>
                        <?php endif; ?>

                        <?php if (!empty($args['primary_button'])) : ?>
                            <?php
                            $primary_defaults = array(
                                'text' => __('OK', 'retail-trade-scanner'),
                                'variant' => 'primary',
                                'type' => 'button',
                                'classes' => 'modal-primary-btn'
                            );
                            $primary_args = wp_parse_args($args['primary_button'], $primary_defaults);
                            
                            get_template_part('template-parts/components/button', null, $primary_args);
                            ?>
                        <?php endif; ?>
                    </div>
                </div>
            <?php endif; ?>
        </div>
    </div>
</div>

<!-- Modal JavaScript -->
<script>
(function() {
    'use strict';
    
    // Modal functionality
    function initModal(modalElement) {
        const modal = modalElement;
        const modalId = modal.id;
        const closable = <?php echo $args['closable'] ? 'true' : 'false'; ?>;
        const focusTrap = <?php echo $args['focus_trap'] ? 'true' : 'false'; ?>;
        
        let focusableElements = [];
        let firstFocusableElement = null;
        let lastFocusableElement = null;
        let previouslyFocusedElement = null;

        function updateFocusableElements() {
            focusableElements = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            firstFocusableElement = focusableElements[0];
            lastFocusableElement = focusableElements[focusableElements.length - 1];
        }

        function showModal() {
            previouslyFocusedElement = document.activeElement;
            
            modal.classList.add('show');
            modal.setAttribute('aria-hidden', 'false');
            document.body.classList.add('modal-open');
            document.body.style.overflow = 'hidden';

            if (focusTrap) {
                updateFocusableElements();
                if (firstFocusableElement) {
                    firstFocusableElement.focus();
                }
            }

            // Trigger custom event
            const showEvent = new CustomEvent('modalShow', {
                detail: { modalId: modalId, modal: modal }
            });
            document.dispatchEvent(showEvent);
        }

        function hideModal() {
            modal.classList.remove('show');
            modal.setAttribute('aria-hidden', 'true');
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';

            if (previouslyFocusedElement) {
                previouslyFocusedElement.focus();
            }

            // Trigger custom event
            const hideEvent = new CustomEvent('modalHide', {
                detail: { modalId: modalId, modal: modal }
            });
            document.dispatchEvent(hideEvent);
        }

        // Close button functionality
        modal.querySelectorAll('[data-dismiss="modal"]').forEach(closeBtn => {
            closeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (closable) {
                    hideModal();
                }
            });
        });

        // Escape key functionality
        if (closable) {
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && modal.classList.contains('show')) {
                    hideModal();
                }
            });
        }

        // Focus trap functionality
        if (focusTrap) {
            modal.addEventListener('keydown', function(e) {
                if (e.key === 'Tab' && modal.classList.contains('show')) {
                    if (e.shiftKey) {
                        if (document.activeElement === firstFocusableElement) {
                            e.preventDefault();
                            lastFocusableElement.focus();
                        }
                    } else {
                        if (document.activeElement === lastFocusableElement) {
                            e.preventDefault();
                            firstFocusableElement.focus();
                        }
                    }
                }
            });
        }

        // Expose modal methods
        modal.show = showModal;
        modal.hide = hideModal;
        modal.toggle = function() {
            if (modal.classList.contains('show')) {
                hideModal();
            } else {
                showModal();
            }
        };

        return modal;
    }

    // Initialize this modal
    const modal = document.getElementById('<?php echo esc_js($args['id']); ?>');
    if (modal) {
        initModal(modal);
    }

    // Global modal utilities
    window.RTS = window.RTS || {};
    window.RTS.showModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal && modal.show) {
            modal.show();
        }
    };

    window.RTS.hideModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal && modal.hide) {
            modal.hide();
        }
    };

    window.RTS.createModal = function(options) {
        const defaults = {
            title: '',
            content: '',
            size: 'medium',
            type: 'default',
            primaryButton: null,
            secondaryButton: null,
            closable: true,
            onShow: null,
            onHide: null
        };

        const settings = Object.assign(defaults, options);
        const modalId = 'dynamic-modal-' + Date.now();

        // Create modal HTML
        const modalHTML = `
            <div id="${modalId}" class="modal modal-${settings.size} modal-${settings.type}" role="dialog" aria-modal="true" aria-hidden="true" tabindex="-1">
                <div class="modal-backdrop" data-dismiss="modal"></div>
                <div class="modal-dialog" role="document">
                    <div class="modal-content glass-card">
                        <div class="modal-header">
                            <h2 class="modal-title">${settings.title}</h2>
                            <button type="button" class="modal-close btn-icon btn-ghost" data-dismiss="modal" aria-label="Close modal">
                                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>
                        <div class="modal-body">
                            ${settings.content}
                        </div>
                        ${settings.primaryButton || settings.secondaryButton ? `
                            <div class="modal-footer">
                                <div class="modal-actions">
                                    ${settings.secondaryButton ? `<button type="button" class="btn btn-secondary modal-secondary-btn" data-dismiss="modal">${settings.secondaryButton.text || 'Cancel'}</button>` : ''}
                                    ${settings.primaryButton ? `<button type="button" class="btn btn-primary modal-primary-btn">${settings.primaryButton.text || 'OK'}</button>` : ''}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;

        // Insert modal into DOM
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        const modal = document.getElementById(modalId);
        
        // Initialize modal
        const modalInstance = initModal(modal);

        // Add button event listeners
        if (settings.primaryButton && settings.primaryButton.onClick) {
            modal.querySelector('.modal-primary-btn').addEventListener('click', settings.primaryButton.onClick);
        }

        if (settings.secondaryButton && settings.secondaryButton.onClick) {
            modal.querySelector('.modal-secondary-btn').addEventListener('click', settings.secondaryButton.onClick);
        }

        // Add lifecycle event listeners
        if (settings.onShow) {
            document.addEventListener('modalShow', function(e) {
                if (e.detail.modalId === modalId) {
                    settings.onShow(e.detail.modal);
                }
            });
        }

        if (settings.onHide) {
            document.addEventListener('modalHide', function(e) {
                if (e.detail.modalId === modalId) {
                    settings.onHide(e.detail.modal);
                    // Clean up - remove modal from DOM after hide animation
                    setTimeout(() => {
                        if (modal.parentNode) {
                            modal.parentNode.removeChild(modal);
                        }
                    }, 300);
                }
            });
        }

        return modalInstance;
    };
})();
</script>

<?php
/*
Usage examples:

// Basic modal
get_template_part('template-parts/components/modal', null, array(
    'id' => 'example-modal',
    'title' => 'Example Modal',
    'content' => '<p>This is modal content.</p>',
    'primary_button' => array(
        'text' => 'Save',
        'attributes' => array('onclick' => 'saveData()')
    )
));

// Confirmation modal
get_template_part('template-parts/components/modal', null, array(
    'id' => 'confirm-delete',
    'title' => 'Confirm Deletion',
    'content' => '<p>Are you sure you want to delete this item?</p>',
    'type' => 'confirm',
    'size' => 'small',
    'primary_button' => array(
        'text' => 'Delete',
        'variant' => 'danger'
    ),
    'secondary_button' => array(
        'text' => 'Cancel'
    )
));

// Large modal with custom content
get_template_part('template-parts/components/modal', null, array(
    'id' => 'stock-details',
    'title' => 'Stock Details',
    'size' => 'large',
    'show_footer' => false
));

// JavaScript usage:
// RTS.showModal('example-modal');
// RTS.hideModal('example-modal');
// 
// RTS.createModal({
//     title: 'Dynamic Modal',
//     content: '<p>This modal was created dynamically</p>',
//     primaryButton: {
//         text: 'OK',
//         onClick: function() { console.log('OK clicked'); }
//     }
// }).show();
*/