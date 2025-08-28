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
      <h1 class="page-title"><?php esc_html_e('Server Error', 'retail-trade-scanner'); ?></h1>
      <p class="page-description"><?php esc_html_e('Something went wrong on our servers. We\'re working to fix this issue. Please try again in a few minutes.', 'retail-trade-scanner'); ?></p>
      <div class="cta-buttons">
        <a class="btn btn-primary" href="<?php echo esc_url(home_url('/')); ?>">
          <span><?php esc_html_e('Go to Homepage', 'retail-trade-scanner'); ?></span>
        </a>
        <button class="btn btn-secondary" onclick="history.back()">
          <span><?php esc_html_e('Go Back', 'retail-trade-scanner'); ?></span>
        </button>
      </div>
    </div>
    
    <div class="grid-2">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title"><?php esc_html_e('What happened?', 'retail-trade-scanner'); ?></h3>
        </div>
        <div class="card-body">
          <p><?php esc_html_e('Our server encountered an unexpected condition that prevented it from fulfilling your request. This is usually a temporary issue.', 'retail-trade-scanner'); ?></p>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3 class="card-title"><?php esc_html_e('What can you do?', 'retail-trade-scanner'); ?></h3>
        </div>
        <div class="card-body">
          <ul>
            <li><?php esc_html_e('Wait a few minutes and try again', 'retail-trade-scanner'); ?></li>
            <li><?php esc_html_e('Check our status page for updates', 'retail-trade-scanner'); ?></li>
            <li><?php esc_html_e('Contact support if the issue persists', 'retail-trade-scanner'); ?></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</main>
<?php get_footer(); ?>