<?php /* Template Name: Alerts */ get_header(); ?>
<section class="section">
  <div class="container">
    <h1>Price Alerts</h1>
    <div class="grid" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;">
      <div class="card" style="padding:16px;">
        <h3>Create alert</h3>
        <form id="rts-alert-form" class="form" style="display:flex;flex-direction:column;gap:12px;">
          <div><label>Ticker</label><input class="input" name="ticker" placeholder="e.g., AAPL" required /></div>
          <div><label>Target price</label><input class="input" type="number" step="0.01" name="target_price" placeholder="e.g., 200" required /></div>
          <div><label>Condition</label>
            <select class="input" name="condition"><option value="above">Above</option><option value="below">Below</option></select>
          </div>
          <div><label>Email</label><input class="input" type="email" name="email" placeholder="you@example.com" required /></div>
          <button class="btn btn-primary" type="submit">Create alert</button>
          <div id="rts-alert-schema" style="color:#6b7280;font-size:12px;">Loading endpoint…</div>
        </form>
      </div>
      <div class="card" style="padding:16px;">
        <div id="rts-alert-banners"></div>
        <h3>Active alerts</h3>
        <table class="table" id="rts-alerts-table"><thead><tr><th>Ticker</th><th>Type</th><th>Target</th><th>Created</th><th>Status</th></tr></thead><tbody><tr><td colspan="5" style="text-align:center;color:#6b7280;">Loading…</td></tr></tbody></table>
      </div>
    </div>
  </div>
</section>
<script>
(function($){
  const schemaEl = document.getElementById('rts-alert-schema');
  fetch(RTS.rest.endpoints.alerts_create, { headers: { 'X-WP-Nonce': RTS.rest.nonce } })
    .then(r=>r.json()).then(d=>{ if(d && d.endpoint){ schemaEl.textContent = `Endpoint: ${d.endpoint} • Method: ${d.method}`; } else { schemaEl.textContent = 'Endpoint info unavailable'; } })
    .catch(()=> schemaEl.textContent = 'Endpoint info unavailable');

  const table = document.getElementById('rts-alerts-table').querySelector('tbody');
  const banners = document.getElementById('rts-alert-banners');
  function banner(type, title, msg){
    const colors = type==='success' ? 'background:#dcfce7;color:#166534;border:1px solid #bbf7d0;' : type==='error' ? 'background:#fee2e2;color:#991b1b;border:1px solid #fecaca;' : 'background:var(--muted);border:1px solid var(--border);';
    banners.innerHTML = `<div style=\"padding:8px;border-radius:8px;${colors}\"><strong>${title}</strong> <span style=\"opacity:.9\">${msg||''}</span></div>`;
  }
  function loadAlerts(){
    fetch(RTS.rest.endpoints.alerts_list + '?limit=20&active=true', { headers: { 'X-WP-Nonce': RTS.rest.nonce } })
      .then(r=>r.json()).then(d=>{
        const arr = d.data || [];
        if(!arr.length){ table.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#6b7280;">No alerts</td></tr>'; return; }
        table.innerHTML = arr.map(a=> `<tr><td><strong>${a.ticker}</strong></td><td>${a.alert_type}</td><td>${a.target_value}</td><td>${new Date(a.created_at).toLocaleString?.()}</td><td>${a.is_active? 'Active':'Inactive'}</td></tr>`).join('');
        banner('success','Alerts loaded',`Loaded ${arr.length} alerts`);
      }).catch(()=>{ table.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#b91c1c;">Failed to load</td></tr>'; banner('error','Unable to load alerts','Could not fetch alerts from the server.'); });
  }
  loadAlerts();

  document.getElementById('rts-alert-form').addEventListener('submit', function(e){
    e.preventDefault(); const fd = new FormData(e.target);
    const payload = Object.fromEntries(fd.entries()); payload.target_price = Number(payload.target_price);
    fetch(RTS.rest.endpoints.alerts_create, { method:'POST', headers: { 'Content-Type':'application/json','X-WP-Nonce': RTS.rest.nonce }, body: JSON.stringify(payload) })
      .then(r=>r.json()).then(()=>{ banner('success','Alert created','Your alert was created.'); e.target.reset(); loadAlerts(); })
      .catch(()=> banner('error','Failed to create alert','Please check your inputs.'));
  });
})(jQuery);
</script>
<?php get_footer(); ?>