<?php /* Template Name: Endpoint Status */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">API Endpoint Status</h1>
      <p class="muted">Live check via theme proxy (/wp-json/finm/v1/endpoint-status).</p>
    </div>
    <div class="card" style="padding:16px;">
      <div id="epSummary" class="muted">Loading…</div>
      <table class="table" style="margin-top:12px;">
        <thead><tr><th>Name</th><th>URL</th><th>Status</th><th>Code</th><th>Time (ms)</th></tr></thead>
        <tbody id="epBody"></tbody>
      </table>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  document.addEventListener('DOMContentLoaded', async function(){
    try{
      const r = await (window.finmApi ? window.finmApi.endpointStatus() : fetch((window.finmConfig?.restBase||'/wp-json/finm/v1').replace(/\/$/,'') + '/endpoint-status').then(x=>x.json()));
      const d = r.data || {};
      $('#epSummary').textContent = `Tested ${d.total_tested||0} • Successful ${d.successful||0} • Failed ${d.failed||0}`;
      const rows = (d.endpoints||[]).map(x=>`<tr><td>${x.name}</td><td class="mono">${x.url}</td><td>${x.status}</td><td>${x.status_code||''}</td><td>${x.response_time||''}</td></tr>`).join('');
      $('#epBody').innerHTML = rows || '<tr><td colspan="5" class="muted">No data.</td></tr>';
    }catch(e){ $('#epSummary').textContent = 'Failed to load status.'; }
  });
})();
</script>
<?php get_footer(); ?>