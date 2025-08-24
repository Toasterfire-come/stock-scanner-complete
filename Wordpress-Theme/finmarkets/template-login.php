<?php /* Template Name: Login */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content" style="max-width:480px;">
    <div class="card" style="padding:20px;">
      <h1 style="color:var(--navy); margin:0 0 8px;">Login</h1>
      <form id="loginForm" onsubmit="return false;">
        <input id="lEmail" class="input" type="email" placeholder="Email" />
        <input id="lPass" class="input" type="password" placeholder="Password" />
        <button id="lBtn" class="btn btn-primary" style="margin-top:12px;">Sign in</button>
      </form>
      <div class="muted" style="margin-top:8px;">Demo only. No real auth.</div>
    </div>
  </div>
</section>
<script defer>
(function(){
  document.addEventListener('DOMContentLoaded', function(){
    document.getElementById('lBtn').addEventListener('click', function(){
      const email = document.getElementById('lEmail').value.trim();
      if(!email) return alert('Enter email');
      localStorage.setItem('finm_user', JSON.stringify({ name: email.split('@')[0] }));
      alert('Signed in (demo).');
    });
  });
})();
</script>
<?php get_footer(); ?>