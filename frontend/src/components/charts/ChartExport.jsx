import React from 'react';
import { toast } from 'sonner';
import logger from '../../lib/logger';

/**
 * Chart Export Utilities
 * Provides functions to export charts as PNG, SVG, or CSV
 */

/**
 * Export chart as PNG image
 * @param {HTMLElement} chartElement - The chart container element
 * @param {string} filename - The filename for the export
 * @param {Object} options - Export options (width, height, backgroundColor)
 */
export const exportChartAsPNG = async (chartElement, filename = 'chart.png', options = {}) => {
  try {
    // Create a canvas from the chart element
    const canvas = await createCanvasFromElement(chartElement, options);

    // Convert canvas to blob
    canvas.toBlob((blob) => {
      if (!blob) {
        throw new Error('Failed to create image blob');
      }

      // Create download link
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast.success('Chart exported as PNG');
    }, 'image/png');
  } catch (error) {
    logger.error('PNG export error:', error);
    toast.error('Failed to export chart as PNG');
  }
};

/**
 * Export chart as SVG
 * @param {HTMLElement} chartElement - The chart container element
 * @param {string} filename - The filename for the export
 */
export const exportChartAsSVG = async (chartElement, filename = 'chart.svg') => {
  try {
    // Find SVG element in chart
    const svgElement = chartElement.querySelector('svg');

    if (!svgElement) {
      throw new Error('No SVG element found in chart');
    }

    // Clone SVG to avoid modifying original
    const svgClone = svgElement.cloneNode(true);

    // Add XML namespace if not present
    svgClone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    svgClone.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');

    // Serialize SVG to string
    const serializer = new XMLSerializer();
    let svgString = serializer.serializeToString(svgClone);

    // Add CSS styles inline
    svgString = addInlineStyles(svgString, chartElement);

    // Create blob and download
    const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    toast.success('Chart exported as SVG');
  } catch (error) {
    logger.error('SVG export error:', error);
    toast.error('Failed to export chart as SVG');
  }
};

/**
 * Export chart data as CSV
 * @param {Array} data - The chart data array
 * @param {string} filename - The filename for the export
 * @param {Array} columns - Column definitions
 */
export const exportChartDataAsCSV = (data, filename = 'chart-data.csv', columns = []) => {
  try {
    if (!data || data.length === 0) {
      throw new Error('No data to export');
    }

    // Determine columns from data keys if not provided
    const csvColumns = columns.length > 0
      ? columns
      : Object.keys(data[0]);

    // Create CSV header
    const header = csvColumns.join(',');

    // Create CSV rows
    const rows = data.map(row => {
      return csvColumns.map(col => {
        const value = row[col];
        // Handle values that need quotes (contain commas, quotes, or newlines)
        if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value ?? '';
      }).join(',');
    });

    // Combine header and rows
    const csvContent = [header, ...rows].join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    toast.success('Data exported as CSV');
  } catch (error) {
    logger.error('CSV export error:', error);
    toast.error('Failed to export data as CSV');
  }
};

/**
 * Helper: Create canvas from HTML element
 * @private
 */
const createCanvasFromElement = async (element, options = {}) => {
  const {
    width = element.offsetWidth,
    height = element.offsetHeight,
    backgroundColor = '#ffffff',
    scale = 2 // For higher resolution
  } = options;

  const canvas = document.createElement('canvas');
  canvas.width = width * scale;
  canvas.height = height * scale;

  const ctx = canvas.getContext('2d');
  ctx.scale(scale, scale);

  // Fill background
  ctx.fillStyle = backgroundColor;
  ctx.fillRect(0, 0, width, height);

  // For SVG elements
  const svgElement = element.querySelector('svg');
  if (svgElement) {
    await drawSVGToCanvas(ctx, svgElement, width, height);
    return canvas;
  }

  // For canvas elements
  const canvasElement = element.querySelector('canvas');
  if (canvasElement) {
    ctx.drawImage(canvasElement, 0, 0, width, height);
    return canvas;
  }

  // Fallback: try to render as image
  try {
    const data = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
      <foreignObject width="100%" height="100%">
        <div xmlns="http://www.w3.org/1999/xhtml">${element.innerHTML}</div>
      </foreignObject>
    </svg>`;

    const img = new Image();
    img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(data);
    await new Promise((resolve, reject) => {
      img.onload = resolve;
      img.onerror = reject;
    });

    ctx.drawImage(img, 0, 0, width, height);
  } catch (err) {
    logger.warn('Fallback rendering failed:', err);
  }

  return canvas;
};

/**
 * Helper: Draw SVG to canvas
 * @private
 */
const drawSVGToCanvas = async (ctx, svgElement, width, height) => {
  const svgClone = svgElement.cloneNode(true);
  svgClone.setAttribute('width', width);
  svgClone.setAttribute('height', height);

  const serializer = new XMLSerializer();
  let svgString = serializer.serializeToString(svgClone);

  // Create image from SVG
  const img = new Image();
  const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(blob);

  img.src = url;

  return new Promise((resolve, reject) => {
    img.onload = () => {
      ctx.drawImage(img, 0, 0, width, height);
      URL.revokeObjectURL(url);
      resolve();
    };
    img.onerror = (err) => {
      URL.revokeObjectURL(url);
      reject(err);
    };
  });
};

/**
 * Helper: Add inline styles to SVG string
 * @private
 */
const addInlineStyles = (svgString, element) => {
  // Get computed styles from parent element
  const computedStyle = window.getComputedStyle(element);

  // Common style properties to inline
  const styleProps = [
    'font-family',
    'font-size',
    'font-weight',
    'color',
    'fill',
    'stroke',
    'stroke-width'
  ];

  // Create style string
  const styleString = styleProps
    .map(prop => `${prop}:${computedStyle.getPropertyValue(prop)}`)
    .join(';');

  // Insert styles into SVG
  return svgString.replace('<svg', `<svg style="${styleString}"`);
};

/**
 * React Hook for Chart Export
 */
export const useChartExport = (chartRef, chartData = []) => {
  const exportPNG = React.useCallback(async (filename) => {
    if (chartRef.current) {
      await exportChartAsPNG(chartRef.current, filename);
    }
  }, [chartRef]);

  const exportSVG = React.useCallback(async (filename) => {
    if (chartRef.current) {
      await exportChartAsSVG(chartRef.current, filename);
    }
  }, [chartRef]);

  const exportCSV = React.useCallback((filename, columns) => {
    exportChartDataAsCSV(chartData, filename, columns);
  }, [chartData]);

  const exportChart = React.useCallback(async (format, filename) => {
    switch (format) {
      case 'png':
        await exportPNG(filename || 'chart.png');
        break;
      case 'svg':
        await exportSVG(filename || 'chart.svg');
        break;
      case 'csv':
        exportCSV(filename || 'chart-data.csv');
        break;
      default:
        toast.error('Unsupported export format');
    }
  }, [exportPNG, exportSVG, exportCSV]);

  return {
    exportPNG,
    exportSVG,
    exportCSV,
    exportChart
  };
};

export default {
  exportChartAsPNG,
  exportChartAsSVG,
  exportChartDataAsCSV,
  useChartExport
};
