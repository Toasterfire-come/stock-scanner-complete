import React from 'react';
import { cn } from '../../lib/utils';

const EnhancedCard = React.forwardRef(({
  className,
  interactive = false,
  children,
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn(
        'card-enhanced',
        interactive && 'card-interactive',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
});

const EnhancedCardHeader = React.forwardRef(({
  className,
  children,
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn('card-header-enhanced', className)}
      {...props}
    >
      {children}
    </div>
  );
});

const EnhancedCardContent = React.forwardRef(({
  className,
  children,
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn('card-body-enhanced', className)}
      {...props}
    >
      {children}
    </div>
  );
});

const EnhancedCardFooter = React.forwardRef(({
  className,
  children,
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn('card-footer-enhanced', className)}
      {...props}
    >
      {children}
    </div>
  );
});

EnhancedCard.displayName = 'EnhancedCard';
EnhancedCardHeader.displayName = 'EnhancedCardHeader';
EnhancedCardContent.displayName = 'EnhancedCardContent';
EnhancedCardFooter.displayName = 'EnhancedCardFooter';

export {
  EnhancedCard,
  EnhancedCardHeader,
  EnhancedCardContent,
  EnhancedCardFooter
};