<?php /* Template Name: Stock Lookup */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Stock Lookup</h1>
      <p class="muted">Type a symbol to view basic profile from mock data or plugin if available.</p>
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
  function find(sym){ sym = (sym||'').trim().toUpperCase(); return (window.MockData?.stocks||[]).find(s=>s.symbol===sym); }
  function render(res){ const el=$('#luResult'); if(!res){ el.innerHTML='<div class="muted">No match.</div>'; return; } el.innerHTML=`<div class="grid cols-2"><div class="card" style="padding:12px;"><h3>${res.name}</h3><div class="mono">${res.symbol}</div><div>Sector: ${res.sector}</div></div><div class="card" style="padding:12px;"><div>Price: ${res.price}</div><div>Change: ${res.change}%</div><div>Cap: ${res.marketCap}</div></div></div>`; }
  document.addEventListener('DOMContentLoaded', function(){ $('#luBtn').addEventListener('click', ()=> render(find($('#luInput').value))); });
})();
</script>
<?php get_footer(); ?>