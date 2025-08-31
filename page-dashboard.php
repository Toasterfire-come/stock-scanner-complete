<?php /* Template Name: Dashboard */ get_header(); ?>
<section class="section">
  <div class="container">
    <h1>Dashboard</h1>
    <div class="grid" style="display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:16px;">
      <div class="card" style="grid-column:span 8;padding:16px;">
        <h3 style="margin:0 0 8px 0;">Market Overview</h3>
        <div id="rts-dash-market" style="color:#6b7280;">Loading…</div>
      </div>
      <div class="card" style="grid-column:span 4;padding:16px;">
        <h3 style="margin:0 0 8px 0;">Watchlist</h3>
        <ul id="rts-dash-watch" style="list-style:none;margin:0;padding:0;color:#6b7280;">
          <li>Loading…</li>
        </ul>
      </div>
    </div>
  </div>
</section>
<script>
(function(){
  // Market snapshot
  const market = document.getElementById('rts-dash-market');
  fetch(RTS.rest.endpoints.market_stats, { headers: { 'X-WP-Nonce': RTS.rest.nonce } })
    .then(r=>r.json())
    .then(d=>{ market.textContent = d && d.data ? 'Gainers: ' + (d.data.top_gainers||[]).length + ', Losers: ' + (d.data.top_losers||[]).length : 'No data'; })
    .catch(()=> market.textContent = 'Failed to load');

  // Simple watchlist preview
  const list = document.getElementById('rts-dash-watch');
  fetch(RTS.rest.endpoints.watchlist, { headers: { 'X-WP-Nonce': RTS.rest.nonce } })
    .then(r=>r.json())
    .then(d=>{
      const items = (d && d.data) || [];
      if(!items.length){ list.innerHTML = '<li style="color:#6b7280;">No items</li>'; return; }
      list.innerHTML = items.slice(0,6).map(w => '<li style="padding:6px 0;border-bottom:1px solid var(--border);"><strong>' + w.symbol + '</strong> <span style="color:#6b7280;">' + (w.notes||'') + '</span></li>').join('');
    })
    .catch(()=> list.innerHTML = '<li style="color:#b91c1c;">Failed</li>');
})();
</script>
<?php get_footer(); ?>

