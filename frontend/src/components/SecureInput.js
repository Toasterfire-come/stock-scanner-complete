import React, { useState, useCallback, forwardRef } from 'react';
import { validateInput, validateEmail } from '../lib/security';
import { cn } from '../lib/utils';

const SecureInput = forwardRef(({
  type = 'text',
  placeholder = '',
  className = '',
  maxLength,
  validationType = 'general',
  validateOnChange = true,
  showValidation = true,
  onValidationChange,
  sanitize = true,
  ...props
}, ref) => {
  const [value, setValue] = useState(props.value || '');
  const [validationError, setValidationError] = useState('');
  const [isValid, setIsValid] = useState(true);

  const validate = useCallback((inputValue) => {
    let error = '';
    let valid = true;

    // Length validation
    if (maxLength && inputValue.length > maxLength) {
      error = `Maximum length is ${maxLength} characters`;
      valid = false;
    }

    // Type-specific validation
    switch (validationType) {
      case 'email':
        if (inputValue && !validateEmail(inputValue)) {
          error = 'Please enter a valid email address';
          valid = false;
        }
        break;
      case 'password':
        if (inputValue && inputValue.length < 8) {
          error = 'Password must be at least 8 characters';
          valid = false;
        }
        break;
      case 'username':
        if (inputValue && (inputValue.length < 3 || !/^[a-zA-Z0-9_-]+$/.test(inputValue))) {
          error = 'Username must be at least 3 characters and contain only letters, numbers, hyphens, and underscores';
          valid = false;
        }
        break;
      case 'search':
        if (inputValue && inputValue.length > 100) {
          error = 'Search query too long';
          valid = false;
        }
        break;
      default:
        break;
    }

    setValidationError(error);
    setIsValid(valid);
    
    if (onValidationChange) {
      onValidationChange(valid, error);
    }

    return { valid, error };
  }, [maxLength, validationType, onValidationChange]);

  const handleChange = useCallback((e) => {
    let inputValue = e.target.value;

    // Sanitize input if enabled
    if (sanitize) {
      inputValue = validateInput(inputValue, validationType);
    }

    setValue(inputValue);

    // Validate on change if enabled
    if (validateOnChange) {
      validate(inputValue);
    }

    // Call parent onChange
    if (props.onChange) {
      props.onChange({ ...e, target: { ...e.target, value: inputValue } });
    }
  }, [sanitize, validationType, validateOnChange, validate, props.onChange]);

  const handleBlur = useCallback((e) => {
    // Always validate on blur
    validate(e.target.value);
    
    if (props.onBlur) {
      props.onBlur(e);
    }
  }, [validate, props.onBlur]);

  return (
    <div className="w-full">
      <input
        {...props}
        ref={ref}
        type={type}
        value={value}
        onChange={handleChange}
        onBlur={handleBlur}
        placeholder={placeholder}
        maxLength={maxLength}
        className={cn(
          'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
          !isValid && showValidation && 'border-red-500 focus-visible:ring-red-500',
          className
        )}
        autoComplete={
          type === 'password' ? 'current-password' :
          type === 'email' ? 'email' :
          validationType === 'username' ? 'username' :
          'off'
        }
        spellCheck={validationType === 'search' || validationType === 'general'}
      />
      {showValidation && validationError && (
        <p className="mt-1 text-sm text-red-600" role="alert">
          {validationError}
        </p>
      )}
    </div>
  );
});

SecureInput.displayName = 'SecureInput';

export default SecureInput;