<?php
/**
 * Front Page Template (Conversion-focused)
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }

get_header();
?>

<main id="primary" class="container mx-auto px-4">
  <!-- Hero -->
  <section class="py-16">
    <div class="max-w-3xl mx-auto text-center">
      <h1 class="leading-tight" style="font-size:clamp(2rem,1.2rem + 3vw,3rem);font-weight:800;">
        Get full access with a 7-day trial for $1
      </h1>
      <p class="mt-3 text-muted-foreground" style="font-size:1.125rem;">
        Unlock all features on any plan. Apply code <strong>TRIAL</strong> at checkout.
      </p>
      <div class="mt-8 flex flex-col md:flex-row items-center justify-center gap-3">
        <a href="/payment-success/" class="btn btn--primary rounded-md px-3 py-2" style="background:var(--foreground);color:var(--background);">
          Start 7-day trial — $1
        </a>
        <a href="/premium-plans/" class="btn btn--ghost rounded-md px-3 py-2">
          View plans
        </a>
      </div>
      <ul class="mt-8 grid gap-3 md:grid-cols-3 text-sm text-muted-foreground">
        <li class="card p-2">All features on any plan</li>
        <li class="card p-2">Cancel anytime</li>
        <li class="card p-2">No hidden fees</li>
      </ul>
    </div>
  </section>

  <!-- Pricing -->
  <section id="pricing" class="py-16">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-8">
        <h2 class="leading-tight" style="font-size:clamp(1.5rem,1rem + 2vw,2.25rem);font-weight:800;">Choose your plan</h2>
        <p class="mt-2 text-muted-foreground">Try any plan for 7 days for $1 with code <strong>TRIAL</strong>.</p>
      </div>

      <div class="grid gap-6 md:grid-cols-3">
        <div class="card p-3">
          <h3 class="font-semibold">Basic</h3>
          <p class="text-muted-foreground mt-1">Great to get started</p>
          <div class="mt-3" style="font-weight:800;font-size:1.8rem;">$19<span class="text-muted-foreground" style="font-weight:500;font-size:.9rem;">/mo</span></div>
          <ul class="mt-3 text-sm text-muted-foreground">
            <li>Core features</li>
            <li>Email support</li>
          </ul>
          <a href="/payment-success/" class="btn btn--primary mt-4 w-full rounded-md px-3 py-2">Start $1 trial</a>
          <p class="mt-2 text-xs text-muted-foreground">Use code TRIAL at checkout.</p>
        </div>

        <div class="card p-3" style="border-width:2px;border-color:var(--primary);">
          <span class="rounded-full px-2 py-1 text-xs" style="background:var(--primary);color:var(--primary-foreground);display:inline-block;">Most Popular</span>
          <h3 class="font-semibold mt-2">Pro</h3>
          <p class="text-muted-foreground mt-1">Advanced for power users</p>
          <div class="mt-3" style="font-weight:800;font-size:1.8rem;">$49<span class="text-muted-foreground" style="font-weight:500;font-size:.9rem;">/mo</span></div>
          <ul class="mt-3 text-sm text-muted-foreground">
            <li>Everything in Basic</li>
            <li>Priority support</li>
          </ul>
          <a href="/payment-success/" class="btn btn--primary mt-4 w-full rounded-md px-3 py-2">Start $1 trial</a>
          <p class="mt-2 text-xs text-muted-foreground">Use code TRIAL at checkout.</p>
        </div>

        <div class="card p-3">
          <h3 class="font-semibold">Enterprise</h3>
          <p class="text-muted-foreground mt-1">For teams and orgs</p>
          <div class="mt-3" style="font-weight:800;font-size:1.8rem;">$99<span class="text-muted-foreground" style="font-weight:500;font-size:.9rem;">/mo</span></div>
          <ul class="mt-3 text-sm text-muted-foreground">
            <li>Everything in Pro</li>
            <li>Dedicated support</li>
          </ul>
          <a href="/payment-success/" class="btn btn--primary mt-4 w-full rounded-md px-3 py-2">Start $1 trial</a>
          <p class="mt-2 text-xs text-muted-foreground">Use code TRIAL at checkout.</p>
        </div>
      </div>
    </div>
  </section>
</main>

<?php get_footer(); ?>

