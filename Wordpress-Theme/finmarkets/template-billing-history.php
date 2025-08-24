<?php /* Template Name: Billing History */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container content">
    <h1 style="color:var(--navy);">Billing History</h1>
    <div class="card" style="padding:16px;">
      <table class="table">
        <thead><tr><th>Date</th><th>Plan</th><th>Amount</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td>2025-08-01</td><td>Pro</td><td>$19</td><td><span class="badge badge-green">Paid</span></td></tr>
          <tr><td>2025-07-01</td><td>Pro</td><td>$19</td><td><span class="badge badge-green">Paid</span></td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>
<?php get_footer(); ?>