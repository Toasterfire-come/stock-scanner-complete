<?php /* Template Name: Market News */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Market News</h1>
      <p class="muted">Plugin news feed will load when available, else fallback to mock items.</p>
    </div>
    <?php if (shortcode_exists('stock_scanner_news')) { echo do_shortcode('[stock_scanner_news]'); } ?>
    <div id="newsGrid" class="grid cols-3"></div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  function render(items){ const grid=$('#newsGrid'); grid.innerHTML = items.map(n=>`<article class=\"card\" style=\"padding:14px;\"><div class=\"badge\">${n.source||''}</div><h4 style=\"margin:8px 0; color:var(--navy);\">${n.title||n.name||'—'}</h4><div class=\"muted\">${n.published_at||n.time||''}</div></article>`).join('')||'<div class="muted">No news available.</div>'; }
  document.addEventListener('DOMContentLoaded', async function(){ render((window.MockData?.news)||[]); });
})();
</script>
<?php get_footer(); ?>