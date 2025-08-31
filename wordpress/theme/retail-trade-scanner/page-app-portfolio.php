<?php /* Template Name: App - Portfolio */ get_header(); ?>
<section class="section"><div class="container">
  <h1>Portfolio</h1>
  <div class="grid" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;">
    <div class="card" style="padding:16px;">
      <h3>Add Holding</h3>
      <form id="rts-pf" style="display:flex;flex-direction:column;gap:12px;">
        <div><label>Symbol</label><input name="symbol" class="input" placeholder="e.g., AAPL" required /></div>
        <div><label>Shares</label><input name="shares" class="input" type="number" required /></div>
        <div><label>Average Cost</label><input name="avg_cost" class="input" type="number" step="0.01" required /></div>
        <div><label>Portfolio name</label><input name="portfolio_name" class="input" value="My Portfolio" /></div>
        <button class="btn btn-primary" type="submit">Add</button>
      </form>
    </div>
    <div class="card" style="padding:16px;">
      <h3>Holdings</h3>
      <table class="table" id="rts-pf-table"><thead><tr><th>Symbol</th><th>Shares</th><th>Avg Cost</th><th>Value</th><th></th></tr></thead><tbody><tr><td colspan="5" style="text-align:center;color:#6b7280;">Loading…</td></tr></tbody></table>
    </div>
  </div>
</div></section>
<script>
(function(){
  const tbody = document.getElementById('rts-pf-table').querySelector('tbody');
  function load(){
    fetch(RTS.rest.endpoints.portfolio, { headers: { 'X-WP-Nonce': RTS.rest.nonce } })
      .then(r=>r.json()).then(d=>{
        const items = d.data||[]; if(!items.length){ tbody.innerHTML='<tr><td colspan="5" style="text-align:center;color:#6b7280;">No holdings</td></tr>'; return; }
        tbody.innerHTML = items.map(h=> `<tr><td><strong>${h.symbol}</strong></td><td>${h.shares}</td><td>${h.avg_cost}</td><td>${h.total_value??'-'}</td><td><button class=\"btn btn-outline\" data-id=\"${h.id}\">Delete</button></td></tr>`).join('');
        tbody.querySelectorAll('button').forEach(btn=> btn.addEventListener('click', function(){ const id=this.getAttribute('data-id'); fetch(RTS.rest.endpoints.portfolio_delete, { method:'POST', headers:{'Content-Type':'application/json','X-WP-Nonce': RTS.rest.nonce}, body: JSON.stringify({ id }) }).then(()=> load()); }));
      }).catch(()=> tbody.innerHTML='<tr><td colspan="5" style="text-align:center;color:#b91c1c;">Failed</td></tr>');
  }
  load();
  document.getElementById('rts-pf').addEventListener('submit', function(e){
    e.preventDefault(); const fd = new FormData(e.target); const data = Object.fromEntries(fd.entries()); data.shares=Number(data.shares); data.avg_cost=Number(data.avg_cost);
    fetch(RTS.rest.endpoints.portfolio_add, { method:'POST', headers:{'Content-Type':'application/json','X-WP-Nonce': RTS.rest.nonce}, body: JSON.stringify(data) }).then(()=>{ e.target.reset(); load(); }).catch(()=> alert('Failed'));
  });
})();
</script>
<?php get_footer(); ?>