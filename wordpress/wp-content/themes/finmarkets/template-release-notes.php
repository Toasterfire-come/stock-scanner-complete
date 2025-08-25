<?php /* Template Name: Release Notes */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <h1 style="color:var(--navy);">Release Notes</h1>
    <div class="card" style="padding:20px;">
      <h3>v0.3.0</h3>
      <ul>
        <li>Dark mode + keyboard shortcuts (D, W, Ctrl/Cmd+R, Esc)</li>
        <li>Components gallery page added</li>
        <li>PayPal checkout with discount flow and revenue recording</li>
        <li>API proxy aligned with spec (/api/* and /revenue/*)</li>
      </ul>
      <h3>v0.2.0</h3>
      <ul>
        <li>API pages: Endpoint Status and Revenue Analytics</li>
        <li>Market Overview + News hydration from external API</li>
        <li>Design system improvements, table/card polish</li>
      </ul>
      <h3>v0.1.0</h3>
      <ul>
        <li>Initial theme scaffolding, mock data, screener/watchlist</li>
      </ul>
    </div>
  </div>
</section>
<?php get_footer(); ?>