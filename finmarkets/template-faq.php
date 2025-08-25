<?php /* Template Name: FAQ */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php the_title(); ?></h1>
      <p class="section-subtitle">Answers to common questions about FinMarkets</p>
    </header>

    <div class="features-grid">
      <div class="card glass-card"><div class="card-body">
        <h2 style="font-size:1.1rem">Getting Started</h2>
        <details><summary>How do I create a free account?</summary><p>Click Sign Up and complete the form. You’ll get access to the free tier immediately.</p></details>
        <details><summary>What’s included in Free?</summary><p>Basic screening, watchlist management, and limited market data.</p></details>
      </div></div>
      <div class="card glass-card"><div class="card-body">
        <h2 style="font-size:1.1rem">Features & Tools</h2>
        <details><summary>Do you support real‑time quotes?</summary><p>Yes, where available from our data providers.</p></details>
        <details><summary>Can I export screen results?</summary><p>Pro subscribers can export results to CSV.</p></details>
      </div></div>
      <div class="card glass-card"><div class="card-body">
        <h2 style="font-size:1.1rem">Billing</h2>
        <details><summary>Can I cancel anytime?</summary><p>Yes, manage your plan from your account settings.</p></details>
        <details><summary>Do you offer refunds?</summary><p>We offer a 30‑day money‑back guarantee for new premium subscriptions.</p></details>
      </div></div>
    </div>

    <div class="card glass-card" style="margin-top:2rem; text-align:center"><div class="card-body">
      <h2 style="font-size:1.25rem">Still Have Questions?</h2>
      <p class="section-subtitle">Contact support or browse the help center.</p>
      <div class="hero-actions"><a href="/contact/" class="btn btn-primary">Contact Support</a><a href="/help-center/" class="btn btn-outline">Help Center</a></div>
    </div></div>
  </div>
</section>
<?php get_footer(); ?>