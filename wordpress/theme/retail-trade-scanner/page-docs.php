<?php /* Template Name: Documentation */ get_header(); ?>
<section class="section"><div class="container">
  <h1>Documentation</h1>
  <p style="color:#6b7280;">API and product documentation.</p>
  <ul style="margin:0;padding-left:18px;">
    <li>REST base: /wp-json/stock-scanner/v1/</li>
    <li>Stocks: /wp-json/stock-scanner/v1/stocks</li>
    <li>Search: /wp-json/stock-scanner/v1/search</li>
    <li>Trending: /wp-json/stock-scanner/v1/trending</li>
    <li>Alerts: /wp-json/stock-scanner/v1/alerts/create</li>
  </ul>
  <div class="card" style="padding:16px;margin-top:16px;">
    <div class="text-sm" style="color:#6b7280;">Live sample</div>
    <div id="rts-docs-live" class="text-sm">Loading…</div>
  </div>
</div></section>
<script>
(function(){
  const el = document.getElementById('rts-docs-live');
  fetch(RTS.rest.endpoints.market_stats, { headers: { 'X-WP-Nonce': RTS.rest.nonce } })
    .then(r=>r.json()).then(d=>{
      const mv = d.market_overview || {}; const g = mv.gainers ?? '-'; const l = mv.losers ?? '-'; const t = mv.total_stocks ?? '-';
      el.innerHTML = `Total stocks: <strong>${t}</strong> • Gainers: <strong style=\"color:#16a34a\">${g}</strong> • Losers: <strong style=\"color:#b91c1c\">${l}</strong>`;
    }).catch(()=> el.textContent='Failed to load');
})();
</script>
<?php get_footer(); ?>