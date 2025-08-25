<?php /* Template Name: Components */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Components</h1>
      <p class="muted">Preview of the theme’s UI building blocks.</p>
    </div>
    <div class="grid cols-3">
      <div class="card" style="padding:16px;">
        <h3>Buttons</h3>
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          <button class="btn">Default</button>
          <button class="btn btn-primary">Primary</button>
          <button class="btn btn-success">Success</button>
          <button class="btn btn-ghost">Ghost</button>
        </div>
      </div>
      <div class="card" style="padding:16px;">
        <h3>Inputs</h3>
        <div class="grid cols-2">
          <input class="input" placeholder="Search" />
          <select class="select"><option>Option</option></select>
          <input class="input" type="number" placeholder="123" />
          <input class="input" type="email" placeholder="email@domain.com" />
        </div>
      </div>
      <div class="card" style="padding:16px;">
        <h3>Badges</h3>
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          <span class="badge">Neutral</span>
          <span class="badge badge-green">Gain +2.3%</span>
          <span class="badge badge-red">Loss -1.1%</span>
        </div>
      </div>
    </div>

    <div class="grid cols-2" style="margin-top:24px;">
      <div class="card" style="padding:16px;">
        <h3>Table</h3>
        <table class="table"><thead><tr><th>Ticker</th><th>Name</th><th>Price</th><th>Δ</th></tr></thead><tbody>
          <tr><td class="mono">AAPL</td><td>Apple Inc.</td><td>$232.13</td><td><span class="badge badge-green">+0.45%</span></td></tr>
          <tr><td class="mono">TSLA</td><td>Tesla Inc.</td><td>$245.55</td><td><span class="badge badge-red">-2.15%</span></td></tr>
        </tbody></table>
      </div>
      <div class="card" style="padding:16px;">
        <h3>Cards</h3>
        <div class="grid cols-2">
          <div class="card" style="padding:12px;"><div class="muted">Coverage</div><strong>8,000+ stocks</strong></div>
          <div class="card" style="padding:12px;"><div class="muted">Uptime</div><strong>99.9%</strong></div>
        </div>
      </div>
    </div>
  </div>
</section>
<?php get_footer(); ?>