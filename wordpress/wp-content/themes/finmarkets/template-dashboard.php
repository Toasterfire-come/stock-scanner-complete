<?php /* Template Name: Dashboard */ if (!defined('ABSPATH')) { exit; } $finm_requires_auth = true; $finm_requires_api = true; get_header(); ?>
<section class="section" data-page="dashboard">
  <div class="container content">
    <?php if (shortcode_exists('stock_scanner_dashboard')) { echo do_shortcode('[stock_scanner_dashboard]'); } ?>
  </div>
  <div class="container grid cols-3" style="margin-top:16px;">
    <div class="card" style="padding:16px;">
      <h3>Welcome</h3>
      <div id="dashUser" class="muted">Signed out</div>
    </div>
    <div class="card" style="padding:16px;">
      <h3>Usage</h3>
      <div id="usageBox" class="muted">Loading…</div>
      <div class="badge" id="usageBadge" style="margin-top:8px;">—</div>
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
  function getU(){ try { return JSON.parse(localStorage.getItem('finm_user')||'null'); } catch(e){ return null; } }
  function getUsage(){ try { return JSON.parse(localStorage.getItem('finm_usage')||'null'); } catch(e){ return null; } }
  function setUsage(u){ localStorage.setItem('finm_usage', JSON.stringify(u)); }
  async function loadNews(){
    const el = $('#dashNews');
    try{
      if(window.finmApi && (window.finmConfig?.hasApiBase)){
        let items = await window.finmApi.wpNews({ limit: 5 });
        if(!Array.isArray(items) || !items.length){ const n2 = await window.finmApi.apiGet('news/', { limit: 5 }); items = Array.isArray(n2)?n2:(n2?.data||[]); }
        el.innerHTML = (items||[]).slice(0,5).map(n=>`<div class="muted">${n.source||n.publisher||''} — ${n.title||n.headline||''}</div>`).join('');
        return;
      }
    }catch(e){}
    const news = (window.MockData?.news)||[]; el.innerHTML = news.slice(0,3).map(n=>`<div class="muted">${n.source} — ${n.title}</div>`).join('');
  }
  document.addEventListener('DOMContentLoaded', function(){
    const u = getU();
    if(!u){ window.location.href = '/'; return; }
    $('#dashUser').textContent = `Hello, ${u.name || u.email || 'User'}`;

    let usage = getUsage();
    if(!usage){ usage = { limit: 1000, used: 0, month: new Date().toISOString().slice(0,7) }; setUsage(usage); }
    const nowMonth = new Date().toISOString().slice(0,7);
    if(usage.month !== nowMonth){ usage = { limit: usage.limit, used: 0, month: nowMonth }; setUsage(usage); }
    const left = Math.max(usage.limit - usage.used, 0);
    $('#usageBox').textContent = `Monthly limit: ${usage.limit} • Used: ${usage.used} • Left: ${left}`;
    $('#usageBadge').textContent = left > 0 ? `You have ${left} actions left` : 'Limit reached';

    loadNews();
  });
})();
</script>
<?php get_footer(); ?>