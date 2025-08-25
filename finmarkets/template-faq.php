<?php /* Template Name: FAQ */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php the_title(); ?></h1>
      <p class="section-subtitle">Find quick answers to common questions</p>
    </header>

    <div class="features-grid">
      <div class="card glass-card"><div class="card-body">
        <h2 class="section-title" style="font-size:1.25rem">Getting Started</h2>
        <details><summary>How do I create a free account?</summary><p>Click the "Sign Up" button, enter your email and create a password. You get immediate access to free features.</p></details>
        <details><summary>What's included in the free plan?</summary><p>Basic screening, watchlist management, and limited market data with a monthly usage cap.</p></details>
      </div></div>

      <div class="card glass-card"><div class="card-body">
        <h2 class="section-title" style="font-size:1.25rem">Features & Tools</h2>
        <details><summary>How accurate is the stock data?</summary><p>We use professional-grade data feeds with real-time updates during market hours.</p></details>
        <details><summary>Can I export my screening results?</summary><p>Premium subscribers can export screening results to CSV.</p></details>
      </div></div>

      <div class="card glass-card"><div class="card-body">
        <h2 class="section-title" style="font-size:1.25rem">Billing & Accounts</h2>
        <details><summary>Can I cancel my subscription anytime?</summary><p>Yes, from your account settings. You retain access until the end of your billing period.</p></details>
        <details><summary>Do you offer refunds?</summary><p>30‑day money‑back guarantee for new premium subscriptions.</p></details>
      </div></div>
    </div>

    <div class="card glass-card" style="margin-top:2rem;text-align:center"><div class="card-body">
      <h2 class="section-title" style="font-size:1.25rem">Still Have Questions?</h2>
      <p class="section-subtitle">Can't find the answer? Our support team is here to help.</p>
      <div class="hero-actions"><a href="/contact/" class="btn btn-primary">Contact Support</a><a href="/help-center/" class="btn btn-outline">Help Center</a></div>
    </div></div>
  </div>
</section>
<?php get_footer(); ?>