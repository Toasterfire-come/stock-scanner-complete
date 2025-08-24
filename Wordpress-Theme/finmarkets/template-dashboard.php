<?php /* Template Name: Dashboard */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container grid cols-3">
    <div class="card" style="padding:16px;">
      <h3>Welcome</h3>
      <div id="dashUser" class="muted">Signed out</div>
    </div>
    <div class="card" style="padding:16px;">
      <h3>Watchlist</h3>
      <ul id="dashWl" style="list-style:none; padding:0; margin:0;"></ul>
    </div>
    <div class="card" style="padding:16px;">
      <h3>News</h3>
      <div id="dashNews"></div>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  const getU=()=>JSON.parse(localStorage.getItem('finm_user')||'null');
  const getWL=()=>JSON.parse(localStorage.getItem('finm_wl')||'[]');
  const fmt = new Intl.NumberFormat(undefined,{style:'currency',currency:'USD'});
  document.addEventListener('DOMContentLoaded', function(){
    const u=getU(); $('#dashUser').textContent = u?`Hello, ${u.name}`:'Signed out';
    const wl=new Set(getWL());
    const items=(window.MockData?.stocks||[]).filter(s=>wl.has(s.symbol));
    $('#dashWl').innerHTML = items.map(s=>`<li style="display:flex; justify-content:space-between; border-bottom:1px solid var(--gray-200); padding:6px 0;"><span class="mono">${s.symbol}</span><span>${fmt.format(s.price)}</span></li>`).join('') || '<li class="muted">Empty.</li>';
    $('#dashNews').innerHTML = (window.MockData?.news||[]).slice(0,3).map(n=>`<div class="muted">${n.source} — ${n.title}</div>`).join('');
  });
})();
</script>
<?php get_footer(); ?>