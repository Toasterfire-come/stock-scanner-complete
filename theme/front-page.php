<?php
/**
 * Front Page Template (no blog posts)
 */
get_header();
?>
<main id="main-content" class="site-main">
  <div class="container">
    <section class="page-header">
      <h1 class="page-title"><?php esc_html_e('Smarter Retail Trading Insights', 'retail-trade-scanner'); ?></h1>
      <p class="page-description"><?php esc_html_e('Scan, screen, and track the market with professional-grade tools.', 'retail-trade-scanner'); ?></p>
      <div class="cta-buttons">
        <a class="btn btn-primary" href="<?php echo esc_url(home_url('/stock-dashboard/')); ?>">
            <span><?php esc_html_e('Open Dashboard', 'retail-trade-scanner'); ?></span>
        </a>
        <a class="btn btn-gold" href="<?php echo esc_url(home_url('/membership-plans/')); ?>">
            <span><?php esc_html_e('See Plans', 'retail-trade-scanner'); ?></span>
        </a>
      </div>
    </section>

    <section class="grid-3">
      <div class="feature-card">
        <h4><?php esc_html_e('Real-time Widgets', 'retail-trade-scanner'); ?></h4>
        <p><?php esc_html_e('Use powerful widgets on any page with shortcodes. Try AAPL, TSLA, NVDA.', 'retail-trade-scanner'); ?></p>
        <?php echo do_shortcode('[stock_scanner symbol="AAPL" show_chart="true" show_details="true"]'); ?>
      </div>
      <div class="feature-card">
        <h4><?php esc_html_e('Market Indices', 'retail-trade-scanner'); ?></h4>
        <p><?php esc_html_e('Track major indices at a glance and stay on top of market movement.', 'retail-trade-scanner'); ?></p>
        <?php echo do_shortcode('[stock_scanner symbol="SPY" show_chart="true" show_details="false"]'); ?>
      </div>
      <div class="feature-card">
        <h4><?php esc_html_e('Membership-ready', 'retail-trade-scanner'); ?></h4>
        <p><?php esc_html_e('Plan-aware UI with premium badges and server-side plan validation.', 'retail-trade-scanner'); ?></p>
        <div class="gradient-box"><?php esc_html_e('Premium-ready theme with plan badge in header', 'retail-trade-scanner'); ?></div>
      </div>
    </section>

    <section class="card">
      <div class="card-header">
        <h2 class="card-title"><?php esc_html_e('Explore Pages', 'retail-trade-scanner'); ?></h2>
        <div class="card-subtitle"><?php esc_html_e('Quick links to important sections', 'retail-trade-scanner'); ?></div>
      </div>
      <div class="card-body">
        <?php echo do_shortcode('[featured_pages count="6" parent="0"]'); ?>
      </div>
    </section>
  </div>
</main>
<?php get_footer(); ?>