<?php /* Template Name: Market Overview */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container grid cols-3">
    <div class="card" style="padding:16px;">
      <h3>Market Overview</h3>
      <div id="moOverview" class="muted">Loading…</div>
    </div>
    <div class="card" style="padding:16px;">
      <h3>Top Gainers</h3>
      <ul id="moGainers"></ul>
    </div>
    <div class="card" style="padding:16px;">
      <h3>Most Active</h3>
      <ul id="moActive"></ul>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $=s=>document.querySelector(s);
  const it=(arr,fmt)=> (arr||[]).slice(0,5).map(x=>`<li style="display:flex; justify-content:space-between; border-bottom:1px solid var(--gray-200); padding:6px 0;"><span class=\"mono\">${x.ticker||x.symbol||x.name}</span><span>${(x.current_price!=null? x.current_price : x.price)||'-'}</span></li>`).join('')||'<li class="muted">No data.</li>';
  document.addEventListener('DOMContentLoaded', async function(){
    try{
      const s = await (window.finmApi? window.finmApi.marketStats(): Promise.reject('no api'));
      const o = s.market_overview || {};
      $('#moOverview').textContent = `Total: ${o.total_stocks||'-'} • Gainers: ${o.gainers||'-'} • Losers: ${o.losers||'-'} • Unchanged: ${o.unchanged||'-'}`;
      $('#moGainers').innerHTML = it(s.top_gainers||[]);
      $('#moActive').innerHTML = it(s.most_active||[]);
    }catch(e){
      // fallback to mock
      $('#moOverview').textContent = 'External API unavailable — showing mock preview';
      $('#moGainers').innerHTML = it((window.MockData?.stocks||[]).slice(0,5));
      $('#moActive').innerHTML = it((window.MockData?.stocks||[]).slice(5,10));
    }
  });
})();
</script>
<?php get_footer(); ?>