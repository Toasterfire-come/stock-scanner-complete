<?php /* Template Name: Notifications */ get_header(); ?>
<section class="section"><div class="container">
  <h1>Notifications</h1>
  <div class="card" style="padding:16px;">
    <table class="table" id="rts-notify"><thead><tr><th>Title</th><th>Type</th><th>Created</th><th>Read</th><th></th></tr></thead><tbody><tr><td colspan="5" style="text-align:center;color:#6b7280;">Loading…</td></tr></tbody></table>
  </div>
</div></section>
<script>
(function($){
  const tbody = document.getElementById('rts-notify').querySelector('tbody');
  function load(){
    fetch(RTS.rest.endpoints.notifications_history + '?page=1&limit=20', { headers: { 'X-WP-Nonce': RTS.rest.nonce } })
      .then(r=>r.json()).then(d=>{
        const list = d.data || [];
        if(!list.length){ tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#6b7280;">No notifications</td></tr>'; return; }
        tbody.innerHTML = list.map(n=> `<tr><td><strong>${n.title}</strong></td><td>${n.type}</td><td>${new Date(n.created_at).toLocaleString?.()}</td><td>${n.is_read?'Yes':'No'}</td><td><button class=\"btn btn-outline\" data-id=\"${n.id}\">Mark read</button></td></tr>`).join('');
        tbody.querySelectorAll('button').forEach(btn=> btn.addEventListener('click', function(){
          const id = this.getAttribute('data-id');
          fetch(RTS.rest.endpoints.notifications_mark_read, { method:'POST', headers:{'Content-Type':'application/json','X-WP-Nonce': RTS.rest.nonce}, body: JSON.stringify({ notification_ids:[Number(id)] }) })
            .then(()=> load());
        }));
      }).catch(()=> tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#b91c1c;">Failed to load</td></tr>');
  }
  load();
})(jQuery);
</script>
<?php get_footer(); ?>