#!/usr/bin/env node

/**
 * Comprehensive Page Error Testing Script
 * Tests all pages on the production frontend and collects errors
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// Configuration
const BASE_URL = process.env.TEST_URL || 'https://tradescanpro.com';
const OUTPUT_FILE = 'page-errors-report.json';
const TIMEOUT = 30000; // 30 seconds per page

// All routes to test (extracted from the frontend structure)
const ROUTES = [
  // Public pages
  '/',
  '/about',
  '/features',
  '/pricing',
  '/contact',
  '/help',
  '/demo',
  '/status',
  '/markets',
  '/partners',
  '/press',
  '/resources',

  // Auth pages
  '/signin',
  '/signup',
  '/forgot-password',
  '/reset-password',

  // Legal pages
  '/privacy',
  '/terms',

  // Documentation
  '/docs',
  '/docs/getting-started',
  '/docs/getting-started/create-account',
  '/docs/getting-started/dashboard',
  '/docs/getting-started/first-screener',

  // App pages (may require auth)
  '/app',
  '/app/dashboard',
  '/app/stocks',
  '/app/watchlists',
  '/app/screeners',
  '/app/alerts',
  '/app/portfolio',
  '/app/markets',
  '/app/news',
  '/app/calendar',
  '/app/backtesting',
  '/app/settings',
  '/app/profile',
  '/app/billing',

  // Account pages
  '/account/profile',
  '/account/settings',
  '/account/billing',
  '/account/password',
  '/account/notifications',

  // Billing
  '/checkout',
  '/checkout/success',
  '/checkout/failure',

  // Enterprise
  '/enterprise',
  '/enterprise/contact',
  '/enterprise/solutions',

  // Education
  '/education',
  '/education/courses',
  '/education/glossary',
  '/education/progress',
];

class PageTester {
  constructor() {
    this.browser = null;
    this.results = [];
    this.startTime = Date.now();
  }

  async init() {
    console.log('🚀 Launching browser...');
    this.browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-web-security', // Allow CORS for testing
      ]
    });
  }

  async testPage(route) {
    const url = `${BASE_URL}${route}`;
    const page = await this.browser.newPage();

    const result = {
      route,
      url,
      timestamp: new Date().toISOString(),
      errors: [],
      warnings: [],
      consoleMessages: [],
      networkErrors: [],
      status: 'unknown',
      loadTime: 0,
      screenshot: null,
    };

    try {
      console.log(`\n📄 Testing: ${url}`);

      // Collect console messages
      page.on('console', (msg) => {
        const type = msg.type();
        const text = msg.text();

        if (type === 'error') {
          result.errors.push({
            type: 'console',
            message: text,
            timestamp: new Date().toISOString()
          });
        } else if (type === 'warning') {
          result.warnings.push({
            type: 'console',
            message: text,
            timestamp: new Date().toISOString()
          });
        }

        result.consoleMessages.push({
          type,
          text: text.substring(0, 500), // Limit length
        });
      });

      // Collect page errors
      page.on('pageerror', (error) => {
        result.errors.push({
          type: 'page',
          message: error.message,
          stack: error.stack,
          timestamp: new Date().toISOString()
        });
      });

      // Collect failed requests
      page.on('requestfailed', (request) => {
        result.networkErrors.push({
          url: request.url(),
          method: request.method(),
          failure: request.failure()?.errorText || 'Unknown error',
          timestamp: new Date().toISOString()
        });
      });

      // Collect response errors
      page.on('response', (response) => {
        const status = response.status();
        const url = response.url();

        if (status >= 400) {
          result.networkErrors.push({
            url,
            status,
            statusText: response.statusText(),
            timestamp: new Date().toISOString()
          });
        }
      });

      // Navigate to page
      const startTime = Date.now();
      const response = await page.goto(url, {
        waitUntil: 'networkidle2',
        timeout: TIMEOUT
      });
      result.loadTime = Date.now() - startTime;

      // Get response status
      result.status = response.status();
      result.statusText = response.statusText();

      // Wait a bit for any async errors
      await page.waitForTimeout(2000);

      // Check for specific error elements in the page
      const hasErrorElement = await page.evaluate(() => {
        const errorSelectors = [
          '[class*="error"]',
          '[class*="Error"]',
          '[data-testid*="error"]',
          '.alert-error',
          '.error-message',
        ];

        for (const selector of errorSelectors) {
          const element = document.querySelector(selector);
          if (element && element.textContent.trim()) {
            return {
              found: true,
              text: element.textContent.trim().substring(0, 200)
            };
          }
        }
        return { found: false };
      });

      if (hasErrorElement.found) {
        result.errors.push({
          type: 'dom',
          message: `Error element found: ${hasErrorElement.text}`,
          timestamp: new Date().toISOString()
        });
      }

      // Take screenshot if there are errors
      if (result.errors.length > 0 || result.networkErrors.length > 0) {
        const screenshotPath = `screenshots/${route.replace(/\//g, '_') || 'home'}.png`;
        await page.screenshot({
          path: screenshotPath,
          fullPage: false
        });
        result.screenshot = screenshotPath;
      }

      // Determine overall status
      if (result.status >= 500) {
        result.testStatus = 'FAIL';
      } else if (result.errors.length > 0 || result.networkErrors.some(e => e.status >= 400)) {
        result.testStatus = 'ERROR';
      } else if (result.warnings.length > 0) {
        result.testStatus = 'WARN';
      } else {
        result.testStatus = 'PASS';
      }

      // Log summary
      const errorCount = result.errors.length;
      const networkErrorCount = result.networkErrors.length;
      const warningCount = result.warnings.length;

      console.log(`   Status: ${result.status} ${result.statusText}`);
      console.log(`   Load Time: ${result.loadTime}ms`);
      console.log(`   Errors: ${errorCount}`);
      console.log(`   Network Errors: ${networkErrorCount}`);
      console.log(`   Warnings: ${warningCount}`);
      console.log(`   Result: ${result.testStatus}`);

      if (errorCount > 0) {
        console.log(`   ⚠️  First Error: ${result.errors[0].message.substring(0, 100)}`);
      }
      if (networkErrorCount > 0) {
        console.log(`   🌐 First Network Error: ${result.networkErrors[0].url} - ${result.networkErrors[0].failure || result.networkErrors[0].status}`);
      }

    } catch (error) {
      result.testStatus = 'FAIL';
      result.errors.push({
        type: 'test',
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString()
      });
      console.log(`   ❌ FAILED: ${error.message}`);
    } finally {
      await page.close();
    }

    return result;
  }

  async runAllTests() {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`Testing ${ROUTES.length} pages on ${BASE_URL}`);
    console.log(`${'='.repeat(60)}`);

    // Create screenshots directory
    if (!fs.existsSync('screenshots')) {
      fs.mkdirSync('screenshots');
    }

    for (const route of ROUTES) {
      const result = await this.testPage(route);
      this.results.push(result);
    }
  }

  generateReport() {
    const endTime = Date.now();
    const duration = endTime - this.startTime;

    const summary = {
      totalPages: this.results.length,
      passed: this.results.filter(r => r.testStatus === 'PASS').length,
      warnings: this.results.filter(r => r.testStatus === 'WARN').length,
      errors: this.results.filter(r => r.testStatus === 'ERROR').length,
      failed: this.results.filter(r => r.testStatus === 'FAIL').length,
      totalErrors: this.results.reduce((sum, r) => sum + r.errors.length, 0),
      totalNetworkErrors: this.results.reduce((sum, r) => sum + r.networkErrors.length, 0),
      totalWarnings: this.results.reduce((sum, r) => sum + r.warnings.length, 0),
      averageLoadTime: Math.round(
        this.results.reduce((sum, r) => sum + r.loadTime, 0) / this.results.length
      ),
      duration,
      timestamp: new Date().toISOString(),
    };

    const report = {
      summary,
      results: this.results,
    };

    // Save full report
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(report, null, 2));

    // Generate readable summary
    const summaryText = this.generateTextSummary(summary);
    fs.writeFileSync('page-errors-summary.txt', summaryText);

    // Generate error details
    const errorDetails = this.generateErrorDetails();
    fs.writeFileSync('page-errors-details.md', errorDetails);

    return report;
  }

  generateTextSummary(summary) {
    return `
${'='.repeat(60)}
PAGE ERROR TESTING SUMMARY
${'='.repeat(60)}

Base URL: ${BASE_URL}
Test Duration: ${(summary.duration / 1000).toFixed(2)}s
Timestamp: ${summary.timestamp}

RESULTS:
  Total Pages: ${summary.totalPages}
  ✅ Passed: ${summary.passed}
  ⚠️  Warnings: ${summary.warnings}
  ❌ Errors: ${summary.errors}
  💥 Failed: ${summary.failed}

DETAILS:
  Total Errors: ${summary.totalErrors}
  Network Errors: ${summary.totalNetworkErrors}
  Warnings: ${summary.totalWarnings}
  Avg Load Time: ${summary.averageLoadTime}ms

${'='.repeat(60)}

PAGES WITH ERRORS:
${this.results
  .filter(r => r.testStatus === 'ERROR' || r.testStatus === 'FAIL')
  .map(r => `  ${r.route} - ${r.testStatus} (${r.errors.length} errors, ${r.networkErrors.length} network errors)`)
  .join('\n') || '  None'}

${'='.repeat(60)}
`;
  }

  generateErrorDetails() {
    let md = '# Page Error Details\n\n';
    md += `**Generated:** ${new Date().toISOString()}\n\n`;
    md += `**Base URL:** ${BASE_URL}\n\n`;
    md += '---\n\n';

    // Group errors by type
    const errorsByType = {};
    const networkErrorsByUrl = {};

    this.results.forEach(result => {
      if (result.errors.length === 0 && result.networkErrors.length === 0) return;

      md += `## ${result.route}\n\n`;
      md += `- **URL:** ${result.url}\n`;
      md += `- **Status:** ${result.status} ${result.statusText}\n`;
      md += `- **Load Time:** ${result.loadTime}ms\n`;
      md += `- **Test Result:** ${result.testStatus}\n\n`;

      if (result.networkErrors.length > 0) {
        md += '### Network Errors:\n\n';
        result.networkErrors.forEach(error => {
          md += `- **${error.url}**\n`;
          md += `  - Status: ${error.status || 'N/A'}\n`;
          md += `  - Error: ${error.failure || error.statusText || 'Unknown'}\n\n`;

          // Track for grouping
          const key = error.url;
          networkErrorsByUrl[key] = (networkErrorsByUrl[key] || 0) + 1;
        });
      }

      if (result.errors.length > 0) {
        md += '### JavaScript Errors:\n\n';
        result.errors.forEach(error => {
          md += `- **Type:** ${error.type}\n`;
          md += `  - Message: \`${error.message}\`\n`;
          if (error.stack) {
            md += `  - Stack: \`\`\`\n${error.stack.substring(0, 500)}\n\`\`\`\n`;
          }
          md += '\n';

          // Track for grouping
          const key = `${error.type}: ${error.message.substring(0, 100)}`;
          errorsByType[key] = (errorsByType[key] || 0) + 1;
        });
      }

      if (result.warnings.length > 0) {
        md += '### Warnings:\n\n';
        result.warnings.slice(0, 5).forEach(warning => {
          md += `- ${warning.message.substring(0, 200)}\n`;
        });
        if (result.warnings.length > 5) {
          md += `- ... and ${result.warnings.length - 5} more warnings\n`;
        }
        md += '\n';
      }

      md += '---\n\n';
    });

    // Add error summary
    md += '## Error Summary by Type\n\n';
    Object.entries(errorsByType)
      .sort((a, b) => b[1] - a[1])
      .forEach(([error, count]) => {
        md += `- **${count}x** ${error}\n`;
      });

    md += '\n## Network Error Summary by URL\n\n';
    Object.entries(networkErrorsByUrl)
      .sort((a, b) => b[1] - a[1])
      .forEach(([url, count]) => {
        md += `- **${count}x** ${url}\n`;
      });

    return md;
  }

  async cleanup() {
    if (this.browser) {
      await this.browser.close();
    }
  }
}

// Main execution
async function main() {
  const tester = new PageTester();

  try {
    await tester.init();
    await tester.runAllTests();
    const report = tester.generateReport();

    console.log('\n' + fs.readFileSync('page-errors-summary.txt', 'utf-8'));
    console.log(`\n✅ Full report saved to: ${OUTPUT_FILE}`);
    console.log(`📝 Error details saved to: page-errors-details.md`);
    console.log(`📊 Summary saved to: page-errors-summary.txt`);

    // Exit with error code if there are failures
    if (report.summary.failed > 0 || report.summary.errors > 0) {
      process.exit(1);
    }

  } catch (error) {
    console.error('❌ Test execution failed:', error);
    process.exit(1);
  } finally {
    await tester.cleanup();
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { PageTester };
