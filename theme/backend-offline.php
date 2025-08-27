<?php
/*
Template Name: Backend Offline
Description: Shows a friendly offline message and an Admin-only "Connectivity & Session" panel
*/
get_header();
?>

<main id="main-content" class="site-main">
  <div class="container">
    <div class="page-header">
      <h1 class="page-title">Service temporarily unavailable</h1>
      <p class="page-description">Our backend service is currently offline. Please try again shortly.</p>
    </div>

    <?php if (current_user_can('manage_options')): ?>
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Connectivity & Session (Admin-only)</h2>
          <p class="card-subtitle">Live diagnostics to help you debug connectivity issues</p>
        </div>
        <div class="card-body">
          <div class="diagnostic-grid">
            <div class="card">
              <div class="card-header"><strong>Current User</strong></div>
              <div class="card-body">
                <?php $u = wp_get_current_user(); ?>
                <ul>
                  <li>ID: <code><?php echo esc_html($u->ID); ?></code></li>
                  <li>Username: <code><?php echo esc_html($u->user_login); ?></code></li>
                  <li>Email: <code><?php echo esc_html($u->user_email); ?></code></li>
                  <li>Roles: <code><?php echo esc_html(implode(', ', $u->roles)); ?></code></li>
                  <?php
                  $plan = function_exists('pmpro_getMembershipLevelForUser') ? pmpro_getMembershipLevelForUser($u->ID) : null;
                  ?>
                  <li>PMPro Level: <code><?php echo $plan ? intval($plan->id) . ' (' . esc_html($plan->name) . ')' : 'None'; ?></code></li>
                </ul>
              </div>
            </div>

            <div class="card">
              <div class="card-header"><strong>Cookie Presence</strong></div>
              <div class="card-body">
                <ul id="cookie-list">
                  <li>Loading cookies…</li>
                </ul>
              </div>
            </div>

            <div class="card diagnostic-full-width">
              <div class="card-header d-flex justify-content-between align-items-center">
                <strong>Raw Health JSON</strong>
                <button class="btn btn-sm btn-secondary" id="refresh-health">Refresh</button>
              </div>
              <div class="card-body">
                <pre id="health-json" class="health-json-output loading">
Fetching…
                </pre>
              </div>
            </div>
          </div>
        </div>
      </div>

      <script>
        (function(){
          const ajaxUrl = '<?php echo esc_js(admin_url('admin-ajax.php')); ?>';
          const nonce = '<?php echo wp_create_nonce('stock_scanner_theme_nonce'); ?>';
          const $health = document.getElementById('health-json');
          const $refresh = document.getElementById('refresh-health');
          const $cookieList = document.getElementById('cookie-list');

          function renderCookies(){
            const raw = document.cookie || '';
            const items = raw.split(';').map(v => v.trim()).filter(Boolean);
            const important = ['wordpress_logged_in', 'sessionid', 'csrftoken', 'wp-settings', 'wp_lang'];
            const ul = [];
            ul.push(`<li>Total cookies: <strong>${items.length}</strong></li>`);
            important.forEach(key => {
              const found = items.find(i => i.startsWith(key));
              ul.push(`<li>${key}: ${found ? '<span class="status-present">present</span>' : '<span class="status-missing">missing</span>'}</li>`);
            });
            // Show first 5 full cookies for debug
            items.slice(0,5).forEach((c, idx) => ul.push(`<li>cookie[${idx}]: <code>${c.replace(/</g,'&lt;')}</code></li>`));
            $cookieList.innerHTML = ul.join('');
          }

          async function fetchHealth(){
            $health.textContent = 'Fetching…';
            try {
              const res = await fetch(ajaxUrl, {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: new URLSearchParams({action:'stock_scanner_get_health', nonce})
              });
              const data = await res.json();
              if (data.success) {
                $health.textContent = JSON.stringify(data.data, null, 2);
              } else {
                $health.textContent = 'Error: ' + (data.data && data.data.message ? data.data.message : 'Unknown error');
              }
            } catch (e) {
              $health.textContent = 'Request failed: ' + e.message;
            }
          }

          renderCookies();
          fetchHealth();
          $refresh.addEventListener('click', function(){ fetchHealth(); });
        })();
      </script>
    <?php endif; ?>
  </div>
</main>

<?php get_footer(); ?>