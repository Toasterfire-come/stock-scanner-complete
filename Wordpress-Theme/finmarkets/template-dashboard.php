<?php /* Template Name: Dashboard */ if (!defined('ABSPATH')) { exit; } $finm_requires_auth = true; get_header(); ?>
<section class="section" data-page="dashboard">
  <div class="container grid cols-3">
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
  document.addEventListener('DOMContentLoaded', function(){
    const u = getU();
    if(!u){ window.location.href = '/'; return; }
    $('#dashUser').textContent = `Hello, ${u.name || u.email || 'User'}`;

    // Initialize usage if absent
    let usage = getUsage();
    if(!usage){ usage = { limit: 1000, used: 0, month: new Date().toISOString().slice(0,7) }; setUsage(usage); }
    const nowMonth = new Date().toISOString().slice(0,7);
    if(usage.month !== nowMonth){ usage = { limit: usage.limit, used: 0, month: nowMonth }; setUsage(usage); }
    const left = Math.max(usage.limit - usage.used, 0);
    $('#usageBox').textContent = `Monthly limit: ${usage.limit} • Used: ${usage.used} • Left: ${left}`;
    $('#usageBadge').textContent = left > 0 ? `You have ${left} actions left` : 'Limit reached';

    // News
    try{
      const news = (window.MockData?.news)||[]; // or finmApi.wpNews
      $('#dashNews').innerHTML = news.slice(0,3).map(n=>`<div class="muted">${n.source} — ${n.title}</div>`).join('');
    }catch(e){ $('#dashNews').textContent = '—'; }
  });
})();
</script>
<?php get_footer(); ?>