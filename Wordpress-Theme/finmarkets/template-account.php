<?php /* Template Name: Account */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <h1 style="color:var(--navy);">Account</h1>
    <div class="card" style="padding:16px;">
      <div id="accStatus" class="muted">Signed out</div>
      <div style="margin-top:12px; display:flex; gap:8px;">
        <button id="accSignOut" class="btn">Sign out</button>
        <a class="btn btn-primary" href="#pricing">Upgrade</a>
      </div>
    </div>
  </div>
</section>
<script defer>
(function(){
  document.addEventListener('DOMContentLoaded', function(){
    const u = JSON.parse(localStorage.getItem('finm_user')||'null');
    document.getElementById('accStatus').textContent = u?`Signed in as ${u.name}`:'Signed out';
    document.getElementById('accSignOut').addEventListener('click', function(){
      localStorage.removeItem('finm_user'); location.reload();
    });
  });
})();
</script>
<?php get_footer(); ?>