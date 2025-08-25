<?php /* Template Name: Stock Lookup */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Stock Lookup</h1>
      <p class="muted">Type a symbol to view basic profile. Uses external API when configured.</p>
    </div>
    <?php if (shortcode_exists('stock_scanner_lookup')) { echo do_shortcode('[stock_scanner_lookup]'); } ?>
    <div class="card" style="padding:16px;">
      <div class="toolbar">
        <input id="luInput" class="input" placeholder="Enter symbol (e.g., AAPL)" />
        <button id="luBtn" class="btn">Lookup</button>
      </div>
      <div id="luResult" style="margin-top:12px;"></div>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  function render(res){ const el=$('#luResult'); if(!res){ el.innerHTML='<div class="muted">No match.</div>'; return; } el.innerHTML=`<div class="grid cols-2"><div class="card" style="padding:12px;"><h3>${res.name||res.company_name||'—'}</h3><div class="mono">${res.symbol||res.ticker||''}</div><div>Sector: ${res.sector||'—'}</div></div><div class="card" style="padding:12px;"><div>Price: ${res.price||res.current_price||'—'}</div><div>Change: ${(res.change!=null?res.change:res.change_percent)||'—'}%</div><div>Cap: ${res.marketCap||res.market_cap||res.market_capitalization||'—'}</div></div>`; }
  async function lookup(sym){
    sym = (sym||'').trim().toUpperCase(); if(!sym) return null;
    if(window.finmApi && (window.finmConfig?.hasApiBase)){
      try { return await window.finmApi.stock(sym); } catch(e) {}
    }
    return (window.MockData?.stocks||[]).find(s=>s.symbol===sym) || null;
  }
  document.addEventListener('DOMContentLoaded', function(){ $('#luBtn').addEventListener('click', async ()=>{ const data = await lookup($('#luInput').value); render(Array.isArray(data)?data[0]:data); }); });
})();
</script>
<?php get_footer(); ?>