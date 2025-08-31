<?php /* Template Name: Documentation */
$rts_title = 'Documentation';
$rts_subtitle = 'API and product documentation.';
ob_start(); ?>
  <ul style="margin:0;padding-left:18px;">
    <li>REST base: /wp-json/stock-scanner/v1/</li>
    <li>Stocks: /wp-json/stock-scanner/v1/stocks</li>
    <li>Search: /wp-json/stock-scanner/v1/search</li>
    <li>Trending: /wp-json/stock-scanner/v1/trending</li>
    <li>Alerts: /wp-json/stock-scanner/v1/alerts/create</li>
  </ul>
<?php $rts_html = ob_get_clean();
require locate_template('partials/template-generic.php');