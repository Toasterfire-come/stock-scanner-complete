#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import puppeteer from 'puppeteer';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const FINANCE = [
  'finance',
  'stocks',
  'stock market',
  'stock screener',
  'stock filter',
];

const INTENTS = [
  '"write for us"',
  '"guest post"',
  '"submit article"',
  '"contribute"',
  '"become a contributor"',
  'inurl:write-for-us',
  'inurl:guest-post',
];

function buildQueries() {
  const q = [];
  for (const f of FINANCE) {
    for (const i of INTENTS) {
      q.push(`${i} ${f}`);
    }
  }
  return q;
}

function parseArgs() {
  const args = process.argv.slice(2);
  const out = { max: 50, csv: path.resolve('/workspace/outreach_targets.csv') };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === '--max') { out.max = Number(args[++i] || 50); }
    else if (a === '--csv') { out.csv = path.resolve(args[++i] || out.csv); }
  }
  return out;
}

async function scrapeDDGLite(page, query, limit = 10) {
  const url = `https://lite.duckduckgo.com/lite/?q=${encodeURIComponent(query)}`;
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  const results = await page.$$eval('a', (as) => {
    const out = [];
    for (const a of as) {
      const href = a.getAttribute('href') || '';
      const txt = a.textContent?.trim() || '';
      if (href.startsWith('http') && !href.includes('duckduckgo.com/l/')) {
        out.push({ url: href, title: txt });
      }
      if (out.length >= 50) break;
    }
    return out;
  });
  // Deduplicate by URL
  const uniq = [];
  const seen = new Set();
  for (const r of results) {
    if (!seen.has(r.url)) { seen.add(r.url); uniq.push(r); }
    if (uniq.length >= limit) break;
  }
  return uniq;
}

async function scrapeBingHTML(page, query, limit = 10) {
  const url = `https://www.bing.com/search?q=${encodeURIComponent(query)}`;
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  const results = await page.$$eval('li.b_algo h2 a', (as) => {
    const out = [];
    for (const a of as) {
      const href = a.getAttribute('href') || '';
      const txt = a.textContent?.trim() || '';
      if (href.startsWith('http')) out.push({ url: href, title: txt });
      if (out.length >= 50) break;
    }
    return out;
  });
  const uniq = [];
  const seen = new Set();
  for (const r of results) {
    if (!seen.has(r.url)) { seen.add(r.url); uniq.push(r); }
    if (uniq.length >= limit) break;
  }
  return uniq;
}

function normDomain(str) {
  try {
    const u = new URL(str);
    let h = (u.hostname || '').toLowerCase();
    if (h.startsWith('www.')) h = h.slice(4);
    return h;
  } catch { return ''; }
}

async function verifyContributor(page, url) {
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    const text = await page.evaluate(() => document.body?.innerText?.toLowerCase() || '');
    return (
      text.includes('write for us') ||
      text.includes('guest post') ||
      text.includes('submit article') ||
      text.includes('become a contributor') ||
      /contribut(e|or)/i.test(text)
    );
  } catch { return false; }
}

async function estimatePopularity(page, domain) {
  try {
    const url = `https://www.bing.com/search?q=${encodeURIComponent('site:' + domain)}`;
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    const text = await page.$eval('#b_tween .sb_count, .sb_count', (el) => el.textContent || '');
    const digits = (text || '').replace(/[^0-9]/g, '');
    return digits ? Number(digits) : 0;
  } catch { return 0; }
}

function buildPrompt(domain, targetUrl) {
  const anchors = [
    ['professional stock screener', 'https://tradescanpro.com/'],
    ['stock screener with alerts', 'https://tradescanpro.com/'],
    ['watchlists and portfolios', 'https://tradescanpro.com/'],
    ['fair price and insider trading metrics', 'https://tradescanpro.com/'],
    ['in-depth individual stock information', 'https://tradescanpro.com/'],
  ].map(([a, u]) => `${a} -> ${u}`).join('; ');
  return `You are a finance writer crafting an authoritative, SEO-optimized article for the site ${domain} (target URL: ${targetUrl}).\n\nTopic: A comprehensive, beginner-to-pro guide covering the U.S. stock market with examples, including how to discover opportunities using screeners.\n\nRequirements:\n- Format: 1,600–2,200 words; clear headings (H2/H3), short paragraphs, bullet lists where helpful.\n- Include 2–3 royalty-free image suggestions with detailed alt text (e.g., Image Idea: … | Alt: …). Do NOT include actual image URLs.\n- Include a short code snippet or table where relevant (e.g., comparing screener criteria).\n- Provide actionable steps, common pitfalls, and pro tips.\n- Include 2–3 internal link suggestions placeholders for ${domain} (write as: Internal Link Idea: … — URL TBD).\n- Include 2–3 external references to reputable sources (Investopedia, SEC, etc.).\n- Include 2–3 contextual backlinks to Trade Scan Pro using natural anchor text; use the following anchor ideas and URLs (select 2–3 where most relevant): ${anchors}\n- Mention Trade Scan Pro’s capabilities: alerts, watchlists, portfolios, fair price, insider trading metrics, in-depth stock information.\n- Tone: expert, practical, and trustworthy. Avoid hype. Cite sources where appropriate.\n- SEO: compelling title tag (<=60 chars), meta description (<=155 chars), and an FAQ section (4–6 Q&As) suitable for rich results.\nOutput:\n- Title:\n- Meta description:\n- Outline (H2/H3):\n- Article body (with inline Image Idea blocks):\n- FAQ:\n- Internal Link Ideas:\n- External Sources:`;
}

async function main() {
  const { max, csv } = parseArgs();
  const queries = buildQueries();
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox','--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36');

  const results = [];
  const seenUrls = new Set();
  const seenDomains = new Set();

  for (const q of queries) {
    // Try DDG lite first, then Bing HTML
    let found = [];
    try { found = await scrapeDDGLite(page, q, 15); } catch {}
    if (found.length < 5) {
      try { const extra = await scrapeBingHTML(page, q, 15); found = found.concat(extra); } catch {}
    }

    for (const r of found) {
      const url = r.url;
      if (!url || seenUrls.has(url)) continue;
      const domain = normDomain(url);
      if (!domain) continue;
      // Quick filter: URL hints
      const lower = url.toLowerCase();
      if (!(lower.includes('write-for-us') || lower.includes('guest') || lower.includes('contribute') || lower.includes('submit'))) {
        // Verify by visiting
        const ok = await verifyContributor(page, url);
        if (!ok) continue;
      }
      seenUrls.add(url);
      if (seenDomains.has(domain)) continue; // prefer unique domains
      seenDomains.add(domain);
      const popularity = await estimatePopularity(page, domain);
      results.push({ domain, url, title: r.title || '', monthly_visitors: popularity });
      if (results.length >= max) break;
    }
    if (results.length >= max) break;
  }

  // Rank by popularity
  results.sort((a, b) => (b.monthly_visitors || 0) - (a.monthly_visitors || 0));

  // Add prompts and export CSV
  const lines = [];
  lines.push(['domain','url','title','monthly_visitors','prompt'].join(','));
  for (const r of results) {
    const prompt = buildPrompt(r.domain, r.url).replaceAll('\n', ' ').replaceAll('"', '""');
    const row = [r.domain, r.url, (r.title||'').replaceAll('"','""'), String(r.monthly_visitors||0), `"${prompt}"`].join(',');
    lines.push(row);
  }
  fs.writeFileSync(csv, lines.join('\n'), 'utf-8');
  console.log(`Saved ${results.length} rows to ${csv}`);
  await browser.close();
}

main().catch((err) => { console.error(err); process.exit(1); });

