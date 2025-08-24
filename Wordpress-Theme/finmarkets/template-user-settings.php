<?php /* Template Name: User Settings */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <h1 style="color:var(--navy);">User Settings</h1>
    <div class="card" style="padding:16px;">
      <form id="usForm" class="grid cols-2" onsubmit="return false;">
        <div>
          <label for="usName" class="muted">Display name</label>
          <input id="usName" class="input" placeholder="Your name" />
        </div>
        <div>
          <label for="usTheme" class="muted">Theme</label>
          <select id="usTheme" class="select"><option value="light">Light</option><option value="dark">Dark</option></select>
        </div>
        <div>
          <button id="usSave" class="btn btn-primary">Save</button>
        </div>
      </form>
    </div>
  </div>
</section>
<script defer>
(function(){
  const $ = s => document.querySelector(s);
  const getU = () => JSON.parse(localStorage.getItem('finm_user')||'{}');
  const setU = (x) => localStorage.setItem('finm_user', JSON.stringify(x));
  function render(){
    const u=getU();
    $('#usName').value = u.name||'';
    $('#usTheme').value = u.theme||'light';
  }
  document.addEventListener('DOMContentLoaded', function(){
    render();
    $('#usSave').addEventListener('click', ()=>{
      setU({ name: $('#usName').value.trim(), theme: $('#usTheme').value });
      alert('Saved!');
    })
  });
})();
</script>
<?php get_footer(); ?>