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

test('unauthenticated backtesting route shows access restricted', async ({ page }) => {
  await page.goto('/app/backtesting');
  await dismissCookieConsentIfPresent(page);

  await expect(page.getByText(/Access Restricted/i)).toBeVisible({ timeout: 10000 });
  const main = page.getByRole('main');
  await expect(main.getByRole('link', { name: /Sign In/i })).toBeVisible();
  await expect(main.getByRole('link', { name: /Create Free Account/i })).toBeVisible();
});

