(function(){
  if (!window.Chart || !Chart.defaults) return;
  
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
      Chart.defaults.font = Chart.defaults.font || {};
      if (Chart.defaults.font) {
        Chart.defaults.font.family = getComputedStyle(document.body).fontFamily || 'system-ui, sans-serif';
      }
      
      if (Chart.defaults.color !== undefined) {
        Chart.defaults.color = palette.text;
      }
      
      // Plugin defaults
      if (Chart.defaults.plugins) {
        if (Chart.defaults.plugins.legend && Chart.defaults.plugins.legend.labels) {
          Chart.defaults.plugins.legend.labels.boxWidth = 12;
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
})();