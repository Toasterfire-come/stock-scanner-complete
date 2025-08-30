<?php
/**
 * Template Name: PayPal Checkout (RTS)
 */
if (!defined('ABSPATH')) { exit; }
if (!is_user_logged_in()) { wp_safe_redirect(wp_login_url(get_permalink())); exit; }

$selected_plan = isset($_GET['plan']) ? sanitize_text_field($_GET['plan']) : 'bronze';
$billing_cycle = isset($_GET['billing']) ? sanitize_text_field($_GET['billing']) : 'monthly';
$valid_plans = array('bronze','silver','gold');
if (!in_array($selected_plan, $valid_plans, true)) { $selected_plan = 'bronze'; }
$valid_cycles = array('monthly','annual');
if (!in_array($billing_cycle, $valid_cycles, true)) { $billing_cycle = 'monthly'; }

$plans = array(
  'bronze' => array('name'=>'Bronze','monthly'=>24.99,'annual'=>249.99,'features'=>array('1,500 Monthly API Calls','5 Portfolios','50 Stocks per Watchlist','25 Price Alerts','Email Support','15-min Delayed Data')),
  'silver' => array('name'=>'Silver','monthly'=>39.99,'annual'=>399.99,'features'=>array('5,000 Monthly API Calls','Unlimited Portfolios','200 Stocks per Watchlist','100 Price Alerts','Real-time Data','Email + Chat Support','REST API Access')),
  'gold'   => array('name'=>'Gold','monthly'=>89.99,'annual'=>899.99,'features'=>array('Unlimited API Calls','Unlimited Everything','Priority Support','Real-time Data','Global Markets','REST + WebSocket API','White Label Option')),
);
$current_plan = $plans[$selected_plan];
$price = $current_plan[$billing_cycle];
$annual_savings = $billing_cycle === 'annual' ? ($current_plan['monthly'] * 12 - $current_plan['annual']) : 0;

$paypal_client_id = get_option('paypal_client_id', '');

get_header();
?>

<main class="container mx-auto px-4 py-10">
  <header class="text-center mb-8">
    <h1 class="text-3xl font-semibold">Complete Your Upgrade</h1>
    <p class="text-muted-foreground">Secure payment processing with PayPal</p>
  </header>

  <div class="grid gap-8 md:grid-cols-2">
    <section class="bg-white border rounded-xl p-6">
      <h2 class="text-xl font-semibold mb-4">Order Summary</h2>
      <div class="bg-muted/30 border-l-4 border-blue-600 rounded p-4 mb-4">
        <div class="text-sm uppercase tracking-wide font-semibold mb-1 <?php echo esc_attr($selected_plan); ?>"><?php echo esc_html($current_plan['name']); ?> Plan</div>
        <div class="flex items-end justify-between gap-3">
          <div class="flex items-end gap-2">
            <span class="text-3xl font-bold">$<?php echo number_format($price, 2); ?></span>
            <span class="text-muted-foreground text-sm">/<?php echo $billing_cycle === 'annual' ? 'year' : 'month'; ?></span>
          </div>
          <?php if ($annual_savings > 0): ?>
          <span class="inline-flex items-center px-2 py-1 rounded-full bg-green-600 text-white text-xs font-semibold">Save $<?php echo number_format($annual_savings, 2); ?></span>
          <?php endif; ?>
        </div>
      </div>

      <div class="mb-6">
        <h3 class="font-semibold mb-2">What's Included</h3>
        <ul class="space-y-1 text-sm">
          <?php foreach ($current_plan['features'] as $feature): ?>
          <li class="flex items-center gap-2"><span class="text-green-600">✓</span> <span><?php echo esc_html($feature); ?></span></li>
          <?php endforeach; ?>
        </ul>
      </div>

      <div>
        <h3 class="font-semibold mb-2">Billing Cycle</h3>
        <div class="grid grid-cols-2 gap-2">
          <button class="border rounded-md py-2 px-3 <?php echo $billing_cycle==='monthly'?'bg-blue-600 text-white border-blue-600':''; ?>" onclick="changeBilling('monthly')">Monthly</button>
          <button class="border rounded-md py-2 px-3 <?php echo $billing_cycle==='annual'?'bg-blue-600 text-white border-blue-600':''; ?>" onclick="changeBilling('annual')">Annual</button>
        </div>
      </div>
    </section>

    <section class="bg-white border rounded-xl p-6">
      <h2 class="text-xl font-semibold mb-4">Payment Method</h2>

      <div class="mb-4">
        <label for="promo-input" class="block text-sm font-medium mb-1">Have a promo code?</label>
        <div class="flex gap-2">
          <input id="promo-input" type="text" class="border rounded-md px-3 py-2 flex-1" placeholder="Enter TRIAL or REF50" />
          <button type="button" class="border rounded-md px-4 py-2" onclick="applyPromo()">Apply</button>
        </div>
        <div id="promo-message" class="text-sm mt-2 hidden"></div>
      </div>

      <div id="paypal-button-container"></div>
      <div id="loading-state" class="hidden mt-4 text-center">
        <div class="animate-spin h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full mx-auto mb-2"></div>
        <p>Setting up secure payment…</p>
      </div>
      <div id="error-state" class="hidden mt-4 text-center">
        <h3 class="text-red-600 font-semibold">Payment Setup Error</h3>
        <p id="error-text" class="text-sm"></p>
        <button onclick="retryPaymentSetup()" class="mt-2 bg-blue-600 text-white rounded-md px-4 py-2">Try Again</button>
      </div>

      <div class="mt-6 grid grid-cols-3 gap-3 text-sm text-muted-foreground">
        <div class="flex items-center gap-2"><span>🔒</span><span>SSL Encrypted</span></div>
        <div class="flex items-center gap-2"><span>🛡️</span><span>PayPal Protected</span></div>
        <div class="flex items-center gap-2"><span>💳</span><span>30-Day Guarantee</span></div>
      </div>
    </section>
  </div>
</main>

<script src="https://www.paypal.com/sdk/js?client-id=<?php echo esc_attr($paypal_client_id); ?>&currency=USD&intent=capture"></script>
<script>
let currentPlan = <?php echo json_encode($selected_plan); ?>;
let currentBilling = <?php echo json_encode($billing_cycle); ?>;
let currentPromo = '';

function showLoading(){ document.getElementById('paypal-button-container').classList.add('hidden'); document.getElementById('loading-state').classList.remove('hidden'); document.getElementById('error-state').classList.add('hidden'); }
function showError(msg){ document.getElementById('paypal-button-container').classList.add('hidden'); document.getElementById('loading-state').classList.add('hidden'); document.getElementById('error-state').classList.remove('hidden'); (document.getElementById('error-text')||{}).textContent = msg||'There was a problem setting up payment.'; }

function changeBilling(type){ const url = new URL(window.location.href); url.searchParams.set('billing', type); window.location.href = url.toString(); }

function applyPromo(){
  const input = document.getElementById('promo-input');
  const msg = document.getElementById('promo-message');
  const code = (input.value||'').trim().toUpperCase();
  if (!code){ currentPromo=''; msg.classList.add('hidden'); return; }
  if (code !== 'TRIAL' && code !== 'REF50'){
    msg.textContent = 'Invalid code. Use TRIAL or REF50.';
    msg.classList.remove('hidden'); msg.classList.remove('text-green-600'); msg.classList.add('text-red-600');
    return;
  }
  currentPromo = code;
  msg.textContent = code==='TRIAL' ? 'TRIAL applied: $1 for 7 days then monthly.' : 'REF50 applied: 50% off first month then monthly.';
  msg.classList.remove('hidden'); msg.classList.remove('text-red-600'); msg.classList.add('text-green-600');
}

function initPayPalButtons(){
  showLoading();
  paypal.Buttons({
    createOrder: function(data, actions){
      return fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' },
        body: new URLSearchParams({
          'action': 'create_paypal_order',
          'plan': currentPlan,
          'billing_cycle': currentBilling,
          'promo_code': currentPromo,
          'nonce': '<?php echo wp_create_nonce('paypal_nonce'); ?>'
        })
      }).then(r=>r.json()).then(json=>{
        if (!json || !json.success){ throw new Error((json&&json.data)||'Setup failed'); }
        window.__ssLocalOrderId = json.data.order_id;
        const note = document.getElementById('promo-message');
        if (json.data.message && note){ note.textContent = json.data.message; note.classList.remove('hidden'); note.classList.add('text-green-600'); }
        return json.data.order_id;
      }).catch(err=>{ showError(err&&err.message?err.message:'Unable to initialize payment'); throw err; });
    },
    onApprove: function(data, actions){
      return fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
        method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' },
        body: new URLSearchParams({ 'action': 'capture_paypal_order', 'order_id': (window.__ssLocalOrderId || data.orderID), 'nonce': '<?php echo wp_create_nonce('paypal_nonce'); ?>' })
      }).then(r=>r.json()).then(json=>{
        if (!json || !json.success){ throw new Error((json&&json.data)||'Capture failed'); }
        window.location.href = '<?php echo home_url('/payment-success/'); ?>';
      }).catch(err=>{ showError(err&&err.message?err.message:'Unable to capture payment'); });
    }
  }).render('#paypal-button-container').then(function(){
    document.getElementById('loading-state').classList.add('hidden');
    document.getElementById('paypal-button-container').classList.remove('hidden');
  }).catch(function(err){ showError('PayPal initialization error'); console.error(err); });
}

document.addEventListener('DOMContentLoaded', function(){ if (typeof paypal !== 'undefined'){ initPayPalButtons(); } });
</script>

<?php get_footer(); ?>

