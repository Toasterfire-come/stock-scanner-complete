<?php
/**
 * Template Name: Disclaimer
 * @package RetailTradeScanner
 */
if (!defined('ABSPATH')) { exit; }
get_header();
?>

<main id="primary" class="site-main container mx-auto px-4 py-8">
  <nav class="text-sm text-muted-foreground mb-2" aria-label="Breadcrumbs">
    <a class="hover:underline" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'retail-trade-scanner'); ?></a>
    <span> / </span>
    <span aria-current="page"><?php esc_html_e('Disclaimer', 'retail-trade-scanner'); ?></span>
  </nav>
  
  <header class="mb-6">
    <h1 class="text-3xl font-bold leading-tight"><?php esc_html_e('Legal Disclaimer', 'retail-trade-scanner'); ?></h1>
    <p class="mt-2 text-muted-foreground max-w-2xl"><?php esc_html_e('Important legal and financial disclaimers regarding the use of our trading analysis platform', 'retail-trade-scanner'); ?></p>
    <p class="text-sm text-muted-foreground mt-1"><?php esc_html_e('Last updated: January 2024', 'retail-trade-scanner'); ?></p>
  </header>

  <section class="prose dark:prose-invert max-w-none py-6">
    <div class="space-y-8">
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-6 rounded-lg">
        <h2 class="text-xl font-semibold mb-3 text-red-800 dark:text-red-200"><?php esc_html_e('⚠️ Investment Risk Warning', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm text-red-700 dark:text-red-300"><?php esc_html_e('Trading stocks, options, and other financial instruments involves substantial risk of loss and is not suitable for all investors. The risk of loss in trading can be substantial. You should carefully consider whether such trading is suitable for you in light of your financial condition. Past performance is not indicative of future results.', 'retail-trade-scanner'); ?></p>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('No Investment Advice', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm mb-3"><?php esc_html_e('Retail Trade Scanner is an informational platform that provides data analysis tools and market information. We do not provide:', 'retail-trade-scanner'); ?></p>
        <ul class="space-y-2 text-sm">
          <li>• <?php esc_html_e('Investment advice or recommendations', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Buy or sell signals or recommendations', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Financial planning or wealth management services', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Tax, legal, or accounting advice', 'retail-trade-scanner'); ?></li>
        </ul>
        <p class="text-sm mt-3"><?php esc_html_e('All content is for informational and educational purposes only. Any trading or investment decisions are entirely your own responsibility.', 'retail-trade-scanner'); ?></p>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Data Accuracy and Reliability', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm mb-3"><?php esc_html_e('While we strive to provide accurate and timely information, we cannot guarantee:', 'retail-trade-scanner'); ?></p>
        <ul class="space-y-2 text-sm">
          <li>• <?php esc_html_e('The accuracy, completeness, or timeliness of any data', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('That our service will be uninterrupted or error-free', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('That any defects will be corrected', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('The availability of any particular stocks or markets', 'retail-trade-scanner'); ?></li>
        </ul>
        <p class="text-sm mt-3"><?php esc_html_e('Market data may be delayed by up to 15 minutes or more. Real-time data, where available, should not be relied upon for time-sensitive trading decisions without independent verification.', 'retail-trade-scanner'); ?></p>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Forward-Looking Statements', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('Our platform may contain forward-looking statements about market trends, stock performance, or economic conditions. These statements are based on current expectations and assumptions and involve significant risks and uncertainties. Actual results may differ materially from those expressed or implied in these statements.', 'retail-trade-scanner'); ?></p>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Third-Party Information', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('Our platform may include information, data, or content from third-party sources. We do not endorse, guarantee, or assume responsibility for the accuracy or reliability of any third-party information. Users should independently verify any third-party information before making investment decisions.', 'retail-trade-scanner'); ?></p>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Professional Advice Recommendation', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('Before making any investment decisions, we strongly recommend that you:', 'retail-trade-scanner'); ?></p>
        <ul class="space-y-2 text-sm mt-3">
          <li>• <?php esc_html_e('Consult with a qualified financial advisor', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Review your financial situation and investment objectives', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Understand the risks associated with trading', 'retail-trade-scanner'); ?></li>
          <li>• <?php esc_html_e('Only invest money you can afford to lose', 'retail-trade-scanner'); ?></li>
        </ul>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Limitation of Liability', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('Retail Trade Scanner, its affiliates, directors, employees, and agents shall not be liable for any direct, indirect, incidental, special, consequential, or punitive damages arising from or related to the use of our platform, including but not limited to trading losses, lost profits, or any other financial losses.', 'retail-trade-scanner'); ?></p>
      </div>

      <div>
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Regulatory Compliance', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('Different jurisdictions have different regulations regarding financial services and investment advice. It is your responsibility to ensure that your use of our platform complies with all applicable laws and regulations in your jurisdiction.', 'retail-trade-scanner'); ?></p>
      </div>

      <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-4 rounded-lg">
        <h2 class="text-xl font-semibold mb-3"><?php esc_html_e('Questions or Concerns?', 'retail-trade-scanner'); ?></h2>
        <p class="text-sm"><?php esc_html_e('If you have any questions about this disclaimer or our services, please contact us:', 'retail-trade-scanner'); ?></p>
        <div class="mt-2 text-sm">
          <p><strong><?php esc_html_e('Email:', 'retail-trade-scanner'); ?></strong> legal@retailtradescanner.com</p>
          <p><strong><?php esc_html_e('Contact Form:', 'retail-trade-scanner'); ?></strong> <a href="<?php echo esc_url(home_url('/contact/')); ?>" class="text-primary hover:underline"><?php esc_html_e('Contact Us', 'retail-trade-scanner') . ' →'; ?></a></p>
        </div>
      </div>
    </div>
  </section>
</main>

<?php get_footer(); ?>