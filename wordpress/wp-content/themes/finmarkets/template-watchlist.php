<?php /* Template Name: Watchlist */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Watchlist</h1>
      <p class="muted">Your saved symbols. Plugin watchlist will render if available.</p>
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
  function render(){
    const list=$('#watchlistItems'); if(!list) return; const wl=new Set(getWL()); const items=(window.MockData?.stocks||[]).filter(s=>wl.has(s.symbol));
    list.innerHTML = items.map(s=>`<li style="display:flex; justify-content:space-between; align-items:center; padding:8px; border-bottom:1px solid var(--gray-200);"><span class="mono">${s.symbol}</span><span>${fmt.format(s.price)}</span></li>`).join('') || '<li class="muted">No symbols yet. Add from the Screener.</li>';
  }
  document.addEventListener('DOMContentLoaded', render);
})();
</script>
<?php get_footer(); ?>