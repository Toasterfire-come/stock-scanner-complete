<?php /* Template Name: Login */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content" style="max-width:480px;">
    <div class="card" style="padding:20px;">
      <h1 style="color:var(--navy); margin:0 0 8px;">Sign in</h1>
      <form id="loginForm" onsubmit="return false;">
        <input id="lEmail" class="input" type="text" placeholder="Username or Email" autocomplete="username" />
        <input id="lPass" class="input" type="password" placeholder="Password" autocomplete="current-password" />
        <button id="lBtn" class="btn btn-primary" style="margin-top:12px; width:100%;">Sign in</button>
        <div id="lMsg" class="muted" style="margin-top:8px;">&nbsp;</div>
      </form>
      <div class="muted" style="margin-top:8px;">No account? <a href="<?php echo esc_url(home_url('/signup')); ?>">Create one</a></div>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  function setMsg(t, good){ const el=$('#lMsg'); el.textContent=t; el.style.color = good? '#0f8a42' : 'var(--muted)'; }
  document.addEventListener('DOMContentLoaded', function(){
    $('#lBtn').addEventListener('click', async function(){
      const username = $('#lEmail').value.trim();
      const password = $('#lPass').value.trim();
      if(!username || !password){ return setMsg('Enter your username and password'); }
      setMsg('Signing in…');
      try{
        if(window.finmApi && (window.finmConfig?.hasApiBase)){
          const res = await window.finmApi.authLogin(username, password);
          if(res && res.success !== false){
            // UI-only convenience; actual auth should rely on backend session cookie
            localStorage.setItem('finm_user', JSON.stringify({ name: res?.data?.username || username, email: res?.data?.email || '' }));
            setMsg('Signed in', true); window.location.href = '/dashboard'; return;
          }
          setMsg(res?.message || 'Login failed');
        } else {
          // Fallback demo
          localStorage.setItem('finm_user', JSON.stringify({ name: username, email: username.includes('@')?username:'' }));
          setMsg('Signed in (demo)', true); window.location.href = '/dashboard';
        }
      }catch(e){ setMsg('Login error'); }
    });
  });
})();
</script>
<?php get_footer(); ?>