<?php
/*
Template Name: Billing History (v3)
Description: Billing history with exports (frontend-only demo)
*/
get_header(); ?>
<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php _e('Billing History', 'stock-scanner'); ?></h1>
      <p class="section-subtitle"><?php _e('View and download your subscription invoices and payment history', 'stock-scanner'); ?></p>
    </header>

    <div class="features-grid">
      <div class="card glass-card"><div class="card-body"><h3><?php _e('Total Spent', 'stock-scanner'); ?></h3><div class="section-title" id="total-spent" style="font-size:1.5rem;color:var(--color-success)">$239.88</div></div></div>
      <div class="card glass-card"><div class="card-body"><h3><?php _e('Total Invoices', 'stock-scanner'); ?></h3><div class="section-title" id="total-invoices" style="font-size:1.5rem;color:var(--color-info)">6</div></div></div>
      <div class="card glass-card"><div class="card-body"><h3><?php _e('Next Payment', 'stock-scanner'); ?></h3><div class="section-title" id="next-payment" style="font-size:1.5rem;color:var(--color-primary)">Feb 15</div></div></div>
    </div>

    <div class="card glass-card" style="margin-top:1rem"><div class="card-body">
      <div style="display:flex;gap:1rem;flex-wrap:wrap;justify-content:space-between;align-items:end">
        <div style="display:flex;gap:1rem;flex-wrap:wrap">
          <div><label class="form-label" for="year-filter"><?php _e('Year', 'stock-scanner'); ?></label><select id="year-filter" class="form-control"><option value=""><?php _e('All Years', 'stock-scanner'); ?></option><option value="2024" selected>2024</option><option value="2023">2023</option></select></div>
          <div><label class="form-label" for="status-filter"><?php _e('Status', 'stock-scanner'); ?></label><select id="status-filter" class="form-control"><option value=""><?php _e('All Status', 'stock-scanner'); ?></option><option value="paid"><?php _e('Paid', 'stock-scanner'); ?></option><option value="pending"><?php _e('Pending', 'stock-scanner'); ?></option><option value="failed"><?php _e('Failed', 'stock-scanner'); ?></option></select></div>
        </div>
        <div style="display:flex;gap:.5rem;flex-wrap:wrap">
          <button onclick="exportBillingHistory('csv')" class="btn btn-secondary">Export CSV</button>
          <button onclick="exportBillingHistory('pdf')" class="btn btn-primary">Export PDF</button>
        </div>
      </div>
    </div></div>

    <div class="card glass-card" style="margin-top:1rem"><div class="card-body">
      <div class="table-responsive">
        <table class="w-full" id="billing-table" data-sortable>
          <thead>
            <tr>
              <th><?php _e('Invoice #', 'stock-scanner'); ?></th>
              <th><?php _e('Date', 'stock-scanner'); ?></th>
              <th><?php _e('Description', 'stock-scanner'); ?></th>
              <th><?php _e('Amount', 'stock-scanner'); ?></th>
              <th><?php _e('Status', 'stock-scanner'); ?></th>
              <th><?php _e('Actions', 'stock-scanner'); ?></th>
            </tr>
          </thead>
          <tbody id="billing-tbody">
            <tr>
              <td class="font-mono">#INV-2024-001</td>
              <td>Jan 15, 2024</td>
              <td>Silver Plan - Monthly Subscription</td>
              <td>$39.99</td>
              <td><span class="badge badge-primary">Paid</span></td>
              <td><div style="display:flex;gap:.5rem"><button onclick="viewInvoice('INV-2024-001')" class="btn btn-outline btn-sm"><?php _e('View', 'stock-scanner'); ?></button><button onclick="downloadInvoice('INV-2024-001')" class="btn btn-outline btn-sm"><?php _e('Download', 'stock-scanner'); ?></button></div></td>
            </tr>
            <tr>
              <td class="font-mono">#INV-2023-012</td>
              <td>Dec 15, 2023</td>
              <td>Silver Plan - Monthly Subscription</td>
              <td>$39.99</td>
              <td><span class="badge badge-primary">Paid</span></td>
              <td><div style="display:flex;gap:.5rem"><button onclick="viewInvoice('INV-2023-012')" class="btn btn-outline btn-sm"><?php _e('View', 'stock-scanner'); ?></button><button onclick="downloadInvoice('INV-2023-012')" class="btn btn-outline btn-sm"><?php _e('Download', 'stock-scanner'); ?></button></div></td>
            </tr>
            <tr>
              <td class="font-mono">#INV-2023-011</td>
              <td>Nov 15, 2023</td>
              <td>Bronze Plan - Monthly Subscription</td>
              <td>$24.99</td>
              <td><span class="badge badge-primary">Paid</span></td>
              <td><div style="display:flex;gap:.5rem"><button onclick="viewInvoice('INV-2023-011')" class="btn btn-outline btn-sm"><?php _e('View', 'stock-scanner'); ?></button><button onclick="downloadInvoice('INV-2023-011')" class="btn btn-outline btn-sm"><?php _e('Download', 'stock-scanner'); ?></button></div></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div></div>

    <!-- Invoice Modal -->
    <div id="invoice-modal" class="modal-overlay" aria-hidden="true"><div class="modal-panel"><div class="modal-header"><h3><?php _e('Invoice Details','stock-scanner'); ?></h3><button class="btn btn-outline btn-sm" data-close-modal>×</button></div><div class="modal-body" id="invoice-content"></div><div class="modal-footer"><button onclick="downloadCurrentInvoice()" class="btn btn-primary"><?php _e('Download PDF', 'stock-scanner'); ?></button><button class="btn btn-secondary" data-close-modal><?php _e('Close','stock-scanner'); ?></button></div></div></div>
  </div>
</section>

<script>
class BillingHistoryManager { constructor(){ this.currentInvoice=null; document.getElementById('year-filter').addEventListener('change',()=>this.filterBilling()); document.getElementById('status-filter').addEventListener('change',()=>this.filterBilling()); }
  filterBilling(){ const y=document.getElementById('year-filter').value; const s=document.getElementById('status-filter').value; document.querySelectorAll('#billing-tbody tr').forEach(row=>{ let show=true; if(y && !row.cells[1].textContent.includes(y)) show=false; if(s){ const status=row.querySelector('.badge')?.textContent.toLowerCase(); if(status!==s) show=false; } row.style.display=show?'':'none'; }); }
}
const billingManager = new BillingHistoryManager();
function exportBillingHistory(fmt){ const data=getBillingData(); if(fmt==='csv') exportToCSV(data); else if(fmt==='pdf') exportToPDF(data); }
function getBillingData(){ return [ {invoice:'INV-2024-001',date:'2024-01-15',description:'Silver Plan - Monthly Subscription',amount:'$39.99',status:'Paid'}, {invoice:'INV-2023-012',date:'2023-12-15',description:'Silver Plan - Monthly Subscription',amount:'$39.99',status:'Paid'}, {invoice:'INV-2023-011',date:'2023-11-15',description:'Bronze Plan - Monthly Subscription',amount:'$24.99',status:'Paid'} ]; }
function exportToCSV(data){ const headers=['Invoice','Date','Description','Amount','Status']; const csv=[headers.join(','), ...data.map(r=>[r.invoice,r.date,'"'+r.description+'"',r.amount,r.status].join(','))].join('\n'); downloadFile(csv,'billing-history.csv','text/csv'); }
function exportToPDF(data){ const pdf=`Billing History Report\nGenerated: ${new Date().toLocaleDateString()}\n\n${data.map(r=>`${r.invoice} | ${r.date} | ${r.description} | ${r.amount} | ${r.status}`).join('\n')}`; downloadFile(pdf,'billing-history.pdf','application/pdf'); }
function downloadFile(content, name, type){ const blob=new Blob([content],{type}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download=name; document.body.appendChild(a); a.click(); URL.revokeObjectURL(url); a.remove(); }
function viewInvoice(id){ const m=document.getElementById('invoice-modal'); const c=document.getElementById('invoice-content'); c.innerHTML=generateInvoiceHTML(id); m.classList.add('show'); m.setAttribute('aria-hidden','false'); billingManager.currentInvoice=id; }
function generateInvoiceHTML(id){ return `<div class="invoice-document"><div class="invoice-header" style="margin-bottom:1rem"><div style="display:flex;justify-content:space-between"><div><h2>INVOICE</h2><p>${id}</p></div><div style="text-align:right"><p><strong>Stock Scanner Pro</strong></p><p>support@stockscanner.com</p></div></div></div><table style="width:100%;margin-top:1rem"><thead><tr><th>Description</th><th style="text-align:right">Amount</th></tr></thead><tbody><tr><td>Silver Plan - Monthly Subscription</td><td style="text-align:right">$39.99</td></tr></tbody><tfoot><tr><td>Total</td><td style="text-align:right">$39.99</td></tr></tfoot></table><p style="margin-top:1rem;color:var(--color-text-muted)">Thank you for your business!</p></div>`; }
function downloadInvoice(id){ const t=`INVOICE ${id}\nDate: Jan 15, 2024\nAmount: $39.99\nDescription: Silver Plan - Monthly Subscription\nStatus: Paid`; downloadFile(t,`invoice-${id}.txt`,'text/plain'); }
function downloadCurrentInvoice(){ if(billingManager.currentInvoice) downloadInvoice(billingManager.currentInvoice); }
// modal close handler
(document.getElementById('invoice-modal')).addEventListener('click',function(e){ if(e.target===this || e.target.matches('[data-close-modal]')){ this.classList.remove('show'); this.setAttribute('aria-hidden','true'); billingManager.currentInvoice=null; } });
</script>

<?php get_footer(); ?>