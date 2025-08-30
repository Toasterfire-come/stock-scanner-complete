<?php
/**
 * Template Name: Privacy Policy
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">
    <a class="hover:underline" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    <span> / </span>
    <span aria-current="page"><?php esc_html_e('Privacy Policy', 'retail-trade-scanner'); ?></span>
  </nav>
  
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php esc_html_e('Privacy Policy', 'retail-trade-scanner'); ?></h1>
    <p class="mt-2 text-muted-foreground max-w-2xl"><?php esc_html_e('Your privacy is important to us. This policy explains how we collect, use, and protect your information.', 'retail-trade-scanner'); ?></p>
    <p class="text-sm text-muted-foreground mt-1"><?php esc_html_e('Last updated: January 2024', 'retail-trade-scanner'); ?></p>
  </header>

  <section class="prose dark:prose-invert max-w-none py-6">
    <div class="space-y-8">
      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Information We Collect', 'retail-trade-scanner'); ?></h2>
        <div class="space-y-4">
          <div>
            <h3 class="font-medium mb-2"><?php esc_html_e('Personal Information', 'retail-trade-scanner'); ?></h3>
            <p class="text-sm"><?php esc_html_e('We may collect personal information such as your name, email address, and payment information when you create an account or subscribe to our services.', 'retail-trade-scanner'); ?></p>
          </div>
          <div>
            <h3 class="font-medium mb-2"><?php esc_html_e('Usage Data', 'retail-trade-scanner'); ?></h3>
            <p class="text-sm"><?php esc_html_e('We collect information about how you use our platform, including pages visited, features used, and interaction patterns to improve our services.', 'retail-trade-scanner'); ?></p>
          </div>
          <div>
            <h3 class="font-medium mb-2"><?php esc_html_e('Technical Information', 'retail-trade-scanner'); ?></h3>
            <p class="text-sm"><?php esc_html_e('We automatically collect technical information such as IP address, browser type, device information, and cookies to ensure platform functionality.', 'retail-trade-scanner'); ?></p>
          </div>
        </div>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('How We Use Your Information', 'retail-trade-scanner'); ?></h2>
        <ul class="space-y-2 text-sm">
          <li>• <?php esc_html_e('Provide and maintain our trading analysis services', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Process payments and manage your subscription', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Send important service updates and notifications', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Improve our platform based on usage patterns', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Provide customer support and respond to inquiries', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Ensure platform security and prevent fraud', 'retail-trade-scanner'); ?></li>
        </ul>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Information Sharing', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm mb-3"><?php esc_html_e('We do not sell, trade, or otherwise transfer your personal information to third parties, except in the following circumstances:', 'retail-trade-scanner'); ?></p>
        <ul class="space-y-2 text-sm">
          <li>• <?php esc_html_e('With your explicit consent', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('To comply with legal obligations or court orders', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('With trusted service providers who assist in operating our platform', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('To protect our rights, property, or safety, or that of our users', 'retail-trade-scanner'); ?></li>
        </ul>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Data Security', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('We implement industry-standard security measures to protect your information, including encryption, secure servers, and regular security audits. However, no method of transmission over the internet is 100% secure.', 'retail-trade-scanner'); ?></p>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Your Rights', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm mb-3"><?php esc_html_e('You have the right to:', 'retail-trade-scanner'); ?></p>
        <ul class="space-y-2 text-sm">
          <li>• <?php esc_html_e('Access and receive a copy of your personal data', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Correct any inaccurate or incomplete information', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Request deletion of your personal data', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Object to or restrict certain processing activities', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Withdraw consent where processing is based on consent', 'retail-trade-scanner'); ?></li>
        </ul>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Cookies and Tracking', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('We use cookies and similar technologies to enhance your experience, analyze usage, and provide personalized content. You can control cookie settings through your browser preferences.', 'retail-trade-scanner'); ?></p>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Changes to This Policy', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('We may update this privacy policy from time to time. We will notify you of any changes by posting the new policy on this page and updating the "Last updated" date.', 'retail-trade-scanner'); ?></p>
      </div>

      <div class="bg-muted/30 p-4 rounded-lg">
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Contact Us', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('If you have any questions about this privacy policy or our data practices, please contact us:', 'retail-trade-scanner'); ?></p>
        <div class="mt-2 text-sm">
          <p><strong><?php esc_html_e('Email:', 'retail-trade-scanner'); ?></strong> privacy@retailtradescanner.com</p>
          <p><strong><?php esc_html_e('Contact Form:', 'retail-trade-scanner'); ?></strong> <a href="<?php echo esc_url(home_url('/contact/')); ?>" class="text-primary hover:underline"><?php esc_html_e('Contact Us', 'retail-trade-scanner'); ?></a></p>
        </div>
      </div>
    </div>
  </section>
</main>

<?php get_footer(); ?>