(function(){
  const $ = s => document.querySelector(s);
  const state = { amount: null, code: '', currency: 'USD', brand: 'FinMarkets Pro' };

  async function loadConfig(){
    const r = await fetch((window.finmConfig?.restBase||'/wp-json/finm/v1').replace(/\/$/,'') + '/paypal-config');
    const j = await r.json();
    state.amount = parseFloat(j.amount_pro||'19') || 19;
    state.currency = j.currency || 'USD';
    state.brand = j.brand || 'FinMarkets Pro';
    return j;
  }

  function injectSdk(clientId, currency, intent){
    return new Promise((resolve, reject)=>{
      if(document.getElementById('pp-sdk')) return resolve();
      const s = document.createElement('script');
      s.id = 'pp-sdk';
      s.src = `https://www.paypal.com/sdk/js?client-id=${encodeURIComponent(clientId)}&currency=${encodeURIComponent(currency)}&intent=${intent||'capture'}&disable-funding=card,credit`;
      s.onload = resolve; s.onerror = reject; document.head.appendChild(s);
    });
  }

  async function validateDiscount(){
    const code = ($('#ppCode')?.value||'').trim();
    state.code = code;
    if(!code) return { valid:false, final: state.amount };
    try{
      const res = await (window.finmApi ? window.finmApi.revenueValidate(code) : Promise.reject('no api'));
      if(res && res.valid){
        const app = await (window.finmApi ? window.finmApi.revenueApply(code, state.amount) : Promise.reject('no api'));
        const finalAmt = (app && app.final_amount != null) ? parseFloat(app.final_amount) : state.amount;
        return { valid:true, final: finalAmt };
      }
    }catch(e){}
    return { valid:false, final: state.amount };
  }

  function renderSummary(amount){
    const el = $('#ppSummary'); if(!el) return;
    el.innerHTML = `<div style="display:flex; justify-content:space-between"><strong>Total</strong><span>${state.currency} ${amount.toFixed(2)}</span></div>`;
  }

  async function init(){
    const conf = await loadConfig();
    const clientId = conf.client_id;
    if(!clientId){ $('#ppStatus').textContent = 'PayPal not configured. Add Client ID in FinMarkets Settings.'; return; }
    renderSummary(state.amount);

    $('#ppApply')?.addEventListener('click', async ()=>{
      $('#ppStatus').textContent = 'Checking code…';
      const r = await validateDiscount();
      renderSummary(r.final); state.amount = r.final; $('#ppStatus').textContent = r.valid ? 'Discount applied' : 'Invalid code';
    });

    await injectSdk(clientId, state.currency, 'capture');
    if(!window.paypal){ $('#ppStatus').textContent='PayPal SDK failed to load.'; return; }

    window.paypal.Buttons({
      style: { layout:'vertical', color:'blue', shape:'pill', label:'subscribe' },
      createOrder: (data, actions) => {
        return actions.order.create({
          purchase_units: [{
            amount: { currency_code: state.currency, value: state.amount.toFixed(2) },
            description: state.brand
          }], application_context: { brand_name: state.brand }
        });
      },
      onApprove: async (data, actions) => {
        const details = await actions.order.capture();
        $('#ppStatus').textContent = 'Payment captured: ' + (details?.id || '');
        try{
          const payload = { user_id: 0, amount: state.amount, discount_code: state.code||null, payment_date: new Date().toISOString() };
          await (window.finmApi ? window.finmApi.revenuePost('record-payment/', payload) : Promise.resolve());
        }catch(e){ console.warn('Revenue record failed', e); }
        window.location.href = (document.getElementById('ppSuccessUrl')?.value || '/');
      },
      onError: (err) => { $('#ppStatus').textContent = 'Payment error. Try again.'; console.error(err); }
    }).render('#paypal-buttons');
  }

  document.addEventListener('DOMContentLoaded', init);
})();