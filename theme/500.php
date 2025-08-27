<?php
/**
 * 500 Error Template
 * Displayed when a server error occurs
 */
get_header();
?>
<main id="main-content" class="site-main">
  <div class="container">
    <?php get_template_part('template-parts/breadcrumbs'); ?>
    <div class="page-header">
      <h1 class="page-title"><?php _e('Server Error', 'finmarkets'); ?></h1>
      <p class="page-description"><?php _e('Something went wrong on our servers. We\'re working to fix this issue. Please try again in a few minutes.', 'finmarkets'); ?></p>
      <div class="cta-buttons">
        <a class="btn btn-primary" href="<?php echo esc_url(home_url('/')); ?>">
          <span><?php _e('Go to Homepage', 'finmarkets'); ?></span>
        </a>
        <button class="btn btn-secondary" onclick="history.back()">
          <span><?php _e('Go Back', 'finmarkets'); ?></span>
        </button>
      </div>
    </div>
    
    <div class="grid-2">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title"><?php _e('What happened?', 'finmarkets'); ?></h3>
        </div>
        <div class="card-body">
          <p><?php _e('Our server encountered an unexpected condition that prevented it from fulfilling your request. This is usually a temporary issue.', 'finmarkets'); ?></p>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3 class="card-title"><?php _e('What can you do?', 'finmarkets'); ?></h3>
        </div>
        <div class="card-body">
          <ul>
            <li><?php _e('Wait a few minutes and try again', 'finmarkets'); ?></li>
            <li><?php _e('Check our status page for updates', 'finmarkets'); ?></li>
            <li><?php _e('Contact support if the issue persists', 'finmarkets'); ?></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</main>
<?php get_footer(); ?>