/**
 * Enhanced UI Components
 * Professional Notification System and Advanced Tooltip System
 */

class EnhancedUI {
    constructor() {
        this.notifications = [];
        this.tooltips = new Map();
        this.init();
    }

    init() {
        this.initNotificationSystem();
        this.initTooltipSystem();
        this.initScrollAnimations();
        this.initProgressIndicators();
        this.initAdvancedModals();
        this.initRippleEffects();
        this.initFloatingLabels();
        this.initAdvancedTables();
        this.initLazyLoading();
        this.initVirtualizedLists();
        this.initAdvancedCharts();
        this.initParallaxEffects();
        this.initAdvancedNavigation();
    }

    // Professional Notification System
    initNotificationSystem() {
        // Create notification container if it doesn't exist
        if (!document.querySelector('.notification-container')) {
            const container = document.createElement('div');
            container.className = 'notification-container';
            container.setAttribute('aria-live', 'polite');
            container.setAttribute('aria-label', 'Notifications');
            document.body.appendChild(container);
        }

        // Global notification function with enhanced features
        window.showNotification = (message, type = 'info', options = {}) => {
            const settings = {
                duration: options.duration !== undefined ? options.duration : 5000,
                persistent: options.persistent || false,
                position: options.position || 'top-right',
                showProgress: options.showProgress !== false,
                allowHtml: options.allowHtml || false,
                onClose: options.onClose || null,
                onClick: options.onClick || null,
                actions: options.actions || [],
                id: options.id || this.generateNotificationId(),
                ...options
            };

            return this.createNotification(message, type, settings);
        };

        // Batch notifications
        window.showNotificationBatch = (notifications) => {
            return notifications.map(notif => 
                window.showNotification(notif.message, notif.type, notif.options)
            );
        };

        // Update existing notification
        window.updateNotification = (id, message, type) => {
            const notification = document.querySelector(`[data-notification-id="${id}"]`);
            if (notification) {
                this.updateNotificationContent(notification, message, type);
            }
        };

        // Close notification
        window.closeNotification = (id) => {
            const notification = document.querySelector(`[data-notification-id="${id}"]`);
            if (notification) {
                this.closeNotification(notification);
            }
        };

        // Clear all notifications
        window.clearAllNotifications = () => {
            const notifications = document.querySelectorAll('.notification');
            notifications.forEach(notif => this.closeNotification(notif));
        };
    }

    createNotification(message, type, settings) {
        const container = document.querySelector('.notification-container');
        const notification = document.createElement('div');
        const notificationId = settings.id;
        
        notification.className = `notification ${type} notification-${settings.position}`;
        notification.setAttribute('data-notification-id', notificationId);
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-atomic', 'true');

        const icon = this.getNotificationIcon(type);
        const title = this.getNotificationTitle(type);
        
        notification.innerHTML = `
            <div class="notification-header">
                <div class="notification-icon" aria-hidden="true">${icon}</div>
                <div class="notification-title">${title}</div>
                <button class="notification-close" aria-label="Close notification" title="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="notification-content">
                ${settings.allowHtml ? message : this.escapeHtml(message)}
            </div>
            ${settings.actions.length > 0 ? this.createActionButtons(settings.actions) : ''}
            ${settings.showProgress && settings.duration > 0 ? '<div class="notification-progress"><div class="notification-progress-bar"></div></div>' : ''}
        `;

        // Add event listeners
        this.setupNotificationEvents(notification, settings);

        // Position the notification container
        this.positionNotificationContainer(container, settings.position);

        // Add to container with stacking
        if (settings.position.includes('bottom')) {
            container.insertBefore(notification, container.firstChild);
        } else {
            container.appendChild(notification);
        }

        // Trigger entrance animation
        requestAnimationFrame(() => {
            notification.classList.add('notification-show');
        });

        // Handle progress bar animation
        if (settings.showProgress && settings.duration > 0) {
            this.animateProgressBar(notification, settings.duration);
        }

        // Auto remove if not persistent
        if (!settings.persistent && settings.duration > 0) {
            setTimeout(() => {
                this.closeNotification(notification);
            }, settings.duration);
        }

        // Store notification reference
        this.notifications.push({
            id: notificationId,
            element: notification,
            settings: settings
        });

        return notificationId;
    }

    setupNotificationEvents(notification, settings) {
        // Close button
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.closeNotification(notification);
            if (settings.onClose) settings.onClose();
        });

        // Click handler
        if (settings.onClick) {
            notification.addEventListener('click', settings.onClick);
            notification.style.cursor = 'pointer';
        }

        // Action buttons
        const actionBtns = notification.querySelectorAll('.notification-action');
        actionBtns.forEach((btn, index) => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = settings.actions[index];
                if (action.handler) {
                    action.handler();
                }
                if (action.closeOnClick !== false) {
                    this.closeNotification(notification);
                }
            });
        });

        // Pause on hover
        notification.addEventListener('mouseenter', () => {
            notification.classList.add('notification-paused');
        });

        notification.addEventListener('mouseleave', () => {
            notification.classList.remove('notification-paused');
        });
    }

    createActionButtons(actions) {
        return `
            <div class="notification-actions">
                ${actions.map(action => `
                    <button class="notification-action ${action.style || 'primary'}" 
                            title="${action.text}">
                        ${action.text}
                    </button>
                `).join('')}
            </div>
        `;
    }

    animateProgressBar(notification, duration) {
        const progressBar = notification.querySelector('.notification-progress-bar');
        if (!progressBar) return;

        progressBar.style.transition = `width ${duration}ms linear`;
        progressBar.style.width = '0%';

        // Start animation
        requestAnimationFrame(() => {
            progressBar.style.width = '100%';
        });

        // Pause/resume on hover
        notification.addEventListener('mouseenter', () => {
            const computedStyle = getComputedStyle(progressBar);
            const currentWidth = computedStyle.width;
            progressBar.style.width = currentWidth;
            progressBar.style.transition = 'none';
        });

        notification.addEventListener('mouseleave', () => {
            const currentWidth = parseFloat(progressBar.style.width);
            const remainingTime = duration * (currentWidth / 100);
            progressBar.style.transition = `width ${remainingTime}ms linear`;
            progressBar.style.width = '100%';
        });
    }

    closeNotification(notification) {
        if (!notification || notification.classList.contains('notification-closing')) return;

        notification.classList.add('notification-closing');
        notification.classList.remove('notification-show');

        // Remove from notifications array
        const index = this.notifications.findIndex(n => n.element === notification);
        if (index > -1) {
            this.notifications.splice(index, 1);
        }

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    updateNotificationContent(notification, message, type) {
        const content = notification.querySelector('.notification-content');
        const icon = notification.querySelector('.notification-icon');
        const title = notification.querySelector('.notification-title');

        if (content) content.textContent = message;
        if (icon) icon.textContent = this.getNotificationIcon(type);
        if (title) title.textContent = this.getNotificationTitle(type);

        // Update notification class
        notification.className = notification.className.replace(/notification-(success|error|warning|info)/, `notification-${type}`);
    }

    positionNotificationContainer(container, position) {
        const positions = {
            'top-right': { top: '20px', right: '20px', left: 'auto', bottom: 'auto' },
            'top-left': { top: '20px', left: '20px', right: 'auto', bottom: 'auto' },
            'top-center': { top: '20px', left: '50%', transform: 'translateX(-50%)', right: 'auto', bottom: 'auto' },
            'bottom-right': { bottom: '20px', right: '20px', left: 'auto', top: 'auto' },
            'bottom-left': { bottom: '20px', left: '20px', right: 'auto', top: 'auto' },
            'bottom-center': { bottom: '20px', left: '50%', transform: 'translateX(-50%)', right: 'auto', top: 'auto' }
        };

        const pos = positions[position] || positions['top-right'];
        Object.assign(container.style, pos);
    }

    generateNotificationId() {
        return 'notification-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    getNotificationIcon(type) {
        const icons = {
            success: '✓',
            error: '✗',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }

    getNotificationTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information'
        };
        return titles[type] || titles.info;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Advanced Tooltip System
    initTooltipSystem() {
        // Enhanced tooltip functionality
        window.showTooltip = (element, content, options = {}) => {
            return this.createTooltip(element, content, options);
        };

        window.hideTooltip = (element) => {
            this.destroyTooltip(element);
        };

        // Auto-initialize tooltips on elements with data-tooltip
        this.observeTooltipElements();

        // Global event listeners
        document.addEventListener('mouseenter', this.handleTooltipMouseEnter.bind(this), true);
        document.addEventListener('mouseleave', this.handleTooltipMouseLeave.bind(this), true);
        document.addEventListener('focus', this.handleTooltipFocus.bind(this), true);
        document.addEventListener('blur', this.handleTooltipBlur.bind(this), true);
        document.addEventListener('scroll', this.handleTooltipScroll.bind(this), true);
        window.addEventListener('resize', this.handleTooltipResize.bind(this));
    }

    observeTooltipElements() {
        // Use MutationObserver to watch for new elements with data-tooltip
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.initializeTooltipsInElement(node);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Initialize existing elements
        this.initializeTooltipsInElement(document);
    }

    initializeTooltipsInElement(element) {
        const tooltipElements = element.querySelectorAll ? 
            element.querySelectorAll('[data-tooltip]') : 
            (element.hasAttribute && element.hasAttribute('data-tooltip') ? [element] : []);

        tooltipElements.forEach(el => {
            if (!el.hasAttribute('data-tooltip-initialized')) {
                el.setAttribute('data-tooltip-initialized', 'true');
                el.setAttribute('aria-describedby', this.generateTooltipId());
            }
        });
    }

    handleTooltipMouseEnter(e) {
        const element = e.target;
        if (element.hasAttribute('data-tooltip')) {
            clearTimeout(element._tooltipTimeout);
            element._tooltipTimeout = setTimeout(() => {
                this.showElementTooltip(element);
            }, this.getTooltipDelay(element));
        }
    }

    handleTooltipMouseLeave(e) {
        const element = e.target;
        if (element.hasAttribute('data-tooltip')) {
            clearTimeout(element._tooltipTimeout);
            this.hideElementTooltip(element);
        }
    }

    handleTooltipFocus(e) {
        const element = e.target;
        if (element.hasAttribute('data-tooltip')) {
            this.showElementTooltip(element);
        }
    }

    handleTooltipBlur(e) {
        const element = e.target;
        if (element.hasAttribute('data-tooltip')) {
            this.hideElementTooltip(element);
        }
    }

    handleTooltipScroll() {
        // Update positions of visible tooltips
        this.tooltips.forEach((tooltip, element) => {
            if (tooltip.visible) {
                this.positionTooltip(element, tooltip.element);
            }
        });
    }

    handleTooltipResize() {
        // Reposition all visible tooltips
        this.handleTooltipScroll();
    }

    showElementTooltip(element) {
        const content = element.getAttribute('data-tooltip');
        const options = this.parseTooltipOptions(element);
        this.createTooltip(element, content, options);
    }

    hideElementTooltip(element) {
        this.destroyTooltip(element);
    }

    createTooltip(element, content, options = {}) {
        // Destroy existing tooltip
        this.destroyTooltip(element);

        const settings = {
            position: options.position || element.getAttribute('data-tooltip-position') || 'top',
            theme: options.theme || element.getAttribute('data-tooltip-theme') || 'dark',
            allowHtml: options.allowHtml || element.hasAttribute('data-tooltip-html'),
            arrow: options.arrow !== false,
            animation: options.animation || 'fade',
            delay: options.delay || parseInt(element.getAttribute('data-tooltip-delay')) || 0,
            maxWidth: options.maxWidth || element.getAttribute('data-tooltip-max-width') || '300px',
            trigger: options.trigger || 'hover',
            interactive: options.interactive || element.hasAttribute('data-tooltip-interactive'),
            ...options
        };

        const tooltip = document.createElement('div');
        tooltip.className = `tooltip-enhanced tooltip-${settings.theme} tooltip-${settings.animation}`;
        tooltip.setAttribute('role', 'tooltip');
        tooltip.style.maxWidth = settings.maxWidth;
        tooltip.style.zIndex = '10000';

        // Content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'tooltip-content';
        if (settings.allowHtml) {
            contentDiv.innerHTML = content;
        } else {
            contentDiv.textContent = content;
        }
        tooltip.appendChild(contentDiv);

        // Arrow
        if (settings.arrow) {
            const arrow = document.createElement('div');
            arrow.className = 'tooltip-arrow';
            tooltip.appendChild(arrow);
        }

        // Add to DOM
        document.body.appendChild(tooltip);

        // Position tooltip
        this.positionTooltip(element, tooltip, settings.position);

        // Show with animation
        requestAnimationFrame(() => {
            tooltip.classList.add('tooltip-visible');
        });

        // Store tooltip reference
        this.tooltips.set(element, {
            element: tooltip,
            settings: settings,
            visible: true
        });

        // Interactive tooltip events
        if (settings.interactive) {
            this.setupInteractiveTooltip(element, tooltip);
        }

        return tooltip;
    }

    destroyTooltip(element) {
        const tooltipData = this.tooltips.get(element);
        if (tooltipData) {
            tooltipData.visible = false;
            tooltipData.element.classList.remove('tooltip-visible');
            
            setTimeout(() => {
                if (tooltipData.element.parentNode) {
                    tooltipData.element.parentNode.removeChild(tooltipData.element);
                }
                this.tooltips.delete(element);
            }, 200);
        }
    }

    positionTooltip(element, tooltip, preferredPosition = 'top') {
        const elementRect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const scrollX = window.pageXOffset;
        const scrollY = window.pageYOffset;

        const spacing = 8;
        let position = preferredPosition;
        let top, left;

        // Calculate position with fallback logic
        const positions = {
            top: {
                top: elementRect.top + scrollY - tooltipRect.height - spacing,
                left: elementRect.left + scrollX + (elementRect.width - tooltipRect.width) / 2,
                canFit: elementRect.top > tooltipRect.height + spacing
            },
            bottom: {
                top: elementRect.bottom + scrollY + spacing,
                left: elementRect.left + scrollX + (elementRect.width - tooltipRect.width) / 2,
                canFit: elementRect.bottom + tooltipRect.height + spacing < viewportHeight
            },
            left: {
                top: elementRect.top + scrollY + (elementRect.height - tooltipRect.height) / 2,
                left: elementRect.left + scrollX - tooltipRect.width - spacing,
                canFit: elementRect.left > tooltipRect.width + spacing
            },
            right: {
                top: elementRect.top + scrollY + (elementRect.height - tooltipRect.height) / 2,
                left: elementRect.right + scrollX + spacing,
                canFit: elementRect.right + tooltipRect.width + spacing < viewportWidth
            }
        };

        // Find best position
        if (!positions[position].canFit) {
            // Try opposite position first
            const opposites = { top: 'bottom', bottom: 'top', left: 'right', right: 'left' };
            const opposite = opposites[position];
            
            if (positions[opposite].canFit) {
                position = opposite;
            } else {
                // Find any position that fits
                position = Object.keys(positions).find(pos => positions[pos].canFit) || position;
            }
        }

        const finalPos = positions[position];
        top = finalPos.top;
        left = finalPos.left;

        // Ensure tooltip doesn't go off screen
        if (left < 10) left = 10;
        if (left + tooltipRect.width > viewportWidth - 10) {
            left = viewportWidth - tooltipRect.width - 10;
        }
        if (top < 10) top = 10;
        if (top + tooltipRect.height > viewportHeight + scrollY - 10) {
            top = viewportHeight + scrollY - tooltipRect.height - 10;
        }

        // Apply position
        tooltip.style.position = 'absolute';
        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;

        // Update arrow position
        const arrow = tooltip.querySelector('.tooltip-arrow');
        if (arrow) {
            this.positionTooltipArrow(arrow, position, elementRect, tooltip.getBoundingClientRect());
        }

        // Add position class
        tooltip.className = tooltip.className.replace(/tooltip-pos-\w+/g, '');
        tooltip.classList.add(`tooltip-pos-${position}`);
    }

    positionTooltipArrow(arrow, position, elementRect, tooltipRect) {
        arrow.className = `tooltip-arrow tooltip-arrow-${position}`;
        
        const arrowSize = 6;
        
        switch (position) {
            case 'top':
            case 'bottom':
                const horizontalCenter = elementRect.left + elementRect.width / 2 - tooltipRect.left;
                arrow.style.left = `${Math.max(arrowSize, Math.min(tooltipRect.width - arrowSize, horizontalCenter))}px`;
                break;
            case 'left':
            case 'right':
                const verticalCenter = elementRect.top + elementRect.height / 2 - tooltipRect.top;
                arrow.style.top = `${Math.max(arrowSize, Math.min(tooltipRect.height - arrowSize, verticalCenter))}px`;
                break;
        }
    }

    setupInteractiveTooltip(element, tooltip) {
        let hideTimeout;

        const cancelHide = () => {
            clearTimeout(hideTimeout);
        };

        const scheduleHide = () => {
            hideTimeout = setTimeout(() => {
                this.destroyTooltip(element);
            }, 100);
        };

        // Keep tooltip visible when hovering over it
        tooltip.addEventListener('mouseenter', cancelHide);
        tooltip.addEventListener('mouseleave', scheduleHide);
        
        // Schedule hide when leaving element
        element.addEventListener('mouseleave', scheduleHide);
        element.addEventListener('mouseenter', cancelHide);
    }

    parseTooltipOptions(element) {
        const options = {};
        
        // Parse data attributes
        const attrs = element.attributes;
        for (let i = 0; i < attrs.length; i++) {
            const attr = attrs[i];
            if (attr.name.startsWith('data-tooltip-')) {
                const key = attr.name.replace('data-tooltip-', '').replace(/-([a-z])/g, (g) => g[1].toUpperCase());
                options[key] = attr.value;
            }
        }

        return options;
    }

    getTooltipDelay(element) {
        return parseInt(element.getAttribute('data-tooltip-delay')) || 500;
    }

    generateTooltipId() {
        return 'tooltip-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    // Keep all other existing methods from the previous implementation
    // (initScrollAnimations, initProgressIndicators, etc.)
    // ... [Previous methods remain the same] ...

    // Scroll Animations
    initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.scroll-reveal').forEach(el => {
            observer.observe(el);
        });

        let lastScrollTop = 0;
        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const nav = document.querySelector('.nav-enhanced');
            
            if (nav) {
                if (scrollTop > 100) {
                    nav.classList.add('scrolled');
                } else {
                    nav.classList.remove('scrolled');
                }

                if (scrollTop > lastScrollTop && scrollTop > 200) {
                    nav.style.transform = 'translateY(-100%)';
                } else {
                    nav.style.transform = 'translateY(0)';
                }
            }
            
            lastScrollTop = scrollTop;
        });
    }

    // Progress Indicators
    initProgressIndicators() {
        window.updateProgress = (element, percentage) => {
            const circle = element.querySelector('.progress-ring-progress');
            const text = element.querySelector('.progress-ring-text');
            
            if (circle && text) {
                const circumference = 2 * Math.PI * 40;
                const strokeDasharray = `${percentage / 100 * circumference} ${circumference}`;
                circle.style.strokeDasharray = strokeDasharray;
                text.textContent = `${Math.round(percentage)}%`;
            }
        };

        const progressRings = document.querySelectorAll('.progress-ring');
        const progressObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const targetPercentage = entry.target.dataset.percentage || 75;
                    this.animateProgress(entry.target, targetPercentage);
                }
            });
        });

        progressRings.forEach(ring => progressObserver.observe(ring));
    }

    animateProgress(element, targetPercentage) {
        let current = 0;
        const increment = targetPercentage / 60;
        
        const animate = () => {
            current += increment;
            if (current <= targetPercentage) {
                window.updateProgress(element, current);
                requestAnimationFrame(animate);
            } else {
                window.updateProgress(element, targetPercentage);
            }
        };
        
        animate();
    }

    // Advanced Modals
    initAdvancedModals() {
        window.showModal = (content, options = {}) => {
            const modal = document.createElement('div');
            modal.className = 'modal-enhanced';
            modal.innerHTML = `
                <div class="modal-content-enhanced" style="max-width: ${options.maxWidth || '600px'}">
                    ${options.showClose !== false ? '<button class="modal-close" onclick="this.closest(\'.modal-enhanced\').remove()">&times;</button>' : ''}
                    ${content}
                </div>
            `;

            document.body.appendChild(modal);
            setTimeout(() => modal.classList.add('show'), 10);

            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });

            return modal;
        };
    }

    closeModal(modal) {
        modal.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
    }

    // Continue with other methods...
    // (Adding remaining methods for completeness)

    initRippleEffects() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('ripple')) {
                this.createRipple(e.target, e);
            }
        });
    }

    createRipple(element, event) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        `;

        element.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    }

    initFloatingLabels() {
        const inputs = document.querySelectorAll('.form-control-enhanced');
        
        inputs.forEach(input => {
            if (!input.nextElementSibling?.classList.contains('floating-label')) {
                const label = document.createElement('label');
                label.className = 'floating-label';
                label.textContent = input.placeholder || 'Enter value';
                input.parentNode.insertBefore(label, input.nextSibling);
            }

            if (!input.placeholder) {
                input.placeholder = ' ';
            }
        });
    }

    initAdvancedTables() {
        const tables = document.querySelectorAll('.table-enhanced');
        
        tables.forEach(table => {
            const headers = table.querySelectorAll('th[data-sortable]');
            headers.forEach(header => {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    this.sortTable(table, header);
                });
            });

            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                row.addEventListener('click', () => {
                    rows.forEach(r => r.classList.remove('selected'));
                    row.classList.add('selected');
                });
            });
        });
    }

    sortTable(table, header) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const columnIndex = Array.from(header.parentNode.children).indexOf(header);
        const isAscending = !header.classList.contains('sorted-asc');

        rows.sort((a, b) => {
            const aValue = a.children[columnIndex].textContent.trim();
            const bValue = b.children[columnIndex].textContent.trim();
            
            const comparison = isNaN(aValue) ? 
                aValue.localeCompare(bValue) : 
                parseFloat(aValue) - parseFloat(bValue);
            
            return isAscending ? comparison : -comparison;
        });

        header.parentNode.querySelectorAll('th').forEach(h => {
            h.classList.remove('sorted-asc', 'sorted-desc');
        });

        header.classList.add(isAscending ? 'sorted-asc' : 'sorted-desc');
        rows.forEach(row => tbody.appendChild(row));
    }

    initLazyLoading() {
        const lazyElements = document.querySelectorAll('[data-lazy]');
        
        if (lazyElements.length === 0) return;

        const lazyObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadLazyElement(entry.target);
                    lazyObserver.unobserve(entry.target);
                }
            });
        });

        lazyElements.forEach(element => lazyObserver.observe(element));
    }

    loadLazyElement(element) {
        const src = element.dataset.lazy;
        
        if (element.tagName === 'IMG') {
            element.src = src;
        } else {
            fetch(src)
                .then(response => response.text())
                .then(html => {
                    element.innerHTML = html;
                    element.classList.add('lazy-loaded');
                });
        }
    }

    initVirtualizedLists() {
        const virtualLists = document.querySelectorAll('[data-virtual-list]');
        virtualLists.forEach(list => this.createVirtualList(list));
    }

    createVirtualList(container) {
        const itemHeight = parseInt(container.dataset.itemHeight) || 50;
        const buffer = 5;
        let scrollTop = 0;
        let data = JSON.parse(container.dataset.items || '[]');

        const viewport = document.createElement('div');
        viewport.style.cssText = `
            height: ${container.dataset.height || '400px'};
            overflow-y: auto;
            position: relative;
        `;

        const content = document.createElement('div');
        content.style.height = `${data.length * itemHeight}px`;

        const visibleItems = document.createElement('div');
        visibleItems.style.position = 'absolute';
        visibleItems.style.top = '0';
        visibleItems.style.width = '100%';

        content.appendChild(visibleItems);
        viewport.appendChild(content);
        container.appendChild(viewport);

        const updateVisibleItems = () => {
            const containerHeight = viewport.clientHeight;
            const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - buffer);
            const endIndex = Math.min(data.length, Math.ceil((scrollTop + containerHeight) / itemHeight) + buffer);

            visibleItems.innerHTML = '';
            visibleItems.style.transform = `translateY(${startIndex * itemHeight}px)`;

            for (let i = startIndex; i < endIndex; i++) {
                const item = document.createElement('div');
                item.style.height = `${itemHeight}px`;
                item.innerHTML = this.renderVirtualListItem(data[i], i);
                visibleItems.appendChild(item);
            }
        };

        viewport.addEventListener('scroll', () => {
            scrollTop = viewport.scrollTop;
            updateVisibleItems();
        });

        updateVisibleItems();
    }

    renderVirtualListItem(item, index) {
        return `<div class="virtual-list-item">${item.name || item.title || `Item ${index}`}</div>`;
    }

    initAdvancedCharts() {
        window.createAdvancedChart = (canvas, config) => {
            const ctx = canvas.getContext('2d');
            
            const defaultConfig = {
                type: 'line',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    },
                    plugins: {
                        tooltip: {
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: '#3498db',
                            borderWidth: 1,
                            cornerRadius: 8,
                            displayColors: false
                        },
                        legend: {
                            position: 'top',
                            labels: {
                                usePointStyle: true,
                                padding: 20
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { color: '#6c757d' }
                        },
                        y: {
                            grid: { color: 'rgba(0,0,0,0.1)' },
                            ticks: { color: '#6c757d' }
                        }
                    },
                    animation: {
                        duration: 2000,
                        easing: 'easeInOutQuart'
                    }
                }
            };

            const mergedConfig = this.deepMerge(defaultConfig, config);
            return new Chart(ctx, mergedConfig);
        };
    }

    initParallaxEffects() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        
        if (parallaxElements.length === 0) return;

        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const speed = element.dataset.parallax || 0.5;
                const yPos = -(scrolled * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        });
    }

    initAdvancedNavigation() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('nav a[href^="#"]');

        if (sections.length > 0 && navLinks.length > 0) {
            const sectionObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        navLinks.forEach(link => {
                            link.classList.remove('active');
                            if (link.getAttribute('href') === `#${entry.target.id}`) {
                                link.classList.add('active');
                            }
                        });
                    }
                });
            }, { threshold: 0.3 });

            sections.forEach(section => sectionObserver.observe(section));
        }
    }

    deepMerge(target, source) {
        const output = Object.assign({}, target);
        if (this.isObject(target) && this.isObject(source)) {
            Object.keys(source).forEach(key => {
                if (this.isObject(source[key])) {
                    if (!(key in target))
                        Object.assign(output, { [key]: source[key] });
                    else
                        output[key] = this.deepMerge(target[key], source[key]);
                } else {
                    Object.assign(output, { [key]: source[key] });
                }
            });
        }
        return output;
    }

    isObject(item) {
        return item && typeof item === 'object' && !Array.isArray(item);
    }
}

// Initialize Enhanced UI
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedUI = new EnhancedUI();
});

// Add required CSS styles
const style = document.createElement('style');
style.textContent = `
    /* Notification System Styles */
    .notification-container {
        position: fixed;
        z-index: 10000;
        max-width: 400px;
        pointer-events: none;
    }

    .notification {
        background: white;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        transform: translateX(450px);
        opacity: 0;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        pointer-events: all;
        position: relative;
        overflow: hidden;
    }

    .notification.notification-show {
        transform: translateX(0);
        opacity: 1;
    }

    .notification.notification-closing {
        transform: translateX(450px);
        opacity: 0;
    }

    .notification.notification-paused .notification-progress-bar {
        animation-play-state: paused;
    }

    .notification.success { border-left: 4px solid #27ae60; }
    .notification.error { border-left: 4px solid #e74c3c; }
    .notification.warning { border-left: 4px solid #f39c12; }
    .notification.info { border-left: 4px solid #3498db; }

    .notification-header {
        display: flex;
        align-items: center;
        padding: 15px 15px 10px 15px;
    }

    .notification-icon {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        font-size: 12px;
        color: white;
        font-weight: bold;
    }

    .notification.success .notification-icon { background: #27ae60; }
    .notification.error .notification-icon { background: #e74c3c; }
    .notification.warning .notification-icon { background: #f39c12; }
    .notification.info .notification-icon { background: #3498db; }

    .notification-title {
        font-weight: 600;
        color: #2c3e50;
        flex: 1;
    }

    .notification-close {
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        opacity: 0.7;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .notification-close:hover {
        opacity: 1;
    }

    .notification-content {
        padding: 0 15px 15px 15px;
        color: #555;
        line-height: 1.4;
    }

    .notification-actions {
        padding: 0 15px 15px 15px;
        display: flex;
        gap: 10px;
        justify-content: flex-end;
    }

    .notification-action {
        padding: 6px 12px;
        border: none;
        border-radius: 6px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .notification-action.primary {
        background: #3498db;
        color: white;
    }

    .notification-action.secondary {
        background: #95a5a6;
        color: white;
    }

    .notification-progress {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: rgba(0,0,0,0.1);
    }

    .notification-progress-bar {
        height: 100%;
        background: #3498db;
        width: 100%;
        transition: width linear;
    }

    /* Tooltip System Styles */
    .tooltip-enhanced {
        position: absolute;
        z-index: 10000;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        line-height: 1.4;
        max-width: 300px;
        word-wrap: break-word;
        opacity: 0;
        transform: scale(0.8);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        pointer-events: none;
    }

    .tooltip-enhanced.tooltip-visible {
        opacity: 1;
        transform: scale(1);
    }

    .tooltip-enhanced.tooltip-dark {
        background: #2c3e50;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .tooltip-enhanced.tooltip-light {
        background: white;
        color: #2c3e50;
        border: 1px solid #e1e5e9;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .tooltip-content {
        position: relative;
        z-index: 1;
    }

    .tooltip-arrow {
        position: absolute;
        width: 0;
        height: 0;
        border: 6px solid transparent;
    }

    .tooltip-pos-top .tooltip-arrow {
        bottom: -12px;
        border-top-color: #2c3e50;
        border-bottom: none;
    }

    .tooltip-pos-bottom .tooltip-arrow {
        top: -12px;
        border-bottom-color: #2c3e50;
        border-top: none;
    }

    .tooltip-pos-left .tooltip-arrow {
        right: -12px;
        border-left-color: #2c3e50;
        border-right: none;
    }

    .tooltip-pos-right .tooltip-arrow {
        left: -12px;
        border-right-color: #2c3e50;
        border-left: none;
    }

    .tooltip-light .tooltip-arrow {
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }

    .tooltip-light.tooltip-pos-top .tooltip-arrow {
        border-top-color: white;
    }

    .tooltip-light.tooltip-pos-bottom .tooltip-arrow {
        border-bottom-color: white;
    }

    .tooltip-light.tooltip-pos-left .tooltip-arrow {
        border-left-color: white;
    }

    .tooltip-light.tooltip-pos-right .tooltip-arrow {
        border-right-color: white;
    }

    /* Animation variants */
    .tooltip-enhanced.tooltip-fade {
        transition: opacity 0.2s ease, transform 0.2s ease;
    }

    .tooltip-enhanced.tooltip-slide {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .tooltip-enhanced.tooltip-bounce {
        transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .notification-container {
            right: 10px !important;
            left: 10px !important;
            max-width: none;
        }
        
        .notification {
            transform: translateX(calc(100vw + 20px));
        }
        
        .notification.notification-show {
            transform: translateX(0);
        }
        
        .notification.notification-closing {
            transform: translateX(calc(100vw + 20px));
        }
        
        .tooltip-enhanced {
            max-width: 250px;
            font-size: 0.8rem;
        }
    }

    /* Other animation keyframes */
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);