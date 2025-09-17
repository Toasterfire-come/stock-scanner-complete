#!/usr/bin/env node
/*
  Headless site crawl: logs into tradescanpro.com and visits key routes,
  capturing console errors, page errors, and failed network requests.
*/

const puppeteer = require('puppeteer');

const BASE_URL = process.env.TSP_BASE_URL || 'https://tradescanpro.com';
const USERNAME = process.env.TSP_USERNAME || 'carter.kiefer2010@outlook.com';
const PASSWORD = process.env.TSP_PASSWORD || 'C2rt3rK#2010';

const ROUTES = [
  '/',
  '/app/dashboard',
  '/app/stocks',
  '/app/top-movers',
  '/app/watchlists',
  '/app/portfolio',
  '/app/alerts',
  '/app/news',
];

async function run() {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1366, height: 850, deviceScaleFactor: 1 });

  const globalErrors = { consoleErrors: [], pageErrors: [], requestFailures: [] };

  page.on('console', (msg) => {
    const type = msg.type();
    if (type === 'error') {
      globalErrors.consoleErrors.push(msg.text());
    }
  });
  page.on('pageerror', (err) => {
    globalErrors.pageErrors.push(String(err));
  });
  page.on('requestfailed', (req) => {
    const url = req.url(); const failure = req.failure();
    globalErrors.requestFailures.push({ url, errorText: failure && failure.errorText });
  });

  // Navigate to sign-in
  await page.goto(`${BASE_URL}/auth/sign-in`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForSelector('#username', { timeout: 30000 });
  await page.type('#username', USERNAME, { delay: 10 });
  await page.type('#password', PASSWORD, { delay: 10 });
  await Promise.all([
    page.click('button[type="submit"]'),
    page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 60000 }).catch(() => {})
  ]);

  // If not redirected, try manual navigation to dashboard
  const currentPath = new URL(page.url()).pathname;
  if (!currentPath.startsWith('/app')) {
    await page.goto(`${BASE_URL}/app/dashboard`, { waitUntil: 'networkidle2', timeout: 60000 }).catch(() => {});
  }

  const results = {};

  for (const path of ROUTES) {
    const routeErrors = { consoleErrors: [], pageErrors: [], requestFailures: [], apiCalls: [] };
    const routeListener = {
      console: (msg) => { if (msg.type() === 'error') routeErrors.consoleErrors.push(msg.text()); },
      pageerror: (err) => routeErrors.pageErrors.push(String(err)),
      requestfailed: (req) => routeErrors.requestFailures.push({ url: req.url(), errorText: req.failure() && req.failure().errorText }),
      response: async (res) => {
        try {
          const url = res.url();
          if (url.includes('https://api.retailtradescanner.com/api/')) {
            routeErrors.apiCalls.push({ url, status: res.status() });
          }
        } catch {}
      },
    };
    page.on('console', routeListener.console);
    page.on('pageerror', routeListener.pageerror);
    page.on('requestfailed', routeListener.requestfailed);
    page.on('response', routeListener.response);

    try {
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2', timeout: 60000 });
      // small idle wait to allow late logs
      await new Promise((r) => setTimeout(r, 800));
    } catch (e) {
      routeErrors.pageErrors.push(`Navigation error: ${e && e.message}`);
    }

    results[path] = routeErrors;

    page.off('console', routeListener.console);
    page.off('pageerror', routeListener.pageerror);
    page.off('requestfailed', routeListener.requestfailed);
    page.off('response', routeListener.response);
  }

  await browser.close();

  // Summarize
  const summary = Object.entries(results).map(([path, r]) => ({
    path,
    consoleErrors: r.consoleErrors.length,
    pageErrors: r.pageErrors.length,
    requestFailures: r.requestFailures.length,
  }));

  const hasIssues = summary.some(s => s.consoleErrors || s.pageErrors || s.requestFailures);
  console.log(JSON.stringify({ baseUrl: BASE_URL, summary, details: results, hasIssues }, null, 2));
  process.exit(hasIssues ? 2 : 0);
}

run().catch((e) => { console.error(e); process.exit(1); });

