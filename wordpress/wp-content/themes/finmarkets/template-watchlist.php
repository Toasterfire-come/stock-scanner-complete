<?php /* Template Name: Watchlist */ if (!defined('ABSPATH')) { exit; } $finm_requires_api = true; get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Watchlist</h1>
      <p class="muted">Server-backed watchlist. Requires API connection.</p>
    </div>
    <?php if (shortcode_exists('stock_scanner_watchlist')) { echo do_shortcode('[stock_scanner_watchlist]'); } ?>
    <div class="card" style="padding:16px;">
      <div class="toolbar" style="margin-bottom:8px;">
        <input id="wlSymbol" class="input" placeholder="Add symbol (e.g., AAPL)" />
        <button id="wlAdd" class="btn btn-primary">Add</button>
        <span id="wlMsg" class="muted"></span>
      </div>
      <ul id="watchlistItems" style="list-style:none; padding:0; margin:0;"></ul>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  const setMsg=(t,ok)=>{ const el=$('#wlMsg'); el.textContent=t; el.style.color=ok?'#0f8a42':'var(--muted)'; };
  let items=[];

  async function fetchServer(){ const j=await window.finmApi.watchlistGet(); if(j && j.success!==false){ items=j.data||[]; } else { throw new Error(j?.message||'Load failed'); } }
  async function addServer(sym){ await window.finmApi.watchlistAdd(sym,'My Watchlist','',null); await fetchServer(); setMsg('Added',true); }
  async function deleteServer(id){ await window.finmApi.watchlistDelete(id); await fetchServer(); setMsg('Removed',true); }

  function render(){ const list=$('#watchlistItems'); list.innerHTML = (items||[]).map(it=>`<li style="display:flex; justify-content:space-between; align-items:center; padding:8px; border-bottom:1px solid var(--gray-200);"><span class="mono">${it.symbol}</span><button class="btn" data-id="${it.id}">Remove</button></li>`).join('') || '<li class="muted">No items.</li>'; }

  document.addEventListener('DOMContentLoaded', async function(){
    try{ await fetchServer(); render(); }catch(e){ setMsg('Failed to load watchlist'); }
    $('#wlAdd').addEventListener('click', async ()=>{ const sym=$('#wlSymbol').value.trim().toUpperCase(); if(!sym) return; try{ await addServer(sym); render(); }catch(e){ setMsg('Add failed'); } $('#wlSymbol').value=''; });
    $('#watchlistItems').addEventListener('click', async (e)=>{ const b=e.target.closest('button[data-id]'); if(!b) return; try{ await deleteServer(b.dataset.id); render(); }catch(e){ setMsg('Remove failed'); } });
  });
})();
</script>
<?php get_footer(); ?>