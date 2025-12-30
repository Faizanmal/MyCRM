import { test as setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

/**
 * Authentication setup for E2E tests
 * 
 * This runs once before all tests and saves the authenticated state
 * to be reused by other test projects.
 */
setup('authenticate', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');

    // Fill in login credentials
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('TestPassword123!');

    // Click login button
    await page.getByRole('button', { name: /sign in|log in/i }).click();

    // Wait for successful login - redirect to dashboard
    await page.waitForURL('/dashboard');

    // Verify we're logged in
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();

    // Save authentication state
    await page.context().storageState({ path: authFile });
});
