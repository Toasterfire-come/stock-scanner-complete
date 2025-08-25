<?php /* Template Name: Portfolio Management */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Portfolio</h1>
      <p class="muted">Manage holdings. Server-backed when API is configured; otherwise saved locally.</p>
    </div>
    <?php if (shortcode_exists('stock_scanner_portfolio')) { echo do_shortcode('[stock_scanner_portfolio]'); } ?>
    <div class="card" style="padding:16px;">
      <form id="pfForm" class="toolbar" onsubmit="return false;" aria-label="Add holding">
        <input id="pfTicker" class="input" placeholder="Symbol (e.g., AAPL)" />
        <input id="pfQty" class="input" placeholder="Qty" type="number" min="1" />
        <input id="pfCost" class="input" placeholder="Cost basis" type="number" step="0.01" />
        <button id="pfAdd" class="btn btn-primary">Add</button>
        <span id="pfMsg" class="muted"></span>
      </form>
      <table class="table" aria-label="Portfolio table" style="margin-top:12px;">
        <thead><tr><th>Symbol</th><th>Qty</th><th>Cost</th><th>Actions</th></tr></thead>
        <tbody id="pfBody"></tbody>
      </table>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  const setMsg=(t,ok)=>{ const el=$('#pfMsg'); el.textContent=t; el.style.color=ok?'#0f8a42':'var(--muted)'; };
  const getPF = () => JSON.parse(localStorage.getItem('finm_pf')||'[]');
  const setPF = (x) => localStorage.setItem('finm_pf', JSON.stringify(x));
  let usingServer = false; let serverRows = [];

  async function fetchServer(){
    if(!(window.finmApi && (window.finmConfig?.hasApiBase))) return false;
    try{ const j = await window.finmApi.portfolioGet(); if(j && j.success!==false){ serverRows = j.data||[]; return true; } }catch(e){}
    return false;
  }

  function render(){
    const body = $('#pfBody');
    if(usingServer){
      body.innerHTML = (serverRows||[]).map(r=>`<tr>
        <td class="mono">${r.symbol||'-'}</td>
        <td>${r.shares||r.qty||'-'}</td>
        <td>${r.avg_cost!=null?r.avg_cost:'-'}</td>
        <td><button data-id="${r.id}" class="btn">Remove</button></td>
      </tr>`).join('') || '<tr><td colspan="4" class="muted">No holdings yet.</td></tr>';
      return;
    }
    const rows = getPF();
    body.innerHTML = rows.map((r,i)=>`<tr>
      <td class="mono">${r.t}</td><td>${r.q}</td><td>${r.c}</td>
      <td><button data-i="${i}" class="btn">Remove</button></td></tr>`).join('') || '<tr><td colspan="4" class="muted">No holdings yet.</td></tr>';
  }

  async function addLocal(){ const t=$('#pfTicker').value.trim().toUpperCase(); const q=parseFloat($('#pfQty').value||'0'); const c=parseFloat($('#pfCost').value||'0'); if(!t||q<=0||c<=0) return setMsg('Fill all fields'); const pf=getPF(); pf.push({t,q,c}); setPF(pf); render(); setMsg('Added', true); }
  async function addServer(){ const t=$('#pfTicker').value.trim().toUpperCase(); const q=parseFloat($('#pfQty').value||'0'); const c=parseFloat($('#pfCost').value||'0'); if(!t||q<=0||c<=0) return setMsg('Fill all fields'); await window.finmApi.portfolioAdd(t,q,c,'My Portfolio'); setMsg('Added', true); await fetchServer(); render(); }

  async function removeLocal(i){ const pf=getPF(); pf.splice(i,1); setPF(pf); render(); }
  async function removeServer(id){ await window.finmApi.portfolioDelete(id); await fetchServer(); render(); }

  document.addEventListener('DOMContentLoaded', async function(){
    usingServer = await fetchServer();
    render();
    $('#pfAdd').addEventListener('click', async ()=>{ try{ usingServer ? await addServer() : await addLocal(); $('#pfTicker').value=''; $('#pfQty').value=''; $('#pfCost').value=''; }catch(e){ setMsg('Add failed'); } });
    $('#pfBody').addEventListener('click', async (e)=>{
      const b=e.target.closest('button[data-i],button[data-id]'); if(!b) return;
      try{ usingServer ? await removeServer(b.dataset.id) : await removeLocal(+b.dataset.i); }catch(e){ setMsg('Remove failed'); }
    });
  });
})();
</script>
<?php get_footer(); ?>