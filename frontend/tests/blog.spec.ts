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

test('blog index loads and a post opens', async ({ page }) => {
  await page.goto('/blog');
  await dismissCookieConsentIfPresent(page);

  await expect(page.getByRole('heading', { name: 'Blog' })).toBeVisible({ timeout: 10000 });
  // First post card should exist
  const firstPostLink = page.locator('a[href^="/blog/"]').first();
  await expect(firstPostLink).toBeVisible();

  await firstPostLink.click({ force: true });
  await expect(page).toHaveURL(/\/blog\//);
  // Post title should render as h1
  await expect(page.locator('h1').first()).toBeVisible();
});

