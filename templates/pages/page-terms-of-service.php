<?php
/**
 * Template Name: Terms of Service
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">
    <a class="hover:underline" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    <span> / </span>
    <span aria-current="page"><?php esc_html_e('Terms of Service', 'retail-trade-scanner'); ?></span>
  </nav>
  
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php esc_html_e('Terms of Service', 'retail-trade-scanner'); ?></h1>
    <p class="mt-2 text-muted-foreground max-w-2xl"><?php esc_html_e('Please read these terms carefully before using our services. By accessing our platform, you agree to be bound by these terms.', 'retail-trade-scanner'); ?></p>
    <p class="text-sm text-muted-foreground mt-1"><?php esc_html_e('Last updated: January 2024', 'retail-trade-scanner'); ?></p>
  </header>

  <section class="prose dark:prose-invert max-w-none py-6">
    <div class="space-y-8">
      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('1. Acceptance of Terms', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('By accessing and using Retail Trade Scanner, you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by the above, please do not use this service.', 'retail-trade-scanner'); ?></p>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('2. Description of Service', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm mb-3"><?php esc_html_e('Retail Trade Scanner provides stock analysis tools, market data, portfolio tracking, and related financial information services. Our services include:', 'retail-trade-scanner'); ?></p>
        <ul class="space-y-2 text-sm">
          <li>• <?php esc_html_e('Stock screening and filtering tools', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Portfolio tracking and performance analytics', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Price alerts and notifications', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Market data and news aggregation', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('API access for developers', 'retail-trade-scanner'); ?></li>
        </ul>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('3. User Accounts', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm mb-3"><?php esc_html_e('When you create an account with us, you must provide information that is accurate, complete, and current at all times. You are responsible for:', 'retail-trade-scanner'); ?></p>
        <ul class="space-y-2 text-sm">
          <li>• <?php esc_html_e('Safeguarding your password and account information', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('All activities that occur under your account', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Immediately notifying us of any unauthorized use', 'retail-trade-scanner'); ?></li>
        </ul>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('4. Acceptable Use', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm mb-3"><?php esc_html_e('You agree not to use our service:', 'retail-trade-scanner'); ?></p>
        <ul class="space-y-2 text-sm">
          <li>• <?php esc_html_e('For any unlawful purpose or to solicit others to unlawful acts', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('To violate any international, federal, provincial, or state regulations, rules, laws, or local ordinances', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('To transmit or create harmful code, viruses, or malware', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('To collect user information without permission', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('To interfere with or circumvent security features', 'retail-trade-scanner'); ?></li>
        </ul>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('5. Investment Disclaimer', 'retail-trade-scanner'); ?></h2>
        <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 p-4 rounded-lg">
          <p class="text-sm font-medium mb-2"><?php esc_html_e('IMPORTANT INVESTMENT DISCLAIMER', 'retail-trade-scanner'); ?></p>
          <p class="text-sm"><?php esc_html_e('Our platform provides informational tools and data for educational purposes only. We do not provide investment advice, recommendations, or guidance. All investment decisions are your own responsibility. Past performance does not guarantee future results. Trading stocks involves substantial risk of loss and is not suitable for all investors.', 'retail-trade-scanner'); ?></p>
        </div>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('6. Data Accuracy', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('While we strive to provide accurate and up-to-date information, we cannot guarantee the accuracy, completeness, or timeliness of any data provided. Market data may be delayed and should not be relied upon for time-sensitive trading decisions.', 'retail-trade-scanner'); ?></p>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('7. Subscription and Billing', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm mb-3"><?php esc_html_e('Our paid services are billed on a subscription basis. By subscribing, you agree that:', 'retail-trade-scanner'); ?></p>
        <ul class="space-y-2 text-sm">
          <li>• <?php esc_html_e('Your subscription will automatically renew unless cancelled', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('You will be charged the then-current subscription fee', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('You can cancel your subscription at any time', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Refunds are provided according to our refund policy', 'retail-trade-scanner'); ?></li>
        </ul>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('8. Limitation of Liability', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('In no event shall Retail Trade Scanner be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses, resulting from your use of the service.', 'retail-trade-scanner'); ?></p>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('9. Changes to Terms', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('We reserve the right to modify or replace these terms at any time. If a revision is material, we will try to provide at least 30 days notice prior to any new terms taking effect.', 'retail-trade-scanner'); ?></p>
      </div>

      <div class="bg-muted/30 p-4 rounded-lg">
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Contact Information', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('If you have any questions about these Terms of Service, please contact us:', 'retail-trade-scanner'); ?></p>
        <div class="mt-2 text-sm">
          <p><strong><?php esc_html_e('Email:', 'retail-trade-scanner'); ?></strong> legal@retailtradescanner.com</p>
          <p><strong><?php esc_html_e('Contact Form:', 'retail-trade-scanner'); ?></strong> <a href="<?php echo esc_url(home_url('/contact/')); ?>" class="text-primary hover:underline"><?php esc_html_e('Contact Us', 'retail-trade-scanner'); ?></a></p>
        </div>
      </div>
    </div>
  </section>
</main>

<?php get_footer(); ?>