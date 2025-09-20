import { mapCriteriaToFilterParams } from "../api/client";

describe('mapCriteriaToFilterParams', () => {
  it('maps ranges and exchange correctly', () => {
    const criteria = [
      { id: 'market_cap', min: 1000000000, max: 50000000000 },
      { id: 'price', min: 5, max: 150 },
      { id: 'volume', min: 100000 },
      { id: 'pe_ratio', max: 20 },
      { id: 'dividend_yield', min: 2 },
      { id: 'change_percent', min: -5, max: 10 },
      { id: 'exchange', value: 'NYSE' }
    ];
    const params = mapCriteriaToFilterParams(criteria);
    expect(params).toMatchObject({
      market_cap_min: 1000000000,
      market_cap_max: 50000000000,
      min_price: 5,
      max_price: 150,
      min_volume: 100000,
      pe_ratio_max: 20,
      dividend_yield_min: 2,
      change_percent_min: -5,
      change_percent_max: 10,
      exchange: 'NYSE'
    });
  });
});

