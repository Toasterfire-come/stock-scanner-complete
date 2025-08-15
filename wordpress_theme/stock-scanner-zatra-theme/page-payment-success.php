<?php
/**
 * Template Name: Payment Success
 */

if (!defined('ABSPATH')) { exit; }
get_header(); ?>

<div class="payment-success-container">
	<div class="container">
		<div class="success-card">
			<div class="icon">✅</div>
			<h1>Thank you for your purchase</h1>
			<p>Your subscription is now active. You can access all features included in your plan.</p>
			<div class="actions">
				<a class="btn btn-primary" href="/dashboard/">Go to Dashboard</a>
				<a class="btn btn-outline" href="/account/">Manage Account</a>
			</div>
			<p class="help">Need help? Email <a href="mailto:Admin@retailtradescanner.com">Admin@retailtradescanner.com</a></p>
		</div>
	</div>
</div>

<style>
.payment-success-container{padding:3rem 0;background:#ffffff}
.success-card{max-width:720px;margin:0 auto;background:#fff;border:1px solid #e5e7eb;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.08);padding:2rem;text-align:center}
.success-card .icon{font-size:2.5rem;margin-bottom:.5rem}
.success-card h1{margin:.25rem 0 1rem;font-size:1.75rem}
.actions{display:flex;gap:.75rem;justify-content:center;margin:1rem 0 0}
.btn{display:inline-block;padding:.6rem 1rem;border-radius:8px;text-decoration:none;font-weight:600;border:1px solid transparent}
.btn-primary{background:#3685fb;color:#fff;border-color:#3685fb}
.btn-outline{background:#fff;color:#111827;border-color:#e5e7eb}
.help{color:#6b7280;margin-top:1rem}
</style>

<?php get_footer(); ?>