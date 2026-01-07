import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30 * 1000,
  expect: { timeout: 5000 },
  fullyParallel: true,
  reporter: 'list',
  webServer: {
    // Disable CRA eslint plugin during E2E to avoid blocking runtime with overlay errors.
    command: 'DISABLE_ESLINT_PLUGIN=true BROWSER=none yarn start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 180 * 1000,
  },
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'Desktop Chrome', use: { ...devices['Desktop Chrome'] } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 13'] } },
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'] } },
  ],
});

