<?php
/**
 * Stock Scanner Theme Main Template (Conversion-Optimized)
 */
get_header(); ?>

<div class="stock-scanner-homepage enhanced-layout">
  <!-- Hero: Clear Value Proposition with Enhanced Design -->
  <section class="hero-section gradient-hero">
    <div class="hero-overlay"></div>
    <div class="container">
      <div class="hero-content scroll-reveal">
        <div class="hero-badge animate-fade-in">
          <span class="badge-icon">🚀</span>
          <span class="badge-text"><?php _e('Professional Stock Analysis Platform', 'stock-scanner'); ?></span>
        </div>
        
        <h1 class="hero-title text-gradient animate-slide-up">
          <?php _e('Find Winning Stocks Fast', 'stock-scanner'); ?>
        </h1>
        
        <p class="hero-subtitle animate-slide-up" style="font-size:1.25rem; animation-delay: 0.2s;">
          <?php _e('Real‑time data, pro‑level screening, and portfolio analytics — in a platform built for speed and clarity.', 'stock-scanner'); ?>
        </p>
        
        <div class="hero-features animate-slide-up" style="animation-delay: 0.4s;">
          <div class="feature-highlight">
            <span class="feature-icon">📊</span>
            <span class="feature-text"><?php _e('50+ indicators with AI insights', 'stock-scanner'); ?></span>
          </div>
          <div class="feature-highlight">
            <span class="feature-icon">⚡</span>
            <span class="feature-text"><?php _e('Unlimited real‑time quotes', 'stock-scanner'); ?></span>
          </div>
          <div class="feature-highlight">
            <span class="feature-icon">🔔</span>
            <span class="feature-text"><?php _e('Alerts, risk metrics, and 360° portfolio view', 'stock-scanner'); ?></span>
          </div>
        </div>
        
        <div class="hero-actions animate-slide-up" style="animation-delay: 0.6s;">
          <?php if (!is_user_logged_in()): ?>
            <a href="<?php echo wp_registration_url(); ?>" class="btn btn-primary btn-lg glass shadow-glass cta-button" data-cta>
              <span class="btn-icon">🚀</span>
              <span class="btn-text"><?php _e('Start 7‑Day Trial for $1', 'stock-scanner'); ?></span>
              <span class="btn-shimmer"></span>
            </a>
            <a href="/compare-plans/" class="btn btn-outline btn-lg glass" data-cta>
              <span class="btn-text"><?php _e('Compare Plans', 'stock-scanner'); ?></span>
            </a>
          <?php else: ?>
            <a href="/dashboard/" class="btn btn-primary btn-lg glass shadow-glass cta-button" data-cta>
              <span class="btn-icon">📊</span>
              <span class="btn-text"><?php _e('Go to Dashboard', 'stock-scanner'); ?></span>
              <span class="btn-shimmer"></span>
            </a>
            <a href="/stock-screener/" class="btn btn-outline btn-lg glass" data-cta>
              <span class="btn-icon">🔎</span>
              <span class="btn-text"><?php _e('Open Screener', 'stock-scanner'); ?></span>
            </a>
          <?php endif; ?>
        </div>
        
        <div class="hero-guarantee animate-fade-in" style="animation-delay: 0.8s;">
          <span class="guarantee-icon">🛡️</span>
          <span class="guarantee-text"><?php _e('30‑day money‑back guarantee • Cancel anytime', 'stock-scanner'); ?></span>
        </div>
      </div>

      <!-- Enhanced Social Proof: Logo Grid -->
      <div class="logo-grid scroll-reveal animate-fade-in" style="animation-delay: 1s;">
        <div class="logos-label"><?php _e('Trusted by traders from:', 'stock-scanner'); ?></div>
        <div class="logos-container">
          <div class="logo-item">
            <span class="logo-text">Bloomberg</span>
          </div>
          <div class="logo-item">
            <span class="logo-text">Reuters</span>
          </div>
          <div class="logo-item">
            <span class="logo-text">CNBC</span>
          </div>
          <div class="logo-item">
            <span class="logo-text">WSJ</span>
          </div>
          <div class="logo-item">
            <span class="logo-text">MarketWatch</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Outcomes Section: What You Achieve with Enhanced Design -->
  <section class="section-padding" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);">
    <div class="visual-container">
      <div class="text-center stack-12">
        <div class="badge-system badge-glass fade-up">
          <span>🎯</span>
          <span><?php _e('Proven Results', 'stock-scanner'); ?></span>
        </div>
        
        <h2 class="display-2 fade-up delay-100"><?php _e('What You'll Achieve In Your First Week', 'stock-scanner'); ?></h2>
        
        <p class="body-large fade-up delay-200" style="max-width: 700px; margin: 0 auto; color: var(--color-text-light);">
          <?php _e('Ship a repeatable workflow for discovering, evaluating, and acting on opportunities.', 'stock-scanner'); ?>
        </p>
      </div>

      <div class="grid-4" style="margin-top: var(--space-16);">
        <div class="card-system card-interactive fade-up delay-100">
          <div class="stack-4 text-center">
            <div class="badge-system badge-primary" style="margin: 0 auto;">
              <span><?php _e('Day 1', 'stock-scanner'); ?></span>
            </div>
            <div class="icon-system">
              <span>⚙️</span>
            </div>
            <h3 class="headline-3"><?php _e('Setup & Configuration', 'stock-scanner'); ?></h3>
            <p class="body-medium">
              <?php _e('Set up your scanners and watchlists with our guided onboarding process', 'stock-scanner'); ?>
            </p>
          </div>
        </div>

        <div class="card-system card-interactive fade-up delay-200">
          <div class="stack-4 text-center">
            <div class="badge-system badge-success" style="margin: 0 auto;">
              <span><?php _e('Day 3', 'stock-scanner'); ?></span>
            </div>
            <div class="icon-system">
              <span>🔍</span>
            </div>
            <h3 class="headline-3"><?php _e('Advanced Screening', 'stock-scanner'); ?></h3>
            <p class="body-medium">
              <?php _e('Run advanced screens and save candidates using professional-grade filters', 'stock-scanner'); ?>
            </p>
          </div>
        </div>

        <div class="card-system card-interactive fade-up delay-300">
          <div class="stack-4 text-center">
            <div class="badge-system badge-warning" style="margin: 0 auto;">
              <span><?php _e('Day 5', 'stock-scanner'); ?></span>
            </div>
            <div class="icon-system">
              <span>⚖️</span>
            </div>
            <h3 class="headline-3"><?php _e('Risk Analysis', 'stock-scanner'); ?></h3>
            <p class="body-medium">
              <?php _e('Analyze risk metrics and set intelligent alerts for your portfolio', 'stock-scanner'); ?>
            </p>
          </div>
        </div>

        <div class="card-system card-interactive fade-up delay-400">
          <div class="stack-4 text-center">
            <div class="badge-system badge-success" style="margin: 0 auto;">
              <span><?php _e('Day 7', 'stock-scanner'); ?></span>
            </div>
            <div class="icon-system">
              <span>🎯</span>
            </div>
            <h3 class="headline-3"><?php _e('Execute with Confidence', 'stock-scanner'); ?></h3>
            <p class="body-medium">
              <?php _e('Execute trades with confidence using real-time data and proven strategies', 'stock-scanner'); ?>
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Comparison Table: Us vs Alternatives with Enhanced Design -->
  <section class="section-padding">
    <div class="visual-container">
      <div class="text-center stack-12">
        <div class="badge-system badge-glass fade-up">
          <span>⚔️</span>
          <span><?php _e('Competitive Edge', 'stock-scanner'); ?></span>
        </div>
        
        <h2 class="display-2 fade-up delay-100"><?php _e('Why Traders Choose Stock Scanner', 'stock-scanner'); ?></h2>
        
        <p class="body-large fade-up delay-200" style="max-width: 600px; margin: 0 auto; color: var(--color-text-light);">
          <?php _e('Serious power without the enterprise bloat', 'stock-scanner'); ?>
        </p>
      </div>

      <div class="card-system fade-up delay-300" style="margin-top: var(--space-16); overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse;">
          <thead>
            <tr style="background: var(--gradient-primary); color: var(--color-white);">
              <th style="padding: var(--space-4) var(--space-6); text-align: left; font-weight: 600; border-radius: var(--radius-lg) 0 0 0;">
                <?php _e('Feature', 'stock-scanner'); ?>
              </th>
              <th style="padding: var(--space-4) var(--space-6); text-align: center; font-weight: 600;">
                <?php _e('Stock Scanner', 'stock-scanner'); ?>
              </th>
              <th style="padding: var(--space-4) var(--space-6); text-align: center; font-weight: 600; border-radius: 0 var(--radius-lg) 0 0;">
                <?php _e('Alternatives', 'stock-scanner'); ?>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr style="border-bottom: 1px solid var(--color-border);">
              <td style="padding: var(--space-4) var(--space-6); font-weight: 500;">
                <?php _e('Real‑time quotes', 'stock-scanner'); ?>
              </td>
              <td style="padding: var(--space-4) var(--space-6); text-align: center;">
                <div class="badge-system badge-success">
                  <span>✅</span>
                  <span><?php _e('Yes', 'stock-scanner'); ?></span>
                </div>
              </td>
              <td style="padding: var(--space-4) var(--space-6); text-align: center;">
                <div class="badge-system badge-error">
                  <span>❌</span>
                  <span><?php _e('Often delayed', 'stock-scanner'); ?></span>
                </div>
              </td>
            </tr>
            <tr style="border-bottom: 1px solid var(--color-border);">
              <td style="padding: var(--space-4) var(--space-6); font-weight: 500;">
                <?php _e('50+ indicators', 'stock-scanner'); ?>
              </td>
              <td style="padding: var(--space-4) var(--space-6); text-align: center;">
                <div class="badge-system badge-success">
                  <span>✅</span>
                  <span><?php _e('Yes', 'stock-scanner'); ?></span>
                </div>
              </td>
              <td style="padding: var(--space-4) var(--space-6); text-align: center;">
                <div class="badge-system badge-error">
                  <span>❌</span>
                  <span><?php _e('Limited', 'stock-scanner'); ?></span>
                </div>
              </td>
            </tr>
            <tr style="border-bottom: 1px solid var(--color-border);">
              <td style="padding: var(--space-4) var(--space-6); font-weight: 500;">
                <?php _e('AI insights', 'stock-scanner'); ?>
              </td>
              <td style="padding: var(--space-4) var(--space-6); text-align: center;">
                <div class="badge-system badge-success">
                  <span>🤖</span>
                  <span><?php _e('Built‑in', 'stock-scanner'); ?></span>
                </div>
              </td>
              <td style="padding: var(--space-4) var(--space-6); text-align: center;">
                <div class="badge-system badge-warning">
                  <span>💰</span>
                  <span><?php _e('Add‑ons', 'stock-scanner'); ?></span>
                </div>
              </td>
            </tr>
            <tr style="border-bottom: 1px solid var(--color-border);">
              <td style="padding: var(--space-4) var(--space-6); font-weight: 500;">
                <?php _e('Portfolio analytics', 'stock-scanner'); ?>
              </td>
              <td style="padding: var(--space-4) var(--space-6); text-align: center;">
                <div class="badge-system badge-success">
                  <span>📊</span>
                  <span><?php _e('Full suite', 'stock-scanner'); ?></span>
                </div>
              </td>
              <td style="padding: var(--space-4) var(--space-6); text-align: center;">
                <div class="badge-system badge-error">
                  <span>📈</span>
                  <span><?php _e('Basic', 'stock-scanner'); ?></span>
                </div>
              </td>
            </tr>
            <tr>
              <td style="padding: var(--space-4) var(--space-6); font-weight: 500;">
                <?php _e('Setup time', 'stock-scanner'); ?>
              </td>
              <td style="padding: var(--space-4) var(--space-6); text-align: center;">
                <div class="badge-system badge-success">
                  <span>⚡</span>
                  <span><?php _e('Minutes', 'stock-scanner'); ?></span>
                </div>
              </td>
              <td style="padding: var(--space-4) var(--space-6); text-align: center;">
                <div class="badge-system badge-error">
                  <span>🐌</span>
                  <span><?php _e('Days', 'stock-scanner'); ?></span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="cluster-4" style="margin-top: var(--space-8); justify-content: center;">
        <a href="/premium-plans/" class="btn-primary-system btn-large" data-cta>
          <span>🚀</span>
          <span><?php _e('Start 7‑Day Trial for $1', 'stock-scanner'); ?></span>
        </a>
        <a href="/compare-plans/" class="btn-secondary-system btn-large" data-cta>
          <span><?php _e('Compare Plans', 'stock-scanner'); ?></span>
        </a>
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