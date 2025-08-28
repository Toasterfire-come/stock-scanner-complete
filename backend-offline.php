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
      <h1 class="page-title"><?php esc_html_e('Service temporarily unavailable', 'retail-trade-scanner'); ?></h1>
      <p class="page-description"><?php esc_html_e('Our backend service is currently offline. Please try again shortly.', 'retail-trade-scanner'); ?></p>
    </div>

    <?php if (current_user_can('manage_options')): ?>
      <div class="card">
        <div class="card-header">
          <h2 class="card-title"><?php esc_html_e('Connectivity & Session (Admin-only)', 'retail-trade-scanner'); ?></h2>
          <p class="card-subtitle"><?php esc_html_e('Live diagnostics to help you debug connectivity issues', 'retail-trade-scanner'); ?></p>
        </div>
        <div class="card-body">
          <div class="diagnostic-grid">
            <div class="card">
              <div class="card-header"><strong><?php esc_html_e('Current User', 'retail-trade-scanner'); ?></strong></div>
              <div class="card-body">
                <?php $u = wp_get_current_user(); ?>
                <ul>
                  <li><?php esc_html_e('ID:', 'retail-trade-scanner'); ?> <code><?php echo esc_html($u->ID); ?></code></li>
                  <li><?php esc_html_e('Username:', 'retail-trade-scanner'); ?> <code><?php echo esc_html($u->user_login); ?></code></li>
                  <li><?php esc_html_e('Email:', 'retail-trade-scanner'); ?> <code><?php echo esc_html($u->user_email); ?></code></li>
                  <li><?php esc_html_e('Roles:', 'retail-trade-scanner'); ?> <code><?php echo esc_html(implode(', ', $u->roles)); ?></code></li>
                  <?php
                  $plan = function_exists('pmpro_getMembershipLevelForUser') ? pmpro_getMembershipLevelForUser($u->ID) : null;
                  ?>
                  <li><?php esc_html_e('PMPro Level:', 'retail-trade-scanner'); ?> <code><?php echo $plan ? intval($plan->id) . ' (' . esc_html($plan->name) . ')' : esc_html__('None', 'retail-trade-scanner'); ?></code></li>
                </ul>
              </div>
            </div>

            <div class="card">
              <div class="card-header"><strong><?php esc_html_e('Cookie Presence', 'retail-trade-scanner'); ?></strong></div>
              <div class="card-body">
                <ul id="cookie-list">
                  <li><?php esc_html_e('Loading cookies…', 'retail-trade-scanner'); ?></li>
                </ul>
              </div>
            </div>

            <div class="card diagnostic-full-width">
              <div class="card-header d-flex justify-content-between align-items-center">
                <strong><?php esc_html_e('Raw Health JSON', 'retail-trade-scanner'); ?></strong>
                <button class="btn btn-sm btn-secondary" id="refresh-health"><?php esc_html_e('Refresh', 'retail-trade-scanner'); ?></button>
              </div>
              <div class="card-body">
                <pre id="health-json" class="health-json-output loading">
<?php esc_html_e('Fetching…', 'retail-trade-scanner'); ?>
                </pre>
              </div>
            </div>
          </div>
        </div>
      </div>

      <script>
        (function(){
          const ajaxUrl = '<?php echo esc_js(admin_url('admin-ajax.php')); ?>';
          const nonce = '<?php echo esc_js(wp_create_nonce('retail_trade_scanner_theme_nonce')); ?>';
          const $health = document.getElementById('health-json');
          const $refresh = document.getElementById('refresh-health');
          const $cookieList = document.getElementById('cookie-list');

          function renderCookies(){
            const raw = document.cookie || '';
            const items = raw.split(';').map(v => v.trim()).filter(Boolean);
            const important = ['wordpress_logged_in', 'sessionid', 'csrftoken', 'wp-settings', 'wp_lang'];
            const ul = [];
            ul.push(`<li><?php esc_html_e('Total cookies:', 'retail-trade-scanner'); ?> <strong>${items.length}</strong></li>`);
            important.forEach(key => {
              const found = items.find(i => i.startsWith(key));
              const presentLabel = '<?php echo esc_js(__('present', 'retail-trade-scanner')); ?>';
              const missingLabel = '<?php echo esc_js(__('missing', 'retail-trade-scanner')); ?>';
              ul.push(`<li>${key}: ${found ? '<span class="status-present">' + presentLabel + '</span>' : '<span class="status-missing">' + missingLabel + '</span>'}</li>`);
            });
            // Show first 5 full cookies for debug
            items.slice(0,5).forEach((c, idx) => ul.push(`<li>cookie[${idx}]: <code>${c.replace(/</g,'&lt;')}</code></li>`));
            $cookieList.innerHTML = ul.join('');
          }

          async function fetchHealth(){
            $health.textContent = '<?php echo esc_js(__('Fetching…', 'retail-trade-scanner')); ?>';
            try {
              const res = await fetch(ajaxUrl, {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: new URLSearchParams({action:'retail_trade_scanner_get_health', nonce})
              });
              const data = await res.json();
              if (data.success) {
                $health.textContent = JSON.stringify(data.data, null, 2);
              } else {
                const errorMsg = '<?php echo esc_js(__('Error:', 'retail-trade-scanner')); ?>';
                $health.textContent = errorMsg + ' ' + (data.data && data.data.message ? data.data.message : '<?php echo esc_js(__('Unknown error', 'retail-trade-scanner')); ?>');
              }
            } catch (e) {
              const errorMsg = '<?php echo esc_js(__('Request failed:', 'retail-trade-scanner')); ?>';
              $health.textContent = errorMsg + ' ' + e.message;
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