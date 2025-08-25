<?php /* Template Name: Payment - Checkout */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content" style="max-width:720px;">
    <h1 style="color:var(--navy);">Checkout</h1>
    <div class="card" style="padding:16px;">
      <div style="display:flex; flex-direction:column; gap:12px;">
        <div>
          <label for="ppCode" class="muted">Discount code (optional)</label>
          <div class="toolbar" style="margin-top:6px;">
            <input id="ppCode" class="input" placeholder="Enter code" />
            <button id="ppApply" class="btn">Apply</button>
          </div>
        </div>
        <div id="ppSummary" class="card" style="padding:12px;"></div>
        <div id="paypal-buttons"></div>
        <div id="ppStatus" class="muted">Pay securely with PayPal.</div>
        <input type="hidden" id="ppSuccessUrl" value="<?php echo esc_url(home_url('/')); ?>" />
      </div>
    </div>
    <p class="muted" style="margin-top:8px;">This integration uses PayPal smart buttons. Amounts are configured in Appearance → FinMarkets Settings.</p>
  </div>
</section>
<script defer src="<?php echo esc_url( get_template_directory_uri() . '/assets/js/paypal.js' ); ?>"></script>
<?php get_footer(); ?>