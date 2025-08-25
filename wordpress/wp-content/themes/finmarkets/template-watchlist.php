<?php /* Template Name: Watchlist */ if (!defined('ABSPATH')) { exit; } $finm_requires_api = true; get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Watchlist</h1>
      <p class="muted">Your saved symbols. Server-backed when API is configured; otherwise local.</p>
    </div>
    <?php if (shortcode_exists('stock_scanner_watchlist')) { echo do_shortcode('[stock_scanner_watchlist]'); } ?>
    <div class="card" style="padding:16px;">
      <div class="toolbar" style="margin-bottom:8px;">
        <input id="wlSymbol" class="input" placeholder="Add symbol (e.g., AAPL)" />
        <button id="wlAdd" class="btn">Add</button>
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
  const getLocal = () => JSON.parse(localStorage.getItem('finm_wl')||'[]');
  const setLocal = (x) => localStorage.setItem('finm_wl', JSON.stringify(x));
  let usingServer=false; let serverItems=[];

  async function fetchServer(){
    if(!(window.finmApi && (window.finmConfig?.hasApiBase))) return false;
    try{ const j=await window.finmApi.watchlistGet(); if(j && j.success!==false){ serverItems=j.data||[]; return true; } }catch(e){}
    return false;
  }

  async function addServer(sym){ await window.finmApi.watchlistAdd(sym,'My Watchlist','',null); setMsg('Added',true); await fetchServer(); render(); }
  async function deleteServer(id){ await window.finmApi.watchlistDelete(id); await fetchServer(); render(); }

  function render(){
    const list=$('#watchlistItems');
    if(usingServer){
      list.innerHTML = (serverItems||[]).map(it=>`<li style="display:flex; justify-content:space-between; align-items:center; padding:8px; border-bottom:1px solid var(--gray-200);"><span class="mono">${it.symbol}</span><button class="btn" data-id="${it.id}">Remove</button></li>`).join('') || '<li class="muted">No items.</li>';
      return;
    }
    const wl=new Set(getLocal());
    list.innerHTML = Array.from(wl).map(sym=>`<li style="display:flex; justify-content:space-between; align-items:center; padding:8px; border-bottom:1px solid var(--gray-200);"><span class="mono">${sym}</span><button class="btn" data-sym="${sym}">Remove</button></li>`).join('') || '<li class="muted">No symbols yet.</li>';
  }

  document.addEventListener('DOMContentLoaded', async function(){
    usingServer = await fetchServer();
    render();
    $('#wlAdd').addEventListener('click', async ()=>{ const sym=$('#wlSymbol').value.trim().toUpperCase(); if(!sym) return; try{ usingServer ? await addServer(sym) : (setLocal([...new Set(getLocal().concat(sym))]), setMsg('Added',true), render()); }catch(e){ setMsg('Add failed'); } $('#wlSymbol').value=''; });
    $('#watchlistItems').addEventListener('click', async (e)=>{
      const b=e.target.closest('button[data-id],button[data-sym]'); if(!b) return;
      try{ usingServer ? await deleteServer(b.dataset.id) : (setLocal(getLocal().filter(s=>s!==b.dataset.sym)), render()); }catch(e){ setMsg('Remove failed'); }
    });
  });
})();
</script>
<?php get_footer(); ?>