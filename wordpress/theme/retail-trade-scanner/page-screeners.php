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
        <select id="s-sortby" class="input">
          <option value="last_updated">Sort: Last Updated</option>
          <option value="price">Sort: Price</option>
          <option value="volume">Sort: Volume</option>
          <option value="market_cap">Sort: Market Cap</option>
          <option value="change_percent">Sort: Change %</option>
        </select>
        <select id="s-order" class="input">
          <option value="desc">Desc</option>
          <option value="asc">Asc</option>
        </select>
        <input id="s-limit" class="input" placeholder="Limit (<=1000)" type="number" value="25" />
        <button id="s-run" class="btn btn-primary">Run</button>
      </div>
    </div>
    <div class="card" style="padding:16px;margin-top:16px;">
      <table class="table" id="s-table"><thead><tr>
        <th><button class="btn btn-outline" id="th-ticker" style="padding:4px 8px;">Ticker</button></th>
        <th>Company</th>
        <th><button class="btn btn-outline" id="th-price" style="padding:4px 8px;">Price</button></th>
        <th><button class="btn btn-outline" id="th-change" style="padding:4px 8px;">Change%</button></th>
        <th><button class="btn btn-outline" id="th-volume" style="padding:4px 8px;">Volume</button></th>
        <th><button class="btn btn-outline" id="th-mcap" style="padding:4px 8px;">Market Cap</button></th>
      </tr></thead><tbody><tr><td colspan="6" style="text-align:center;color:#6b7280;">No results</td></tr></tbody></table>
      <div id="s-paginator" style="display:flex;align-items:center;justify-content:space-between;margin-top:8px;">
        <div id="s-summary" style="color:#6b7280;font-size:14px;">Page 1 of 1 • Total 0</div>
        <div>
          <button class="btn btn-outline" id="s-prev" disabled>Prev</button>
          <button class="btn btn-outline" id="s-next" disabled>Next</button>
        </div>
      </div>
    </div>
  </div>
</section>
<script>
(function($){
  const st = { page:1, limit:25, total:0 };
  function Q(){ return {
    search: $('#s-q').val(), category: $('#s-category').val(), exchange: $('#s-exchange').val(), min_price: $('#s-minp').val(), max_price: $('#s-maxp').val(), min_volume: $('#s-minv').val(), sort_by: $('#s-sortby').val(), sort_order: $('#s-order').val(), limit: Number($('#s-limit').val()||25), offset: (st.page-1) * Number($('#s-limit').val()||25)
  }; }
  function summary(){ const pages = Math.max(1, Math.ceil((st.total||0) / (st.limit||25))); $('#s-summary').text(`Page ${st.page} of ${pages} • Total ${st.total||0}`); $('#s-prev').prop('disabled', st.page<=1); $('#s-next').prop('disabled', st.page>=pages); }
  function render(list){ const rows = list.map(s=> `<tr><td><strong>${s.ticker||s.symbol}</strong></td><td>${s.company_name||s.name||''}</td><td>${s.current_price||''}</td><td style=\"color:${(s.change_percent||0)>=0?'#16a34a':'#b91c1c'}\">${s.change_percent||''}</td><td>${(s.volume||'').toLocaleString?.()}</td><td>${(s.market_cap||'').toLocaleString?.()}</td></tr>`).join(''); $('#s-table tbody').html(rows); }
  function run(){
    const p = Q(); st.limit = p.limit;
    if (p.min_price && p.max_price && Number(p.min_price) > Number(p.max_price)) { alert('Min price cannot exceed Max price'); return; }
    if (p.limit > 1000) { alert('Limit cannot exceed 1000'); return; }
    $('#s-table tbody').html('<tr><td colspan="6" style="text-align:center;color:#6b7280;">Loading…</td></tr>');
    fetch(RTS.rest.endpoints.stocks + '?' + new URLSearchParams(p), { headers: { 'X-WP-Nonce': RTS.rest.nonce } })
      .then(r=>r.json()).then(d=>{ const list = d.data || d.stocks || []; st.total = d.total_available || d.total_count || list.length; render(list); summary(); })
      .catch(()=> $('#s-table tbody').html('<tr><td colspan="6" style="text-align:center;color:#b91c1c;">Failed to fetch</td></tr>'));
  }
  $('#s-run').on('click', function(){ st.page=1; run(); });
  $('#s-prev').on('click', function(){ st.page=Math.max(1, st.page-1); run(); });
  $('#s-next').on('click', function(){ st.page=st.page+1; run(); });
  function bindSort(btnId, field){ $(btnId).on('click', function(){ const cur = $('#s-sortby').val(); const order = $('#s-order').val(); if(cur===field){ $('#s-order').val(order==='asc'?'desc':'asc'); } else { $('#s-sortby').val(field); $('#s-order').val('desc'); } st.page=1; run(); }); }
  bindSort('#th-ticker','ticker'); bindSort('#th-price','price'); bindSort('#th-change','change_percent'); bindSort('#th-volume','volume'); bindSort('#th-mcap','market_cap');
})(jQuery);
</script>
<?php get_footer(); ?>