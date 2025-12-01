import { test, expect } from '@playwright/test';

test('mobile marketing home loads and primary CTA visible', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /trade scan pro/i })).toBeVisible({ timeout: 10000 });
  await expect(page.getByRole('link', { name: /Try Now for Free/i })).toBeVisible();
});

test('mobile app nav visible and routes work', async ({ page }) => {
  await page.goto('/');
  // Navigate to app route (unauthenticated to see layout and nav)
  await page.goto('/app/markets');
  // Bottom nav present
  await expect(page.getByRole('navigation', { name: /Primary/i })).toBeVisible();
  // Nav to watchlists
  await page.getByRole('link', { name: /Watchlists/i }).click();
  await expect(page).toHaveURL(/\/app\/watchlists/);
});

