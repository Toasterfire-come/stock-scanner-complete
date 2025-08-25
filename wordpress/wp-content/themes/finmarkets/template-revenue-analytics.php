<?php /* Template Name: Revenue Analytics */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content"><h1 style="color:var(--navy);">Revenue Analytics</h1><p class="muted">Fetched via /wp-json/finm/v1/revenue/analytics</p></div>
    <div class="card" style="padding:16px;">
      <form class="toolbar" onsubmit="return false;">
        <input id="raMonth" class="input" placeholder="YYYY-MM (optional)" />
        <button id="raLoad" class="btn">Load</button>
      </form>
      <pre id="raOut" style="white-space:pre-wrap; overflow:auto; max-height:420px; background:#0a0a0a; color:#c0f9c0; padding:12px;">(results)</pre>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $=s=>document.querySelector(s);
  async function load(){
    const m=$('#raMonth').value.trim();
    try{
      const j = await (window.finmApi ? window.finmApi.revenueAnalytics(m||undefined) : fetch(((window.finmConfig?.restBase)||'/wp-json/finm/v1').replace(/\/$/,'') + (m?('/revenue/analytics/'+encodeURIComponent(m)): '/revenue/analytics')).then(x=>x.json()));
      $('#raOut').textContent = JSON.stringify(j, null, 2);
    }catch(e){ $('#raOut').textContent = String(e); }
  }
  document.addEventListener('DOMContentLoaded', function(){
    $('#raLoad').addEventListener('click', load); load();
  });
})();
</script>
<?php get_footer(); ?>