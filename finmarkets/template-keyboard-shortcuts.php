<?php /* Template Name: Keyboard Shortcuts */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <h1 style="color:var(--navy);">Keyboard Shortcuts</h1>
    <div class="card" style="padding:16px;">
      <p class="muted">These shortcuts are active site-wide.</p>
      <ul>
        <li><strong>D</strong> — Go to dashboard</li>
        <li><strong>W</strong> — Scroll to Watchlist (on pages with Watchlist)</li>
        <li><strong>Ctrl/Cmd + R</strong> — Refresh stock data preview</li>
        <li><strong>Esc</strong> — Dismiss focus</li>
      </ul>
      <div id="refreshStatus" class="muted" style="margin-top:8px;">Ready</div>
    </div>
  </div>
</section>
<?php get_footer(); ?>