<?php /* Template Name: Watchlist */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Watchlist</h1>
      <p class="muted">Your saved symbols. Enriched with live quotes when API is configured.</p>
    </div>
    <?php if (shortcode_exists('stock_scanner_watchlist')) { echo do_shortcode('[stock_scanner_watchlist]'); } ?>
    <div class="card" style="padding:16px;">
      <ul id="watchlistItems" style="list-style:none; padding:0; margin:0;"></ul>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  const getWL = () => JSON.parse(localStorage.getItem('finm_wl')||'[]');
  const fmt = new Intl.NumberFormat(undefined,{style:'currency',currency:'USD',maximumFractionDigits:2});
  async function loadLive(symbols){
    if(!(window.finmApi && (window.finmConfig?.hasApiBase))) return {};
    const out = {};
    const limit = 10; // avoid too many requests
    const subset = symbols.slice(0, limit);
    await Promise.all(subset.map(async sym => {
      try {
        const j = await window.finmApi.realtime(sym);
        const price = j?.price || j?.current_price || j?.last || null;
        if(price!=null) out[sym] = price;
      } catch(e) {}
    }));
    return out;
  }
  async function render(){
    const list=$('#watchlistItems'); if(!list) return; const wl=new Set(getWL()); const items=(window.MockData?.stocks||[]).filter(s=>wl.has(s.symbol));
    const live = await loadLive(Array.from(wl));
    list.innerHTML = items.map(s=>{
      const price = live[s.symbol] != null ? live[s.symbol] : s.price;
      return `<li style="display:flex; justify-content:space-between; align-items:center; padding:8px; border-bottom:1px solid var(--gray-200);"><span class="mono">${s.symbol}</span><span>${price!=null?fmt.format(price):'—'}</span></li>`;
    }).join('') || '<li class="muted">No symbols yet. Add from the Screener.</li>';
  }
  document.addEventListener('DOMContentLoaded', render);
})();
</script>
<?php get_footer(); ?>