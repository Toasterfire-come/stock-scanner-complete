<?php
/**
 * Template Name: Dashboard
 * Template for the Stock Scanner dashboard page
 */

get_header(); ?>

<div class="dashboard-container">
    <div class="dashboard-header">
        <h1>Stock Scanner Dashboard</h1>
        <?php if (is_user_logged_in()): ?>
            <div class="user-welcome">
                Welcome back, <?php echo wp_get_current_user()->display_name; ?>!
            </div>
        <?php endif; ?>
    </div>
    
    <div class="dashboard-content">
        <?php if (have_posts()): ?>
            <?php while (have_posts()): the_post(); ?>
                <div class="page-content">
                    <?php the_content(); ?>
                </div>
            <?php endwhile; ?>
        <?php endif; ?>
        
        <?php if (!is_user_logged_in()): ?>
            <div class="login-prompt">
                <h2>Please Log In</h2>
                <p>You need to be logged in to access your dashboard.</p>
                <a href="<?php echo wp_login_url(get_permalink()); ?>" class="btn btn-primary">Login</a>
                <a href="<?php echo wp_registration_url(); ?>" class="btn btn-secondary">Register</a>
            </div>
        <?php endif; ?>
    </div>
</div>

<style>
.dashboard-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.dashboard-header {
    background: linear-gradient(135deg, #2271b1 0%, #135e96 100%);
    color: white;
    padding: 30px;
    border-radius: 12px;
    margin-bottom: 30px;
    text-align: center;
}

.dashboard-header h1 {
    margin: 0 0 10px 0;
    font-size: 2.5em;
}

.user-welcome {
    font-size: 1.2em;
    opacity: 0.9;
}

.dashboard-content {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    overflow: hidden;
}

.page-content {
    padding: 30px;
}

.login-prompt {
    text-align: center;
    padding: 60px 30px;
}

.login-prompt h2 {
    color: #2271b1;
    margin-bottom: 15px;
}

.login-prompt p {
    color: #666;
    margin-bottom: 25px;
    font-size: 1.1em;
}

.btn {
    display: inline-block;
    padding: 12px 24px;
    margin: 0 10px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: bold;
    transition: all 0.3s ease;
}

.btn-primary {
    background: #2271b1;
    color: white;
}

.btn-primary:hover {
    background: #135e96;
}

.btn-secondary {
    background: #646970;
    color: white;
}

.btn-secondary:hover {
    background: #50575e;
}
</style>

<?php get_footer(); ?>