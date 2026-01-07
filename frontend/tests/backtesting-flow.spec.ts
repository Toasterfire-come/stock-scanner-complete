import { test, expect } from "@playwright/test";

async function seedAuth(page) {
  await page.addInitScript(() => {
    // Bypass cookie prompt
    try {
      localStorage.setItem("cookie_consent", "accepted");
      localStorage.setItem("cookie_consent_date", new Date().toISOString());
    } catch {}

    // Seed SecureAuthContext (it accepts plain JSON too)
    const user = { id: 1, username: "e2e", email: "e2e@example.com", plan: "plus", isVerified: true };
    try {
      localStorage.setItem("rts_user", JSON.stringify(user));
      localStorage.setItem("rts_token", "test-token");
      localStorage.setItem(
        "session",
        JSON.stringify({ startTime: Date.now(), lastActivity: Date.now(), isActive: true })
      );
    } catch {}
  });
}

test("backtester create/run shows advanced metrics and can create share link (mocked API)", async ({ page }) => {
  await seedAuth(page);

  // Health pings
  await page.route("**/health/**", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "healthy" }) });
  });

  // History list on mount
  await page.route("**/backtesting/list/**", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, backtests: [] }) });
  });

  // Create
  await page.route("**/backtesting/create/**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ success: true, backtest_id: 101, status: "pending", backtests_remaining: -1 }),
    });
  });

  // Run
  await page.route("**/backtesting/101/run/**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        results: {
          total_return: 12.34,
          annualized_return: 8.9,
          sharpe_ratio: 1.23,
          sortino_ratio: 1.8,
          calmar_ratio: 0.7,
          omega_ratio: 1.4,
          max_drawdown: -10.1,
          win_rate: 55.5,
          profit_factor: 1.2,
          total_trades: 42,
          winning_trades: 23,
          losing_trades: 19,
          ulcer_index: 4.2,
          var_95: -2.5,
          cvar_95: -3.8,
          t_statistic: 2.1,
          p_value: 0.0321,
          composite_score: 78.0,
          quality_grade: "B",
        },
        trades: [],
        equity_curve: [10000, 10100, 9900, 11234],
        achievements_unlocked: [],
      }),
    });
  });

  // Get details
  await page.route("**/backtesting/101/**", async (route) => {
    // Avoid matching the /run/ above
    if (route.request().url().includes("/run/")) return route.fallback();
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        backtest: {
          id: 101,
          name: "E2E Strategy",
          strategy_text: "Buy when RSI < 30, sell when RSI > 70",
          generated_code: "",
          category: "swing_trading",
          symbols: ["AAPL"],
          start_date: "2024-01-01",
          end_date: "2024-12-31",
          initial_capital: 10000,
          status: "completed",
          error_message: "",
          is_public: false,
          share_slug: null,
          public_view_count: 0,
          fork_count: 0,
          forked_from: null,
          results: {
            total_return: 12.34,
            annualized_return: 8.9,
            sharpe_ratio: 1.23,
            sortino_ratio: 1.8,
            calmar_ratio: 0.7,
            omega_ratio: 1.4,
            max_drawdown: -10.1,
            win_rate: 55.5,
            profit_factor: 1.2,
            total_trades: 42,
            winning_trades: 23,
            losing_trades: 19,
            ulcer_index: 4.2,
            var_95: -2.5,
            cvar_95: -3.8,
            t_statistic: 2.1,
            p_value: 0.0321,
            composite_score: 78.0,
            quality_grade: "B",
          },
          trades: [],
          equity_curve: [10000, 10100, 9900, 11234],
          created_at: new Date().toISOString(),
          completed_at: new Date().toISOString(),
        },
      }),
    });
  });

  // Share link creation
  await page.route("**/share/backtests/101/create", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ success: true, slug: "e2e-strategy-abc123", share_url: "/backtest/e2e-strategy-abc123" }),
    });
  });

  await page.goto("/app/backtesting");

  await expect(page.getByRole("heading", { name: /AI Backtesting/i })).toBeVisible({ timeout: 15000 });
  await page.getByTestId("strategy-name-input").fill("E2E Strategy");
  await page.getByTestId("strategy-text-input").fill("Buy when RSI < 30, sell when RSI > 70");

  await page.getByTestId("run-backtest-btn").click();

  // Results should show advanced metrics section values
  await expect(page.getByText(/Sortino Ratio/i)).toBeVisible({ timeout: 15000 });
  await expect(page.getByText(/Calmar Ratio/i)).toBeVisible();
  await expect(page.getByText(/Omega Ratio/i)).toBeVisible();
  await expect(page.getByText(/Strategy Quality:/i)).toBeVisible();

  // Make public share link toggles the badge to Public
  await page.getByRole("button", { name: /Make Public Link/i }).click();
  await expect(page.getByText(/^Public$/)).toBeVisible({ timeout: 10000 });
});

