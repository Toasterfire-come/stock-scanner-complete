<?php /* Template Name: Payment - Checkout */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <h1 style="color:var(--navy);">Checkout</h1>
    <div class="card" style="padding:16px;">
      <p class="muted">This is a placeholder checkout page. No real payment is processed in this theme demo.</p>
      <form class="grid cols-2" onsubmit="return false;">
        <input class="input" placeholder="Name on card" />
        <input class="input" placeholder="Email" type="email" />
        <input class="input" placeholder="Card number" inputmode="numeric" />
        <input class="input" placeholder="MM/YY" inputmode="numeric" />
        <input class="input" placeholder="CVC" inputmode="numeric" />
        <button class="btn btn-primary">Pay $19</button>
      </form>
    </div>
  </div>
</section>
<?php get_footer(); ?>