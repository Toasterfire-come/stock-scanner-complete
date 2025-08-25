<?php /* Template Name: User Settings */ if (!defined('ABSPATH')) { exit; } $finm_requires_auth = true; get_header(); ?>
<section class="section">
  <div class="container content" style="max-width:720px;">
    <h1 style="color:var(--navy);">User Settings</h1>
    <div class="card" style="padding:16px;">
      <form id="usForm" class="grid cols-2" onsubmit="return false;">
        <div>
          <label for="usName" class="muted">Display name</label>
          <input id="usName" class="input" placeholder="Your name" />
        </div>
        <div>
          <label for="usTheme" class="muted">Theme</label>
          <select id="usTheme" class="select"><option value="light">Light</option><option value="dark">Dark</option></select>
        </div>
        <div class="col-span-2">
          <h3 style="margin:12px 0 4px;">Notifications</h3>
          <div class="grid cols-2">
            <label><input type="checkbox" id="nTrading" /> Trading alerts</label>
            <label><input type="checkbox" id="nPortfolio" /> Portfolio summary</label>
            <label><input type="checkbox" id="nNews" /> Market news</label>
            <label><input type="checkbox" id="nSecurity" /> Security updates</label>
          </div>
        </div>
        <div>
          <button id="usSave" class="btn btn-primary">Save</button>
          <span id="usMsg" class="muted" style="margin-left:8px;"></span>
        </div>
      </form>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  const setMsg = (t, ok)=>{ const el=$('#usMsg'); el.textContent=t; el.style.color = ok? '#0f8a42':'var(--muted)'; };
  function getU(){ try {return JSON.parse(localStorage.getItem('finm_user')||'{}');}catch(e){return {};}}
  document.addEventListener('DOMContentLoaded', async function(){
    // Load profile + notification settings
    try{
      if(window.finmApi && (window.finmConfig?.hasApiBase)){
        try{ const prof = await window.finmApi.userProfileGet(); $('#usName').value = prof?.data?.first_name || prof?.data?.username || ''; }catch(e){}
        try{ const ns = await window.finmApi.notificationsSettingsGet(); const d=ns?.data||{}; $('#nTrading').checked=!!(d.trading?.price_alerts||d.trading); $('#nPortfolio').checked=!!(d.portfolio?.daily_summary||d.portfolio); $('#nNews').checked=!!(d.news?.breaking_news||d.news); $('#nSecurity').checked=!!(d.security?.login_alerts||d.security); }catch(e){}
      } else {
        const u=getU(); $('#usName').value = u.name||'';
      }
      $('#usTheme').value = (localStorage.getItem('finm_theme')||'light');
    }catch(e){}

    $('#usSave').addEventListener('click', async ()=>{
      try{
        localStorage.setItem('finm_theme', $('#usTheme').value);
        if(window.finmApi && (window.finmConfig?.hasApiBase)){
          const name=$('#usName').value.trim(); if(name){ await window.finmApi.userProfileUpdate({ first_name: name }); }
          const payload={
            trading: { price_alerts: $('#nTrading').checked, volume_alerts: false, market_hours: false },
            portfolio: { daily_summary: $('#nPortfolio').checked, weekly_report: false, milestone_alerts: false },
            news: { breaking_news: $('#nNews').checked, earnings_alerts: false, analyst_ratings: false },
            security: { login_alerts: $('#nSecurity').checked, billing_updates: true, plan_updates: true }
          };
          await window.finmApi.notificationsSettingsUpdate(payload);
        } else {
          const u=getU(); u.name=$('#usName').value.trim(); localStorage.setItem('finm_user', JSON.stringify(u));
        }
        setMsg('Saved', true);
      }catch(e){ setMsg('Save failed'); }
    });
  });
})();
</script>
<?php get_footer(); ?>