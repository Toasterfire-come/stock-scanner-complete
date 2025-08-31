<?php /* Template Name: App - Watchlists */ get_header(); ?>
<section class="section"><div class="container">
  <h1>Watchlists</h1>
  <div class="grid" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;">
    <div class="card" style="padding:16px;">
      <h3>Add to watchlist</h3>
      <form id="rts-wl" style="display:flex;flex-direction:column;gap:12px;">
        <div><label>Symbol</label><input name="symbol" class="input" required /></div>
        <div><label>Watchlist name</label><input name="watchlist_name" class="input" value="My Watchlist" /></div>
        <div><label>Notes</label><textarea name="notes" class="input" style="min-height:100px"></textarea></div>
        <div><label>Alert price (optional)</label><input name="alert_price" class="input" type="number" step="0.01" /></div>
        <button class="btn btn-primary" type="submit">Add</button>
      </form>
    </div>
    <div class="card" style="padding:16px;">
      <h3>Items</h3>
      <table class="table" id="rts-wl-table"><thead><tr><th>Symbol</th><th>Notes</th><th>Alert Price</th><th>Added</th><th></th></tr></thead><tbody><tr><td colspan="5" style="text-align:center;color:#6b7280;">Loading…</td></tr></tbody></table>
    </div>
  </div>
</div></section>
<script>
(function(){
  const tbody = document.getElementById('rts-wl-table').querySelector('tbody');
  function load(){
    fetch(RTS.rest.endpoints.watchlist, { headers: { 'X-WP-Nonce': RTS.rest.nonce } })
      .then(r=>r.json()).then(d=>{
        const items = d.data||[]; if(!items.length){ tbody.innerHTML='<tr><td colspan="5" style="text-align:center;color:#6b7280;">No items</td></tr>'; return; }
        tbody.innerHTML = items.map(w=> `<tr><td><strong>${w.symbol}</strong></td><td>${w.notes||'-'}</td><td>${w.alert_price??'-'}</td><td>${new Date(w.added_date).toLocaleString?.()||'-'}</td><td><button class=\"btn btn-outline\" data-id=\"${w.id}\">Delete</button></td></tr>`).join('');
        tbody.querySelectorAll('button').forEach(btn=> btn.addEventListener('click', function(){ const id=this.getAttribute('data-id'); fetch(RTS.rest.endpoints.watchlist_delete, { method:'POST', headers:{'Content-Type':'application/json','X-WP-Nonce': RTS.rest.nonce}, body: JSON.stringify({ id }) }).then(()=> load()); }));
      }).catch(()=> tbody.innerHTML='<tr><td colspan="5" style="text-align:center;color:#b91c1c;">Failed</td></tr>');
  }
  load();
  document.getElementById('rts-wl').addEventListener('submit', function(e){ e.preventDefault(); const fd = new FormData(e.target); const data = Object.fromEntries(fd.entries()); if(data.alert_price) data.alert_price = Number(data.alert_price); else data.alert_price=null; fetch(RTS.rest.endpoints.watchlist_add, { method:'POST', headers:{'Content-Type':'application/json','X-WP-Nonce': RTS.rest.nonce}, body: JSON.stringify(data) }).then(()=>{ e.target.reset(); load(); }).catch(()=> alert('Failed')); });
})();
</script>
<?php get_footer(); ?>