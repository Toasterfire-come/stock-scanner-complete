import React from 'react';

/**
 * SkipToContent - Accessibility component for keyboard navigation
 * Allows screen reader and keyboard users to skip repetitive navigation
 * WCAG 2.1 AA Requirement: 2.4.1 Bypass Blocks
 */
const SkipToContent = () => {
  const handleSkip = (e) => {
    e.preventDefault();
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
      mainContent.focus();
      mainContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <a
      href="#main-content"
      onClick={handleSkip}
      className="skip-to-content"
      style={{
        position: 'absolute',
        left: '-9999px',
        zIndex: 999999,
        padding: '1em',
        backgroundColor: '#000',
        color: '#fff',
        textDecoration: 'none',
        fontWeight: 'bold',
        border: '2px solid #fff',
        borderRadius: '4px',
        transition: 'left 0.2s ease-in-out'
      }}
      onFocus={(e) => {
        e.target.style.left = '10px';
        e.target.style.top = '10px';
      }}
      onBlur={(e) => {
        e.target.style.left = '-9999px';
      }}
      aria-label="Skip to main content"
    >
      Skip to main content
    </a>
  );
};

export default SkipToContent;
