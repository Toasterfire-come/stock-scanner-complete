<?php /* Template Name: Login */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content" style="max-width:480px;">
    <div class="card" style="padding:20px;">
      <h1 style="color:var(--navy); margin:0 0 8px;">Sign in</h1>
      <form id="loginForm" onsubmit="return false;">
        <input id="lEmail" class="input" type="email" placeholder="Email" />
        <input id="lPass" class="input" type="password" placeholder="Password" />
        <button id="lBtn" class="btn btn-primary" style="margin-top:12px; width:100%;">Sign in</button>
      </form>
      <div class="muted" style="margin-top:8px;">No account? <a href="<?php echo esc_url(home_url('/signup')); ?>">Create one</a></div>
    </div>
  </div>
</section>
<script defer>
(function(){
  document.addEventListener('DOMContentLoaded', function(){
    document.getElementById('lBtn').addEventListener('click', function(){
      const email = document.getElementById('lEmail').value.trim();
      if(!email) return alert('Enter email');
      localStorage.setItem('finm_user', JSON.stringify({ name: email.split('@')[0], email }));
      if(!localStorage.getItem('finm_usage')){ localStorage.setItem('finm_usage', JSON.stringify({ limit: 1000, used: 0, month: new Date().toISOString().slice(0,7) })); }
      window.location.href = '/dashboard';
    });
  });
})();
</script>
<?php get_footer(); ?>