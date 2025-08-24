<?php
/**
 * Stock Scanner Theme Main Template (Conversion-Optimized)
 */
get_header(); ?>

<div class="stock-scanner-homepage enhanced-layout">
  <!-- Hero: Clear Value Proposition -->
  <section class="hero-section gradient-hero">
    <div class="container">
      <div class="hero-content scroll-reveal">
        <h1 class="hero-title text-gradient">
          <?php _e('Find Winning Stocks Fast', 'stock-scanner'); ?>
        </h1>
        <p class="hero-subtitle" style="font-size:1.25rem">
          <?php _e('Real‑time data, pro‑level screening, and portfolio analytics — in a platform built for speed and clarity.', 'stock-scanner'); ?>
        </p>
        <ul style="display:grid;gap:.5rem;margin:1rem 0;color:var(--color-white)">
          <li>✅ <?php _e('50+ indicators with AI insights', 'stock-scanner'); ?></li>
          <li>✅ <?php _e('Unlimited real‑time quotes', 'stock-scanner'); ?></li>
          <li>✅ <?php _e('Alerts, risk metrics, and 360° portfolio view', 'stock-scanner'); ?></li>
        </ul>
        <div class="hero-actions">
          <?php if (!is_user_logged_in()): ?>
            <a href="<?php echo wp_registration_url(); ?>" class="btn btn-primary btn-lg glass shadow-glass" data-cta>
              🚀 <?php _e('Start 7‑Day Trial for $1', 'stock-scanner'); ?>
            </a>
            <a href="/compare-plans/" class="btn btn-outline btn-lg glass" data-cta>
              <?php _e('Compare Plans', 'stock-scanner'); ?>
            </a>
          <?php else: ?>
            <a href="/dashboard/" class="btn btn-primary btn-lg glass shadow-glass" data-cta>
              📊 <?php _e('Go to Dashboard', 'stock-scanner'); ?>
            </a>
            <a href="/stock-screener/" class="btn btn-outline btn-lg glass" data-cta>
              🔎 <?php _e('Open Screener', 'stock-scanner'); ?>
            </a>
          <?php endif; ?>
        </div>
        <div style="margin-top:.5rem;color:var(--color-white);opacity:.9">
          🛡️ <?php _e('30‑day money‑back guarantee • Cancel anytime', 'stock-scanner'); ?>
        </div>
      </div>

      <!-- Social Proof: Logo Grid -->
      <div class="logo-grid scroll-reveal" style="margin-top:2rem">
        <div class="logo">Bloomberg</div>
        <div class="logo">Reuters</div>
        <div class="logo">CNBC</div>
        <div class="logo">WSJ</div>
        <div class="logo">MarketWatch</div>
      </div>
    </div>
  </section>

  <!-- Outcomes Section: What You Achieve -->
  <section class="glass-section">
    <div class="container">
      <div class="section-intro scroll-reveal">
        <h2 class="section-title text-gradient"><?php _e('What You’ll Achieve In Your First Week', 'stock-scanner'); ?></h2>
        <p class="section-subtitle"><?php _e('Ship a repeatable workflow for discovering, evaluating, and acting on opportunities.', 'stock-scanner'); ?></p>
      </div>
      <div class="features-grid">
        <div class="card glass-card scroll-reveal"><div class="card-body"><h3>Day 1</h3><p><?php _e('Set up your scanners and watchlists', 'stock-scanner'); ?></p></div></div>
        <div class="card glass-card scroll-reveal"><div class="card-body"><h3>Day 3</h3><p><?php _e('Run advanced screens and save candidates', 'stock-scanner'); ?></p></div></div>
        <div class="card glass-card scroll-reveal"><div class="card-body"><h3>Day 5</h3><p><?php _e('Analyze risk and set alerts', 'stock-scanner'); ?></p></div></div>
        <div class="card glass-card scroll-reveal"><div class="card-body"><h3>Day 7</h3><p><?php _e('Execute with confidence using live data', 'stock-scanner'); ?></p></div></div>
      </div>
    </div>
  </section>

  <!-- Comparison Table: Us vs Alternatives -->
  <section class="glass-section">
    <div class="container">
      <div class="section-intro">
        <h2 class="section-title"><?php _e('Why Traders Choose Stock Scanner', 'stock-scanner'); ?></h2>
        <p class="section-subtitle"><?php _e('Serious power without the enterprise bloat', 'stock-scanner'); ?></p>
      </div>
      <div class="card glass-card">
        <div class="card-body">
          <div class="table-responsive">
            <table data-sortable>
              <thead>
                <tr>
                  <th><?php _e('Feature', 'stock-scanner'); ?></th>
                  <th><?php _e('Stock Scanner', 'stock-scanner'); ?></th>
                  <th><?php _e('Alternatives', 'stock-scanner'); ?></th>
                </tr>
              </thead>
              <tbody>
                <tr><td><?php _e('Real‑time quotes', 'stock-scanner'); ?></td><td><span class="badge-yes">Yes</span></td><td><span class="badge-no">Often delayed</span></td></tr>
                <tr><td><?php _e('50+ indicators', 'stock-scanner'); ?></td><td><span class="badge-yes">Yes</span></td><td><span class="badge-no">Limited</span></td></tr>
                <tr><td><?php _e('AI insights', 'stock-scanner'); ?></td><td><span class="badge-yes">Built‑in</span></td><td><span class="badge-no">Add‑ons</span></td></tr>
                <tr><td><?php _e('Portfolio analytics', 'stock-scanner'); ?></td><td><span class="badge-yes">Full suite</span></td><td><span class="badge-no">Basic</span></td></tr>
                <tr><td><?php _e('Setup time', 'stock-scanner'); ?></td><td><span class="badge-yes"><?php _e('Minutes', 'stock-scanner'); ?></span></td><td><span class="badge-no"><?php _e('Days', 'stock-scanner'); ?></span></td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div class="hero-actions" style="margin-top:1rem">
        <a href="/premium-plans/" class="btn btn-primary btn-lg" data-cta><?php _e('Start 7‑Day Trial for $1', 'stock-scanner'); ?></a>
        <a href="/compare-plans/" class="btn btn-outline btn-lg" data-cta><?php _e('Compare Plans', 'stock-scanner'); ?></a>
      </div>
    </div>
  </section>

  <!-- Pricing: shortcode with graceful fallback -->
  <section class="pricing-section glass-section">
    <div class="container">
      <div class="section-intro">
        <h2 class="section-title text-gradient"><?php _e('Choose Your Plan', 'stock-scanner'); ?></h2>
        <p class="section-subtitle"><?php _e('Flexible options that grow with you', 'stock-scanner'); ?></p>
      </div>
      <div id="pricing-shortcode" class="scroll-reveal">
        <?php $pricing = do_shortcode('[stock_scanner_pricing show_trial="true" highlight_plan="premium"]'); echo $pricing; ?>
      </div>
      <?php if (empty($pricing)): ?>
        <div class="features-grid" style="margin-top:1rem">
          <div class="card glass-card"><div class="card-body"><h3><?php _e('Basic', 'stock-scanner'); ?></h3><p><?php _e('Core screening and watchlists', 'stock-scanner'); ?></p><a href="/premium-plans/" class="btn btn-outline" data-cta><?php _e('Get Started', 'stock-scanner'); ?></a></div></div>
          <div class="card glass-card"><div class="card-body"><h3><?php _e('Premium', 'stock-scanner'); ?></h3><p><?php _e('Real‑time data & advanced tools', 'stock-scanner'); ?></p><a href="/premium-plans/" class="btn btn-primary" data-cta><?php _e('Start $1 Trial', 'stock-scanner'); ?></a></div></div>
          <div class="card glass-card"><div class="card-body"><h3><?php _e('Pro', 'stock-scanner'); ?></h3><p><?php _e('Everything in Premium + AI', 'stock-scanner'); ?></p><a href="/premium-plans/" class="btn btn-outline" data-cta><?php _e('Talk to us', 'stock-scanner'); ?></a></div></div>
        </div>
      <?php endif; ?>
    </div>
  </section>

  <!-- FAQ: Objection Handling -->
  <section class="glass-section">
    <div class="container">
      <div class="section-intro">
        <h2 class="section-title"><?php _e('Frequently Asked Questions', 'stock-scanner'); ?></h2>
      </div>
      <div class="accordion" data-accordion>
        <div class="accordion-item"><div class="accordion-header"><?php _e('Can I cancel anytime?', 'stock-scanner'); ?></div><div class="accordion-content"><?php _e('Yes. You can cancel from your account page; you retain access through the billing period.', 'stock-scanner'); ?></div></div>
        <div class="accordion-item"><div class="accordion-header"><?php _e('Is the $1 trial really full access?', 'stock-scanner'); ?></div><div class="accordion-content"><?php _e('Yes. You get full access to all Premium features during the 7‑day trial.', 'stock-scanner'); ?></div></div>
        <div class="accordion-item"><div class="accordion-header"><?php _e('Do I need a credit card?', 'stock-scanner'); ?></div><div class="accordion-content"><?php _e('Yes. This verifies your account and enables uninterrupted access after trial if you choose.', 'stock-scanner'); ?></div></div>
      </div>
      <div class="hero-actions" style="margin-top:1rem">
        <a href="/premium-plans/" class="btn btn-primary btn-lg" data-cta><?php _e('Start 7‑Day Trial for $1', 'stock-scanner'); ?></a>
      </div>
    </div>
  </section>

  <!-- Final CTA -->
  <section class="cta-section gradient-hero">
    <div class="container">
      <div class="cta-content glass-card shadow-glass scroll-reveal">
        <h2 class="cta-title"><?php _e('Trade with confidence on a pro platform', 'stock-scanner'); ?></h2>
        <p class="cta-description"><?php _e('Join thousands of investors who rely on Stock Scanner for real‑time decisions.', 'stock-scanner'); ?></p>
        <div class="cta-actions">
          <a href="<?php echo wp_registration_url(); ?>" class="btn btn-primary btn-lg gradient-primary shadow-glass" data-cta>
            <?php _e('Start 7‑Day Trial for $1', 'stock-scanner'); ?>
          </a>
          <a href="/compare-plans/" class="btn btn-outline btn-lg glass" data-cta>
            <?php _e('Compare Plans', 'stock-scanner'); ?>
          </a>
        </div>
        <div class="cta-guarantee glass" style="margin-top:.5rem">
          🛡️ <?php _e('30‑day money‑back guarantee • Cancel anytime', 'stock-scanner'); ?>
        </div>
      </div>
    </div>
  </section>
</div>

<script>
// Optional: countdown timer on hero CTA (7 days rolling from visit)
(function(){
  try{
    const key='ssp_urgency_start_v1';
    let start = localStorage.getItem(key);
    if(!start){ start = Date.now(); localStorage.setItem(key, String(start)); }
    const end = Number(start) + (7*24*60*60*1000);
    const node = document.createElement('div');
    node.style.cssText='margin-top:.5rem;color:#fff;opacity:.9';
    node.textContent='Offer ends in: ';
    const span = document.createElement('span'); node.appendChild(span);
    document.querySelector('.hero-content')?.appendChild(node);
    window.renderCountdown(span, end);
  }catch(e){}
})();
</script>

<?php get_footer(); ?>