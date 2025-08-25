<?php /* Template Name: About */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<div class="about-page">
  <div class="container">
    <div class="page-header">
      <h1>About FinMarkets</h1>
      <p class="page-description">Our mission is to deliver professional stock research tools with clarity, speed, and trust.</p>
    </div>

    <div class="card glass-card p-6 mb-6">
      <div style="display:grid; gap:var(--space-6);">
        <div>
          <h2 style="margin-bottom:var(--space-2);">Our Mission</h2>
          <p>We help investors make informed decisions with lightning‑fast screening, watchlists, portfolio tracking, and clean design.</p>
        </div>
        <div>
          <h2 style="margin-bottom:var(--space-2);">Our Vision</h2>
          <p>Democratize professional‑grade stock analysis for everyone—not just institutions.</p>
        </div>
        <div>
          <h2 style="margin-bottom:var(--space-2);">What We Value</h2>
          <div class="features-grid">
            <div class="card" style="padding:12px; text-align:center;"><h3>Clarity</h3><p>Intuitive UX without sacrificing power.</p></div>
            <div class="card" style="padding:12px; text-align:center;"><h3>Performance</h3><p>Fast, accurate data and robust APIs.</p></div>
            <div class="card" style="padding:12px; text-align:center;"><h3>Privacy</h3><p>Data handled responsibly and securely.</p></div>
          </div>
        </div>
      </div>
    </div>

    <div class="card glass-card p-6" style="text-align:center;">
      <h2 style="margin-bottom:var(--space-3);">Join Our Community</h2>
      <p class="muted" style="margin-bottom:var(--space-4);">Start free, upgrade anytime.</p>
      <div style="display:flex; gap:8px; justify-content:center; flex-wrap:wrap;">
        <a href="/signup/" class="btn btn-primary">Get Started</a>
        <a href="/premium-plans/" class="btn btn-outline">View Premium Plans</a>
      </div>
    </div>
  </div>
</div>
<?php get_footer(); ?>