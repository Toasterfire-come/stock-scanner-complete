import { test, expect } from '@playwright/test';

async function dismissCookieConsentIfPresent(page) {
  const byTestId = page.getByTestId('cookie-accept-button');
  if (await byTestId.isVisible().catch(() => false)) {
    await byTestId.click();
    return;
  }
  const byRole = page.getByRole('button', { name: /Accept All/i });
  if (await byRole.isVisible().catch(() => false)) {
    await byRole.click();
  }
}

test('mobile marketing home loads and primary CTA visible', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'Desktop Chrome', 'Mobile-only assertion');
  await page.goto('/');
  await dismissCookieConsentIfPresent(page);
  await expect(page.getByRole('heading', { name: /Turn Market Data Into Profitable Trades/i })).toBeVisible({
    timeout: 10000,
  });
  await expect(page.getByRole('link', { name: /Try free — no card required/i })).toBeVisible();
});

test('mobile app nav visible and routes work', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'Desktop Chrome', 'Mobile-only bottom navigation');
  await page.goto('/');
  await dismissCookieConsentIfPresent(page);
  // Navigate to app route (unauthenticated to see layout and nav)
  await page.goto('/app/markets');
  await dismissCookieConsentIfPresent(page);
  // Bottom nav present
  await expect(page.getByRole('navigation', { name: /Primary/i })).toBeVisible();
  // Nav to watchlists
  await dismissCookieConsentIfPresent(page);
  await page.getByRole('link', { name: /Watchlists/i }).click();
  await expect(page).toHaveURL(/\/app\/watchlists/);
});

