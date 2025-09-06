import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth');
  });

  test('should display login form by default', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
    await expect(page.getByRole('textbox', { name: /username/i })).toBeVisible();
    await expect(page.getByRole('textbox', { name: /password/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('should toggle between login and register forms', async ({ page }) => {
    // Start with login form
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
    
    // Click toggle to register
    await page.getByRole('button', { name: /create account/i }).click();
    
    // Should show register form
    await expect(page.getByRole('heading', { name: /create account/i })).toBeVisible();
    await expect(page.getByRole('textbox', { name: /first name/i })).toBeVisible();
    await expect(page.getByRole('textbox', { name: /last name/i })).toBeVisible();
    await expect(page.getByRole('textbox', { name: /email/i })).toBeVisible();
    
    // Toggle back to login
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
  });

  test('should show validation errors for invalid login', async ({ page }) => {
    await page.getByRole('textbox', { name: /username/i }).fill('invalid');
    await page.getByRole('textbox', { name: /password/i }).fill('wrong');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Should show error message
    await expect(page.getByText(/invalid credentials/i)).toBeVisible();
  });

  test('should successfully login with valid credentials', async ({ page }) => {
    await page.getByRole('textbox', { name: /username/i }).fill('testuser');
    await page.getByRole('textbox', { name: /password/i }).fill('password');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
  });

  test('should successfully register new user', async ({ page }) => {
    // Switch to register form
    await page.getByRole('button', { name: /create account/i }).click();
    
    // Fill registration form
    await page.getByRole('textbox', { name: /first name/i }).fill('John');
    await page.getByRole('textbox', { name: /last name/i }).fill('Doe');
    await page.getByRole('textbox', { name: /username/i }).fill('johndoe');
    await page.getByRole('textbox', { name: /email/i }).fill('john@example.com');
    await page.getByRole('textbox', { name: /password/i }).fill('password123');
    
    await page.getByRole('button', { name: /create account/i }).click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
  });

  test('should redirect authenticated users away from auth page', async ({ page }) => {
    // First login
    await page.getByRole('textbox', { name: /username/i }).fill('testuser');
    await page.getByRole('textbox', { name: /password/i }).fill('password');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    await expect(page).toHaveURL('/dashboard');
    
    // Try to go back to auth page
    await page.goto('/auth');
    
    // Should redirect back to dashboard
    await expect(page).toHaveURL('/dashboard');
  });
});