<?php
// (appended) Shortcodes for professional embeds
if (!defined('ABSPATH')) { exit; }
add_shortcode('finm_health', function(){
  $rest = esc_url( rest_url('finm/v1/health') );
  ob_start(); ?>
  <span class="badge" id="finmHealthBadge">Checking…</span>
  <script defer>(function(){document.addEventListener('DOMContentLoaded', async function(){ const el=document.getElementById('finmHealthBadge'); try{ const r=await fetch('<?php echo $rest; ?>'); const j=await r.json(); const st=(j.status||'').toLowerCase(); if(st==='healthy'){ el.textContent='API: Healthy'; el.classList.add('badge-green'); } else { el.textContent='API: Degraded'; el.classList.add('badge-red'); } }catch(e){ el.textContent='API: Offline'; el.classList.add('badge-red'); } });})();</script>
  <?php return ob_get_clean();
});