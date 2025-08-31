<?php /* Template Name: System Status */
get_header(); ?>
<section class="section"><div class="container">
  <h1>System Status</h1>
  <div class="grid" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:16px;">
    <div class="card" style="padding:16px;">
      <div class="text-sm" style="color:#6b7280;">Overall</div>
      <div id="rts-overall" style="font-size:22px;font-weight:600;margin-top:4px;">Loading…</div>
      <div class="text-sm" id="rts-db" style="margin-top:6px;">Database: <span style="font-weight:600;">-</span></div>
      <div class="text-sm" id="rts-ver" style="margin-top:6px;">Version: <span style="font-weight:600;">-</span></div>
    </div>
    <div class="card" style="padding:16px;">
      <div class="text-sm" style="color:#6b7280;margin-bottom:8px;">Endpoints</div>
      <ul id="rts-endpoints" style="margin:0;padding:0;list-style:none;"></ul>
    </div>
  </div>
</div></section>
<script>
(function(){
  fetch(RTS.rest.endpoints.health, { headers: { 'X-WP-Nonce': RTS.rest.nonce } })
    .then(r=>r.json()).then(d=>{
      document.getElementById('rts-overall').textContent = d.status || 'degraded';
      document.getElementById('rts-db').innerHTML = 'Database: <span style="font-weight:600;">'+(d.database||'-')+'</span>';
      document.getElementById('rts-ver').innerHTML = 'Version: <span style="font-weight:600;">'+(d.version||'-')+'</span>';
      var ul = document.getElementById('rts-endpoints');
      if(d.endpoints){ Object.keys(d.endpoints).forEach(function(k){ var li = document.createElement('li'); li.style.padding='6px 0'; li.style.borderBottom='1px solid var(--border)'; li.innerHTML = '<span style="text-transform:capitalize;">'+k.replace('_',' ')+'</span> <span style="color:#6b7280;">'+d.endpoints[k]+'</span>'; ul.appendChild(li); }); }
    }).catch(()=>{ document.getElementById('rts-overall').textContent = 'degraded'; });
})();
</script>
<?php get_footer(); ?>