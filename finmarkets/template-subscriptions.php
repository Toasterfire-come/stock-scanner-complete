<?php /* Template Name: Subscriptions */ if (!defined('ABSPATH')) { exit; } $finm_requires_auth = true; $finm_requires_api = true; get_header(); ?>
<section class="section">
  <div class="container content" style="max-width:720px;">
    <h1 style="color:var(--navy);">Subscriptions</h1>
    <div class="card" style="padding:16px;">
      <div id="subStatus" class="muted">Loading…</div>
      <div id="subDetails" style="margin-top:12px;"></div>
      <form id="planForm" class="toolbar" onsubmit="return false;" style="margin-top:12px;">
        <select id="planType" class="select">
          <option value="free">Free</option>
          <option value="basic">Basic</option>
          <option value="pro">Pro</option>
          <option value="enterprise">Enterprise</option>
        </select>
        <select id="billingCycle" class="select">
          <option value="monthly">Monthly</option>
          <option value="annual">Annual</option>
        </select>
        <button id="planSave" class="btn btn-primary">Change Plan</button>
        <span id="planMsg" class="muted"></span>
      </form>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $=s=>document.querySelector(s);
  const setMsg=(t,ok)=>{ const el=$('#planMsg'); el.textContent=t; el.style.color=ok?'#0f8a42':'var(--muted)'; };
  async function load(){
    try{
      const j = await window.finmApi.billingCurrentPlan();
      const d = j?.data || {};
      $('#subStatus').textContent = j?.success===false ? (j?.message||'Failed to load') : 'Loaded';
      $('#subDetails').innerHTML = `<div class="grid cols-2"><div class="card" style="padding:12px;"><div class="muted">Plan</div><strong>${d.plan_name||'-'}</strong></div><div class="card" style="padding:12px;"><div class="muted">Billing</div><strong>${d.billing_cycle||'-'}</strong></div><div class="card" style="padding:12px;"><div class="muted">Premium</div><strong>${d.is_premium?'Yes':'No'}</strong></div><div class="card" style="padding:12px;"><div class="muted">Next billing date</div><strong>${d.next_billing_date||'-'}</strong></div></div>`;
      $('#planType').value = d.plan_type || 'free';
      $('#billingCycle').value = d.billing_cycle || 'monthly';
    }catch(e){ $('#subStatus').textContent = 'Failed to load'; }
  }
  async function save(){
    try{
      const plan_type=$('#planType').value; const billing_cycle=$('#billingCycle').value;
      const j = await window.finmApi.billingChangePlan(plan_type, billing_cycle);
      if(j && j.success!==false){ setMsg('Plan updated', true); await load(); }
      else { setMsg(j?.message||'Update failed'); }
    }catch(e){ setMsg('Update failed'); }
  }
  document.addEventListener('DOMContentLoaded', function(){
    load();
    $('#planSave').addEventListener('click', save);
  });
})();
</script>
<?php get_footer(); ?>