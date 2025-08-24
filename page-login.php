<?php
/**
 * Template Name: Login
 */
if (is_user_logged_in()) { wp_redirect(home_url('/dashboard/')); exit; }
get_header(); ?>

<section class="glass-section">
  <div class="container" style="max-width:720px;margin:0 auto;">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php _e('Sign in to Stock Scanner', 'stock-scanner'); ?></h1>
      <p class="section-subtitle"><?php _e('Access your dashboard, watchlists and premium tools', 'stock-scanner'); ?></p>
    </header>

    <div class="card glass-card">
      <div class="card-body">
        <?php
          $redirect = isset($_GET['redirect_to']) ? esc_url_raw($_GET['redirect_to']) : home_url('/dashboard/');
          wp_login_form(array(
            'echo'           => true,
            'redirect'       => $redirect,
            'remember'       => true,
            'label_username' => __('Username or Email', 'stock-scanner'),
            'label_password' => __('Password', 'stock-scanner'),
            'label_remember' => __('Remember Me', 'stock-scanner'),
            'label_log_in'   => __('Sign In', 'stock-scanner'),
          ));
        ?>
        <div style="display:flex;justify-content:space-between;gap:1rem;margin-top:1rem;flex-wrap:wrap">
          <a class="btn btn-outline" href="<?php echo esc_url(wp_registration_url()); ?>"><?php _e('Create account', 'stock-scanner'); ?></a>
          <a class="btn btn-outline" href="<?php echo esc_url(wp_lostpassword_url()); ?>"><?php _e('Forgot password?', 'stock-scanner'); ?></a>
        </div>
      </div>
    </div>
  </div>
</section>

<?php get_footer(); ?>