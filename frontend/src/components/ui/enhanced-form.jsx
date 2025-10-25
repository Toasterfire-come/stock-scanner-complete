import React from 'react';
import { cn } from '../../lib/utils';

const EnhancedFormGroup = React.forwardRef(({
  className,
  children,
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn('form-group-enhanced', className)}
      {...props}
    >
      {children}
    </div>
  );
});

const EnhancedFormLabel = React.forwardRef(({
  className,
  children,
  required,
  ...props
}, ref) => {
  return (
    <label
      ref={ref}
      className={cn('form-label-enhanced', className)}
      {...props}
    >
      {children}
      {required && (
        <span className="text-red-500 ml-1" aria-label="required">
          *
        </span>
      )}
    </label>
  );
});

const EnhancedFormControl = React.forwardRef(({
  className,
  type = 'text',
  error,
  success,
  icon,
  ...props
}, ref) => {
  const inputClass = cn(
    'form-control-enhanced',
    'focus-enhanced',
    error && 'border-red-500 focus:border-red-500 focus:shadow-glow-error',
    success && 'border-green-500 focus:border-green-500 focus:shadow-glow-success',
    icon && 'pl-12',
    className
  );

  if (icon) {
    return (
      <div className="input-icon-enhanced">
        <input
          ref={ref}
          type={type}
          className={inputClass}
          {...props}
        />
        <span className="icon icon-enhanced icon-md">
          {icon}
        </span>
      </div>
    );
  }

  return (
    <input
      ref={ref}
      type={type}
      className={inputClass}
      {...props}
    />
  );
});

const EnhancedFormTextarea = React.forwardRef(({
  className,
  error,
  success,
  rows = 4,
  ...props
}, ref) => {
  const textareaClass = cn(
    'form-control-enhanced',
    'focus-enhanced',
    'resize-vertical',
    error && 'border-red-500 focus:border-red-500 focus:shadow-glow-error',
    success && 'border-green-500 focus:border-green-500 focus:shadow-glow-success',
    className
  );

  return (
    <textarea
      ref={ref}
      rows={rows}
      className={textareaClass}
      {...props}
    />
  );
});

const EnhancedFormSelect = React.forwardRef(({
  className,
  error,
  success,
  children,
  ...props
}, ref) => {
  const selectClass = cn(
    'form-control-enhanced',
    'focus-enhanced',
    'cursor-pointer',
    error && 'border-red-500 focus:border-red-500 focus:shadow-glow-error',
    success && 'border-green-500 focus:border-green-500 focus:shadow-glow-success',
    className
  );

  return (
    <select
      ref={ref}
      className={selectClass}
      {...props}
    >
      {children}
    </select>
  );
});

const EnhancedFormFloating = React.forwardRef(({
  className,
  label,
  id,
  children,
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn('form-floating-enhanced', className)}
      {...props}
    >
      {children}
      <EnhancedFormLabel htmlFor={id}>
        {label}
      </EnhancedFormLabel>
    </div>
  );
});

const EnhancedFormError = React.forwardRef(({
  className,
  children,
  ...props
}, ref) => {
  if (!children) return null;

  return (
    <div
      ref={ref}
      className={cn(
        'mt-2 text-sm text-red-600 flex items-center gap-2',
        className
      )}
      role="alert"
      {...props}
    >
      <svg
        className="w-4 h-4 flex-shrink-0"
        fill="currentColor"
        viewBox="0 0 20 20"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          fillRule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
          clipRule="evenodd"
        />
      </svg>
      {children}
    </div>
  );
});

const EnhancedFormSuccess = React.forwardRef(({
  className,
  children,
  ...props
}, ref) => {
  if (!children) return null;

  return (
    <div
      ref={ref}
      className={cn(
        'mt-2 text-sm text-green-600 flex items-center gap-2',
        className
      )}
      {...props}
    >
      <svg
        className="w-4 h-4 flex-shrink-0"
        fill="currentColor"
        viewBox="0 0 20 20"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
          clipRule="evenodd"
        />
      </svg>
      {children}
    </div>
  );
});

const EnhancedFormHelp = React.forwardRef(({
  className,
  children,
  ...props
}, ref) => {
  if (!children) return null;

  return (
    <div
      ref={ref}
      className={cn(
        'mt-2 text-sm text-gray-500',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
});

EnhancedFormGroup.displayName = 'EnhancedFormGroup';
EnhancedFormLabel.displayName = 'EnhancedFormLabel';
EnhancedFormControl.displayName = 'EnhancedFormControl';
EnhancedFormTextarea.displayName = 'EnhancedFormTextarea';
EnhancedFormSelect.displayName = 'EnhancedFormSelect';
EnhancedFormFloating.displayName = 'EnhancedFormFloating';
EnhancedFormError.displayName = 'EnhancedFormError';
EnhancedFormSuccess.displayName = 'EnhancedFormSuccess';
EnhancedFormHelp.displayName = 'EnhancedFormHelp';

export {
  EnhancedFormGroup,
  EnhancedFormLabel,
  EnhancedFormControl,
  EnhancedFormTextarea,
  EnhancedFormSelect,
  EnhancedFormFloating,
  EnhancedFormError,
  EnhancedFormSuccess,
  EnhancedFormHelp
};