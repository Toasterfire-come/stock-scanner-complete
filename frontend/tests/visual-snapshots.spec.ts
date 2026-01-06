import { test, expect } from "@playwright/test";
import path from "path";
import fs from "fs";

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

test("visual snapshots (marketing + blog + share + embed + protected)", async ({ page }, testInfo) => {
  // Mock share endpoint for stable public pages.
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

  const shots = [
    { name: "home", path: "/" },
    { name: "pricing", path: "/pricing" },
    { name: "blog", path: "/blog" },
    { name: "blog-post", path: "/blog/understanding-sharpe-ratio-a-beginners-guide" },
    { name: "public-backtest", path: "/backtest/my-public-backtest-abc123" },
    { name: "embed-backtest", path: "/embed/backtest/my-public-backtest-abc123" },
    { name: "protected-backtesting", path: "/app/backtesting" },
  ];

  await fs.promises.mkdir(path.resolve(process.cwd(), "visual-snapshots"), { recursive: true });

  for (const s of shots) {
    await page.goto(s.path);
    await dismissCookieConsentIfPresent(page);
    // basic smoke: page should have something visible
    await expect(page.locator("body")).toBeVisible();
    await page.waitForTimeout(250);
    await page.screenshot({
      path: path.resolve(process.cwd(), "visual-snapshots", `visual-${s.name}.png`),
      fullPage: true,
    });
  }
});

