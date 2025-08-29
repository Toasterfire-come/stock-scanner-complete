<?php
/**
 * Template Name: API Docs
 * 
 * Developer documentation for integrating with Retail Trade Scanner APIs
 *
 * @package RetailTradeScanner
 */

get_header();

$layout_args = array(
    'page_title' => __('API Documentation', 'retail-trade-scanner'),
    'page_description' => __('Guides and references for building with the Retail Trade Scanner platform', 'retail-trade-scanner'),
    'page_class' => 'api-docs-page',
    'header_actions' => array(
        array(
            'text' => __('Get API Key', 'retail-trade-scanner'),
            'variant' => 'primary',
            'icon' => 'key'
        )
    )
);

get_template_part('template-parts/layout/main-shell', null, $layout_args);
?>

<div class="grid grid-cols-12 gap-lg">
    <!-- Sidebar Nav -->
    <aside class="col-span-3">
        <nav class="card glass-card api-nav" aria-label="<?php esc_attr_e('API Sections', 'retail-trade-scanner'); ?>">
            <div class="card-header">
                <h3 class="card-title"><?php esc_html_e('On this page', 'retail-trade-scanner'); ?></h3>
            </div>
            <div class="card-body">
                <ul class="toc-list">
                    <li><a href="#overview"><?php esc_html_e('Overview', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="#auth"><?php esc_html_e('Authentication', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="#requests"><?php esc_html_e('Making Requests', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="#endpoints"><?php esc_html_e('Endpoints', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="#errors"><?php esc_html_e('Errors', 'retail-trade-scanner'); ?></a></li>
                    <li><a href="#sdks"><?php esc_html_e('SDKs', 'retail-trade-scanner'); ?></a></li>
                </ul>
            </div>
        </nav>
    </aside>

    <!-- Content -->
    <section class="col-span-9">
        <!-- Overview -->
        <div id="overview" class="card glass-card">
            <div class="card-header">
                <h3 class="card-title m-0"><?php esc_html_e('Overview', 'retail-trade-scanner'); ?></h3>
            </div>
            <div class="card-body">
                <p><?php esc_html_e('Retail Trade Scanner provides a unified REST API to access screening, market data, news, and user portfolio endpoints.', 'retail-trade-scanner'); ?></p>
                <ul class="list">
                    <li><?php esc_html_e('All endpoints are versioned and prefixed via your environment configuration.', 'retail-trade-scanner'); ?></li>
                    <li><?php esc_html_e('All backend routes must be prefixed with /api when called from the frontend (ingress routing).', 'retail-trade-scanner'); ?></li>
                    <li><?php esc_html_e('Responses are JSON. UUIDs are used for identifiers.', 'retail-trade-scanner'); ?></li>
                </ul>
            </div>
        </div>

        <!-- Authentication -->
        <div id="auth" class="card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title m-0"><?php esc_html_e('Authentication', 'retail-trade-scanner'); ?></h3>
            </div>
            <div class="card-body">
                <p><?php esc_html_e('Use Bearer tokens for authenticated routes. Include the Authorization header with each request.', 'retail-trade-scanner'); ?></p>
                <pre class="code-block"><code>GET /api/portfolio
Authorization: Bearer &lt;token&gt;
Accept: application/json</code></pre>
                <p class="text-sm text-muted"><?php esc_html_e('Note: Never hardcode URLs or credentials. Use environment variables configured in your deployment.', 'retail-trade-scanner'); ?></p>
            </div>
        </div>

        <!-- Making Requests -->
        <div id="requests" class="card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title m-0"><?php esc_html_e('Making Requests', 'retail-trade-scanner'); ?></h3>
            </div>
            <div class="card-body">
                <p><?php esc_html_e('Frontend applications must read the backend base URL from REACT_APP_BACKEND_URL and prefix routes with /api. Backend reads its database URL from MONGO_URL.', 'retail-trade-scanner'); ?></p>
                <div class="grid grid-2 gap-md">
                    <div>
                        <h4><?php esc_html_e('JavaScript example', 'retail-trade-scanner'); ?></h4>
                        <pre class="code-block"><code>const base = process.env.REACT_APP_BACKEND_URL; // env-managed
const resp = await fetch(`${base}/api/stocks/search?query=NVDA`);
const data = await resp.json();</code></pre>
                    </div>
                    <div>
                        <h4><?php esc_html_e('Python (FastAPI) example', 'retail-trade-scanner'); ?></h4>
                        <pre class="code-block"><code># Use os.environ.get('MONGO_URL') in backend for DB access
# Do not hardcode ports/URLs; ingress handles routing</code></pre>
                    </div>
                </div>
            </div>
        </div>

        <!-- Endpoints -->
        <div id="endpoints" class="card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title m-0"><?php esc_html_e('Endpoints (Preview)', 'retail-trade-scanner'); ?></h3>
            </div>
            <div class="card-body">
                <div class="endpoints">
                    <div class="endpoint">
                        <div class="method get">GET</div>
                        <div class="path">/api/stocks/search</div>
                        <div class="desc"><?php esc_html_e('Search stocks by symbol or name', 'retail-trade-scanner'); ?></div>
                    </div>
                    <div class="endpoint">
                        <div class="method get">GET</div>
                        <div class="path">/api/news</div>
                        <div class="desc"><?php esc_html_e('Fetch latest market news', 'retail-trade-scanner'); ?></div>
                    </div>
                    <div class="endpoint">
                        <div class="method get">GET</div>
                        <div class="path">/api/portfolio</div>
                        <div class="desc"><?php esc_html_e('Get authenticated user portfolio summary', 'retail-trade-scanner'); ?></div>
                    </div>
                </div>
                <p class="text-sm text-muted mt-md"><?php esc_html_e('Full reference will be expanded as endpoints are finalized.', 'retail-trade-scanner'); ?></p>
            </div>
        </div>

        <!-- Errors -->
        <div id="errors" class="card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title m-0"><?php esc_html_e('Errors', 'retail-trade-scanner'); ?></h3>
            </div>
            <div class="card-body">
                <ul class="list">
                    <li><strong>400</strong> — <?php esc_html_e('Bad request or validation error', 'retail-trade-scanner'); ?></li>
                    <li><strong>401</strong> — <?php esc_html_e('Missing or invalid token', 'retail-trade-scanner'); ?></li>
                    <li><strong>403</strong> — <?php esc_html_e('Not authorized to access resource', 'retail-trade-scanner'); ?></li>
                    <li><strong>404</strong> — <?php esc_html_e('Resource not found', 'retail-trade-scanner'); ?></li>
                    <li><strong>429</strong> — <?php esc_html_e('Rate limit exceeded', 'retail-trade-scanner'); ?></li>
                    <li><strong>5xx</strong> — <?php esc_html_e('Server error', 'retail-trade-scanner'); ?></li>
                </ul>
            </div>
        </div>

        <!-- SDKs & Support -->
        <div id="sdks" class="card glass-card mt-lg">
            <div class="card-header">
                <h3 class="card-title m-0"><?php esc_html_e('SDKs & Support', 'retail-trade-scanner'); ?></h3>
            </div>
            <div class="card-body">
                <p><?php esc_html_e('Official SDKs and Postman collections will be published here. For questions, visit the Help Center or contact us.', 'retail-trade-scanner'); ?></p>
                <div class="flex gap-md mt-md">
                    <a class="btn btn-outline" href="<?php echo esc_url(home_url('/help/')); ?>"><?php esc_html_e('Help Center', 'retail-trade-scanner'); ?></a>
                    <a class="btn btn-primary" href="<?php echo esc_url(home_url('/contact/')); ?>"><?php esc_html_e('Contact Support', 'retail-trade-scanner'); ?></a>
                </div>
            </div>
        </div>
    </section>
</div>

<style>
.api-nav .toc-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: var(--spacing-sm); }
.api-nav .toc-list a { color: var(--gray-700); text-decoration: none; }
.api-nav .toc-list a:hover { color: var(--primary-600); }
.code-block { background: var(--gray-900); color: #fff; padding: var(--spacing-md); border-radius: var(--radius-lg); overflow-x: auto; }
.endpoints .endpoint { display: grid; grid-template-columns: 80px 1fr; gap: var(--spacing-md); padding: var(--spacing-sm) 0; border-bottom: 1px solid var(--gray-200); }
.endpoints .endpoint:last-child { border-bottom: 0; }
.method { font-weight: 800; letter-spacing: .06em; }
.method.get { color: var(--success); }
.path { font-family: var(--font-mono); }
</style>

<?php get_template_part('template-parts/layout/main-shell-end'); ?>

<?php get_footer(); ?>