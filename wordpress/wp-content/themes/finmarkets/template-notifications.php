<?php /* Template Name: Notifications */ if (!defined('ABSPATH')) { exit; } $finm_requires_auth = true; $finm_requires_api = true; get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Notifications</h1>
      <p class="muted">Your latest alerts and updates.</p>
    </div>
    <div class="card" style="padding:16px;">
      <div class="toolbar" style="margin-bottom:8px;">
        <button id="nReload" class="btn">Reload</button>
        <button id="nMarkAll" class="btn">Mark all read</button>
        <span id="notifSummary" class="muted">Loading…</span>
      </div>
      <ul id="notifList" style="list-style:none; padding:0; margin:12px 0 0;"></ul>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  async function load(page=1, limit=20){
    try{
      const j = await window.finmApi.notificationsHistory({ page, limit });
      const items = (j?.data)||[]; const unread = (j?.summary?.total_unread) ?? items.filter(x=>!x.is_read).length;
      $('#notifSummary').textContent = `${unread} unread • ${items.length} loaded`;
      $('#notifList').innerHTML = items.map(n=>`<li class="card" style="padding:12px; margin:8px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div><strong>${n.title||'-'}</strong><div class="muted">${n.message||''}</div></div>
          <button class="btn" data-id="${n.id}">${n.is_read?'Read':'Mark read'}</button>
        </div>
      </li>`).join('') || '<li class="muted">No notifications.</li>';
    }catch(e){ $('#notifSummary').textContent = 'Failed to load'; }
  }
  async function mark(ids, all=false){ try{ await window.finmApi.notificationsMarkRead(ids, all); await load(); }catch(e){} }
  document.addEventListener('DOMContentLoaded', function(){
    load();
    $('#nReload').addEventListener('click', ()=>load());
    $('#nMarkAll').addEventListener('click', ()=>mark([], true));
    $('#notifList').addEventListener('click', (e)=>{ const b=e.target.closest('button[data-id]'); if(!b) return; const id=+b.dataset.id; mark([id], false); });
  });
})();
</script>
<?php get_footer(); ?>