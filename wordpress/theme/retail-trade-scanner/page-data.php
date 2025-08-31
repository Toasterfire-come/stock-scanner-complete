<?php /* Template Name: Data Coverage */ get_header(); ?>
<section class="section"><div class="container">
  <h1>Data Coverage</h1>
  <p style="color:#6b7280;max-width:760px;">Exchanges, asset classes and refresh rates supported by Retail Trade Scanner.</p>
  <div class="grid" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:16px;">
    <div class="card" style="padding:16px;">
      <h3>Exchanges</h3>
      <ul style="margin:0;padding-left:18px;">
        <li>NYSE</li>
        <li>NASDAQ</li>
        <li>AMEX</li>
      </ul>
    </div>
    <div class="card" style="padding:16px;">
      <h3>Asset Classes</h3>
      <ul style="margin:0;padding-left:18px;">
        <li>Equities</li>
        <li>ETFs</li>
      </ul>
    </div>
    <div class="card" style="padding:16px;">
      <h3>Refresh Rates</h3>
      <ul style="margin:0;padding-left:18px;">
        <li>Realtime (where available)</li>
        <li>Intra-day periodic updates</li>
      </ul>
    </div>
  </div>
  <div class="card" style="padding:16px;margin-top:16px;">
    <h3>Live market overview</h3>
    <div id="rts-data-market" style="color:#6b7280;">Loading…</div>
  </div>
</div></section>
<script>
(function(){
  const el = document.getElementById('rts-data-market');
  fetch(RTS.rest.endpoints.market_stats, { headers: { 'X-WP-Nonce': RTS.rest.nonce } })
    .then(r=>r.json()).then(d=>{
      if(!d || !d.market_overview){ el.textContent='No data'; return; }
      const m = d.market_overview;
      el.innerHTML = `<div style=\"display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;\">
        <div><strong>Total:</strong> ${m.total_stocks||'-'}</div>
        <div><strong>Gainers:</strong> <span style=\"color:#16a34a\">${m.gainers||'-'}</span></div>
        <div><strong>Losers:</strong> <span style=\"color:#b91c1c\">${m.losers||'-'}</span></div>
      </div>`;
    }).catch(()=> el.textContent='Failed to load');
})();
</script>
<?php get_footer(); ?>