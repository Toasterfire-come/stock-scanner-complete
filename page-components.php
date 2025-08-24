<?php
/**
 * Template Name: UI Components Showcase (Dev)
 * Description: Developer page to preview theme components (frontend-only)
 */
get_header(); ?>
<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1 class="section-title text-gradient">UI Components</h1>
      <p class="section-subtitle">Preview of buttons, cards, tabs, accordion, tables, and callouts</p>
    </header>

    <div class="features-grid">
      <div class="card glass-card"><div class="card-body">
        <h3>Buttons</h3>
        <div class="hero-actions">
          <a class="btn btn-primary">Primary</a>
          <a class="btn btn-outline">Outline</a>
          <a class="btn btn-secondary">Secondary</a>
          <a class="btn btn-primary btn-sm">Small</a>
          <a class="btn btn-primary btn-lg">Large</a>
        </div>
      </div></div>

      <div class="card glass-card"><div class="card-body">
        <h3>Tabs</h3>
        <div class="tabs" data-tabs>
          <div class="tab-list">
            <button role="tab" class="tab-button" data-tab="a" aria-selected="true">Overview</button>
            <button role="tab" class="tab-button" data-tab="b">Details</button>
            <button role="tab" class="tab-button" data-tab="c">Notes</button>
          </div>
          <div role="tabpanel" class="tab-panel active" data-tab-panel="a">Overview content</div>
          <div role="tabpanel" class="tab-panel" data-tab-panel="b">Detailed content</div>
          <div role="tabpanel" class="tab-panel" data-tab-panel="c">Some notes</div>
        </div>
      </div></div>

      <div class="card glass-card"><div class="card-body">
        <h3>Accordion</h3>
        <div class="accordion" data-accordion>
          <div class="accordion-item"><div class="accordion-header">Question 1</div><div class="accordion-content">Answer 1</div></div>
          <div class="accordion-item"><div class="accordion-header">Question 2</div><div class="accordion-content">Answer 2</div></div>
        </div>
      </div></div>

      <div class="card glass-card"><div class="card-body">
        <h3>Sortable Table</h3>
        <div class="table-responsive">
          <table data-sortable>
            <thead><tr><th>Symbol</th><th>Price</th><th>Change</th></tr></thead>
            <tbody>
              <tr><td>AAPL</td><td>$187.23</td><td>+0.8%</td></tr>
              <tr><td>MSFT</td><td>$422.11</td><td>-0.2%</td></tr>
              <tr><td>GOOGL</td><td>$153.09</td><td>+1.3%</td></tr>
            </tbody>
          </table>
        </div>
      </div></div>

      <div class="card glass-card"><div class="card-body">
        <h3>Callouts</h3>
        <div class="callout info">Information callout</div>
        <div class="callout success" style="margin-top:.5rem">Success callout</div>
        <div class="callout warn" style="margin-top:.5rem">Warning callout</div>
        <div class="callout error" style="margin-top:.5rem">Error callout</div>
      </div></div>
    </div>
  </div>
</section>
<?php get_footer(); ?>