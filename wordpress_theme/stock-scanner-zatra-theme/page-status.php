<?php
/*
Template Name: Status
*/
get_header();
?>
<main id="primary" class="site-main" role="main">
	<div class="container" style="margin: 2rem auto; max-width: 1100px;">
		<div class="card">
			<h1 style="margin-bottom: .5rem; color: var(--text-primary);">System Status</h1>
			<p style="color: var(--text-secondary); margin-bottom: 1rem;">Real-time status of API endpoints and services</p>
			<div style="display:flex; gap:.75rem; flex-wrap:wrap; margin-bottom:1rem;">
				<a class="btn" href="/endpoint-status/">Open Status Page</a>
				<a class="btn btn-secondary" href="/endpoint-status/?format=json">View JSON</a>
				<a class="btn btn-secondary" href="/api/health/">API Health</a>
			</div>
			<div style="border-top:1px solid var(--border-light); padding-top:1rem; color: var(--text-secondary);">
				<p>If the embedded status doesn’t load, use the links above to view the Django backend’s live status and health endpoints.</p>
			</div>
		</div>
	</div>
</main>
<?php get_footer(); ?>