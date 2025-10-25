export function mapCriteriaToFilterParams(criteria = []) {
  const params = {};
  for (const c of criteria) {
    if (c.id === 'market_cap') { if (c.min) params.market_cap_min = c.min; if (c.max) params.market_cap_max = c.max; }
    if (c.id === 'price') { if (c.min) params.min_price = c.min; if (c.max) params.max_price = c.max; }
    if (c.id === 'volume') { if (c.min) params.min_volume = c.min; if (c.max) params.max_volume = c.max; }
    if (c.id === 'pe_ratio') { if (c.min) params.pe_ratio_min = c.min; if (c.max) params.pe_ratio_max = c.max; }
    if (c.id === 'dividend_yield') { if (c.min) params.dividend_yield_min = c.min; if (c.max) params.dividend_yield_max = c.max; }
    if (c.id === 'change_percent') { if (c.min) params.change_percent_min = c.min; if (c.max) params.change_percent_max = c.max; }
    if (c.id === 'exchange') { if (c.value) params.exchange = c.value; }
  }
  return params;
}

