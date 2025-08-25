<?php /* Template Name: Newsletter Signup */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content" style="max-width:520px;">
    <h1 style="color:var(--navy);">Newsletter</h1>
    <div class="card" style="padding:20px;">
      <form id="nlForm" onsubmit="return false;">
        <input id="nlEmail" class="input" type="email" placeholder="Email" required />
        <button id="nlBtn" class="btn btn-primary" style="margin-left:8px;">Subscribe</button>
        <div id="nlMsg" class="muted" style="margin-top:8px;">&nbsp;</div>
      </form>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $=s=>document.querySelector(s);
  function setMsg(t,ok){ const el=$('#nlMsg'); el.textContent=t; el.style.color=ok?'#0f8a42':'var(--muted)'; }
  document.addEventListener('DOMContentLoaded', function(){
    $('#nlBtn').addEventListener('click', async ()=>{
      const email=$('#nlEmail').value.trim(); if(!email) return setMsg('Please enter a valid email');
      try{
        if(window.finmApi && (window.finmConfig?.hasApiBase)){
          // Try WordPress-specific endpoint first, else generic subscription
          try{ await window.finmApi.subscribeWordPress({ email }); setMsg('Subscribed!', true); return; }catch(e){}
          await window.finmApi.subscription({ email }); setMsg('Subscribed!', true); return;
        }
        setMsg('Subscribed (demo)', true);
      }catch(e){ setMsg('Failed to subscribe'); }
    });
  });
})();
</script>
<?php get_footer(); ?>