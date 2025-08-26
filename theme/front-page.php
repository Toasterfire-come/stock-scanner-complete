<?php
/**
 * Front Page Template (no blog posts)
 */
get_header();
?>
<main id="main-content" class="site-main">
  <div class="container">
    <section class="page-header">
      <h1 class="page-title">Smarter Stock Insights</h1>
      <p class="page-description">Scan, screen, and track the market with professional-grade tools.</p>
      <div style="margin-top:1rem; display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
        <a class="btn btn-primary" href="/stock-dashboard/"><span>Open Dashboard</span></a>
        <a class="btn btn-gold" href="/membership-plans/"><span>See Plans</span></a>
      </div>
    </section>

    <section class="grid-3">
      <div class="feature-card">
        <h4>Real-time Widgets</h4>
        <p>Use powerful widgets on any page with shortcodes. Try AAPL, TSLA, NVDA.</p>
        <?php echo do_shortcode('[stock_scanner symbol="AAPL" show_chart="true" show_details="true"]'); ?>
      </div>
      <div class="feature-card">
        <h4>Market Indices</h4>
        <p>Track major indices at a glance and stay on top of market movement.</p>
        <?php echo do_shortcode('[stock_scanner symbol="SPY" show_chart="true" show_details="false"]'); ?>
      </div>
      <div class="feature-card">
        <h4>Membership-ready</h4>
        <p>Plan-aware UI with premium badges and server-side plan validation.</p>
        <div class="gradient-box">Premium-ready theme with plan badge in header</div>
      </div>
    </section>

    <section class="card">
      <div class="card-header">
        <h2 class="card-title">Explore Pages</h2>
        <div class="card-subtitle">Quick links to important sections</div>
      </div>
      <div class="card-body">
        <?php echo do_shortcode('[featured_pages count="6" parent="0"]'); ?>
      </div>
    </section>
  </div>
</main>
<?php get_footer(); ?>