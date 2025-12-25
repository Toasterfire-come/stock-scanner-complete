// app/frontend/src/pages/education/InfoTooltip.jsx
/**
 * Info Tooltip Component
 * Phase 7 Implementation - TradeScanPro
 * Hover-triggered glossary tooltips
 */

import React, { useState, useRef, useEffect } from 'react';
import { api } from '../../api/client';
import logger from '../../lib/logger';

const InfoTooltip = ({ term, children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [termData, setTermData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const tooltipRef = useRef(null);
  const triggerRef = useRef(null);

  useEffect(() => {
    if (isOpen && !termData && !loading) {
      fetchTermData();
    }
  }, [isOpen]);

  useEffect(() => {
    if (isOpen && tooltipRef.current && triggerRef.current) {
      calculatePosition();
    }
  }, [isOpen, termData]);

  const fetchTermData = async () => {
    setLoading(true);
    try {
      // If term is an object (already fetched), use it directly
      if (typeof term === 'object' && term.slug) {
        setTermData(term);
        
        // Track tooltip hover
        await api.post(`/api/education/glossary/${term.slug}/track-tooltip/`);
      } else {
        // If term is a string, fetch it
        const slug = term.toLowerCase().replace(/\s+/g, '-');
        const response = await api.get(`/api/education/glossary/${slug}/`);
        setTermData(response.data);
        
        // Track tooltip hover
        await api.post(`/api/education/glossary/${slug}/track-tooltip/`);
      }
    } catch (error) {
      logger.error('Error fetching term:', error);
      // Set a default error state
      setTermData({
        term: typeof term === 'string' ? term : term.term,
        definition: 'Definition not found.',
        example: ''
      });
    } finally {
      setLoading(false);
    }
  };

  const calculatePosition = () => {
    if (!tooltipRef.current || !triggerRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let top = triggerRect.bottom + 8; // Default: below trigger
    let left = triggerRect.left;

    // Check if tooltip goes off right edge
    if (left + tooltipRect.width > viewportWidth - 16) {
      left = viewportWidth - tooltipRect.width - 16;
    }

    // Check if tooltip goes off left edge
    if (left < 16) {
      left = 16;
    }

    // Check if tooltip goes off bottom edge
    if (top + tooltipRect.height > viewportHeight - 16) {
      top = triggerRect.top - tooltipRect.height - 8; // Position above trigger
    }

    setPosition({ top, left });
  };

  const handleMouseEnter = () => {
    setIsOpen(true);
  };

  const handleMouseLeave = () => {
    setIsOpen(false);
  };

  return (
    <>
      <span
        ref={triggerRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className="inline-block"
      >
        {children}
      </span>

      {isOpen && (
        <div
          ref={tooltipRef}
          style={{
            position: 'fixed',
            top: `${position.top}px`,
            left: `${position.left}px`,
          }}
          className="z-50 w-80 bg-[#1E222D] border border-[#3A3E49] rounded-lg shadow-2xl
                   animate-fadeIn"
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          {loading ? (
            <div className="p-4">
              <div className="animate-pulse">
                <div className="h-4 bg-[#2A2E39] rounded w-1/2 mb-3"></div>
                <div className="h-3 bg-[#2A2E39] rounded w-full mb-2"></div>
                <div className="h-3 bg-[#2A2E39] rounded w-3/4"></div>
              </div>
            </div>
          ) : termData ? (
            <div className="p-4">
              {/* Term Header */}
              <div className="flex items-start justify-between mb-3">
                <h4 className="text-lg font-semibold text-[#D1D4DC]">
                  {termData.term}
                </h4>
                {termData.category && (
                  <span className="px-2 py-1 bg-[#2962FF]/20 text-[#2962FF] text-xs rounded">
                    {termData.category.replace('_', ' ')}
                  </span>
                )}
              </div>

              {/* Definition */}
              <p className="text-sm text-[#D1D4DC] mb-3 leading-relaxed">
                {termData.definition}
              </p>

              {/* Example */}
              {termData.example && (
                <div className="mt-3 pt-3 border-t border-[#2A2E39]">
                  <p className="text-xs text-[#787B86] mb-1 font-semibold uppercase">
                    Example
                  </p>
                  <p className="text-sm text-[#D1D4DC] italic">
                    {termData.example}
                  </p>
                </div>
              )}

              {/* Related Terms */}
              {termData.related_term_names && termData.related_term_names.length > 0 && (
                <div className="mt-3 pt-3 border-t border-[#2A2E39]">
                  <p className="text-xs text-[#787B86] mb-2 font-semibold uppercase">
                    Related Terms
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {termData.related_term_names.map((relatedTerm, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-[#2A2E39] text-[#D1D4DC] text-xs rounded
                                 hover:bg-[#3A3E49] cursor-pointer"
                      >
                        {relatedTerm}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Difficulty Badge */}
              {termData.difficulty && (
                <div className="mt-3 pt-3 border-t border-[#2A2E39] flex justify-between items-center">
                  <span className="text-xs text-[#787B86]">
                    Difficulty: {termData.difficulty}
                  </span>
                  <a
                    href={`/glossary/${termData.slug}`}
                    className="text-xs text-[#2962FF] hover:underline"
                    onClick={(e) => e.stopPropagation()}
                  >
                    Learn more →
                  </a>
                </div>
              )}
            </div>
          ) : null}
        </div>
      )}
    </>
  );
};

export default InfoTooltip;

/* CSS Animation (add to your global CSS or Tailwind config) */
/*
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.15s ease-out;
}
*/
