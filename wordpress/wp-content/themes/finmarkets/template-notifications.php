<?php /* Template Name: Notifications */ if (!defined('ABSPATH')) { exit; } $finm_requires_auth = true; get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Notifications</h1>
      <p class="muted">Your latest alerts and updates.</p>
    </div>
    <div class="card" style="padding:16px;">
      <div id="notifSummary" class="muted">Loading…</div>
      <ul id="notifList" style="list-style:none; padding:0; margin:12px 0 0;"></ul>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  function getU(){ try { return JSON.parse(localStorage.getItem('finm_user')||'null'); } catch(e){ return null; } }
  const storeKey = 'finm_notifications';
  function getN(){ try{ return JSON.parse(localStorage.getItem(storeKey)||'[]'); }catch(e){ return []; } }
  function setN(v){ localStorage.setItem(storeKey, JSON.stringify(v)); }
  document.addEventListener('DOMContentLoaded', async function(){
    if(!getU()){ window.location.href='/'; return; }
    // seed demo
    if(!getN().length){ setN([
      { id:1, title:'Welcome to FinMarkets', message:'Your account was created successfully.', type:'info', is_read:false, created_at:new Date().toISOString() },
      { id:2, title:'Pro tip', message:'Use filters in Screener to find high-momentum stocks quickly.', type:'tip', is_read:false, created_at:new Date().toISOString() }
    ]); }
    const data = getN();
    $('#notifSummary').textContent = `${data.filter(x=>!x.is_read).length} unread • ${data.length} total`;
    $('#notifList').innerHTML = data.map(n=>`<li class="card" style="padding:12px; margin:8px 0;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div><strong>${n.title}</strong><div class="muted">${n.message}</div></div>
        <button class="btn" data-id="${n.id}">${n.is_read?'Read':'Mark read'}</button>
      </div>
    </li>`).join('');
    $('#notifList').addEventListener('click', (e)=>{
      const b=e.target.closest('button[data-id]'); if(!b) return; const id=+b.dataset.id; const arr=getN(); const it=arr.find(x=>x.id===id); if(it){ it.is_read=true; setN(arr); location.reload(); }
    });
  });
})();
</script>
<?php get_footer(); ?>