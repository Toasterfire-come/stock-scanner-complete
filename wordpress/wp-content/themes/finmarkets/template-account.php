<?php /* Template Name: Account */ if (!defined('ABSPATH')) { exit; } $finm_requires_auth = true; $finm_requires_api = true; get_header(); ?>
<section class="section">
  <div class="container content" style="max-width:720px;">
    <h1 style="color:var(--navy);">Account</h1>
    <div class="card" style="padding:16px;">
      <div id="accStatus" class="muted">Checking session…</div>
      <div id="accInfo" class="grid cols-2" style="margin-top:12px;"></div>
      <div style="margin-top:12px; display:flex; gap:8px; flex-wrap:wrap;">
        <button id="accSignOut" class="btn">Sign out</button>
        <a class="btn btn-primary" href="/premium-plans/">Upgrade</a>
      </div>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  function showProfile(p){
    $('#accStatus').textContent = 'Signed in';
    $('#accInfo').innerHTML = `
      <div class="card" style="padding:12px;"><div class="muted">Username</div><strong>${p.username||'-'}</strong></div>
      <div class="card" style="padding:12px;"><div class="muted">Email</div><strong>${p.email||'-'}</strong></div>`;
  }
  document.addEventListener('DOMContentLoaded', async function(){
    try{
      if(window.finmApi && (window.finmConfig?.hasApiBase)){
        const j = await window.finmApi.userProfileGet();
        if(j && j.success !== false){ showProfile(j.data||{}); }
        else { $('#accStatus').textContent = 'Not signed in'; }
      } else {
        const u = JSON.parse(localStorage.getItem('finm_user')||'null');
        if(!u){ window.location.href='/'; return; }
        showProfile({ username: u.name||'', email: u.email||'' });
      }
    }catch(e){ $('#accStatus').textContent = 'Not signed in'; }

    $('#accSignOut').addEventListener('click', async function(){
      try{ if(window.finmApi && (window.finmConfig?.hasApiBase)) { await window.finmApi.authLogout(); } }catch(e){}
      localStorage.removeItem('finm_user'); location.href='/';
    });
  });
})();
</script>
<?php get_footer(); ?>