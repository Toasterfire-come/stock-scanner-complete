import { test, expect } from "@playwright/test";

test.describe("Auth pages", () => {
  test("Sign up page loads (no crash)", async ({ page }) => {
    await page.goto("/auth/sign-up");
    await expect(page.getByRole("heading", { name: /create your account/i })).toBeVisible();
    await expect(page.getByText(/something went wrong/i)).toHaveCount(0);
  });

  test("Plan selection page loads (no crash)", async ({ page }) => {
    await page.goto("/auth/plan-selection");
    await expect(page.getByRole("heading", { name: /choose your trading plan/i })).toBeVisible();
    await expect(page.getByText(/something went wrong/i)).toHaveCount(0);
  });
});

