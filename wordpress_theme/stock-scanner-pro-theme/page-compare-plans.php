<?php
/**
 * Template Name: Compare Plans
 */
get_header(); ?>
<div class="compare-plans">
  <div class="container" style="max-width:1000px;margin:40px auto;padding:0 20px;">
    <h1>Compare Plans</h1>
    <div class="card" style="padding:0;overflow:auto;">
      <table style="width:100%;border-collapse:collapse;">
        <thead>
          <tr style="background:#f5f7fb;">
            <th style="text-align:left;padding:12px;">Feature</th>
            <th style="padding:12px;">Free</th>
            <th style="padding:12px;">Bronze</th>
            <th style="padding:12px;">Silver</th>
            <th style="padding:12px;">Gold</th>
          </tr>
        </thead>
        <tbody>
          <tr><td style="padding:12px;">Daily Scans</td><td>10</td><td>Unlimited</td><td>Unlimited</td><td>Unlimited</td></tr>
          <tr><td style="padding:12px;">Real-time Data</td><td>Basic</td><td>Yes</td><td>Yes</td><td>Yes</td></tr>
          <tr><td style="padding:12px;">Advanced Charts</td><td>-</td><td>Yes</td><td>Yes</td><td>Yes</td></tr>
          <tr><td style="padding:12px;">Options Data</td><td>-</td><td>-</td><td>Yes</td><td>Yes</td></tr>
          <tr><td style="padding:12px;">Level 2 Data</td><td>-</td><td>-</td><td>-</td><td>Yes</td></tr>
          <tr><td style="padding:12px;">AI Insights</td><td>-</td><td>-</td><td>Yes</td><td>Yes</td></tr>
        </tbody>
      </table>
    </div>
    <p style="margin-top:12px;">Ready to upgrade? <a href="/premium-plans/">View Premium Plans</a></p>
  </div>
</div>
<?php get_footer(); ?>