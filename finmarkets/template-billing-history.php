<?php /* Template Name: Billing History */ if (!defined('ABSPATH')) { exit; } $finm_requires_auth = true; get_header(); ?>
<section class="section">
  <div class="container content">
    <h1 style="color:var(--navy);">Billing History</h1>
    <div class="card" style="padding:16px;">
      <div id="bhStatus" class="muted">Loading…</div>
      <table class="table" style="margin-top:12px;">
        <thead><tr><th>Date</th><th>Description</th><th>Amount</th><th>Status</th><th>Method</th></tr></thead>
        <tbody id="bhBody"></tbody>
      </table>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  function renderRows(items){
    return (items||[]).map(i=>`<tr>
      <td>${i.date||i.created_at||'-'}</td>
      <td>${i.description||i.plan_name||'—'}</td>
      <td>${(i.amount!=null?('$'+Number(i.amount).toFixed(2)):'—')}</td>
      <td>${i.status||'—'}</td>
      <td>${i.method||'—'}</td>
    </tr>`).join('') || '<tr><td colspan="5" class="muted">No records</td></tr>';
  }
  document.addEventListener('DOMContentLoaded', async function(){
    try{
      if(window.finmApi && (window.finmConfig?.hasApiBase)){
        const j = await window.finmApi.billingHistory(1, 20);
        const items = (j?.data)||[];
        $('#bhStatus').textContent = j?.success===false ? (j?.message||'Failed to load') : `Loaded ${items.length}`;
        $('#bhBody').innerHTML = renderRows(items);
        return;
      }
    }catch(e){ $('#bhStatus').textContent='Failed to load'; }
    // Fallback
    $('#bhStatus').textContent = 'Showing demo data';
    $('#bhBody').innerHTML = renderRows([
      { date:'2025-08-01', description:'Pro', amount:19, status:'Paid', method:'PayPal' },
      { date:'2025-07-01', description:'Pro', amount:19, status:'Paid', method:'PayPal' }
    ]);
  });
})();
</script>
<?php get_footer(); ?>