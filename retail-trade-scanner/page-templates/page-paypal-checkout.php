<?php
/**
 * Template Name: PayPal Checkout
 * Minimal PayPal checkout page with promo code entry
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="container mx-auto px-4 py-8 checkout-page">
  <header class="mb-6 text-center">
    <h1 class="text-3xl font-bold leading-tight">Complete Your Upgrade</h1>
    <p class="text-muted-foreground">Secure payment processing with PayPal</p>
  </header>

  <div class="grid gap-6 md:grid-cols-2">
    <section class="pricing-card p-3">
      <h2 class="text-lg font-semibold mb-2">Order Summary</h2>
      <div class="border rounded p-2">
        <div class="flex items-center justify-between">
          <div class="font-semibold">Selected Plan</div>
          <div id="rts-plan-price" class="text-lg">$49<span class="text-sm text-muted-foreground">/mo</span></div>
        </div>
        <div class="mt-2 text-sm text-muted-foreground">Includes premium features and priority support.</div>
      </div>

      <div class="mt-4">
        <h3 class="font-semibold mb-2">Promo Code</h3>
        <div class="flex gap-2">
          <input id="rts-promo-input" class="border rounded px-3 py-2" type="text" placeholder="Enter TRIAL or REF50" />
          <button id="rts-apply-promo" class="btn btn-outline rounded px-3 py-2" type="button">Apply</button>
        </div>
        <div id="rts-promo-message" class="text-sm mt-2"></div>
      </div>
    </section>

    <section class="pricing-card p-3">
      <h2 class="text-lg font-semibold mb-2">Payment Method</h2>
      <div class="border rounded p-3">
        <div id="paypal-button-container"></div>
        <div id="paypal-loading" class="text-sm text-muted-foreground" style="display:none;">Setting up secure payment…</div>
        <div id="paypal-error" class="notice notice-error mt-2" style="display:none;"></div>
      </div>
      <div class="mt-3 text-xs text-muted-foreground">SSL encrypted • PayPal protected • Cancel anytime</div>
    </section>
  </div>
</main>

<script>
(function(){
  var applyBtn = document.getElementById('rts-apply-promo');
  var input = document.getElementById('rts-promo-input');
  var msg = document.getElementById('rts-promo-message');
  if (applyBtn && input && msg){
    applyBtn.addEventListener('click', function(){
      var code = (input.value||'').trim().toUpperCase();
      if (!code){ msg.textContent = ''; return; }
      if (code === 'TRIAL'){
        msg.textContent = 'Applied TRIAL: 7-day trial for $1 will be used.';
        msg.className = 'text-sm notice notice-success mt-2';
      } else {
        msg.textContent = 'Code applied.';
        msg.className = 'text-sm notice notice-success mt-2';
      }
    });
  }
})();
</script>

<?php get_footer(); ?>

