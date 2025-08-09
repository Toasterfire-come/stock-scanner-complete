<?php
/**
 * Template Name: Help Center
 */
get_header(); ?>
<div class="help-center">
  <div class="container" style="max-width:1000px;margin:40px auto;padding:0 20px;">
    <h1>Help Center</h1>
    <div class="grid" style="display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));">
      <div class="card">
        <h3>Getting Started</h3>
        <p>New? Start here.</p>
        <a class="btn" href="/getting-started/">Open guide</a>
      </div>
      <div class="card">
        <h3>FAQ</h3>
        <p>Common questions answered.</p>
        <a class="btn" href="/faq/">View FAQ</a>
      </div>
      <div class="card">
        <h3>Contact</h3>
        <p>Need more help?</p>
        <a class="btn" href="/contact/">Contact Support</a>
      </div>
    </div>
    <div class="card" style="margin-top:16px;">
      <h3>Tips</h3>
      <ul>
        <li>Use the Stock Lookup for quick quotes and snapshots.</li>
        <li>Create a Watchlist to track ideas.</li>
        <li>Visit Market Overview to see indices and breadth.</li>
      </ul>
    </div>
  </div>
</div>
<?php get_footer(); ?>