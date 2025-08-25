<?php /* Template Name: Market News */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Market News</h1>
      <p class="muted">Live when API is configured, otherwise fallback to mock items.</p>
    </div>
    <?php if (shortcode_exists('stock_scanner_news')) { echo do_shortcode('[stock_scanner_news]'); } ?>
    <div id="newsGrid" class="grid cols-3"></div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  function render(items){ const grid=$('#newsGrid'); grid.innerHTML = items.map(n=>`<article class="card" style="padding:14px;"><div class="badge">${n.source||''}</div><h4 style="margin:8px 0; color:var(--navy);">${n.title||n.name||'—'}</h4><div class="muted">${n.published_at||n.time||''}</div></article>`).join('')||'<div class="muted">No news available.</div>'; }
  async function loadNews(){
    // try API via window.finmApi
    if(window.finmApi && (window.finmConfig?.hasApiBase)){
      try {
        let items = await window.finmApi.wpNews({ limit: 12 });
        if(!Array.isArray(items) || !items.length){
          const n2 = await window.finmApi.apiGet('news/', { limit: 12 });
          items = Array.isArray(n2) ? n2 : (n2?.data || []);
        }
        const mapped = items.map(n=>({ title:n.title||n.headline||n.name, source:n.source||n.publisher||'', published_at:n.published_at||n.time||'' }));
        render(mapped);
        return;
      } catch(e) { /* fall through to mock */ }
    }
    // fallback to mock
    render((window.MockData?.news)||[]);
  }
  document.addEventListener('DOMContentLoaded', loadNews);
})();
</script>
<?php get_footer(); ?>