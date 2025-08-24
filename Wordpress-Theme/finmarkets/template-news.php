<?php /* Template Name: Market News */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Market News</h1>
      <p class="muted">Mock headlines to demonstrate layout and accessibility.</p>
    </div>
    <div id="newsGrid" class="grid cols-3"></div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  document.addEventListener('DOMContentLoaded', function(){
    const grid = $('#newsGrid');
    grid.innerHTML = (window.MockData?.news||[]).map(n=>`<article class="card" style="padding:14px;"><div class="badge">${n.source}</div><h4 style="margin:8px 0; color:var(--navy);">${n.title}</h4><div class="muted">${n.time}</div></article>`).join('');
  });
})();
</script>
<?php get_footer(); ?>