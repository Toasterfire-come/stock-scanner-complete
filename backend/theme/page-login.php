<?php
/**
 * Template Name: Login
 */

if (is_user_logged_in()) {
    wp_redirect(home_url('/dashboard/'));
    exit;
}

get_header(); ?>

<div class="login-page">
    <div class="container" style="max-width:600px;margin:40px auto;">
        <h1 style="text-align:center;margin-bottom:20px;">Sign in to Stock Scanner</h1>
        <div class="card" style="background:#fff;padding:24px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,0.06);">
            <?php
            $redirect = isset($_GET['redirect_to']) ? esc_url_raw($_GET['redirect_to']) : home_url('/dashboard/');
            wp_login_form(array(
                'echo'           => true,
                'redirect'       => $redirect,
                'remember'       => true,
                'label_username' => __('Username or Email'),
                'label_password' => __('Password'),
                'label_remember' => __('Remember Me'),
                'label_log_in'   => __('Sign In'),
            ));
            ?>
            <p style="margin-top:16px;text-align:center;">
                Don't have an account? <a href="<?php echo esc_url(wp_registration_url()); ?>">Create one</a>
            </p>
        </div>
    </div>
</div>

<?php get_footer(); ?>