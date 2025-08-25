<?php /* Template Name: Portfolio Management */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Portfolio</h1>
      <p class="muted">Manage holdings. If plugin portfolio components exist, they will render above.</p>
    </div>
    <?php if (shortcode_exists('stock_scanner_portfolio')) { echo do_shortcode('[stock_scanner_portfolio]'); } ?>
    <div class="card" style="padding:16px;">
      <form id="pfForm" class="toolbar" onsubmit="return false;" aria-label="Add holding">
        <input id="pfTicker" class="input" placeholder="Symbol (e.g., AAPL)" />
        <input id="pfQty" class="input" placeholder="Qty" type="number" min="1" />
        <input id="pfCost" class="input" placeholder="Cost basis" type="number" step="0.01" />
        <button id="pfAdd" class="btn btn-primary">Add</button>
      </form>
      <table class="table" aria-label="Portfolio table">
        <thead><tr><th>Symbol</th><th>Qty</th><th>Cost</th><th>Actions</th></tr></thead>
        <tbody id="pfBody"></tbody>
      </table>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  const getPF = () => JSON.parse(localStorage.getItem('finm_pf')||'[]');
  const setPF = (x) => localStorage.setItem('finm_pf', JSON.stringify(x));
  function render(){ const body = $('#pfBody'); const rows = getPF().map((r,i)=>`<tr><td class="mono">${r.t}</td><td>${r.q}</td><td>${r.c}</td><td><button data-i="${i}" class="btn">Remove</button></td></tr>`).join(''); body.innerHTML = rows || '<tr><td colspan="4" class="muted">No holdings yet.</td></tr>'; }
  document.addEventListener('DOMContentLoaded', function(){ render(); $('#pfAdd').addEventListener('click', ()=>{ const t=$('#pfTicker').value.trim().toUpperCase(); const q=parseFloat($('#pfQty').value||'0'); const c=parseFloat($('#pfCost').value||'0'); if(!t||q<=0||c<=0) return; const pf=getPF(); pf.push({t,q,c}); setPF(pf); render(); $('#pfTicker').value=''; $('#pfQty').value=''; $('#pfCost').value=''; }); $('#pfBody').addEventListener('click', (e)=>{ const b=e.target.closest('button[data-i]'); if(!b) return; const i=+b.dataset.i; const pf=getPF(); pf.splice(i,1); setPF(pf); render(); }); });
})();
</script>
<?php get_footer(); ?>