<?php
if (!defined('ABSPATH')) { exit; }

function rts_analytics_id() {
  return apply_filters('rts_analytics_id', ''); // Hook allows setting GA4 ID externally
}

function rts_enqueue_consent_banner() {
  ?>
  <div id="rts-consent" style="position:fixed;bottom:20px;left:20px;right:20px;max-width:640px;margin:0 auto;background:#fff;border:1px solid var(--border);box-shadow:0 6px 24px rgba(0,0,0,.08);padding:12px 14px;border-radius:12px;z-index:9999;display:none;">
    <div style="display:flex;gap:12px;align-items:center;justify-content:space-between;">
      <div style="font-size:14px;"><?php echo wp_kses_post( sprintf( __( 'We use cookies to enhance your experience and analyze traffic. See our %s.', 'rts' ), '<a href="' . esc_url( site_url('/legal/cookies') ) . '">' . esc_html__( 'Cookie Policy', 'rts' ) . '</a>' ) ); ?></div>
      <div style="display:flex;gap:8px;">
        <button id="rts-consent-decline" class="btn btn-outline" type="button">Decline</button>
        <button id="rts-consent-accept" class="btn btn-primary" type="button">Accept</button>
      </div>
    </div>
  </div>
  <script>
    (function(){
      function hasConsent(){ return document.cookie.indexOf('rts_consent=1') !== -1; }
      function setConsent(v){ var d=new Date(); d.setFullYear(d.getFullYear()+1); document.cookie = 'rts_consent='+ (v? '1':'0') +'; path=/; expires='+d.toUTCString(); }
      var el = document.getElementById('rts-consent');
      if (!hasConsent()) { el.style.display='block'; }
      document.getElementById('rts-consent-accept').addEventListener('click', function(){ setConsent(true); el.style.display='none'; window.dispatchEvent(new Event('rts-consented')); });
      document.getElementById('rts-consent-decline').addEventListener('click', function(){ setConsent(false); el.style.display='none'; });
    })();
  </script>
  <?php
}
add_action('wp_footer', 'rts_enqueue_consent_banner');

function rts_inject_analytics() {
  $ga = rts_analytics_id();
  if (!$ga) { return; }
  ?>
  <script>
    (function(){
      function loadGA(){
        var s = document.createElement('script'); s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=<?php echo esc_js($ga); ?>'; document.head.appendChild(s);
        window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} window.gtag = gtag; gtag('js', new Date()); gtag('config', '<?php echo esc_js($ga); ?>');
      }
      function hasConsent(){ return document.cookie.indexOf('rts_consent=1') !== -1; }
      if (hasConsent()) { loadGA(); }
      window.addEventListener('rts-consented', loadGA);
    })();
  </script>
  <?php
}
add_action('wp_head', 'rts_inject_analytics', 9);