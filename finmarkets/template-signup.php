<?php /* Template Name: Signup */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content" style="max-width:520px;">
    <div class="card" style="padding:20px;">
      <h1 style="color:var(--navy); margin:0 0 8px;">Create your account</h1>
      <form id="suForm" onsubmit="return false;">
        <input id="suName" class="input" placeholder="Full name" />
        <input id="suEmail" class="input" type="email" placeholder="Email" />
        <input id="suPass" class="input" type="password" placeholder="Password (min 8)" />
        <button id="suBtn" class="btn btn-primary" style="margin-top:12px; width:100%;">Sign up</button>
      </form>
      <div class="muted" style="margin-top:8px;">Already have an account? <a href="<?php echo esc_url(home_url('/login')); ?>">Sign in</a></div>
    </div>
  </div>
</section>
<script defer>
(function(){
  document.addEventListener('DOMContentLoaded', function(){
    document.getElementById('suBtn').addEventListener('click', function(){
      const name = document.getElementById('suName').value.trim();
      const email = document.getElementById('suEmail').value.trim();
      const pass = document.getElementById('suPass').value.trim();
      if(!name || !email || pass.length < 8) { alert('Fill all fields (password >= 8)'); return; }
      localStorage.setItem('finm_user', JSON.stringify({ name, email }));
      // initialize usage
      localStorage.setItem('finm_usage', JSON.stringify({ limit: 1000, used: 0, month: new Date().toISOString().slice(0,7) }));
      window.location.href = '/dashboard';
    });
  });
})();
</script>
<?php get_footer(); ?>