<?php
/**
 * Template Name: Frequently Asked Questions
 */
get_header(); ?>

<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php the_title(); ?></h1>
      <p class="section-subtitle"><?php _e('Find quick answers to common questions', 'stock-scanner'); ?></p>
    </header>

    <div class="features-grid">
      <div class="card glass-card">
        <div class="card-body">
          <h2 class="section-title" style="font-size:1.25rem"><?php _e('Getting Started', 'stock-scanner'); ?></h2>
          <details>
            <summary><?php _e('How do I create a free account?', 'stock-scanner'); ?></summary>
            <p><?php _e('Click the "Sign Up" button, enter your email and create a password. You get immediate access to free features.', 'stock-scanner'); ?></p>
          </details>
          <details>
            <summary><?php _e('What\'s included in the free plan?', 'stock-scanner'); ?></summary>
            <p><?php _e('Basic screening, watchlist management, and limited market data with a monthly usage cap.', 'stock-scanner'); ?></p>
          </details>
        </div>
      </div>

      <div class="card glass-card">
        <div class="card-body">
          <h2 class="section-title" style="font-size:1.25rem"><?php _e('Features & Tools', 'stock-scanner'); ?></h2>
          <details>
            <summary><?php _e('How accurate is the stock data?', 'stock-scanner'); ?></summary>
            <p><?php _e('We use professional-grade data feeds with real-time updates during market hours.', 'stock-scanner'); ?></p>
          </details>
          <details>
            <summary><?php _e('Can I export my screening results?', 'stock-scanner'); ?></summary>
            <p><?php _e('Premium subscribers can export screening results to CSV.', 'stock-scanner'); ?></p>
          </details>
        </div>
      </div>

      <div class="card glass-card">
        <div class="card-body">
          <h2 class="section-title" style="font-size:1.25rem"><?php _e('Billing & Accounts', 'stock-scanner'); ?></h2>
          <details>
            <summary><?php _e('Can I cancel my subscription anytime?', 'stock-scanner'); ?></summary>
            <p><?php _e('Yes, from your account settings. You retain access until the end of your billing period.', 'stock-scanner'); ?></p>
          </details>
          <details>
            <summary><?php _e('Do you offer refunds?', 'stock-scanner'); ?></summary>
            <p><?php _e('30‑day money‑back guarantee for new premium subscriptions.', 'stock-scanner'); ?></p>
          </details>
        </div>
      </div>
    </div>

    <div class="card glass-card" style="margin-top:2rem;text-align:center">
      <div class="card-body">
        <h2 class="section-title" style="font-size:1.25rem"><?php _e('Still Have Questions?', 'stock-scanner'); ?></h2>
        <p class="section-subtitle"><?php _e('Can\'t find the answer? Our support team is here to help.', 'stock-scanner'); ?></p>
        <div class="hero-actions">
          <a href="/contact/" class="btn btn-primary"><?php _e('Contact Support', 'stock-scanner'); ?></a>
          <a href="/help-center/" class="btn btn-outline"><?php _e('Help Center', 'stock-scanner'); ?></a>
        </div>
      </div>
    </div>
  </div>
</section>

<?php get_footer(); ?>