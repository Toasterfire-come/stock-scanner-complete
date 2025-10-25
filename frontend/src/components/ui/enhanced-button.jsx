import React from 'react';
import { cn } from '../../lib/utils';

const EnhancedButton = React.forwardRef(({
  className,
  variant = 'primary',
  size = 'md',
  children,
  disabled,
  loading,
  icon,
  ...props
}, ref) => {
  const variants = {
    primary: 'btn-primary-enhanced',
    secondary: 'btn-secondary-enhanced',
    outline: 'btn-outline-enhanced',
    ghost: 'btn-ghost-enhanced',
    destructive: 'btn-destructive-enhanced'
  };

  const sizes = {
    sm: 'btn-sm',
    md: '',
    lg: 'btn-lg',
    xl: 'btn-xl'
  };

  const buttonClass = cn(
    'btn-enhanced',
    variants[variant],
    sizes[size],
    'focus-enhanced',
    disabled && 'opacity-60 cursor-not-allowed',
    loading && 'cursor-wait',
    className
  );

  return (
    <button
      ref={ref}
      className={buttonClass}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent" />
      )}
      {icon && !loading && (
        <span className="icon-enhanced icon-sm">
          {icon}
        </span>
      )}
      {children}
    </button>
  );
});

EnhancedButton.displayName = 'EnhancedButton';

export default EnhancedButton;