<?php
/**
 * Template Name: Payment Cancelled
 */

if (!defined('ABSPATH')) { exit; }
get_header(); ?>

<div class="payment-cancelled-container">
	<div class="container">
		<div class="cancelled-card">
			<div class="icon">⚠️</div>
			<h1>Payment was cancelled</h1>
			<p>Your subscription was not charged. You can retry checkout or return to your account.</p>
			<div class="actions">
				<a class="btn btn-primary" href="/premium-plans/">View Plans</a>
				<a class="btn btn-outline" href="/account/">Go to Account</a>
			</div>
			<p class="help">Questions? Email <a href="mailto:Admin@retailtradescanner.com">Admin@retailtradescanner.com</a></p>
		</div>
	</div>
</div>

<style>
.payment-cancelled-container{padding:3rem 0;background:#ffffff}
.cancelled-card{max-width:720px;margin:0 auto;background:#fff;border:1px solid #e5e7eb;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.08);padding:2rem;text-align:center}
.cancelled-card .icon{font-size:2.5rem;margin-bottom:.5rem}
.cancelled-card h1{margin:.25rem 0 1rem;font-size:1.75rem}
.actions{display:flex;gap:.75rem;justify-content:center;margin:1rem 0 0}
.btn{display:inline-block;padding:.6rem 1rem;border-radius:8px;text-decoration:none;font-weight:600;border:1px solid transparent}
.btn-primary{background:#3685fb;color:#fff;border-color:#3685fb}
.btn-outline{background:#fff;color:#111827;border-color:#e5e7eb}
.help{color:#6b7280;margin-top:1rem}
</style>

<?php get_footer(); ?>