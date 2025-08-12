(function(){
  // Wait for Chart.js to be fully loaded
  function initChartTheme() {
    if (!window.Chart || !Chart.defaults) {
      setTimeout(initChartTheme, 100);
      return;
    }
  
  const palette = {
    text: getComputedStyle(document.documentElement).getPropertyValue('--brand-charcoal')?.trim() || '#2C2C2C',
    grid: '#E5E7EB',
    blue: getComputedStyle(document.documentElement).getPropertyValue('--brand-blue')?.trim() || '#1F4E79',
    emerald: getComputedStyle(document.documentElement).getPropertyValue('--brand-emerald')?.trim() || '#21A179',
    red: getComputedStyle(document.documentElement).getPropertyValue('--brand-red')?.trim() || '#D64545',
    gold: getComputedStyle(document.documentElement).getPropertyValue('--brand-gold')?.trim() || '#E3B341'
  };
  
  // Set global defaults
  try {
    if (Chart.defaults) {
      // Initialize font object if it doesn't exist
      Chart.defaults.font = Chart.defaults.font || {};
      if (Chart.defaults.font) {
        Chart.defaults.font.family = getComputedStyle(document.body).fontFamily || 'system-ui, sans-serif';
      }
      
      // Set global text color
      if (Chart.defaults.color !== undefined) {
        Chart.defaults.color = palette.text;
      }
      
      // Plugin defaults with proper null checks
      if (Chart.defaults.plugins) {
        if (Chart.defaults.plugins.legend) {
          Chart.defaults.plugins.legend.labels = Chart.defaults.plugins.legend.labels || {};
          Chart.defaults.plugins.legend.labels.boxWidth = 12;
          Chart.defaults.plugins.legend.labels.color = palette.text;
        }
        
        if (Chart.defaults.plugins.tooltip) {
          Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(11,27,51,0.9)';
          Chart.defaults.plugins.tooltip.titleColor = '#fff';
          Chart.defaults.plugins.tooltip.bodyColor = '#fff';
        }
      }
    }
  } catch (error) {
    console.warn('Chart.js theme configuration failed:', error);
  }
  }
  
  // Start the initialization
  initChartTheme();
})();