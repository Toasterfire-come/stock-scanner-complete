import React, { useId } from 'react';

/**
 * AccessibleFormField - Fully accessible form input component
 * Ensures proper labels, ARIA attributes, error messages, and keyboard navigation
 * WCAG 2.1 AA Requirements: 1.3.1, 3.3.1, 3.3.2, 4.1.3
 */
const AccessibleFormField = ({
  label,
  type = 'text',
  value,
  onChange,
  onBlur,
  error,
  helperText,
  required = false,
  disabled = false,
  placeholder,
  className = '',
  inputClassName = '',
  testId,
  autoComplete,
  ...props
}) => {
  const inputId = useId();
  const errorId = `${inputId}-error`;
  const helperId = `${inputId}-helper`;

  const hasError = Boolean(error);

  const baseInputClasses = 'w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 transition-colors duration-200';
  const errorClasses = hasError
    ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
    : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500';
  const disabledClasses = disabled ? 'bg-gray-100 cursor-not-allowed opacity-60' : 'bg-white';

  const combinedInputClasses = `${baseInputClasses} ${errorClasses} ${disabledClasses} ${inputClassName}`;

  return (
    <div className={`space-y-1 ${className}`}>
      <label
        htmlFor={inputId}
        className="block text-sm font-medium text-gray-700"
      >
        {label}
        {required && (
          <span className="text-red-500 ml-1" aria-label="required">
            *
          </span>
        )}
      </label>

      <input
        id={inputId}
        type={type}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        disabled={disabled}
        required={required}
        placeholder={placeholder}
        autoComplete={autoComplete}
        className={combinedInputClasses}
        aria-invalid={hasError}
        aria-describedby={
          hasError ? errorId : helperText ? helperId : undefined
        }
        aria-required={required}
        data-testid={testId}
        {...props}
      />

      {helperText && !hasError && (
        <p
          id={helperId}
          className="text-sm text-gray-500"
        >
          {helperText}
        </p>
      )}

      {hasError && (
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

export default AccessibleFormField;
