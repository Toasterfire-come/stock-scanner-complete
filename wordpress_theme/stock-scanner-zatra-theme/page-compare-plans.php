<?php
/**
 * Template Name: Compare Plans
 * Description: Side-by-side plan comparison with detailed feature matrix using Zatra styling
 */

get_header(); ?>

<div class="compare-plans-container">
	<div class="container">
		<div class="page-header text-center">
			<h1 class="page-title">Compare Our Plans</h1>
			<p class="page-subtitle">Choose the plan that fits your workflow. Clear limits, honest features, and professional tools.</p>
		</div>

		<div class="comparison-card">
			<div class="table-wrapper">
				<table class="comparison-table">
					<thead>
						<tr>
							<th class="feature-col">Features</th>
							<th class="plan-col free">
								<div class="plan-header">
									<h3>Free</h3>
									<div class="price-display">
										<span class="price">$0</span>
										<span class="period">/month</span>
									</div>
									<button class="btn btn-outline w-full mt-2" onclick="selectPlanCompare('free')">Current Plan</button>
								</div>
							</th>
							<th class="plan-col silver popular">
								<div class="popular-badge">Most Popular</div>
								<div class="plan-header">
									<h3>Silver</h3>
									<div class="price-display">
										<span class="price">$49.99</span>
										<span class="period">/month</span>
									</div>
									<button class="btn btn-primary w-full mt-2" onclick="selectPlanCompare('silver')">Upgrade to Silver</button>
								</div>
							</th>
							<th class="plan-col gold">
								<div class="plan-header">
									<h3>Gold</h3>
									<div class="price-display">
										<span class="price">$79.99</span>
										<span class="period">/month</span>
									</div>
									<button class="btn btn-primary w-full mt-2" onclick="selectPlanCompare('gold')">Upgrade to Gold</button>
								</div>
							</th>
						</tr>
					</thead>
					<tbody>
						<tr class="category-row"><td colspan="4">API Access & Data</td></tr>
						<tr>
							<td>Monthly API Calls</td>
							<td>100</td>
							<td>5,000</td>
							<td>Unlimited</td>
						</tr>
						<tr>
							<td>Real-time Data</td>
							<td><span class="feature-no">✗</span></td>
							<td><span class="feature-yes">✓</span></td>
							<td><span class="feature-yes">✓</span></td>
						</tr>
						<tr>
							<td>Historical Data Access</td>
							<td>1 year</td>
							<td>5 years</td>
							<td>Unlimited</td>
						</tr>

						<tr class="category-row"><td colspan="4">Portfolio & Watchlists</td></tr>
						<tr>
							<td>Portfolios</td>
							<td>1</td>
							<td>Unlimited</td>
							<td>Unlimited</td>
						</tr>
						<tr>
							<td>Stocks per Watchlist</td>
							<td>10</td>
							<td>200</td>
							<td>Unlimited</td>
						</tr>
						<tr>
							<td>Portfolio Analytics</td>
							<td><span class="feature-no">✗</span></td>
							<td><span class="feature-yes">✓</span></td>
							<td><span class="feature-yes">✓</span></td>
						</tr>

						<tr class="category-row"><td colspan="4">Screening & Analysis</td></tr>
						<tr>
							<td>Advanced Stock Screener</td>
							<td><span class="feature-no">✗</span></td>
							<td><span class="feature-yes">✓</span></td>
							<td><span class="feature-yes">✓</span></td>
						</tr>
						<tr>
							<td>AI Insights</td>
							<td><span class="feature-no">✗</span></td>
							<td><span class="feature-no">✗</span></td>
							<td><span class="feature-yes">✓</span></td>
						</tr>

						<tr class="category-row"><td colspan="4">Support</td></tr>
						<tr>
							<td>Support Level</td>
							<td>Community</td>
							<td>Email</td>
							<td>Priority Email</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>
	</div>
</div>

<style>
.compare-plans-container { padding: 2rem 0; background:#ffffff; }
.compare-plans-container .page-title { font-size:2.25rem; font-weight:700; margin:0; }
.compare-plans-container .page-subtitle { color:#6b7280; margin-top:.5rem; }
.comparison-card { background:#ffffff; border-radius:12px; box-shadow:0 2px 10px rgba(0,0,0,0.08); }
.table-wrapper { overflow-x:auto; }
.comparison-table { width:100%; border-collapse:separate; border-spacing:0; }
.comparison-table thead th { padding:1rem; text-align:center; background:#f8fafc; position:sticky; top:0; z-index:1; }
.feature-col { text-align:left; min-width:240px; }
.plan-col { min-width:220px; vertical-align:top; }
.plan-header h3 { margin:.25rem 0 .5rem; font-size:1.1rem; font-weight:700; }
.price-display { font-weight:700; font-size:1.5rem; color:#111827; }
.popular .plan-header { position:relative; }
.popular-badge { position:absolute; top:-10px; right:10px; background:#f59e0b; color:#fff; padding:.25rem .5rem; border-radius:6px; font-size:.75rem; }
.btn { display:inline-block; padding:.6rem 1rem; border-radius:8px; text-decoration:none; font-weight:600; border:1px solid transparent; cursor:pointer; }
.btn-primary { background:#3685fb; color:#fff; border-color:#3685fb; }
.btn-outline { background:#fff; color:#111827; border-color:#e5e7eb; }
.w-full { width:100%; }
.mt-2 { margin-top:.5rem; }
.category-row td { background:#f3f4f6; font-weight:700; color:#111827; padding: .75rem 1rem; }
.comparison-table tbody td { text-align:center; padding:.85rem 1rem; border-top:1px solid #e5e7eb; }
.comparison-table tbody tr td:first-child { text-align:left; font-weight:500; color:#374151; }
.feature-yes { color:#10b981; font-weight:700; }
.feature-no { color:#ef4444; font-weight:700; }
@media (max-width: 768px) { .feature-col { min-width:180px; } .plan-col { min-width:180px; } }
</style>

<script>
function selectPlanCompare(plan) {
	const isLoggedIn = <?php echo is_user_logged_in() ? 'true' : 'false'; ?>;
	const billing = 'monthly';
	if (!isLoggedIn) { window.location.href = `/signup/?plan=${plan}`; return; }
	window.location.href = `/paypal-checkout/?plan=${plan}&billing=${billing}`;
}
</script>

<?php get_footer(); ?>