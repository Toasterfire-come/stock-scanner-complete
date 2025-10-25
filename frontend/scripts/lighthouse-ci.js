const { execSync } = require('child_process');

// Simple Lighthouse budget run against built site (assumes serve -s build)
const BUDGETS = {
  performance: 0.85,
  accessibility: 0.9,
  'best-practices': 0.9,
  seo: 0.9,
};

function run(cmd) {
  return execSync(cmd, { stdio: 'pipe' }).toString('utf8');
}

function main() {
  console.log('Starting temporary server...');
  const serve = require('serve-handler');
  const http = require('http');
  const server = http.createServer((request, response) => serve(request, response, { public: 'build' }));
  server.listen(5050, async () => {
    try {
      console.log('Running Lighthouse...');
      const res = run('npx lighthouse http://localhost:5050 --quiet --output=json --output-path=stdout');
      const json = JSON.parse(res);
      const cats = json.categories;
      const scores = {
        performance: cats.performance.score,
        accessibility: cats.accessibility.score,
        'best-practices': cats['best-practices'].score,
        seo: cats.seo.score,
      };
      console.log('Lighthouse scores:', scores);
      for (const [k, min] of Object.entries(BUDGETS)) {
        if (scores[k] < min) {
          console.error(`Budget failed for ${k}: ${scores[k]} < ${min}`);
          process.exitCode = 1;
        }
      }
    } catch (e) {
      console.error('Lighthouse run failed:', e.message);
      process.exitCode = 1;
    } finally {
      server.close();
    }
  });
}

main();

