/**
 * Accessibility Helper Components
 * ================================
 * QA Fix: Issue #5 - Poor Accessibility Compliance
 *
 * Provides accessible UI components and utilities
 * WCAG 2.1 AA Compliant
 */

import React from 'react';

/**
 * VisuallyHidden - Hide content visually but keep it for screen readers
 */
export const VisuallyHidden = ({ children, as: Component = 'span' }) => {
  return (
    <Component className="sr-only">
      {children}
    </Component>
  );
};

/**
 * SkipToContent - Skip navigation link for keyboard users
 */
export const SkipToContent = ({ targetId = 'main-content' }) => {
  return (
    <a
      href={`#${targetId}`}
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-blue-600 focus:text-white focus:px-4 focus:py-2 focus:rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
      data-testid="skip-to-content-link"
    >
      Skip to main content
    </a>
  );
};

/**
 * FocusableImage - Image with proper alt text and focus handling
 */
export const FocusableImage = ({
  src,
  alt,
  decorative = false,
  className = '',
  ...props
}) => {
  return (
    <img
      src={src}
      alt={decorative ? '' : alt}
      role={decorative ? 'presentation' : undefined}
      className={className}
      {...props}
    />
  );
};

/**
 * IconButton - Accessible button with icon
 */
export const IconButton = ({
  icon: Icon,
  label,
  onClick,
  className = '',
  variant = 'default',
  disabled = false,
  ...props
}) => {
  const variants = {
    default: 'hover:bg-gray-100',
    primary: 'hover:bg-blue-100 text-blue-600',
    danger: 'hover:bg-red-100 text-red-600'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`p-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400 ${variants[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
      aria-label={label}
      title={label}
      type="button"
      {...props}
    >
      <Icon className="h-5 w-5" aria-hidden="true" />
      <VisuallyHidden>{label}</VisuallyHidden>
    </button>
  );
};

/**
 * FormField - Accessible form input wrapper
 */
export const FormField = ({
  id,
  label,
  error,
  required = false,
  helpText,
  children
}) => {
  const errorId = error ? `${id}-error` : undefined;
  const helpTextId = helpText ? `${id}-help` : undefined;
  const describedBy = [errorId, helpTextId].filter(Boolean).join(' ');

  return (
    <div className="space-y-2">
      <label
        htmlFor={id}
        className="block text-sm font-medium text-gray-700"
      >
        {label}
        {required && (
          <span className="text-red-500 ml-1" aria-label="required">
            *
          </span>
        )}
      </label>

      {React.cloneElement(children, {
        id,
        'aria-invalid': error ? 'true' : 'false',
        'aria-describedby': describedBy || undefined,
        'aria-required': required
      })}

      {helpText && (
        <p id={helpTextId} className="text-sm text-gray-600">
          {helpText}
        </p>
      )}

      {error && (
        <p
          id={errorId}
          className="text-sm text-red-600"
          role="alert"
          aria-live="polite"
        >
          {error}
        </p>
      )}
    </div>
  );
};

/**
 * LiveRegion - Announce dynamic content to screen readers
 */
export const LiveRegion = ({
  children,
  politeness = 'polite',
  atomic = true,
  className = ''
}) => {
  return (
    <div
      role="status"
      aria-live={politeness}
      aria-atomic={atomic}
      className={className}
    >
      {children}
    </div>
  );
};

/**
 * Alert - Accessible alert/notification component
 */
export const Alert = ({
  type = 'info',
  title,
  message,
  onClose,
  className = ''
}) => {
  const types = {
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-800',
      icon: '🔵'
    },
    success: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-800',
      icon: '✅'
    },
    warning: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      text: 'text-yellow-800',
      icon: '⚠️'
    },
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-800',
      icon: '❌'
    }
  };

  const config = types[type];

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`${config.bg} ${config.border} ${config.text} border rounded-lg p-4 ${className}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <span aria-hidden="true">{config.icon}</span>
          <div>
            {title && (
              <h4 className="font-semibold mb-1">{title}</h4>
            )}
            <p className="text-sm">{message}</p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-current hover:opacity-70 focus:outline-none focus:ring-2 focus:ring-current rounded p-1"
            aria-label="Close alert"
          >
            <span aria-hidden="true">×</span>
          </button>
        )}
      </div>
    </div>
  );
};

/**
 * ProgressiveDisclosure - Expandable section (accordion)
 */
export const ProgressiveDisclosure = ({
  title,
  children,
  defaultExpanded = false,
  id
}) => {
  const [isExpanded, setIsExpanded] = React.useState(defaultExpanded);
  const contentId = `${id}-content`;
  const buttonId = `${id}-button`;

  return (
    <div className="border rounded-lg">
      <button
        id={buttonId}
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-400 rounded-lg"
        aria-expanded={isExpanded}
        aria-controls={contentId}
      >
        <span className="font-medium">{title}</span>
        <span
          aria-hidden="true"
          className={`transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}
        >
          ▼
        </span>
      </button>
      {isExpanded && (
        <div
          id={contentId}
          role="region"
          aria-labelledby={buttonId}
          className="p-4 border-t"
        >
          {children}
        </div>
      )}
    </div>
  );
};

/**
 * KeyboardNavigable - Wrapper for keyboard navigation
 */
export const KeyboardNavigable = ({ children, onEscape }) => {
  React.useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && onEscape) {
        onEscape();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onEscape]);

  return children;
};

/**
 * FocusTrap - Trap focus within a component (for modals)
 */
export const FocusTrap = ({ children, active = true }) => {
  const ref = React.useRef(null);

  React.useEffect(() => {
    if (!active || !ref.current) return;

    const focusableElements = ref.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTabKey = (e) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement?.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement?.focus();
          e.preventDefault();
        }
      }
    };

    // Focus first element
    firstElement?.focus();

    document.addEventListener('keydown', handleTabKey);
    return () => document.removeEventListener('keydown', handleTabKey);
  }, [active]);

  return <div ref={ref}>{children}</div>;
};

/**
 * Tooltip - Accessible tooltip component
 */
export const Tooltip = ({ content, children }) => {
  const [isVisible, setIsVisible] = React.useState(false);
  const tooltipId = React.useId();

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onFocus={() => setIsVisible(true)}
        onBlur={() => setIsVisible(false)}
        aria-describedby={isVisible ? tooltipId : undefined}
      >
        {children}
      </div>
      {isVisible && (
        <div
          id={tooltipId}
          role="tooltip"
          className="absolute z-10 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg -top-10 left-1/2 transform -translate-x-1/2 whitespace-nowrap"
        >
          {content}
          <div className="absolute w-2 h-2 bg-gray-900 transform rotate-45 -bottom-1 left-1/2 -translate-x-1/2" />
        </div>
      )}
    </div>
  );
};

// Export all components
export default {
  VisuallyHidden,
  SkipToContent,
  FocusableImage,
  IconButton,
  FormField,
  LiveRegion,
  Alert,
  ProgressiveDisclosure,
  KeyboardNavigable,
  FocusTrap,
  Tooltip
};
