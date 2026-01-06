import { test, expect } from "@playwright/test";

async function dismissCookieConsentIfPresent(page) {
  const byTestId = page.getByTestId("cookie-accept-button");
  if (await byTestId.isVisible().catch(() => false)) {
    await byTestId.click();
    return;
  }
  const byRole = page.getByRole("button", { name: /Accept All/i });
  if (await byRole.isVisible().catch(() => false)) {
    await byRole.click();
  }
}

test("public backtest share page renders from mocked API", async ({ page }) => {
  await page.route("**/api/share/backtests/**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        backtest: {
          id: 123,
          name: "My Public Backtest",
          strategy_text: "Buy when RSI < 30, sell when RSI > 70",
          category: "swing_trading",
          symbols: ["AAPL"],
          start_date: "2024-01-01",
          end_date: "2024-12-31",
          initial_capital: 10000,
          share_slug: "my-public-backtest-abc123",
          public_view_count: 42,
          fork_count: 3,
          creator: { username: "alice" },
          results: {
            total_return: 25.5,
            annualized_return: 10.2,
            sharpe_ratio: 1.2,
            max_drawdown: -12.3,
            win_rate: 55,
            profit_factor: 1.4,
            total_trades: 120,
            composite_score: 78,
            quality_grade: "B",
          },
          equity_curve: [10000, 10100, 9900, 11000],
          created_at: new Date().toISOString(),
        },
      }),
    });
  });

  await page.goto("/backtest/my-public-backtest-abc123");
  await dismissCookieConsentIfPresent(page);

  // Basic sanity that page isn't stuck in a loader/error state
  await expect(page.getByText(/My Public Backtest/i)).toBeVisible({ timeout: 15000 });
  await expect(page.getByText(/@alice/i)).toBeVisible();
});

test("embed backtest page renders from mocked API", async ({ page }) => {
  await page.route("**/api/share/backtests/**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        backtest: {
          id: 123,
          name: "Embed Backtest",
          category: "swing_trading",
          symbols: ["AAPL"],
          share_slug: "embed-backtest-abc123",
          results: { total_return: 25.5, sharpe_ratio: 1.2, max_drawdown: -12.3 },
          equity_curve: [10000, 10100, 9900, 11000],
        },
      }),
    });
  });

  await page.goto("/embed/backtest/embed-backtest-abc123");
  await dismissCookieConsentIfPresent(page);
  await expect(page.getByText(/Embed Backtest/i)).toBeVisible({ timeout: 15000 });
});

