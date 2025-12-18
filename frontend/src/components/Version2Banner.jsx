import React, { useState } from 'react';

const Version2Banner = () => {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div className="version-2-banner" style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      padding: '12px 20px',
      textAlign: 'center',
      position: 'relative',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      zIndex: 1000
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '15px',
        flexWrap: 'wrap'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <span style={{
            background: 'rgba(255,255,255,0.2)',
            padding: '4px 12px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: 'bold',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            NEW
          </span>
          <span style={{
            fontSize: '16px',
            fontWeight: '600'
          }}>
            Version 2.0 Now Live!
          </span>
        </div>

        <span style={{
          fontSize: '14px',
          opacity: 0.95
        }}>
          AI-Powered Backtesting, Enhanced Analytics & More
        </span>

        <button
          onClick={() => setIsVisible(false)}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'white',
            cursor: 'pointer',
            fontSize: '20px',
            padding: '0 8px',
            opacity: 0.8,
            transition: 'opacity 0.2s',
            marginLeft: 'auto'
          }}
          onMouseEnter={(e) => e.target.style.opacity = '1'}
          onMouseLeave={(e) => e.target.style.opacity = '0.8'}
          aria-label="Close banner"
        >
          ×
        </button>
      </div>

      <style jsx>{`
        @media (max-width: 768px) {
          .version-2-banner {
            padding: 10px 15px !important;
            font-size: 14px !important;
          }
          .version-2-banner button {
            margin-left: 0 !important;
          }
        }
      `}</style>
    </div>
  );
};

export default Version2Banner;
