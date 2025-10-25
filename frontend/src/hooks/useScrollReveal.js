import { useEffect, useRef } from 'react';

const useScrollReveal = (options = {}) => {
  const elementRef = useRef();
  const observerRef = useRef();

  const defaultOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px',
    triggerOnce: true,
    ...options
  };

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    // Create intersection observer
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            
            // If triggerOnce is true, stop observing after first reveal
            if (defaultOptions.triggerOnce) {
              observerRef.current.unobserve(entry.target);
            }
          } else if (!defaultOptions.triggerOnce) {
            // Remove revealed class if element goes out of view and triggerOnce is false
            entry.target.classList.remove('revealed');
          }
        });
      },
      {
        threshold: defaultOptions.threshold,
        rootMargin: defaultOptions.rootMargin
      }
    );

    // Start observing
    observerRef.current.observe(element);

    // Cleanup function
    return () => {
      if (observerRef.current && element) {
        observerRef.current.unobserve(element);
      }
    };
  }, [defaultOptions.threshold, defaultOptions.rootMargin, defaultOptions.triggerOnce]);

  // Cleanup observer on unmount
  useEffect(() => {
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, []);

  return elementRef;
};

export default useScrollReveal;