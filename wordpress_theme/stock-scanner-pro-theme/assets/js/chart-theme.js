(function(){
  if (!window.Chart) return;
  const palette = {
    text: getComputedStyle(document.documentElement).getPropertyValue('--brand-charcoal')?.trim() || '#2C2C2C',
    grid: '#E5E7EB',
    blue: getComputedStyle(document.documentElement).getPropertyValue('--brand-blue')?.trim() || '#1F4E79',
    emerald: getComputedStyle(document.documentElement).getPropertyValue('--brand-emerald')?.trim() || '#21A179',
    red: getComputedStyle(document.documentElement).getPropertyValue('--brand-red')?.trim() || '#D64545',
    gold: getComputedStyle(document.documentElement).getPropertyValue('--brand-gold')?.trim() || '#E3B341'
  };
  Chart.defaults.font.family = getComputedStyle(document.body).fontFamily || 'system-ui, sans-serif';
  Chart.defaults.color = palette.text;
  Chart.defaults.plugins.legend.labels.boxWidth = 12;
  Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(11,27,51,0.9)';
  Chart.defaults.plugins.tooltip.titleColor = '#fff';
  Chart.defaults.plugins.tooltip.bodyColor = '#fff';
  Chart.defaults.scales.category.grid.color = palette.grid;
  Chart.defaults.scales.linear.grid.color = palette.grid;
})();