<?php /* Template Name: Screeners */ get_header(); ?>
<section class="section">
  <div class="container">
    <h1>Stock Scanner</h1>
    <div class="card" style="padding:16px;">
      <div class="grid" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;">
        <input id="s-q" class="input" placeholder="Search (ticker or company)" />
        <select id="s-category" class="input">
          <option value="all">Any Category</option>
          <option value="gainers">Gainers</option>
          <option value="losers">Losers</option>
          <option value="high_volume">High Volume</option>
          <option value="large_cap">Large Cap</option>
          <option value="small_cap">Small Cap</option>
        </select>
        <input id="s-exchange" class="input" placeholder="Exchange (or all)" />
        <input id="s-minp" class="input" placeholder="Min Price" type="number" />
        <input id="s-maxp" class="input" placeholder="Max Price" type="number" />
        <input id="s-minv" class="input" placeholder="Min Volume" type="number" />
        <button id="s-run" class="btn btn-primary">Run</button>
      </div>
    </div>
    <div class="card" style="padding:16px;margin-top:16px;">
      <table class="table" id="s-table"><thead><tr><th>Ticker</th><th>Company</th><th>Price</th><th>Change%</th><th>Volume</th><th>Market Cap</th></tr></thead><tbody><tr><td colspan="6" style="text-align:center;color:#6b7280;">No results</td></tr></tbody></table>
    </div>
  </div>
</section>
<script>
(function($){
  const Q = ()=> ({
    search: $('#s-q').val(),
    category: $('#s-category').val(),
    exchange: $('#s-exchange').val(),
    min_price: $('#s-minp').val(),
    max_price: $('#s-maxp').val(),
    min_volume: $('#s-minv').val(),
    sort_by: 'last_updated', sort_order: 'desc', limit: 50
  });
  function run(){
    const p = Q();
    if (p.min_price && p.max_price && Number(p.min_price) > Number(p.max_price)) { alert('Min price cannot exceed Max price'); return; }
    $('#s-table tbody').html('<tr><td colspan="6" style="text-align:center;color:#6b7280;">Loading…</td></tr>');
    fetch(RTS.rest.endpoints.stocks + '?' + new URLSearchParams(p), { headers: { 'X-WP-Nonce': RTS.rest.nonce } })
      .then(r=>r.json()).then(d=>{
        const list = d.data || d.stocks || [];
        if (!list.length){ $('#s-table tbody').html('<tr><td colspan="6" style="text-align:center;color:#6b7280;">No results</td></tr>'); return; }
        const rows = list.map(s=> `<tr><td><strong>${s.ticker||s.symbol}</strong></td><td>${s.company_name||s.name||''}</td><td>${s.current_price||''}</td><td style=\"color:${(s.change_percent||0)>=0?'#16a34a':'#b91c1c'}\">${s.change_percent||''}</td><td>${(s.volume||'').toLocaleString?.()}</td><td>${(s.market_cap||'').toLocaleString?.()}</td></tr>`).join('');
        $('#s-table tbody').html(rows);
      }).catch(()=> $('#s-table tbody').html('<tr><td colspan="6" style="text-align:center;color:#b91c1c;">Failed to fetch</td></tr>'));
  }
  $('#s-run').on('click', run);
})(jQuery);
</script>
<?php get_footer(); ?>