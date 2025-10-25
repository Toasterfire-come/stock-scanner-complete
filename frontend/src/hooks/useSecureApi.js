import { useState, useEffect, useCallback, useRef } from 'react';
import { apiRateLimiter, requestQueue, sanitizeError } from '../lib/security';

// Custom hook for secure API calls with built-in security features
export const useSecureApi = (apiFunction, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [rateLimited, setRateLimited] = useState(false);
  
  const abortControllerRef = useRef(null);
  
  const {
    initialLoad = false,
    onSuccess,
    onError,
    retryAttempts = 3,
    retryDelay = 1000,
    dependencies = []
  } = options;

  const execute = useCallback(async (...args) => {
    // Check rate limiting
    if (!apiRateLimiter.canMakeRequest()) {
      setRateLimited(true);
      const resetTime = apiRateLimiter.getResetTime();
      const waitTime = Math.max(0, resetTime - Date.now());
      const error = new Error(`Rate limit exceeded. Try again in ${Math.ceil(waitTime / 1000)} seconds.`);
      setError(sanitizeError(error));
      if (onError) onError(error);
      return { success: false, error };
    }

    setRateLimited(false);
    setLoading(true);
    setError(null);

    // Cancel previous request if it exists
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    let attempts = 0;
    let lastError = null;

    while (attempts < retryAttempts) {
      try {
        // Add abort signal to request if apiFunction supports it
        const result = await requestQueue.add(() => 
          apiFunction(...args, { signal: abortControllerRef.current.signal })
        );
        
        setData(result);
        setLoading(false);
        
        if (onSuccess) {
          onSuccess(result);
        }
        
        return { success: true, data: result };
      } catch (err) {
        lastError = err;
        attempts++;

        // Don't retry on abort or authentication errors
        if (err.name === 'AbortError' || err.response?.status === 401) {
          break;
        }

        // Don't retry on client errors (4xx except 429)
        if (err.response?.status >= 400 && err.response?.status < 500 && err.response?.status !== 429) {
          break;
        }

        // Wait before retry (exponential backoff)
        if (attempts < retryAttempts) {
          await new Promise(resolve => setTimeout(resolve, retryDelay * Math.pow(2, attempts - 1)));
        }
      }
    }

    // All attempts failed
    const sanitizedError = sanitizeError(lastError);
    setError(sanitizedError);
    setLoading(false);
    
    if (onError) {
      onError(sanitizedError);
    }
    
    return { success: false, error: sanitizedError };
  }, [apiFunction, onSuccess, onError, retryAttempts, retryDelay]);

  // Execute on mount if initialLoad is true
  useEffect(() => {
    if (initialLoad) {
      execute();
    }
    
    // Cleanup on unmount
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [initialLoad, execute, ...dependencies]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
    setRateLimited(false);
    
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setLoading(false);
  }, []);

  return {
    data,
    loading,
    error,
    rateLimited,
    execute,
    reset,
    cancel,
    remainingCalls: apiRateLimiter.getRemainingCalls(),
    resetTime: apiRateLimiter.getResetTime()
  };
};

// Hook for secure form handling
export const useSecureForm = (initialValues = {}, validationRules = {}) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = useCallback((fieldName, value) => {
    const rule = validationRules[fieldName];
    if (!rule) return '';

    if (rule.required && (!value || (typeof value === 'string' && !value.trim()))) {
      return rule.requiredMessage || `${fieldName} is required`;
    }

    if (rule.validate && typeof rule.validate === 'function') {
      const validationResult = rule.validate(value);
      if (validationResult !== true) {
        return typeof validationResult === 'string' ? validationResult : `${fieldName} is invalid`;
      }
    }

    return '';
  }, [validationRules]);

  const setValue = useCallback((fieldName, value) => {
    setValues(prev => ({ ...prev, [fieldName]: value }));
    
    // Validate field if it's been touched
    if (touched[fieldName]) {
      const error = validate(fieldName, value);
      setErrors(prev => ({ ...prev, [fieldName]: error }));
    }
  }, [validate, touched]);

  const setTouched = useCallback((fieldName, isTouched = true) => {
    setTouched(prev => ({ ...prev, [fieldName]: isTouched }));
    
    if (isTouched) {
      const error = validate(fieldName, values[fieldName]);
      setErrors(prev => ({ ...prev, [fieldName]: error }));
    }
  }, [validate, values]);

  const validateAll = useCallback(() => {
    const newErrors = {};
    let isValid = true;

    Object.keys(validationRules).forEach(fieldName => {
      const error = validate(fieldName, values[fieldName]);
      if (error) {
        newErrors[fieldName] = error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  }, [validate, values, validationRules]);

  const handleSubmit = useCallback(async (onSubmit) => {
    setIsSubmitting(true);
    
    // Mark all fields as touched
    const touchedFields = {};
    Object.keys(validationRules).forEach(fieldName => {
      touchedFields[fieldName] = true;
    });
    setTouched(touchedFields);

    // Validate all fields
    if (!validateAll()) {
      setIsSubmitting(false);
      return { success: false, error: 'Please fix validation errors' };
    }

    try {
      const result = await onSubmit(values);
      setIsSubmitting(false);
      return result;
    } catch (error) {
      setIsSubmitting(false);
      const sanitizedError = sanitizeError(error);
      return { success: false, error: sanitizedError };
    }
  }, [values, validateAll, validationRules]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);

  return {
    values,
    errors,
    touched,
    isSubmitting,
    setValue,
    setTouched,
    validateAll,
    handleSubmit,
    reset,
    isValid: Object.keys(errors).length === 0 && Object.keys(touched).length > 0
  };
};

export default useSecureApi;